# -*- coding: utf-8 -*-
"""
    lantz_drivers.attocube.anc300
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the ANC300 open-loop positioner controller.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.

"""
from time import sleep
from timeit import default_timer

from lantz_core.has_features import channel, set_feat
from lantz_core.channel import Channel
from lantz_core.features import Unicode, Float, Feature, Int
from lantz_core.action import Action
from lantz_core.errors import InvalidCommand, LantzError
from lantz_core.backends.visa import VisaMessageBased, errors
from lantz_core.unit import UNIT_SUPPORT, get_unit_registry


def check_answer(res, msg):
    """Check the message returned by the ANC for errors.

    Parameters
    ----------
    msg : unicode
        Answer to the command sent to the ANC300.

    Raises
    ------
    InvalidCommand :
        Raised if an error was signaled by the instrument.

    """
    if not res:
        err = ' '.join(msg.split('\r\n')[:-1])
        raise InvalidCommand(err)


class ANCModule(Channel):
    """Generic base class for ANC300 modules.

    """
    #: Serial number of the module.
    serial_number = Unicode('getser {ch_id}')

    #: Current operating mode of the module.
    mode = Unicode('getm {ch_id}', 'setm {ch_id} {}')

    #: Current value of the saved capacitance. Can be None if the value was
    # never measured.
    saved_capacitance = Feature('getc {ch_id}')

    @Action()
    def stop_motion(self):
        """Stop any motion.

        """
        res, msg = self.parent.anc_query('stop {}'.format(self.ch_id))
        check_answer(res, msg)

    @Action(units=('V', (None)))
    def read_output_voltage(self):
        """Read the voltage currently applied on the module.

        """
        res, msg = self.parent.anc_query('geto {}'.format((self.ch_id)))
        check_answer(res, msg)
        return float(msg.split('\r\n')[0])

    @Action(units=('muF', (None)))
    def read_saved_capacitance(self):
        """Read the saved capacitance load for this module.

        """
        res, msg = self.parent.anc_query('getc {}'.format((self.ch_id)))
        check_answer(res, msg)
        val = msg.split('\r\n')[0]
        return float(msg.split('\r\n')[0]) if val != '?' else None

    @Action()
    def measure_capacitance(self, block=False, timeout=10):
        """Ask the system to measure the capacitance.

        Parameters
        ----------
        block : bool, optional
            Whether or not to wait on the measure to finish before returning.
        timeout : float, optional
            Timeout to use when waiting for measure completion.

        Returns
        -------
        value : float, Quantity or None
            Return the new measured value if block is True, else return None.
            The value can be read at a later time using read_saved_capacitance
            but first wait_for_capacitance_measure should be called to ensure
            that the measure is over.

        """
        with self.lock():
            self.clear_cache(features=('saved_capacitance', 'mode'))
            self.parent.anc_query('setm {} cap'.format(self.ch_id))
            if block:
                self.wait_for_capacitance_measure(timeout)
                return self.read_saved_capacitance()

    @Action()
    def wait_for_capacitance_measure(self, timeout=10):
        """Wait for the capacitance measurement to finish.

        """
        with self.lock():
            self.parent.write('capw {}'.format(self.ch_id))
            self._wait_for(timeout)

    def _wait_for(self, timeout):
        """Wait for completion of an operation.

        """
        t = 0
        while t < timeout:
            try:
                tic = default_timer()
                msg = self.parent.read()
                check_answer(msg)
            except errors.VisaIOError as e:
                if e.error_code != errors.VI_ERROR_TMO:
                    raise
                sleep(0.1)
                t += default_timer() - tic

    def _post_get_saved_capacitance(self, feat, value):
        """Transform the value returned by the instrument.

        """
        if value == '?':
            return None

        val = float(value)
        if UNIT_SUPPORT:
            val *= get_unit_registry().parse_unit('muF')
        return val


class ANCStepper(ANCModule):
    """Base class for ANC300 stepper modules.

    """
    #: Stepping frequency.
    frequency = Float('getf {ch_id}', 'setf {ch_id} {}', unit='Hz',
                      limits='frequency')

    #: Stepping amplitude.
    amplitude = Float('getv {ch_id}', 'setv {ch_id} {}', unit='V',
                      limits=(0, 150, 1e-3), discard={'limits': ['frequency']})

    #: Trigger triggering an up step
    up_trigger = Int('gettu {ch_id}', 'settu {ch_id} {}', values=range(1, 8))

    #: Trigger triggering a down step
    down_trigger = Int('gettd {ch_id}', 'settd {ch_id} {}', values=range(1, 8))

    mode = set_feat(mapping={'Ground': 'gnd', 'Step': 'stp'})

    @Action(checks='self.mode == "Step";direction in ("Up", "Down"')
    def step(self, direction, steps):
        """Execute steps in the positive direction.

        Parameters
        ----------
        direction : {'Up', 'Down'}
            Direction in which to execute the steps.

        steps : int
            Number of steps to execute, a negative value (<1) can be used to
            indicate a continuous sweep.

        """
        steps = 'c' if steps < 1 else steps
        cmd = 'stepu' if direction == 'Up' else 'stepd'
        cmd += ' {} {}'
        res, msg = self.parent.anc_query(cmd.format(self.ch_id, steps))
        check_answer(res, msg)

    @Action()
    def wait_for_stepping_end(self, timeout=10):
        """Wait for the current stepping operation to end.

        """
        with self.lock():
            self.parent.write('setpw {}'.format(self.ch_id))
            self._wait_for(timeout)

    # XXXX
    def _limits_frequency(self):
        """Compute the limit frequency from the current voltage and measured
        capacitance.

        """
        pass


# TODO implement
class ANCScanner(ANCModule):
    """Base class for ANC scanning modules.

    """
    pass


# TODO add ANM200 and ANM300 modules.
class ANC300(VisaMessageBased):
    """Driver for the ANC300 piezo controller.

    Notes
    -----
    If you set a password different from the default one on your system
    you should pass it under the key password in the connection_infos

    """
    PROTOCOLES = {'TCPIP': '7230::SOCKET'}

    DEFAULTS = {'COMMONS': {'write_termination': '\r\n',
                            'read_termination': '\r\n'}}

    #: Drivers of the ANM150 modules.
    anm150 = channel('_available_anm150', ANCStepper, cache=True)

    def __init__(self, connection_infos, caching_allowed=True):
        """Extract the password from the connection info.

        """
        super(ANC300, self).__init__(connection_infos, caching_allowed)
        self.password = connection_infos.get('password', '123456')

    def initialize(self):
        """Handle autentification after connection opening.


        """
        super(ANC300, self).initialize()
        self.write(self.password)
        # First line contains non-ascii characters
        try:
            self.read()
        except UnicodeDecodeError:
            pass

        self.read()  # Get stupid infos.
        self.read()  # Get authentification request with given password.
        msg = self.read()  # Get authentification status

        if msg != 'Authentification success':
            raise LantzError('Failed to authentify :' + msg)

        res, msg = self.anc_query('echo off')  # Desactivate command echo
        check_answer(res, msg)

    @property
    def connected(self):
        """Query the serial number to check connection.

        """
        try:
            self.anc_query('ver')
        except Exception:
            return False

        return True

    def anc_query(self, msg):
        """Special query taking into account that answer can be multiple lines
        and are termintaed either with OK or ERROR.

        """
        with self.lock:
            self.write(msg)
            answer = ''
            while True:
                ans = self.read()
                if ans in ('OK', 'ERROR'):
                    break
                else:
                    answer += ans + '\n'

        return True if ans == 'OK' else False, answer.rstrip()

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    def _list_anm150(self):
        """List the ANM150 modules installed on that rack.

        """
        anm150 = []
        for i in self._modules:
            res, msg = self.anc_query('getser {}'.format(i))
            if msg.startswith('ANM150'):
                anm150.append(i)

        return anm150

    def _list_modules(self):
        """List the modules installed on the rack.

        """
        if not hasattr(self, '_modules'):
            modules = []
            for i in range(1, 8):
                res, msg = self.anc_query('getser {}'.format(i))
                if res:
                    modules.append(i)

            self._modules = modules

        return self._modules
