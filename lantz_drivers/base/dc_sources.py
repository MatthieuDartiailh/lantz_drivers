# -*- coding: utf-8 -*-
"""
    lantz_drivers.base.dc_sources
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Definition of the standard expected from DC sources.

    :copyright: 2015 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)
from lantz_core.has_features import (HasFeatures, channel, Subsystem, Action)
from lantz_core.features import Bool, Float, Unicode


class DCPowerSource(HasFeatures):
    """Standard interface expected from all DC Power sources.

    """

    #:
    output = channel((0,))

    with output as o:

        #:
        o.enabled = Bool(aliases={True: ['On', 'ON', 'On'],
                                  False: ['Off', 'OFF', 'off']})

        #:
        o.voltage = Float(unit='V')

        #:
        o.voltage_range = Float(unit='V')

        #:
        o.voltage_limit_behavior = Unicode(values=('irrelevant', 'trip',
                                                   'regulate'))

        #:
        o.current = Float(unit='A')

        #:
        o.current_range = Float(unit='A')

        #:
        o.current_limit_behavior = Unicode(values=('irrelevant', 'trip',
                                                   'regulate'))


class DCPowerSourceWithMeasure(Subsystem):
    """
    """
    #:
    output = channel((0,))

    with output as o:

        @o
        @Action()
        def measure(self, kind, **kwargs):
            """
            """
            pass


class DCSourceTriggerSubsystem(Subsystem):
    """
    """
    #:
    mode = Unicode(values=('disabled', 'enabled'))

    #:
    source = Unicode()

    #:
    delay = Float(unit='s')

    @Action()
    def arm(self):
        """
        """
        pass


class DCSourceProtectionSubsystem(Subsystem):
    """
    """
    #:
    enabled = Bool(aliases={True: ['On', 'ON', 'On'],
                            False: ['Off', 'OFF', 'off']})

    #:
    behavior = Unicode()

    #:
    low_level = Float()

    #:
    high_level = Float()

    @Action()
    def read_status(self):
        """
        """
        pass

    @Action()
    def reset(self):
        """
        """
        pass
