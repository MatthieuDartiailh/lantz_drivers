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
from lantz_core.limits import FloatLimitsValidator

from ..standards.scpi.dc_sources import SCPIDCPowerSource

VOLTAGE_RESOLUTION = {10e-3: 1e-7,
                      100e-3: 1e-6,
                      1.0: 1e-5,
                      10: 1e-4,
                      30: 1e-3}

CURRENT_RESOLUTION = {1e-3: 1e-8,
                      10e-3: 1e-7,
                      100e-3: 1e-6,
                      200e-3: 1e-6}


class YokogawaGS200(SCPIDCPowerSource):
    """Driver for the Yokogawa GS200 DC power source.

    """
    voltage = set_feat(limits='voltage')

    voltage_range = set_feat(values=(10e-3, 100e-3, 1.0, 10.0, 30.0),
                             discard={'limits': 'voltage'})

    current_limit = set_feat(limits=(1e-3, 200e-3, 1e-3),
                             checks='{voltage_range} not in (10e-3, 100e-3)\
                                     or {value} == 200e-3')

    current = set_feat(limits='current')

    current_range = set_feat(values=(1e-3, 10e-3, 100e-3, 200e-3),
                             discard={'limits': 'current'})

    voltage_limit = set_feat(limits=(1.0, 30.0, 1))

    def default_check_operation(self, feat, value, i_value, state=None):
        """Check that the operation did not result in any error.

        """
        if self.status_byte[2]:
            return False, self.read_errors()

        return True, None

    def _limits_voltage(self):
        """Determine the voltage limits based on the currently selected range.

        """
        ran = float(self.voltage_range)  # Casting handling possible Quantity
        res = VOLTAGE_RESOLUTION[ran]
        if ran != 30.0:
            ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res, 'V')

    def _limits_current(self):
        """Determine the current limits based on the currently selected range.

        """
        ran = float(self.current_range)  # Casting handling possible Quantity
        res = CURRENT_RESOLUTION[ran]
        if ran != 200e-3:
            ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res, 'A')
