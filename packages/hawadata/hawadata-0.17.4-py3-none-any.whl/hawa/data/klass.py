from dataclasses import dataclass
from typing import Optional

import pandas as pd

from hawa.common.query import MetaUnit
from hawa.config import project
from hawa.paper.health import HealthApiData


@dataclass
class ClassMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'class'


@dataclass
class ClassHealthApiData(ClassMixin, HealthApiData):
    """使用 school id 作为 meta_unit_id，额外增加班级的逻辑"""
    meta_class_id: Optional[int] = None  # 必填
    class_id: Optional[int] = None
    class_name: Optional[str] = ''

    def _to_init_a0_meta(self):
        if not self.grade:
            raise ValueError("grade 必填")
        if not self.meta_class_id:
            raise ValueError("meta_class_id 必填")
        self.class_id = self.meta_class_id % 100
        self.class_name = f"{self.grade}年级{self.class_id}班"

    def _to_init_a_meta_unit(self):
        super()._to_init_a_meta_unit()
        self.meta_unit = MetaUnit(
            id=self.meta_unit_id, name=f"{self.meta_unit.name}{self.class_name}",
            short_name=self.meta_unit.short_name
        )

    def _to_init_e_answers(self):
        """筛选班级的答案"""
        super()._to_init_e_answers()
        records = []
        for _, row in self.answers.iterrows():
            if int(str(row['student_id'])[:15]) == self.meta_class_id:
                records.append(row)
        self.answers = pd.DataFrame.from_records(records)
