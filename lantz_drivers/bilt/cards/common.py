# -*- coding: utf-8 -*-
"""
    lantz_drivers.bilt.common
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Common driver for Bilt cards.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from lantz_core.channel import Channel


def make_card_detector(model_id):
    """Create a function listing the available card of a given model.

    Parameters
    ----------
    model_id : unicode or list of unicode
        Id or ids of the model. ex BE2100

    """
    if isinstance(model_id, list):
        model_id = [m[2:] for m in model_id]
    else:
        model_id = [model_id[2:]]

    def list_channel(driver):
        """Query all the cards fitted on the rack and filter based on the model

        """
        cards = {id: int(i)
                 for card in driver.query('I:L?').split(';')
                 for i, id, _ in card.split(',')}

        return [cards[id] for id in cards if id in model_id]


class BN100Card(Channel):
    """Base driver for cards used with the Bilt BN100 chassis.

    """

    def default_get_feature(self, feat, cmd, *args, **kwargs):
        """Prepend module selection to command.

        """
        cmd = 'I{ch_id};'+cmd
        super(BN100Card, self).default_get_feature(feat, cmd, *args, **kwargs)

    def default_set_feature(self, feat, cmd, *args, **kwargs):
        """Prepend module selection to command.

        """
        cmd = 'I{ch_id};'+cmd
        super(BN100Card, self).default_set_feature(feat, cmd, *args, **kwargs)
