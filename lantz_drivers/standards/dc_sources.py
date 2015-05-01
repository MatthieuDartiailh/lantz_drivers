# -*- coding: utf-8 -*-
"""
    lantz_drivers.standards.dc_sources
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Definition of the standard expected from DC sources.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from lantz_core.has_features import HasFeatures, set_feat
from lantz_core.features.mappings import Bool
from lantz_core.features.scalars import Float, Unicode
from lantz_core.action import Action


class DCVoltageSource(HasFeatures):
    """Basic DC voltage source.

    """

    #: Status of the output.
    output = Bool(aliases={True: ['On', 'ON', 'On'],
                           False: ['Off', 'OFF', 'off']})

    #: Voltage applied on the ouput if on.
    voltage = Float(unit='V')

    #: Selected range for the voltage.
    voltage_range = Float(unit='V')


class DCCurrentSource(HasFeatures):
    """Basic DC current source.

    """

    #: Status of the output.
    output = Bool(aliases={True: ['On', 'ON', 'On'],
                           False: ['Off', 'OFF', 'off']})

    #: Current flowing if the ouput is on.
    current = Float(unit='A')

    #: Slected range for the current.
    current_range = Float(unit='A')


class DCPowerSource(DCVoltageSource, DCCurrentSource):
    """Basic DC power source whose ouput can be expressed either in term
    of voltage or currnet.

    """

    #: Selected mode of operation.
    function = Unicode(mapping={'Voltage': '', 'Current': ''})

    #: Maximal voltage to apply in 'Current' mode.
    voltage_limit = Float(checks="{function}=='Current'", unit='V')

    #: Maximal current to deliver in 'Voltage' mode.
    current_limit = Float(checks="{function}=='Voltage'", unit='A')

    voltage = set_feat(checks="{function}=='Voltage'")

    voltage_range = set_feat(checks="{function}=='Voltage'")

    current = set_feat(checks="{function}=='Current'")

    current_range = set_feat(checks="{function}=='Current'")
