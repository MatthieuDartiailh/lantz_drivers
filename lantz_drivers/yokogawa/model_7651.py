# -*- coding: utf-8 -*-
"""
    lantz_drivers.yokogawa.model_7651
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the Yokogawa 7651 DC power source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core import (set_feat, channel, conditional, constant, subsystem,
                        Action)
from lantz_core.features import LinkedTo, Register
from lantz_core.limits import FloatLimitsValidator
from lantz_core.backends.visa import VisaMessageDriver

from ..base.dc_sources import DCPowerSource, DCSourceProtectionSubsystem


VOLTAGE_RESOLUTION = {10e-3: 1e-7,
                      100e-3: 1e-6,
                      1.0: 1e-5,
                      10: 1e-4,
                      30: 1e-3}

CURRENT_RESOLUTION = {1e-3: 1e-8,
                      10e-3: 1e-7,
                      100e-3: 1e-6,
                      200e-3: 1e-6}


class Yokogawa7651(VisaMessageDriver, DCPowerSource):
    """Driver for the Yokogawa 7651 DC power source.

    This driver can also be used on Yokogawa GS200 used in compatibility mode.

    """
    PROTOCOLS = {'GPIB': 'INSTR'}

    DEFAULTS = {'COMMON': {'read_termination': '\r\n'},
                'ASRL': {'write_termination': '\r\n'}}

    # XXXX
    status_byte = Register()

    # XXXX
    status_code = Register()

    def initialize(self):
        """Set the data termination.

        """
        super(Yokogawa7651, self).initialize()
        self.write('DL0')

    output = channel()

    with output as o:
        o.function = set_feat(getter='OD',
                              setter='F{}E',
                              mapping=({'Voltage': '1', 'Current': '5'},
                                       {'V': 'Voltage', 'A': 'Current'}),
                              extract='{_}DC{}{_:+E}')

        o.enabled = set_feat(getter=True,
                             setter='O{}E',
                             mapping={True: 1, False: 0})

        o.voltage = set_feat(getter='OD',
                             setter='S{:+E}E',
                             limits='voltage',
                             extract='{_}DC{_}{:E+}')

        o.voltage_range = set_feat(getter=True,
                                   setter=':SOUR:RANG {:E}',
                                   extract='F1R{}S{_}',
                                   mapping={10e-3: 2, 100e-3: 3, 1.0: 4,
                                            10.0: 5, 30.0: 6},
                                   discard={'feature': ('ocp.enabled',),
                                            'limits': ('voltage',)})

        o.voltage_limit_behavior = set_feat(getter=conditional(
            '"trip" if self.mode=="current" else "irrelevant"'))

        o.current_limit = set_feat(getter=True,
                                   setter='LA{}E',
                                   extract='LV{_}LA{}',
                                   limits=(5e-3, 120e-3, 1e-3))

        o.current = set_feat(getter='OD',
                             setter='S{:+E}E',
                             limits='current',
                             extract='{_}DC{_}{:E+}')

        o.current_range = set_feat(getter=True,
                                   setter=':SOURce:RANGe {:E}',
                                   extract='F5R{}S{_}',
                                   mapping={1e-3: 4, 10e-3: 5, 100e-3: 6},
                                   discard={'limits': ('current',)})

        o.voltage_limit_behavior = set_feat(getter=conditional(
            '"irrelevant" if self.mode=="current" else "trip"'))

        o.ovp = subsystem(DCSourceProtectionSubsystem)
        with o.ovp as ovp:

            ovp.enabled = set_feat(getter=constant(True),
                                   checks='driver.mode == "current"')

            ovp.behavior = set_feat(getter=constant('regulate'))

            ovp.high_level = set_feat(getter=True,
                                      setter='LV{}E',
                                      extract='LV{}LA{_}',
                                      checks='driver.mode == "current"',
                                      limits=(1, 30, 1))

            ovp.low_level = LinkedTo('high_level',
                                     relation=('value = -driver.high_level',
                                               'driver.high_level = value'),)

            @ovp
            @Action(checks='driver.mode == "current"')
            def read_status(self):
                """Check whether the overcurrent protection tripped the
                output.

                """
                if self.parent.status_byte['Limit error']:
                    if self.parent.status_code['Output']:
                        return 'overload'
                    return 'tripped'

                return 'normal'

            @ovp
            @Action(checks='driver.mode == "current"')
            def reset(self):
                """Clear the over-voltage and switch the output back on.

                """
                self.clear_cache(('output',))
                self.output = 'on'

        o.ocp = subsystem(DCSourceProtectionSubsystem)
        with o.ocp as ocp:
            # XXXX disabled in mV range
            ocp.enabled = set_feat(getter=True,
                                   checks='driver.mode == "voltage"')

            ocp.behavior = set_feat(getter=constant('regulate'))

            ocp.high_level = set_feat(getter=True,
                                      setter='LA{}E',
                                      extract='LV{_}LA{}',
                                      limits=(5e-3, 120e-3, 1e-3))

            ocp.low_level = LinkedTo('high_level',
                                     relation=('value = driver.high_level',
                                               'driver.high_level = -value'))

            @ocp
            @Action(checks='driver.mode == "voltage"')
            def read_status(self):
                """Check whether the over-current protection tripped the
                output.

                """
                if self.parent.status_byte['Limit error']:
                    if self.parent.status_code['Output']:
                        return 'overload'
                    return 'tripped'

                return 'normal'

            @ocp
            @Action(checks='driver.mode == "voltage"')
            def reset(self):
                """Clear the over-current and switch the output back on.

                """
                self.clear_cache(('output',))
                self.output = 'on'

            # XXXX
            @ocp
            def _get_enabled(self, feat):
                """
                """
                pass

        # =====================================================================
        # --- Private API -----------------------------------------------------
        # =====================================================================

        @o
        def default_check_operation(self, feat, value, i_value, state=None):
            """Check that the operation did not result in any error.

            """
            stb = self.read_status_byte()
            if stb[6]:
                msg = 'Syntax error' if stb[3] else 'Overload'
                return False, msg

            return True, None

        @o
        def _limits_voltage(self):
            """Determine the voltage limits based on the currently selected
            range.

            """
            ran = float(self.voltage_range)  # Casting handling Quantity
            res = VOLTAGE_RESOLUTION[ran]
            if ran != 30.0:
                ran *= 1.2
            else:
                ran = 32.0
            return FloatLimitsValidator(-ran, ran, res, 'V')

        @o
        def _limits_current(self):
            """Determine the current limits based on the currently selected
            range.

            """
            ran = float(self.current_range)  # Casting handling Quantity
            res = CURRENT_RESOLUTION[ran]
            if ran != 200e-3:
                ran *= 1.2
            else:
                ran = 220e-3
            return FloatLimitsValidator(-ran, ran, res, 'A')

        @o
        def _get_ouput(self):
            """Read the output current status byte and extract the output state

            """
            return 'Output' in self.status_code

        @o
        def _get_range(self):
            """Read the range.

            """
            self.write('OS')
            self.read()  # Model and software version
            msg = self.read()  # Function, range, output data
            self.read()  # Program parameters
            self.read()  # Limits
            return msg

        o._get_voltage_range = _get_range

        o._get_current_range = _get_range

        @o
        def _get_limit(self):
            """Read the limiter value.

            """
            self.write('OS')
            self.read()  # Model and software version
            self.read()  # Function, range, output data
            self.read()  # Program parameters
            return self.read()  # Limits

        o._get_current_limit = _get_limit

        o._get_voltage_limit = _get_limit
