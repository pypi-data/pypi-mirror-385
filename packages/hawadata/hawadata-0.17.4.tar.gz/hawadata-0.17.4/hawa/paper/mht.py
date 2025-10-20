from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set

import pandas as pd

from hawa.common.data import CommonData
from hawa.common.utils import Util
from hawa.config import project


@dataclass
class MhtData(CommonData):
    test_types: list[str] = field(default_factory=lambda: ['mht', 'mhtPlus', 'XxMhtPlusQus'])
    code_word_list: Set[str] = field(default_factory=lambda: {'mht'})

    # 计算数据
    scale_student_score: dict = field(default_factory=dict)
    sub_scale_score: dict = field(default_factory=dict)
    grade_scale_student_score: dict = field(default_factory=list)
    grade_sub_scale_score: dict = field(default_factory=dict)
    grade_special_students: dict = field(default_factory=dict)

    # 计算数据2
    invalid_student_count: int = 0
    unused_student_count: int = 0
    unused_student_ids: list[int] = field(default_factory=list)

    mht_final_answers: pd.DataFrame = field(default_factory=pd.DataFrame)  # 去除社会期许效应后的 mht 数据
    psy_final_answers: pd.DataFrame = field(default_factory=pd.DataFrame)  # phq 9 道题
    mgarbage_final_answers: pd.DataFrame = field(default_factory=pd.DataFrame)  # mgarbage 问卷数据
    mht_8_final_answers: pd.DataFrame = field(default_factory=pd.DataFrame)  # 移除效度数据

    def _to_count_a_final_answers(self):
        super()._to_count_a_final_answers()
        old_answers = self.final_answers
        old_answers['score'] = old_answers['score'].astype(int)

        # 去除具备社会期许效应的学生
        to_count_validity_answers = old_answers.loc[old_answers['mht'] == '效度', :]
        unused_student_ids = []
        for student_id, group in to_count_validity_answers.groupby(by='student_id'):
            if group['score'].sum() >= 8:
                unused_student_ids.append(student_id)

        self.unused_student_ids = unused_student_ids
        self.unused_student_count = len(unused_student_ids)
        self.total_student_count = self.student_count + self.unused_student_count

        self.mht_final_answers = old_answers[~old_answers['student_id'].isin(unused_student_ids)]
        psy_item_ids = self.psy_item_ids
        self.psy_final_answers = old_answers.loc[old_answers['item_id'].isin(psy_item_ids), :]
        mgarbage_item_ids = self.mgarbage_item_ids
        self.mgarbage_final_answers = old_answers.loc[old_answers['item_id'].isin(mgarbage_item_ids), :]


    def _to_count_c_mht_ans_score(self):
        ans = self.mht_final_answers
        self.mht_8_final_answers = ans.loc[ans['mht'] != '效度', :]

    def _to_count_d_scale_student_score(self):
        """学生总量表得分图数据，横轴分数，纵轴人数 （总 及 各年级）"""
        self.scale_student_score = self._tool_count_student_score(score=self.final_scores)

    def _to_count_e_sub_scale_code_score(self):
        """在 8 个子量表上的得分图，横轴量表，纵轴分数"""
        self.sub_scale_score = self._tool_count_sub_code_score(
            answers=self.mht_8_final_answers
        )

    def _to_count_f_grade_student_score(self):
        """参考 _to_count_c_student_score， 分年级计算"""
        res = {}
        for grade, grade_group in self.final_scores.groupby(by='grade'):
            grade_data = self._tool_count_student_score(score=grade_group)
            res[grade] = grade_data
        self.grade_scale_student_score = res

    def _to_count_g_grade_sub_scale_code_score(self):
        """在 8 个子量表上的得分图，横轴量表，纵轴分数"""
        res = {}
        for grade, grade_ans_group in self.mht_8_final_answers.groupby('grade'):
            grade_data = self._tool_count_sub_code_score(answers=grade_ans_group)
            res[grade] = grade_data
        self.grade_sub_scale_score = res

    def _to_count_h_grade_special_students(self):
        """计算各年级 某量表超过8分的学生"""
        res = defaultdict(list)
        for grade, grade_ans_group in self.mht_final_answers.groupby('grade'):
            for student_id, student_group in grade_ans_group.groupby('student_id'):
                student_name = student_group['username'].tolist()[0]
                student_score = Util.format_num(student_group['score'].sum(), precision=project.precision)
                if student_score > 65:
                    res[grade].append(
                        self._tool_count_sub_code_score(answers=student_group, unit_name=student_name)
                    )
        self.grade_special_students = res

    # 计算工具
    def _tool_count_student_score(self, score: pd.DataFrame):
        data = []
        handred = set(range(0, 101))
        score['score'] = score.score.apply(lambda x: int(x))

        for s, row in score.groupby('score'):
            handred.discard(s)
            data.append((s, int(row.score.count())))
        for h in handred:
            data.append((h, 0))
        data.sort(key=lambda x: x[0])
        x_axis, y_axis = [], []
        for (s, student_count) in data:
            x_axis.append(s)
            y_axis.append(student_count)

        return {
            "name": self.meta_unit.name,
            "x_axis": x_axis,
            "y_axis": y_axis
        }

    def _tool_count_sub_code_score(self, answers: pd.DataFrame, unit_name: str = ''):
        mht_scores = defaultdict(list)
        x_axis, y_axis = [], []
        for (student_id, mht), group in answers.groupby(by=['student_id', 'mht']):
            if mht == '效度':
                continue
            mht_scores[mht].append(group.score.sum())
        for mht, score_list in mht_scores.items():
            x_axis.append(mht)
            y_axis.append(Util.format_num(float(sum(score_list) / len(score_list)), precision=project.precision))

        return {
            "name": unit_name if unit_name else self.meta_unit.name,
            "x_axis": x_axis,
            "y_axis": y_axis,
        }


@dataclass
class MhtWebData(MhtData):
    pass


@dataclass
class MhtPlusApiData(MhtData):
    code_word_list: Set[str] = field(default_factory=lambda: {'mht', 'psy'})


@dataclass
class MhtPlusQusApiData(MhtData):
    code_word_list: Set[str] = field(default_factory=lambda: {'mht', 'psy', 'mgarbage'})
