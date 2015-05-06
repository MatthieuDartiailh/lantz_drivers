# -*- coding: utf-8 -*-
"""
    lantz_drivers.attocube.anc300
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the ANC300 open-loop positioner controller.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
#from time import sleep
#from timeit import default_timer

from lantz_core.has_features import channel, set_feat
from lantz_core.base_driver import BaseDriver
from lantz_core.channel import Channel
from lantz_core.features import Unicode, Float, Bool, Feature
from lantz_core.action import Action
from lantz_core.errors import InvalidCommand
from lantz_core.backends.visa import errors
from lantz_core.unit import UNIT_SUPPORT, get_unit_registry


def check_answer(msg):
    """Check the message returned by the ANC for errors.

    Parameters
    ----------
    msg : unicode
        Answer to the a command sent to the ANC300.

    Raises
    ------
    InvalidCommand :
        Raised if an error was signaled by the instrument.

    """
    if 'ERROR\r\n' in msg:
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
        msg = self.parent.anc_query('stop {}'.format(self.ch_id))
        check_answer(msg)

    @Action(units=('V', (None)))
    def read_output_voltage(self):
        """Read the voltage currently applied on the module.

        """
        msg = self.parent.anc_query('geto {}'.format((self.ch_id)))
        check_answer(msg)
        return float(msg.split('\r\n')[0])

    @Action(units=('muF', (None)))
    def read_saved_capacitance(self):
        """Read the saved capacitance load for this module.

        """
        msg = self.parent.anc_query('getc {}'.format((self.ch_id)))
        check_answer(msg)
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
            Timeout to use when wait for measure completion.

        Returns
        -------
        value : float, Quantity or None
            Return the new measured value if block is True, else return None.
            The value can be read at a later time using read_saved_capacitance,
            but first wait_for_capacitance_measure should be called to ensure
            that the measure is over.

        """
        with self.lock():
            self.clear_cache(features=('saved_capacitance', 'mode'))
            self.parent.write('setm {} cap'.format(self.ch_id))
            if block:
                self.wait_for_capacitance_measure(timeout)
                return self.read_saved_capacitance()

#    @Action()
#    def wait_for_capacitance_measure(self, timeout=10):
#        """Wait for the capacitance measurement to finish.
#
#        """
#        with self.lock():
#            self.parent.write('capw')
#            self._wait_for(timeout)
#
#    def _wait_for(self, timeout):
#        """Wait for completion of an operation.
#
#        """
#        t = 0
#        while t < timeout:
#            try:
#                tic = default_timer()
#                msg = self.parent.read()
#                check_answer(msg)
#            except errors.VisaIOError as e:
#                if e.error_code != errors.VI_ERROR_TMO:
#                    raise
#                sleep(0.1)
#                t += default_timer() - tic

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

    mode = set_feat(mapping={'Ground': 'gnd', 'Step': 'stp'})

    @Action()
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
        assert self.mode == 'Step',\
            'Can step only in "Step" mode not %s' % self.mode
        steps = 'c' if steps < 1 else steps
        cmd = 'stepu' if direction == 'Up' else 'stepd'
        cmd += ' {} {}'
        msg = self.parent.anc_query(cmd.format(self.ch_id, steps))
        check_answer(msg)

#    @Action()
#    def wait_for_stepping_end(self):
#        """
#        """
#        pass

class ANCScanner(ANCModule):
    pass


class ANC300(BaseDriver):
    pass
