from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from sqlalchemy import text

from hawa.base.db import DbUtil
from hawa.config import project


class Measurement:
    db = DbUtil()

    @property
    def level_names(self):
        return '、'.join(project.ranks['FEEDBACK_LEVEL'].values())

    @property
    def level_columns(self):
        data = project.ranks['FEEDBACK_LEVEL']
        res = [data[i] for i in sorted(data.keys())]
        return res

    @property
    def field_names(self):
        return self._get_field_names('field')

    @property
    def dimension_names(self):
        return self._get_field_names('dimension')

    @property
    def fields(self):
        return self._get_fields(category='field')

    @property
    def dimensions(self):
        return self._get_fields(category='dimension')

    def _get_fields(self, category: str):
        sql = (f"select code, category, name from codebook "
               f"where category='{category}' and name<>'其他' order by `order`;")
        with self.db.engine_conn() as conn:
            data = pd.read_sql(text(sql), conn)
        return data['name'].to_list()

    def _get_field_names(self, category: str):
        codes = self._get_fields(category=category)
        return '、'.join(codes)


@dataclass
class CaseData:
    cases: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def join_date(self):
        valid_from = self.cases['valid_from'].min()
        valid_to = self.cases['valid_to'].max()
        if (valid_from.month, valid_from.day) == (valid_to.month, valid_to.day):
            join_date = f"参测日期：{valid_from:%Y年%m月%d日}"
        else:
            join_date = f"参测日期：{valid_from:%Y年%m月%d日}~{valid_to:%Y年%m月%d日}"
        return join_date

    @property
    def start_date(self) -> str:
        return self.join_date.split('~')[0].removeprefix('参测日期：')

    @property
    def end_date(self):
        if '~' in self.join_date:
            temp = self.join_date.split('~')[1]
        else:
            temp = self.join_date
        return temp.removeprefix('参测日期：')

    @property
    def start_month(self):
        return self.start_date.split('月')[0] + '月'


@dataclass
class GradeData:
    case_ids: list[int]
    grades: Optional[list[int]] = None
    is_single_grade: bool = False

    def __post_init__(self):
        self.grades = sorted(set(int(str(i)[-2:]) for i in self.case_ids))
        self.is_single_grade = len(self.grades) == 1

    @property
    def grade_name(self) -> str:
        return '、'.join([project.grade_simple[i] for i in self.grades]) + '年级'

    @property
    def grade_periods(self):
        res = []
        for g in self.grades:
            if g <= 6:
                word = '小学'

            elif g <= 9:
                word = '初中'
            else:
                word = '高中'
            if word not in res:
                res.append(word)
        return res

    @property
    def grade_period_text(self):
        return ''.join(self.grade_periods)

    @property
    def grade_name_list(self) -> list[str]:
        return [f"{project.grade_simple[i]}年级" for i in self.grades]


class Util:
    @classmethod
    def format_num(cls, num: float | int, precision: int = 1):
        return round(float(num), precision)
