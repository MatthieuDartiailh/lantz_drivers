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

    voltage_range = set_feat(getter=True,
                             setter=':SOUR:RANG {:E}',
                             extract='{_},R{},{}',
                             mapping={10e-3: 2, 100e-3: 3, 1.0: 4, 10.0: 5,
                                      30.0: 6},
                             discard={'limits': 'voltage'})

    current_limit = set_feat(getter=True,
                             setter='LA{}E',
                             limits=(5e-3, 120e-3, 1e-3))

    current = set_feat(getter='OD',
                       setter='S{:+E}E',
                       limits='current',
                       extract='{_}DC{_}{:E+}')

    current_range = set_feat(getter=':SOURce:RANGe?',
                             setter=':SOURce:RANGe {:E}',
                             values={1e-3: 4, 10e-3: 5, 100e-3: 6},
                             discard={'limits': ('current',)})

    voltage_limit = set_feat(getter=True,
                             setter='LV{}E',
                             limits=(1.0, 30.0, 1))

    def default_check_operation(self, feat, value, i_value, state=None):
        """Check that the operation did not result in any error.

        """
        stb = self.read_status_byte()
        if stb[6]:
            msg = 'Syntax error' if stb[3] else 'Overload'
            return False, msg

        return True, None

    def _limits_voltage(self):
        """Determine the voltage limits based on the currently selected range.

        """
        ran = float(self.voltage_range)  # Casting handling possible Quantity
        res = VOLTAGE_RESOLUTION[ran]
        ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res, 'V')

    def _limits_current(self):
        """Determine the current limits based on the currently selected range.

        """
        ran = float(self.current_range)  # Casting handling possible Quantity
        res = CURRENT_RESOLUTION[ran]
        ran *= 1.2
        return FloatLimitsValidator(-ran, ran, res, 'A')

    def _get_ouput(self):
        """Read the output current status byte and extract the output state.

        """
        return bool(int(self.query('OC')[5::]) & 16)

    def _get_range(self):
        """Read the range.

        """
        self.write('OS')
        self.read()  # Model and software version
        msg = self.read()  # Function, range, output data
        self.read()  # Program parameters
        self.read()  # Limits
        return msg

    _get_voltage_range = _get_range

    _get_current_range = _get_range

    def _get_limit(self):
        """Read the limiter value.

        """
        self.write('OS')
        self.read()  # Model and software version
        self.read()  # Function, range, output data
        self.read()  # Program parameters
        return self.read()  # Limits

    _get_current_limit = _get_limit

    _get_voltage_limit = _get_limit
