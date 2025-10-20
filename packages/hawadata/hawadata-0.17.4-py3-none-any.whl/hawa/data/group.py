from dataclasses import dataclass

from hawa.paper.health import HealthApiData


@dataclass
class GroupMixin:
    """
    为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前
    集团校
    """
    meta_unit_type: str = 'group'


@dataclass
class GroupHealthApiData(GroupMixin, HealthApiData):
    def _to_init_c_schools(self):
        """查询集团校的学校"""
