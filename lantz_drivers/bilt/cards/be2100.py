# -*- coding: utf-8 -*-
"""
    lantz_drivers.bilt.cards.be2100
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the Bilt BE2100 card : high stability DC voltage source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.has_features import set_feat, subsystem
from lantz_core.features.scalars import Float, Unicode
from lantz_core.limits import FloatLimitsValidator
from lantz_core.action import Action

from .common import BN100Card, make_card_detector
from ...standards.dc_sources import DCVoltageSource


detect_be2100 = make_card_detector(['BE2101', 'BE2102', 'BE2103'])


class BE2100(BN100Card, DCVoltageSource):
    """Driver for the Bilt BE2100 high precision dc voltage source.

    """

    output = set_feat(getter='OUT?', setter='OUT {}')

    voltage = set_feat(getter='VOLT?', setter='VOLT {:E}',
                       limits='voltage')

    voltage_range = set_feat(getter='VOLT:RANG?', setter='VOLT:RANG {}',
                             values=(1.2, 12), extract='{},{_}',
                             checks='not {output}',
                             discard={'limits': 'voltage'})

    #: Set the voltage settling filter. Slow 100 ms, Fast 10 ms
    voltage_filter = Unicode('VOLT:FILT?', 'VOLT:FILT {}',
                             mapping={'Slow': 0, 'Fast': 1})

    #: Specify stricter voltage limitations than the ones linked to the range.
    voltage_saturation = subsystem()
    with voltage_saturation as vs:
        #: Lowest allowed voltage.
        vs.low = Float('VOLT:SAT:NEG?', 'VOLT:SAT:NEG {}', unit='V',
                       limits=(-12, 0), discard={'limits': 'voltage'})

        #: Highest allowed voltage.
        vs.high = Float('VOLT:SAT:POS?', 'VOLT:SAT:POS {}', unit='V',
                        limits=(-12, 0), discard={'limits': 'voltage'})

    #: Subsystem handling reaction to triggering.
    trigger = subsystem()
    with trigger as tr:
        #: Type of response to triggering :
        #: - off : immediate update of voltage everytime the voltage feature is
        #:   updated.
        #: - slope : update after receiving a trigger based on the slope value.
        #: - stair : update after receiving a trigger using step_amplitude
        #:   and step_width.
        #: - step : increment by one step_amplitude till target value for each
        #:   triggering.
        #: - auto : update after receiving a trigger by steps but determining
        #:   when to move to next step based on voltage sensing.
        tr.mode = Unicode('TRIG:IN?', 'TRIG:IN {}',
                          mapping={'off': '0', 'slope': '1', 'stair': '2',
                                   'step': '4', 'auto': '5'})

        #: Delay to wait after receiving a trigger event before reacting.
        tr.delay = Float('TRIG:IN:DEL?', 'TRIG:IN:DEL {}', unit='ms',
                         limits=(0, 60000, 1))

        #: Voltage slope to use in slope mode.
        tr.slope = Float('VOLT:SLOP?', 'VOLT:SLOP {}', unit='V/ms',
                         limits=(1.2e-6, 1))

        #: High of each update in stair and step mode.
        tr.step_amplitude = Float('VOLT:ST:AMPL?', 'VOLT:ST:AMPL {}', unit='V',
                                  limits=(1.2e-6, 12))

        #: Width of each step in stair mode.
        tr.step_width = Float('VOLT:ST:WID?', 'VOLT:ST:WID {}', unit='ms',
                              limits=(100, 60000, 1))

        #: Absolute threshold value of the settling tracking comparator.
        tr.ready_amplitude = Float('TRIG:READY:AMPL?', 'TRIG:READY:AMPL {}',
                                   unit='V', limits=(1.2e-6, 1))

        @tr
        @Action
        def fire(self):
            """Send a software trigger.

            """
            self.write('I {};TRIG:IN:INIT'.format(self.ch_id))

    @Action
    def read_voltage_status(self):
        """Status of the current voltage update.

        """
        return self.query('I {};VOLT:STAT?'.format(self.ch_id))

    def _limits_voltage(self):
        """Compute the voltage limits based on range and saturation.

        """
        rng = float(self.voltage_range)  # Casting handling possible Quantity
        low = max(-rng, float(self.voltage_saturation.low))
        high = min(rng, float(self.voltage_saturation.high))

        step = 1.2e-6 if rng == 1.2 else 1.2e-5

        return FloatLimitsValidator(low, high, step, 'V')
