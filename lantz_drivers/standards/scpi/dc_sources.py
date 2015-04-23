# -*- coding: utf-8 -*-
"""
    lantz_drivers.standards.scpi.dc_sources
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.has_features import set_feat
from lantz_core.action import Action

from ..dc_sources import DCPowerSource
from ..iee488 import IEEE488


class SCPIDCPowerSource(IEEE488, DCPowerSource):
    """Driver for the Yokogawa GS200 DC power source.

    """
    function = set_feat(getter=':SOUR:FUNC?',
                        setter=':SOUR:FUNC {}',
                        mapping={'Voltage': 'VOLT', 'Current': 'CURR'})

    output = set_feat(getter='OUTP:STAT?',
                      setter='OUTP:STAT {}',
                      mapping={True: 1, False: 0})

    voltage = set_feat(getter=':SOUR:LEV?',
                       setter=':SOUR:LEV {:E}')

    voltage_range = set_feat(getter=':SOUR:RANG?',
                             setter=':SOUR:RANG {:E}')

    current_limit = set_feat(getter=':SOUR:PROT:CURR?',
                             setter=':SOUR:PROT:CURR {}')

    current = set_feat(getter=':SOURce:LEVel?',
                       setter=':SOURce:LEVel {:E}')

    current_range = set_feat(getter=':SOURce:RANGe?',
                             setter=':SOURce:RANGe {:E}')

    voltage_limit = set_feat(getter=':SOUR:PROT:VOLT?',
                             setter=':SOUR:PROT:VOLT {}')

    @Action
    def read_errors(self):
        """Read the error message available in the queue.

        """
        return self.query(':SYST:ERR?')
