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

from lantz_core.has_features import set_feat, channel

from ..dc_sources import DCPowerSource
from ..iee488 import IEEE488


class SCPIDCPowerSource(IEEE488, DCPowerSource):
    """Driver for the Yokogawa GS200 DC power source.

    """
    output = channel()

    with output as o:
        o.function = set_feat(getter=':SOUR:FUNC?',
                              setter=':SOUR:FUNC {}',
                              mapping={'Voltage': 'VOLT', 'Current': 'CURR'})

        o.enabled = set_feat(getter='OUTP:STAT?',
                             setter='OUTP:STAT {}',
                             mapping={True: 1, False: 0})

        o.voltage = set_feat(getter=':SOUR:LEV?',
                             setter=':SOUR:LEV {:E}')

        o.voltage_range = set_feat(getter=':SOUR:RANG?',
                                   setter=':SOUR:RANG {:E}')

        o.current_limit = set_feat(getter=':SOUR:PROT:CURR?',
                                   setter=':SOUR:PROT:CURR {}')

        o.current = set_feat(getter=':SOURce:LEVel?',
                             setter=':SOURce:LEVel {:E}')

        o.current_range = set_feat(getter=':SOURce:RANGe?',
                                   setter=':SOURce:RANGe {:E}')

        o.voltage_limit = set_feat(getter=':SOUR:PROT:VOLT?',
                                   setter=':SOUR:PROT:VOLT {}')
