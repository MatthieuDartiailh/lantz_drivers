# -*- coding: utf-8 -*-
"""
    lantz_drivers.keysight.model_E363XA
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the keysight E3633A and E3634A DC power source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core import set_feat, channel, subsystem, Action
from lantz_core.limits import FloatLimitsValidator
from lantz_core.unit import to_float
from lantz_core.features import conditional

from ..base.dc_sources import (DCPowerSourceWithMeasure,
                               DCSourceTriggerSubsystem)
from ..common.ieee488 import (IEEEInternalOperations, IEEEStatusReporting,
                              IEEEOperationComplete, IEEEOptionsIdentification,
                              IEEEStoredSettings, IEEETrigger,
                              IEEESynchronisation, IEEEPowerOn)


class _KeysightE363XA(DCPowerSourceWithMeasure, IEEEInternalOperations,
                      IEEEStatusReporting, IEEEOperationComplete,
                      IEEEOptionsIdentification, IEEEStoredSettings,
                      IEEETrigger, IEEESynchronisation, IEEEPowerOn):
    """Driver for the Keysight E3631A DC power source.

    """
    PROTOCOLS = {'GPIB': 'INSTR', 'ASRL': 'INSTR'}

    DEFAULTS = {'COMMON': {'write_termination': '\n',
                           'read_termination': '\n'}}

    output = channel()

    with output as o:

        o.enabled = set_feat(getter='OUTP?', setter='OUTP {}',
                             aliases={True: ['On', 'ON', 'On'],
                                      False: ['Off', 'OFF', 'off']})

        o.voltage = set_feat(
            getter=conditional(('"VOLT?" if driver.trigger.mode != "enabled"'
                                ' else "VOLT:TRIG?"'), default=True),
            setter=conditional(('"VOLT {}" if driver.trigger.mode != "enabled"'
                                ' else "VOLT:TRIG {}"'), default=True),
            limits='voltage')

        o.voltage_range = set_feat(getter='VOLT:RANGE?',
                                   setter='VOLT:RANGE {}')

        o.current = set_feat(
            getter=conditional(('"CURR?" if driver.trigger.mode != "enabled"'
                                ' else "CURR:TRIG?"'), default=True),
            setter=conditional(('"CURR {}" if driver.trigger.mode != "enabled"'
                                ' else "CURR:TRIG {}"'), default=True),
            limits='current')

        o.current_range = set_feat(getter='CURR:RANGE?',
                                   setter='CURR:RANGE {}')
# XXXX
        @o
        @Action()
        def measure(self, kind, **kwargs):
            """
            """
            pass
# XXXX
        @o
        @Action(unit=(None, (None, 'V', 'A')),
                limits={'voltage': 'voltage', 'current': 'current'})
        def apply(self, voltage, current):
            """
            """
            pass
# XXXX
        @o
        @Action()
        def read_output_status(self):
            """
            """
            pass

        o.trigger = subsystem(DCSourceTriggerSubsystem)

        with o.trigger as t:

            #:
            t.mode = set_feat(getter=True, setter=True)

            t.source = set_feat('TRIG:SOUR?', 'TRIG:SOUR {}',
                                mapping={'immediate': 'IMM', 'bus': 'BUS'})

            t.delay = set_feat('TRIG:DEL?', 'TRIG:DEL {}',
                               limits=(1, 3600, 1))

            # Actually the caching do the rest for us.
            @t
            def _get_mode(self, feat):
                return 'disabled'

            @t
            def _set_mode(self, feat, value):
                pass

# XXXX use generic SCPI class
    @Action()
    def read_error(self):
        """Read the first error in the error queue.

        If an unhandle error occurs, the error queue should be polled till it
        is empty.

        """
        code, msg = self.query('SYST:ERR?').split(',')
        return int(code), msg

    def default_check_operation(self, feat, value, i_value, response):
        """Check if an error is present in the error queue.

        """
        code, msg = self.read_error()
        return bool(code), msg


class Keysight3633A(_KeysightE363XA):
    """
    """
    output = channel()

    with output as o:

        o.voltage_range = set_feat(values=(8, 20))

        o.current_range = set_feat(values=(20, 10))

        @o
        def _limits_voltage(self):
            """Build the voltage limits.

            """
            if to_float(self.voltage_range) == 8:
                return FloatLimitsValidator(0, 8.24, 1e-3, unit='V')
            else:
                return FloatLimitsValidator(0, 20.6, 1e-2, unit='V')

        @o
        def _limits_current(self):
            """Build the current limits.

            """
            if to_float(self.current_range) == 20:
                return FloatLimitsValidator(0, 20.60, 1e-3, unit='A')
            else:
                return FloatLimitsValidator(0, 10.3, 1e-3, unit='A')


class Keysight3634A(_KeysightE363XA):
    """
    """
    output = channel()

    with output as o:

        o.voltage_range = set_feat(values=(25, 50))

        o.current_range = set_feat(values=(7, 4))

        @o
        def _limits_voltage(self):
            """Build the voltage limits based on the range.

            """
            if to_float(self.voltage_range) == 25:
                return FloatLimitsValidator(0, 25.75, 1e-3, unit='V')
            else:
                return FloatLimitsValidator(0, 51.5, 1e-3, unit='V')

        @o
        def _limits_current(self):
            """Build the current limits based on the range.

            """
            if to_float(self.current_range) == 7:
                return FloatLimitsValidator(0, 7.21, 1e-3, unit='A')
            else:
                return FloatLimitsValidator(0, 4.12, 1e-3, unit='A')
