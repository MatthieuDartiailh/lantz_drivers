# -*- coding: utf-8 -*-
"""
    lantz_drivers.bilt.bn100
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Driver for the Bilt BN100 chassis.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.has_features import channel
from lantz_core.action import Action
from lantz_core.backends.visa import VisaMessageDriver

from .cards.be2100 import BE2100, detect_be2100


class BN100(VisaMessageDriver):
    """Driver for the Bilt BN100 chassis.

    """

    be2100 = channel('_list_be2100', BE2100)

    def initialize(self):
        """Make sure the communication parameters are correctly sets.

        """
        super(BN100, self).initialize()
        self.write('SYST:VERB 0')

    @Action
    def read_error(self):
        """Read the first error in the error queue.

        """
        return self.query('SYST:ERR?')

    _list_be2100 = detect_be2100
