from dataclasses import dataclass

from hawa.paper.health import HealthApiData


@dataclass
class CityMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'city'


@dataclass
class CityHealthApiData(CityMixin, HealthApiData):
    pass
