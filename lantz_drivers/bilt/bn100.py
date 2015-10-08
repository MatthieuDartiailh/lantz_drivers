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

# Add identity support
class BN100(VisaMessageDriver):
    """Driver for the Bilt BN100 chassis.

    """

    PROTOCOLS = {'TCPIP': '5025::SOCKET'}

    DEFAULTS = {'COMMON': {'read_termination': '\n',
                           'write_termination': '\n'}
                }

    be2100 = channel('_list_be2100', BE2100)

    def initialize(self):
        """Make sure the communication parameters are correctly sets.

        """
        super(BN100, self).initialize()
        self.write('SYST:VERB 0')

    @Action
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

    _list_be2100 = detect_be2100
