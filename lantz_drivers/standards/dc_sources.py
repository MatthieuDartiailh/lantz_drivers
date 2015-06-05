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
from lantz_core.has_features import HasFeatures, channel, set_feat
from lantz_core.features import Bool, Float, Unicode


class DCVoltageSource(HasFeatures):
    """Basic DC voltage source.

    """

    # Output channels (present even for single output instruments).
    output = channel((1,))

    with output as o:

        #: Status of the output.
        o.enabled = Bool(aliases={True: ['On', 'ON', 'On'],
                                  False: ['Off', 'OFF', 'off']})

        #: Voltage applied on the ouput if on.
        o.voltage = Float(unit='V')

        #: Selected range for the voltage.
        o.voltage_range = Float(unit='V')


class DCCurrentSource(HasFeatures):
    """Basic DC current source.

    """

    # Output channels (present even for single output instruments).
    output = channel((1,))

    with output as o:

        #: Status of the output.
        o.enabled = Bool(aliases={True: ['On', 'ON', 'On'],
                                  False: ['Off', 'OFF', 'off']})

        #: Current flowing if the ouput is on.
        o.current = Float(unit='A')

        #: Slected range for the current.
        o.current_range = Float(unit='A')


class DCPowerSource(DCVoltageSource, DCCurrentSource):
    """Basic DC power source whose ouput can be expressed either in term
    of voltage or currnet.

    """

    # Output channels (present even for single output instruments).
    output = channel((1,))

    with output as o:

        #: Selected mode of operation.
        o.function = Unicode(mapping={'Voltage': '', 'Current': ''})

        #: Maximal voltage to apply in 'Current' mode.
        o.voltage_limit = Float(checks="{function}=='Current'", unit='V')

        #: Maximal current to deliver in 'Voltage' mode.
        o.current_limit = Float(checks="{function}=='Voltage'", unit='A')

        o.voltage = set_feat(checks="{function}=='Voltage'")

        o.voltage_range = set_feat(checks="{function}=='Voltage'")

        o.current = set_feat(checks="{function}=='Current'")

        o.current_range = set_feat(checks="{function}=='Current'")
