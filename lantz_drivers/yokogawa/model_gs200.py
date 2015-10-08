# -*- coding: utf-8 -*-
"""
    lantz_drivers.yokogawa.model_gs200
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the Yokogawa GS200 DC power source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core import (set_feat, channel, subsystem, conditional, constant,
                        Action)
from lantz_core.limits import FloatLimitsValidator
from lantz_core.features import Unicode, LinkedTo
from lantz_core.unit import to_float

from ..base.dc_sources import (DCPowerSource,
                               DCSourceProtectionSubsystem)
from ..common.ieee488 import (IEEEInternalOperations, IEEEStatusReporting,
                              IEEEOperationComplete, IEEEOptionsIdentification,
                              IEEEStoredSettings)

VOLTAGE_RESOLUTION = {10e-3: 1e-7,
                      100e-3: 1e-6,
                      1.0: 1e-5,
                      10: 1e-4,
                      30: 1e-3}

CURRENT_RESOLUTION = {1e-3: 1e-8,
                      10e-3: 1e-7,
                      100e-3: 1e-6,
                      200e-3: 1e-6}


class YokogawaGS200(DCPowerSource, IEEEInternalOperations,
                    IEEEStatusReporting, IEEEOperationComplete,
                    IEEEOptionsIdentification, IEEEStoredSettings):
    """Driver for the Yokogawa GS200 DC power source.

    """
    PROTOCOLS = {'GPIB': 'INSTR', 'USB': 'INSTR', 'TCPIP': 'INSTR'}

    DEFAULTS = {'COMMON': {'read_termination': '\n'}}

    MANUFACTURER_ID = 0xB21

    MODEL_CODE = 0x39

    def default_check_operation(self, feat, value, i_value, state=None):
        """Check that the operation did not result in any error.

        """
        if self.status_byte[2]:
            return False, self.read_errors()

        return True, None

    output = channel()

    with output as o:
        o.mode = Unicode(getter=':SOUR:FUNC?',
                         setter=':SOUR:FUNC {}',
                         mapping={'voltage': 'VOLT', 'current': 'CURR'},
                         discard={'feature': ('voltage', 'voltage_range',
                                              'current', 'current_range'),
                                  'limits': ('voltage', 'current')})

        o.voltage = set_feat(getter=True,
                             setter=':SOUR:LEV {}',
                             checks=(None, 'driver.mode == "voltage"'),
                             limits='voltage')

        o.voltage_range = set_feat(getter=True,
                                   setter=':SOUR:RANG {}',
                                   checks=(None, 'driver.mode == "voltage"'),
                                   values=(10e-3, 100e-3, 1.0, 10.0, 30.0),
                                   discard={'limits': ('voltage',)})

        o.voltage_limit_behavior = set_feat(getter=conditional(
            '"trip" if self.mode=="current" else "irrelevant"'))

        o.current = set_feat(getter=True,
                             setter=':SOUR:LEV {}',
                             checks=(None, 'driver.mode == "current"'),
                             limits='voltage')

        o.current_range = set_feat(getter=True,
                                   setter=':SOUR:RANG {}',
                                   checks=(None, 'driver.mode == "current"'),
                                   values=(1e-3, 10e-3, 100e-3, 200e-3),
                                   discard={'limits': 'current'})

        o.voltage_limit_behavior = set_feat(getter=conditional(
            '"irrelevant" if self.mode=="current" else "trip"'))

        o.ovp = subsystem(DCSourceProtectionSubsystem)
        with o.ovp as ovp:

            ovp.enabled = set_feat(getter=constant(True),
                                   checks='driver.mode == "current"')

            ovp.behavior = set_feat(getter=constant('trip'))

            ovp.high_level = set_feat(getter=':SOUR:PROT:VOLT?',
                                      setter=':SOUR:PROT:VOLT {}',
                                      checks='driver.mode == "current"',
                                      limits=(1, 30, 1),
                                      )

            ovp.low_level = LinkedTo('high_level',
                                     relation=('value = -driver.high_level',
                                               'driver.high_level = value'),)

            @ovp
            @Action(checks='driver.mode == "current"')
            def read_status(self):
                """Check whether the overvoltage protection tripped the
                output.

                """
                tripped = int(self.query(':STAT:EVEN?')) & 2**12
                return 'tripped' if tripped else 'normal'

            @ovp
            @Action(checks='driver.mode == "current"')
            def reset(self):
                """Clear the over-voltage and switch the output back on.

                """
                self.clear_cache(('output',))
                self.output = 'on'

        o.ocp = subsystem(DCSourceProtectionSubsystem)
        with o.ocp as ocp:

            ocp.enabled = set_feat(getter=constant(True),
                                   checks='driver.mode == "voltage"')

            ocp.high_level = set_feat(getter=':SOUR:PROT:CURR?',
                                      setter=':SOUR:PROT:CURR {}',
                                      checks='driver.mode == "voltage"',
                                      limits=(1e-3, 200e-3, 1e-3),
                                      )

            ocp.low_level = LinkedTo('high_level',
                                     relation=('value = driver.high_level',
                                               'driver.high_level = -value'))

            @ocp
            @Action(checks='driver.mode == "voltage"')
            def read_status(self):
                """Check whether the overcurrent protection tripped the
                output.

                """
                tripped = int(self.query(':STAT:EVEN?')) & 2**12
                return 'tripped' if tripped else 'normal'

            @ocp
            @Action(checks='driver.mode == "voltage"')
            def reset(self):
                """Clear the over-voltage and switch the output back on.

                """
                self.clear_cache(('output',))
                self.output = 'on'

        # =====================================================================
        # --- Private API -----------------------------------------------------
        # =====================================================================

        @o
        def _get_voltage(self, feat):
            """Get the voltage in voltage mode and return the maximum voltage
            in current mode.

            """
            if self.mode != 'voltage':
                return 30
            return self.default_get_feature(':SOUR:LEV?')

        @o
        def _get_current(self, feat):
            """Get the current in current mode and return the maximum curent
            in voltage mode.

            """
            if self.mode != 'current':
                return 0.2
            return self.default_get_feature(':SOUR:LEV?')

        @o
        def _limits_voltage(self):
            """Determine the voltage limits based on the currently selected
            range.

            """
            ran = to_float(self.voltage_range)
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
