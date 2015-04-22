# -*- coding: utf-8 -*-

from lantz_core.has_features import HasFeatures, set_feat
from lantz_core.features.mappings import Mapping, Bool
from lantz_core.features.scalars import Float


class DCVoltageSource(HasFeatures):
    """
    """

    #:
    output = Bool()

    #:
    voltage = Float()

    #:
    voltage_range = Mapping()


class DCCurrentSource(HasFeatures):
    """
    """

    #:
    output = Bool()

    #:
    current = Float()

    #:
    current_range = Mapping()


class DCPowerSource(DCVoltageSource, DCCurrentSource):
    """
    """

    #:
    function = Mapping()

    #:
    voltage_limit = Mapping(checks="{function}=='Current'")

    #:
    current_limit = Mapping(checks="{function}=='Voltage'")

    voltage = set_feat(checks="{function}=='Voltage'")

    voltage_range = set_feat(checks="{function}=='Voltage'")

    current = set_feat(checks="{function}=='Current'")

    current_range = set_feat(checks="{function}=='Current'")
