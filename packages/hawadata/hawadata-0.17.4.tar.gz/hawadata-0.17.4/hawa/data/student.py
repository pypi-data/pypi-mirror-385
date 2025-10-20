import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from hawa.base.errors import NoAnswersError
from hawa.common.query import DataQuery
from hawa.config import project
from hawa.paper.health import HealthApiData
from hawa.paper.mht import MhtPlusApiData


@dataclass
class StudentMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'student'
    meta_student_id: Optional[int] = None  # 必填
    student_name: Optional[str] = ''

    def _to_init_a0_meta(self):
        if not self.meta_student_id:
            raise ValueError("meta_student_id 必填")


@dataclass
class StudentHealthApiData(StudentMixin, HealthApiData):
    is_filter_cls_less10: bool = False

    def _to_init_a_meta_unit(self):
        try:
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_student_id))
        except TypeError as e:
            self.__class__.query = DataQuery()
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_unit_id))
        self.student_name = self.meta_unit.name
        if self.meta_unit.client_id == 10:
            self.different_mode = 'xx'

    def _to_init_d_cases(self, is_cleared: bool = True):
        super()._to_init_d_cases(is_cleared=False)

    def _to_init_e_answers(self):
        """筛选学生的答案"""
        self.answers = self.query.query_answers(case_ids=self.case_ids, student_id=self.meta_student_id)

        if len(self.answers) == 0:
            raise NoAnswersError(f"学生 {self.meta_student_id} 没有答题记录")



def count_segment_scores(score: float, limit_group: list[float]) -> list[float]:
    reduce_limit = [item - limit_group[i - 1] if i else item for i, item in enumerate(limit_group)]
    for i, limit in enumerate(limit_group):
        if score <= limit:
            if i == 0:
                return [score]
            else:
                return reduce_limit[:i] + [score - limit_group[i - 1]]


def get_mht_code_describe(code: str, level: str):
    mht_map = {
        "学习焦虑": {
            "非常健康": "非常健康(3分以下)：学习焦虑低，学习不会受到困扰，能正确对待考试成绩。",
            "健康": "正常波动（3-8分）：学习焦虑在正常范围波动，建议主动关注自己的学习、考试等相关问题，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：对考试怀有恐惧心理，无法安心学习，十分关心考试分数。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "对人焦虑": {
            "非常健康": "非常健康(3分以下)：热情，大方，容易结交朋友。",
            "健康": "正常波动（3-8分）：对人焦虑在正常范围波动，建议主动关注自己的人际适应、师生关系、亲子关系、同学关系等相关问题，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：过分注重自己的形象，害怕与人交往，退缩。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "孤独倾向": {
            "非常健康": "非常健康(3分以下)：爱好社交，喜欢寻求刺激，喜欢与他人在一起。",
            "健康": "正常波动（3-8分）：孤独倾向在正常范围波动，建议主动关注自己心境和情绪的波动，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：孤独、抑郁，不善与人交往，自我封闭。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "自责倾向": {
            "非常健康": "非常健康(3分以下)：自信，能正确看待失败。",
            "健康": "正常波动（3-8分）：自责倾向在正常范围波动，建议主动关注自己对成败、挫折的认知，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：自卑，常怀疑自己的能力，常将失败、过失归咎于自己。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "过敏倾向": {
            "非常健康": "非常健康(3分以下)：敏感性较低，能较好地处理日常事物。",
            "健康": "正常波动（3-8分）：过敏倾向在正常范围波动，建议主动关注自己对学习、生活和人际关系的调整需求，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：过于敏感，容易为一些小事而烦恼。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "身体症状": {
            "非常健康": "非常健康(3分以下)：基本没有身体异常表现。",
            "健康": "正常波动（3-8分）：身体症状在正常范围波动，建议主动关注自己身体生理上的明显改变，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：在极度焦虑的时候，会出现呕吐失眠、小便失禁等明显症状。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "恐怖倾向": {
            "非常健康": "非常健康(3分以下)：基本没有恐怖感。",
            "健康": "正常波动（3-8分）：恐怖倾向在正常范围波动，建议主动关注自己对日常生活中常见事物的恐怖反应，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：对某些日常事物，如黑暗等，有较严重的恐惧感。这类被试必须接受为他制定的有针对性的特别指导计划。"
        },
        "冲动倾向": {
            "非常健康": "非常健康(3分以下)：基本没有冲动。",
            "健康": "正常波动（3-8分）：冲动倾向在正常范围波动，建议主动关注自己对情况、行为的冲动倾向，在必要的时候主动寻求教师、家长和同学帮助。",
            "预警": "单项预警(8分以上)：十分冲动，自制力差。这类被试必须接受为他制定的有针对性的特别指导计划。"
        }
    }
    return mht_map[code][level]


@dataclass
class StudentMhtPlusApiData(StudentMixin, MhtPlusApiData):
    """"""
    meta_student_id: Optional[int] = None  # 必填
    student_name: Optional[str] = ''
    is_filter_cls_less10: bool = False

    def _to_init_a_meta_unit(self):
        try:
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_student_id))
        except TypeError as e:
            self.__class__.query = DataQuery()
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_unit_id))
        if self.meta_unit.client_id == 10:
            self.different_mode = 'xx'
        self.student_name = self.meta_unit.name

    def _to_init_d_cases(self, is_cleared: bool = True):
        super()._to_init_d_cases(is_cleared=False)

    def _to_init_e_answers(self):
        """筛选学生的答案"""
        self.answers = self.query.query_answers(case_ids=self.case_ids, student_id=self.meta_student_id)

        if len(self.answers) == 0:
            raise NoAnswersError(f"学生 {self.meta_student_id} 没有答题记录")


    def count_student_archive(self):
        """获取学生档案"""
        student = self.students.iloc[0]
        school = self.schools.iloc[0]
        extra = json.loads(student.extra)

        # source 2021浙江心理 9 source mht 100
        items = self.items
        answers = self.answers
        if len(answers) not in (109, 129):
            raise ValueError('答题数量不对')
        answer_map = {a.item_id: a.answer for _, a in answers.iterrows()}
        item_codes = self.item_codes.loc[self.item_codes.category == 'mht', :]
        codes = self.codebook.loc[self.codebook.code.isin(item_codes.code), :]
        item_chinese_code_names = {c['code']: c['name'] for _, c in codes.iterrows()}
        item_code_map = {row['item_id']: item_chinese_code_names[row['code']] for _, row in item_codes.iterrows()}

        records, ph9_records, mht_records = [], [], []
        for _, item in items.iterrows():
            try:
                record = {
                    'item_id': item['id'], 'answer': answer_map[item.id], 'code': item_code_map.get(item['id'], ''),
                    "score": 0, 'category': item.source
                }
            except KeyError:
                continue
            if item.source == 'mht' and answer_map[item.id] == 'A':
                record['score'] = 1
            elif item.source == '2021浙江心理':
                ans_score_map = dict(zip('ABCDE', range(5)))
                record['score'] = ans_score_map[answer_map[item.id]]
            match item.source:
                case 'mht':
                    mht_records.append(record)
                case '2021浙江心理':
                    ph9_records.append(record)
            records.append(record)

        ph9_score = sum([i['score'] for i in ph9_records])
        ph9_descrite = '没有忧郁症(注意自我保重)'
        if ph9_score >= 20:
            ph9_descrite = '可能有重度忧郁症 (一定要看心理医生或精神科医生)'
        elif ph9_score >= 15:
            ph9_descrite = '可能有中重度忧郁症 (建议咨询心理医生或精神科医生)'
        elif ph9_score >= 10:
            ph9_descrite = '可能有中度忧郁症 (最好咨询心理医生或心理医学工作者)'
        elif ph9_score >= 5:
            ph9_descrite = '可能有轻微忧郁症 (建议咨询心理医生或心理医学工作者)'

        mht_score = sum([i['score'] for i in mht_records if i['code'] != '效度'])

        mht_thing_score = defaultdict(float)
        mht_group_records = defaultdict(list)
        mht_radar_codes, mht_radar_score = [], []
        for mht_r in mht_records:
            if mht_r['code'] != '效度':
                mht_thing_score[mht_r['code']] += mht_r['score']
                mht_group_records[mht_r['code']].append(mht_r)

        is_super_bad = False
        if max(mht_thing_score.values()) > 10:
            is_super_bad = True
        for k, v in mht_thing_score.items():
            mht_radar_codes.append({"name": k, "max": 15})
            mht_radar_score.append(v)

        mht_code_records = []
        for code, mht_group in mht_group_records.items():
            code_score = mht_thing_score[code]
            code_describe = '非常健康'
            if code_score >= 8:
                code_describe = '预警'
            elif code_score >= 3:
                code_describe = '健康'

            record = {
                "code": code, "max": 15, "total_score": code_score,
                "describe": code_describe,
                "scores": count_segment_scores(score=code_score, limit_group=[3, 8, 15]),
                "detail": get_mht_code_describe(code=code, level=code_describe)
            }
            mht_code_records.append(record)
        return {
            "student": {
                "school": school['name'],
                "gender": student.gender,
                "name": student.nickname,
                "grade": extra['grade'] if extra.get('grade') else extra['case_id'][-2:],
                "klass": extra.get('class', extra.get('klass', extra.get('cls', 0)))
            },
            "score": {
                "ph9": ph9_score,
                "ph9_scores": count_segment_scores(score=ph9_score, limit_group=[4, 9, 14, 19, 27]),
                "mht": mht_score,
                "mht_code_records": mht_code_records,
                "radar": {
                    "codes": mht_radar_codes,
                    "scores": mht_radar_score
                }
            },
            "result": {
                "ph9": ph9_descrite,
            },
            "is_super_bad": is_super_bad,
        }
