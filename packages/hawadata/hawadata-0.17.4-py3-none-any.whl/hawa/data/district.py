from dataclasses import dataclass

from hawa.paper.health import HealthReportData, HealthApiData


@dataclass
class DistrictMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'district'


@dataclass
class DistrictHealthApiData(DistrictMixin, HealthApiData):
    pass


@dataclass
class DistrictHealthReportData(DistrictMixin, HealthReportData):
    pass
