# -*- coding: utf-8 -*-
"""
    lantz_drivers.keysight.model_E3631A
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the keysight E3631A DC power source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core import set_feat, channel, subsystem, Action
from lantz_core.limits import FloatLimitsValidator
from lantz_core.unit import UNIT_SUPPORT, get_unit_registry
from lantz_core.features import Feature, Bool, Alias, conditional
from lantz_core.features.util import append

from ..base.dc_sources import (DCPowerSourceWithMeasure,
                               DCSourceTriggerSubsystem)
from ..common.ieee488 import (IEEEInternalOperations, IEEEStatusReporting,
                              IEEEOperationComplete, IEEEOptionsIdentification,
                              IEEEStoredSettings, IEEETrigger,
                              IEEESynchronisation, IEEEPowerOn)


VOLTAGE_RANGES = {'P6V': 6, 'P25V': 25, 'N25V': -25}

CURRENT_RANGES = {'P6V': 5, 'P25V': 1, 'N25V': 1}


class KeysightE3631A(DCPowerSourceWithMeasure, IEEEInternalOperations,
                     IEEEStatusReporting, IEEEOperationComplete,
                     IEEEOptionsIdentification, IEEEStoredSettings,
                     IEEETrigger, IEEESynchronisation, IEEEPowerOn):
    """Driver for the Keysight E3631A DC power source.

    """
    PROTOCOLS = {'GPIB': 'INSTR', 'ASRL': 'INSTR'}

    DEFAULTS = {'COMMON': {'write_termination': '\n',
                           'read_termination': '\n'}}

    #: In this model, outputs are always enabled together.
    outputs_enabled = Bool('OUTP?', 'OUTP {}',
                           aliases={True: ['On', 'ON', 'On'],
                                    False: ['Off', 'OFF', 'off']})

    #: Whether to couple together teh output triggers, causing a trigger
    #: received on one to update the other values.
    coupled_triggers = Feature(getter=True, setter=True,
                               checks=(None, ('value is False or '
                                              'not driver.outputs_tracking'))
                               )

    #: Activate tracking between the P25V and the N25V output. In tracking
    #: one have P25V.voltage = - N25V
    outputs_tracking = Bool('OUTP:TRAC?',
                            'OUTP:TRAC {}',
                            aliases={True: ['On', 'ON', 'On'],
                                     False: ['Off', 'OFF', 'off']},
                            checks=(None,
                                    ('value is False or'
                                     'driver.coupled_triggers is None or '
                                     '1 not in driver.coupled_triggers or '
                                     '2 not in driver.coupled_triggers')))

    output = channel({'P6V': 1, 'P25V': 2, 'N25V': 3})

    with output as o:

        o.enabled = Alias('.outputs_enabled')  #: should this be settable ?

        o.voltage = set_feat(
            getter=conditional(('"VOLT?" if driver.trigger.mode != "enabled"'
                                ' else "VOLT:TRIG?"'), default=True),
            setter=conditional(('"VOLT {}" if driver.trigger.mode != "enabled"'
                                ' else "VOLT:TRIG {}"'), default=True),
            limits='voltage')

        o.voltage_range = set_feat(getter=True)

        o.current = set_feat(
            getter=conditional(('"CURR?" if driver.trigger.mode != "enabled"'
                                ' else "CURR:TRIG?"'), default=True),
            setter=conditional(('"CURR {}" if driver.trigger.mode != "enabled"'
                                ' else "CURR:TRIG {}"'), default=True),
            limits='current')

        o.current_range = set_feat(getter=True)
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

        @o
        def default_get_feature(self, feat, cmd, *args, **kwargs):
            """Always select the channel before getting.

            """
            cmd = 'INSTR:SELECT {ch_id};' + cmd
            kwargs['ch_id'] = self.id
            return super(type(self), self).default_get_feature(feat, cmd,
                                                               *args, **kwargs)

        @o
        def default_set_feature(self, feat, cmd, *args, **kwargs):
            """Always select the channel before getting.

            """
            cmd = 'INSTR:SELECT {ch_id};' + cmd
            kwargs['ch_id'] = self.id
            return super(type(self), self).default_set_feature(feat, cmd,
                                                               *args, **kwargs)

        @o
        @append
        def _post_setattr_voltage(self, feat, value, i_value, state=None):
            """Make sure that in tracking mode teh voltage cache is correct.

            """
            if self.id != 'P6V':
                self.parent.output['P25V'].clear_cache(features=('voltage',))
                self.parent.output['N25V'].clear_cache(features=('voltage',))

        @o
        def _get_voltage_range(self, feat):
            """Get the voltage range.

            """
            return VOLTAGE_RANGES[self.id]

        @o
        def _get_current_range(self, feat):
            """Get the current range.

            """
            return CURRENT_RANGES[self.id]

        @o
        def _limits_voltage(self):
            """Build the voltage limits.

            """
            if self.id == 'P6V':
                return FloatLimitsValidator(0, 6.18, 1e-3, unit='V')
            elif self.id == 'P25V':
                return FloatLimitsValidator(0, 25.75, 1e-2, unit='V')
            else:
                return FloatLimitsValidator(-25.75, 0, 1e-2, unit='V')

        @o
        def _limits_current(self):
            """
            """
            if self.id == 'P6V':
                return FloatLimitsValidator(0, 5.15, 1e-3, unit='A')
            elif self.id == 'P25V':
                return FloatLimitsValidator(0, 1.03, 1e-3, unit='A')
            else:
                return FloatLimitsValidator(0, 1.03, 1e-3, unit='A')

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
