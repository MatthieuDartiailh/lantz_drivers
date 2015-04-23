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

from lantz_core.has_features import set_feat
from lantz_core.action import Action
from lantz_core.limits import FloatLimitsValidator
from lantz_core.backends.visa import VisaMessageDriver

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


class Yokogawa7651(VisaMessageDriver, DCPowerSource):
    """Driver for the Yokogawa 7651 DC power source.

    This driver can also be used on Yokogawa GS200 used in compatibility mode.

    """
    function = set_feat(getter='OD',
                        setter='F{}E',
                        mapping=({'Voltage': '1', 'Current': '5'},
                                 {'V': 'Voltage', 'A': 'Current'}),
                        extract='{_}DC{}{_:+E}')

    output = set_feat(getter=True,
                      setter='O{}E',
                      mapping={True: 1, False: 0})

    voltage = set_feat(getter='OD',
                       setter='S{:+E}E',
                       limits='voltage',
                       extract='{_}DC{_}{:E+}')

    # Will wait decision about mapping for float, int, unicode
    voltage_range = set_feat(getter=True,
                             setter=':SOUR:RANG {:E}',
                             values=(10e-3, 100e-3, 1.0, 10.0, 30.0),
                             discard={'limits': 'voltage'})

    current_limit = set_feat(getter=True,
                             setter='LA{}E',
                             limits=(5e-3, 120e-3, 1e-3))

    current = set_feat(getter='OD',
                       setter='S{:+E}E',
                       limits='current',
                       extract='{_}DC{_}{:E+}')

    # Will wait decision about mapping for float, int, unicode
    current_range = set_feat(getter=':SOURce:RANGe?',
                             setter=':SOURce:RANGe {:E}',
                             values=(1e-3, 10e-3, 100e-3),
                             discard={'limits': 'current'})

    voltage_limit = set_feat(getter=True,
                             setter='LV{}E',
                             limits=(1.0, 30.0, 1))

    @Action
    def read_errors(self):
        """Read the error message available in the queue.

        """
        pass

    def default_check_operation(self, feat, value, i_value, state=None):
        """Check that the operation did not result in any error.

        """
        if self.status_byte[6]:
            return False, self.read_errors()

        return True, None

    def _limits_voltage(self):
        """Determine the voltage limits based on the currently selected range.

        """
        ran = self.voltage_range
        res = VOLTAGE_RESOLUTION[ran]
        ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res)

    def _limits_current(self):
        """Determine the current limits based on the currently selected range.

        """
        ran = self.current_range
        res = CURRENT_RESOLUTION[ran]
        ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res)

    def _get_ouput(self):
        """Read the output current status byte and extract the output state.

        """
        return bool(int(self.query('OC')) & 16)

    def _get_voltage_range(self):
        """
        """
        pass

    def _get_current_range(self):
        """
        """
        pass

    def _get_current_limit(self):
        """
        """
        pass

    def _get_voltage_limit(self):
        """
        """
        pass
