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

from lantz_core.has_features import set_feat

from .common import BN100Card, make_card_detector
from ...standards.dc_sources import DCVoltageSource


detect_be2100 = make_card_detector(['BE2101', 'BE2102', 'BE2103'])


class BE2100(BN100Card, DCVoltageSource):
    """Driver for the Bilt BN100 chassis.

    """

    output = set_feat(getter='OUT?', setter='OUT {}')

    voltage = set_feat(getter='VOLT?', setter='VOLT {:E}',
                       limits='voltage')

    voltage_range = set_feat(getter='VOLT:RANG?', setter='VOLT:RANG {}',
                             values=(1.2, 12), extract='{},{_}',
                             checks='not {output}')
