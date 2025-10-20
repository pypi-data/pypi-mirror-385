"""仅为集合，无上级单位"""
from dataclasses import dataclass

from hawa.base.errors import NoSchoolIdsError
from hawa.common.query import MetaUnit
from hawa.paper.health import HealthApiData
from hawa.paper.mht import MhtPlusQusApiData, MhtPlusApiData


@dataclass
class AssembleMixin:
    """
    为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前
    学校集合
    """
    meta_unit_id: int = 0
    meta_unit_type: str = 'assemble'


@dataclass
class AssembleHealthApiData(AssembleMixin, HealthApiData):
    """依赖 school_ids 工作"""

    def _to_init_a_meta_unit(self):
        self.meta_unit = MetaUnit(id=self.meta_unit_id, name='学校集合', short_name='学校集合')

    def _to_init_c_schools(self):
        if not self.school_ids:
            raise NoSchoolIdsError("Assemble 参数 school_Ids 不能为空")
        super()._to_init_c_schools()


@dataclass
class AssembleMhtPlusPlusApiData(AssembleMixin, MhtPlusApiData):
    """依赖 school_ids 工作"""


@dataclass
class AssembleMhtPlusQusPlusApiData(AssembleMixin, MhtPlusQusApiData):
    """依赖 school_ids 工作"""
