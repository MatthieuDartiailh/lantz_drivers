# -*- coding: utf-8 -*-
"""
    lantz_drivers.yokogawa.model_7651
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the Yokogawa GS200 DC power source.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.has_features import set_feat
from lantz_core.action import Action
from lantz_core.limits import FloatLimitsValidator

from ..standards.iee488 import IEEE488
from ..standards.dc_sources import DCPowerSource


VOLTAGE_RESOLUTION = {10e-3: 1e-7,
                      100e-3: 1e-6,
                      1.0: 1e-5,
                      10: 1e-4,
                      30: 1e-3}

CURRENT_RESOLUTION = {1e-3: 1e-8,
                      10e-3: 1e-7,
                      100e-3: 1e-6,
                      200e-3: 1e-6}


# XXXX a large part can be abstracted away in scpi.dc_sources module.
class YokogawaGS200(IEEE488, DCPowerSource):
    """Driver for the Yokogawa GS200 DC power source.

    """
    function = set_feat(getter=':SOUR:FUNC?',
                        setter=':SOUR:FUNC {}',
                        mapping={'Voltage': 'VOLT', 'Current': 'CURR'})

    output = set_feat(getter='OUTP:STAT?',
                      setter='OUTP:STAT {}',
                      mapping={True: 1, False: 0})

    voltage = set_feat(getter=':SOUR:LEV?',
                       setter=':SOUR:LEV {:E}',
                       limits='voltage')

    voltage_range = set_feat(getter=':SOUR:RANG?',
                             setter=':SOUR:RANG {:E}',
                             values=(10e-3, 100e-3, 1.0, 10.0, 30.0),
                             discard={'limits': 'voltage'})

    current_limit = set_feat(getter=':SOUR:PROT:CURR?',
                             setter=':SOUR:PROT:CURR {}',
                             limits=(1e-3, 200e-3, 1e-3),
                             checks='{voltage_range} not in (10e-3, 100e-3)\
                                     or {value} == 200e-3')

    current = set_feat(getter=':SOURce:LEVel?',
                       setter=':SOURce:LEVel {:E}',
                       limits='current')

    current_range = set_feat(getter=':SOURce:RANGe?',
                             setter=':SOURce:RANGe {:E}',
                             values=(1e-3, 10e-3, 100e-3, 200e-3),
                             discard={'limits': 'current'})

    voltage_limit = set_feat(getter=':SOUR:PROT:VOLT?',
                             setter=':SOUR:PROT:VOLT {}',
                             limits=(1.0, 30.0, 1))

    @Action
    def read_errors(self):
        """Read the error message available in the queue.

        """
        return self.query(':SYST:ERR?')

    def default_check_operation(self, feat, value, i_value, state=None):
        """Check that the operation did not result in any error.

        """
        if self.status_byte[2]:
            return False, self.read_errors()

        return True, None

    def _limits_voltage(self):
        """Determine the voltage limits based on the currently selected range.

        """
        ran = self.voltage_range
        res = VOLTAGE_RESOLUTION[ran]
        if ran != 30.0:
            ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res)

    def _limits_current(self):
        """Determine the current limits based on the currently selected range.

        """
        ran = self.current_range
        res = CURRENT_RESOLUTION[ran]
        if ran != 200e-3:
            ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res)
