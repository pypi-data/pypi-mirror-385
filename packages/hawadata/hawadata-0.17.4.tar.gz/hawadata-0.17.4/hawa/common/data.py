"""通用的 report data 构造器，支持 校、区、市、省、全国级别的通用报告数据构造"""
import itertools
import json
import string
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from json import JSONDecodeError
from typing import Optional, ClassVar, Any, Set

import pandas as pd
import pendulum

from hawa.base.db import DbUtil, RedisUtil
from hawa.base.decos import log_func_time
from hawa.base.errors import NoCasesError, NoValidAnswers
from hawa.common.query import DataQuery
from hawa.common.utils import GradeData, CaseData, Measurement, Util
from hawa.config import project


class MetaCommonData(type):
    def __new__(cls, name, bases, attrs):
        attrs['db'] = DbUtil()
        attrs['redis'] = RedisUtil()
        attrs['query'] = DataQuery()
        return super().__new__(cls, name, bases, attrs)


@dataclass
class TargetsCount:
    targets: set[str] = field(default_factory=set)
    count: int = 0
    field_extra: str = ''
    field_extra_count: int = 0


@dataclass
class CommonData(metaclass=MetaCommonData):
    # 构造单位
    meta_unit_type: Optional[str] = ''  # class/school/group/district/city/province/country
    meta_unit_id: Optional[int] = None
    meta_unit: Optional[Any] = None
    grade: Optional[GradeData] = None  # 必填

    different_mode: Optional[str] = 'default'  # 用于区分数据的不同模式 default默认/xx新乡

    # 时间目标
    target_year: Optional[int] = None
    last_year_num: Optional[int] = None
    is_load_last: bool = True  # 仅计算往年数据时 为 False

    is_load_all: bool = True  # 加载全部数据
    is_filter_cls_less10: bool = True

    # 卷子
    test_type: str = ''
    test_types: list = field(default_factory=list)
    code_word_list: Set[str] = field(default=set)  # 卷子使用指标的词表，详见继承

    # meta class tool
    db: ClassVar[DbUtil] = None
    redis: ClassVar[RedisUtil] = None
    query: ClassVar[DataQuery] = None

    # 原始数据

    school_ids: list[int] = field(default_factory=list)
    schools: pd.DataFrame = field(default_factory=pd.DataFrame)

    codebook: pd.DataFrame = field(default_factory=pd.DataFrame)

    cases: pd.DataFrame = field(default_factory=pd.DataFrame)
    case_ids: list[int] = field(default_factory=list)
    paper_ids: list[int] = field(default_factory=list)
    case_project_ids: Counter = field(default_factory=Counter)

    answers: pd.DataFrame = field(default_factory=pd.DataFrame)
    item_codes: pd.DataFrame = field(default_factory=pd.DataFrame)

    students: pd.DataFrame = field(default_factory=pd.DataFrame)
    student_ids: set[int] = field(default_factory=set)
    student_count: Optional[int] = None

    item_ids: Optional[set[int]] = None
    items: Optional[pd.DataFrame] = None

    # 辅助工具
    grade_util: Optional[GradeData] = None
    case_util: Optional[CaseData] = None
    rank_names = ['待提高', '中等', '良好', '优秀']
    measurement = Measurement()

    # 计算数据
    final_answers: pd.DataFrame = field(default_factory=pd.DataFrame)
    final_scores: pd.DataFrame = field(default_factory=pd.DataFrame)
    grade_final_scores: pd.DataFrame = field(default_factory=pd.DataFrame)

    # 去年全国数据
    last_year = None
    last_year_code_scores: Optional[pd.DataFrame] = field(default_factory=pd.DataFrame)

    def __post_init__(self):
        # 初始化数据
        if self.is_load_all:
            self.load_all_data()

            # 构建辅助工具
            self._to_build_helper()

            # 计算数据
            count_functions = [i for i in dir(self) if i.startswith('_to_count_')]
            for func in count_functions:
                getattr(self, func)()

        else:
            self.load_less_data()
            self._to_build_helper()

    def _to_init_a_meta_unit(self):
        try:
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_unit_id))
        except TypeError as e:
            self.__class__.query = DataQuery()
            self.meta_unit = self.query.query_unit(self.meta_unit_type, str(self.meta_unit_id))
        if '百万' in self.meta_unit.name:
            self.different_mode = 'xx'

    def _to_init_b_time(self):
        if not self.target_year:
            self.target_year = pendulum.now().year
        self.last_year_num = self.target_year - 1

    def _to_init_c_schools(self):
        if self.school_ids:
            self.schools = self.query.query_schools_by_ids(self.school_ids)
        else:
            match self.meta_unit_type:
                case 'country':
                    self.schools = self.query.query_schools_all()
                case 'province':
                    self.schools = self.query.query_schools_by_startwith(self.meta_unit_id // 10000)
                case 'city':
                    self.schools = self.query.query_schools_by_startwith(self.meta_unit_id // 100)
                case 'district':
                    self.schools = self.query.query_schools_by_startwith(self.meta_unit_id)
                case 'school' | 'class' | 'student':
                    self.schools = self.query.query_schools_by_ids([self.meta_unit_id])
                case 'group':
                    self.schools = self.query.query_schools_by_group_id(group_id=self.meta_unit_id)
                case _:
                    raise ValueError(f'unknown meta_unit_type: {self.meta_unit_type}')
            self.school_ids = self.schools['id'].tolist()

    def _to_init_d_cases(self, is_cleared: bool = True):
        start_stamp = pendulum.datetime(self.target_year, 1, 1)
        end_stamp = pendulum.datetime(self.target_year + 1, 1, 1)
        start_stamp_str = start_stamp.format(project.format)
        end_stamp_str = end_stamp.format(project.format)

        papers = self.query.query_papers(test_types=self.test_types, test_type=self.test_type)
        paper_ids = papers['id'].tolist()

        self.cases = self.query.query_cases(
            school_ids=self.school_ids,
            paper_ids=paper_ids,
            valid_to_start=start_stamp_str,
            valid_to_end=end_stamp_str,
            is_cleared=is_cleared
        )
        if self.cases.empty:
            raise NoCasesError(f'no cases:{self.meta_unit} {self.school_ids}')
        self.case_ids = self.cases['id'].tolist()
        self.school_ids = self.cases['school_id'].unique().tolist()

        if self.grade:
            self.cases = self.cases.loc[self.cases['id'] % 100 == self.grade, :]
            self.case_ids = self.cases['id'].tolist()
        if len(self.cases) == 0:
            raise NoCasesError(f'grade {self.grade} cases is empty')
        self.paper_ids = self.cases['paper_id'].tolist()

    def _to_init_e2_paper_items(self):
        self.paper_items = self.query.query_paper_items(self.paper_ids)


    @log_func_time
    def _to_init_e_answers(self):
        self.answers = self.query.query_answers(case_ids=self.case_ids)
        if self.answers.empty:
            raise NoValidAnswers(f"{self.meta_unit.id} no valid answers")

    def _to_init_f_students(self):
        self.student_ids = set(self.answers['student_id'].tolist())
        student_id_list = list(self.student_ids)
        self.students = self.query.query_students(student_id_list, mode=self.different_mode)
        self.student_count = len(self.students)
        try:
            self.students['student_grade'] = self.students['extra'].apply(lambda x: json.loads(x)['grade'])
        except (KeyError, JSONDecodeError):
            self.students['student_grade'] = None

    def _to_init_g_items(self):
        """Hawa测评仅取试卷 items/answers，其他测评取全部"""
        is_hawa = 'publicWelfare' in self.test_types
        self.item_ids = set(self.answers['item_id'].drop_duplicates())
        paper_item_ids = set(self.paper_items['item_id'].tolist())
        self.item_ids = self.item_ids & paper_item_ids
        self.items = self.query.query_items(self.item_ids, is_hawa=is_hawa)
        if is_hawa:
            self.item_ids = set(self.items['id'].tolist())
            self.answers = self.answers.loc[self.answers['item_id'].isin(self.item_ids)]

    def _to_init_y_item_codes(self):
        word_list = self.code_word_list | {'other'} if len(self.code_word_list) == 1 else self.code_word_list
        self.item_codes = self.query.query_item_codes(self.item_ids, categories=list(word_list))

    def _to_init_z_dim_field(self):
        cache_key = f"{project.PROJECT}:codebook"
        if data := self.redis.conn.get(cache_key):
            self.codebook = pd.DataFrame.from_records(json.loads(data))
        else:
            self.codebook = self.query.query_codebook()
            cache_data = self.codebook.to_json(orient='records', force_ascii=False)
            self.redis.conn.set(cache_key, cache_data, ex=60 * 60 * 24 * 7)

    def _to_build_helper(self):
        self.grade = GradeData(case_ids=self.case_ids)
        self.case = CaseData(cases=self.cases)
        self.grade_util = GradeData(case_ids=self.case_ids)
        self.case_util = CaseData(cases=self.cases)

    @log_func_time
    def _to_count_a_final_answers(self):
        items = {k: {} for k in self.code_word_list}
        # code-dimension/field  ~  item_id  ~ code   name
        for (item_id, category), codes in self.item_codes.groupby(['item_id', 'category']):
            if category in self.code_word_list:
                for _, code_data in codes.iterrows():
                    items[category][item_id] = code_data['name']

        data = pd.merge(
            self.answers, self.students.loc[:, ['id', 'gender', 'nickname', 'student_grade']],
            left_on='student_id', right_on='id'
        )
        # inner 时，final_answers 和 answers 数目不等：final_answers 过滤掉了 没有 code_word_list（维度领域或其他）的题目
        # outer 时，数目相等，不过滤任何题目
        data = pd.merge(data, self.item_codes, left_on='item_id', right_on='item_id', how='inner')


        self.set_data_extra(d=data, set_grade=True, set_class=True)

        data['username'] = data['nickname']

        # clear user.grade != case.grade
        temp_compare_data = data.loc[data['grade'] == data['student_grade'], :]
        if not temp_compare_data.empty:
            data = temp_compare_data

        for code_word in self.code_word_list:
            data[code_word] = data.item_id.apply(
                lambda x: self.get_code_name_items(item_id=x, word=code_word, items=items))
        self.final_answers = data.drop_duplicates(subset=['case_id', 'student_id', 'item_id'])

        if self.is_filter_cls_less10:
            self.final_answers = self.filter_answers_cls_less10(ans=self.final_answers)
            self.student_ids = set(self.final_answers['student_id'].tolist())


    @log_func_time
    def _to_count_b_final_scores(self):
        self.final_scores = self.count_final_score(answers=self.final_answers)

    @staticmethod
    def get_code_name_items(item_id, word: str, items: dict):
        try:
            return items[word][item_id]
        except KeyError:
            return ''

    @staticmethod
    def count_level(score, mode: str = 'f'):
        assert mode in ('f', 'r'), 'only support feedback or report'
        if score >= 90:
            a = 'A'
        elif score >= 80:
            a = 'B'
        elif score >= 60:
            a = 'C'
        else:
            a = 'D'
        key = "RANK_LABEL" if mode == 'r' else 'FEEDBACK_LEVEL'
        return project.ranks[key][a]

    def count_final_score(self, answers: pd.DataFrame):
        records = []
        for case_id, group in answers.groupby('case_id'):
            for student_id, student_group in group.groupby('student_id'):
                score = student_group.score.mean() * 100
                record = {
                    "student_id": student_id,
                    "username": self.get_col_value(student_group['username']),
                    "grade": self.get_col_value(student_group['grade']),
                    "gender": self.get_col_value(student_group['gender']),
                    "score": score,
                    "level": self.count_level(score),
                    "cls": self.get_col_value(student_group['cls']),
                }
                records.append(record)
        return pd.DataFrame.from_records(records)

    def get_last_year_miss(self, grade: int):
        key = f'{project.REDIS_PREFIX}{self.last_year_num}:data'
        data = json.loads(self.redis.conn.get(key))
        try:
            grade_data = data[str(grade)]
        except KeyError:
            for i in range(1, grade):
                temp_grade = grade - i
                grade_data = data.get(str(temp_grade))
                if grade_data:
                    break
            else:
                grade_data = data[str(3)]

        grade_data['people']['grade'] = f"{grade}年级"
        for k, v in grade_data['code'].items():
            grade_data['code'][k]['grade'] = grade
        return grade_data

    def sort_rank(self, name: str) -> int:
        order_map = dict(zip(self.rank_names, range(0, 4)))
        return order_map[name]

    def count_dim_field_ranks(self, item_code: str):
        """
        计算维度、领域的 ranks 分级比例
        :param item_code:dimision or field
        """
        r = defaultdict(list)
        codes = set()
        for (s, c), student_code_group in self.final_answers.groupby(['student_id', item_code]):
            s_c_score = Util.format_num(student_code_group.score.mean() * 100, project.precision)
            codes.add(c)
            r[c].append(s_c_score)
        codes = list(codes)
        df = pd.DataFrame.from_records(r)
        res = {}
        for c in codes:
            row = df[c]
            base_row_ranks = {k: 0 for k in self.rank_names}
            count_row_ranks = pd.cut(
                row, bins=[0, 60, 80, 90, 100], labels=self.rank_names,
                right=False, include_lowest=True,
            ).value_counts().to_dict()
            sum_value = sum(count_row_ranks.values())
            row_ranks = {k: Util.format_num(v / sum_value * 100, project.precision) for k, v in
                         (base_row_ranks | count_row_ranks).items()}
            res[c] = row_ranks
        code_map = self.get_dim_field_order(key=item_code)
        return {
            "data": res, "codes": sorted(codes, key=lambda x: code_map[x]),
            "legend": self.rank_names,
        }

    def count_sub_units(self, target_level: str = 'school'):
        """查询下辖单位"""
        match target_level:
            case 'school':
                return self.school_ids
            case 'district':
                return {i // (10 ** 4) for i in self.school_ids}
            case _:
                raise ValueError(f"target_level: {target_level} not support")

    def get_cascade_students(self):
        """年级/班级/学生嵌套"""
        data = self.final_scores
        self.set_data_extra(d=data, set_grade=False, set_class=True)
        res = []
        for grade, grade_group in data.groupby('grade'):
            grade_row = {
                'label': f'{grade}年级', 'value': grade,
                'children': [], "is_leaf": False
            }
            for cls, cls_group in grade_group.groupby('cls'):
                cls_row = {
                    'label': f'{cls}班', 'value': int(str(cls)),
                    'children': [], "is_leaf": False
                }
                for _, student_g_row in cls_group.iterrows():
                    student_row = {
                        'label': student_g_row['username'],
                        'value': str(student_g_row['student_id']),
                        "is_leaf": True
                    }
                    cls_row['children'].append(student_row)
                if not cls_row['children']:
                    cls_row['is_leaf'] = True
                grade_row['children'].append(cls_row)
            if not grade_row['children']:
                grade_row['is_leaf'] = True
            res.append(grade_row)
        return res

    def get_cascade_schools_from_province(self):
        """省-市-区县-学校的 cascade 数据"""
        sch_ids = self.school_ids
        province_ids = {i // (10 ** 8) * 10000 for i in sch_ids}
        city_ids = {i // (10 ** 6) * 100 for i in sch_ids}
        district_ids = {i // (10 ** 4) for i in sch_ids}
        location_ids = province_ids | city_ids | district_ids
        locations = self.query.query_locations(list(location_ids))
        schools = self.schools
        location_map = {lo['id']: lo for _, lo in locations.iterrows()}
        school_map = {sch['id']: sch for _, sch in schools.iterrows()}
        res = []
        for p_id in province_ids:
            p = location_map[p_id]
            p_row = {
                'label': p['name'], 'value': p['id'], 'children': [], "is_leaf": False
            }
            if p_id not in project.municipality_ids:
                for c_id in city_ids:
                    if c_id // 10000 * 10000 != p_id:
                        continue
                    c = location_map[c_id]
                    c_row = {
                        'label': c['name'], 'value': c['id'], 'children': [], "is_leaf": False
                    }
                    for d_id in district_ids:
                        if d_id // 100 * 100 != c_id:
                            continue
                        d = location_map[d_id]
                        d_row = {
                            'label': d['name'], 'value': d['id'], 'children': [], "is_leaf": False
                        }
                        for s_id in sch_ids:
                            if s_id // 10000 != d_id:
                                continue
                            s = school_map[s_id]
                            s_row = {
                                'label': s['name'], 'value': s['id'], "is_leaf": True
                            }
                            d_row['children'].append(s_row)
                        c_row['children'].append(d_row)
                    p_row['children'].append(c_row)
                res.append(p_row)
            else:
                for d_id in district_ids:
                    if d_id // 10000 * 10000 != p_id:
                        continue
                    d = location_map[d_id]
                    d_row = {
                        'label': d['name'], 'value': d['id'], 'children': [], "is_leaf": False
                    }
                    for s_id in sch_ids:
                        if s_id // 10000 != d_id:
                            continue
                        s = school_map[s_id]
                        s_row = {
                            'label': s['name'], 'value': s['id'], "is_leaf": True
                        }
                        d_row['children'].append(s_row)
                    p_row['children'].append(d_row)
                res.append(p_row)
        return res

    def get_dim_field_order(self, key: str):
        """获取维度/领域顺序的映射
        :param key: dimension/field
        """
        data = self.codebook.loc[self.codebook['category'] == key, :]
        order_map = {i['name']: i['order'] for _, i in data.iterrows()}
        if '其他' in order_map.keys():
            del order_map['其他']
        return order_map

    def load_less_data(self):
        init_functions = [i for i in dir(self) if i.startswith('_to_init_')]
        for func in init_functions:
            if '_to_init_e_' in func:
                break
            getattr(self, func)()

    def load_all_data(self):
        init_functions = [i for i in dir(self) if i.startswith('_to_init_')]
        for func in init_functions:
            getattr(self, func)()

    def set_data_extra(self, d: pd.DataFrame, set_grade: bool = True, set_class: bool = True):
        """为 数据 设置不同模式下的 extra 字段"""
        if self.different_mode == 'xx':
            user_classes = {}
            user_grades = {}
            for _, row in self.students.iterrows():
                extra = json.loads(row['extra'])
                user_grades[row['id']] = extra.get('grade', 0)
                user_classes[row['id']] = extra.get('class', 0)
            if set_grade:
                d['grade'] = d['student_id'].apply(lambda x: user_grades.get(x, ''))
            if set_class:
                d['cls'] = d['student_id'].apply(lambda x: user_classes.get(x, ''))
        else:
            if set_grade:
                d['grade'] = d['case_id'].apply(lambda x: x % 100)
            if set_class:
                d['cls'] = d['student_id'].apply(lambda x: int(str(x)[13:15]))

    @property
    def psy_item_ids(self):
        items = self.query.query_phq_items()
        return set(items['id'].tolist())

    @property
    def mgarbage_item_ids(self):
        items = self.query.query_mgarbage_items()
        return set(items['id'].tolist())

    def count_rank_students(self):
        """计算各等级人数"""
        base_ranks = {k: 0 for k in project.ranks['FEEDBACK_LEVEL'].values()}
        count_ranks = self.final_scores['level'].value_counts().to_dict()
        return base_ranks | count_ranks

    @staticmethod
    def get_col_value(col):
        return col.tolist()[0]

    @staticmethod
    def filter_answers_cls_less10(ans: pd.DataFrame):
        """过滤班级学生数小于10的班级"""

        # 步骤2: 对student_id去重，然后根据grade和cls分组，计数每组的学生数量
        grouped_data = ans.drop_duplicates(subset='student_id').groupby(['grade', 'cls']).size().reset_index(
            name='student_count')

        # 步骤3: 过滤出学生人数大于或等于10的年级和班级
        filtered_groups = grouped_data[grouped_data['student_count'] >= 10]

        # 步骤4: 使用过滤后的数据过滤原始数据集
        filtered_data = ans[
            ans.set_index(['grade', 'cls']).index.isin(filtered_groups.set_index(['grade', 'cls']).index)]

        # 显示过滤后的数据
        return filtered_data

    def count_dim_or_field_scores_by_answers(self, answers, item_code, res_format: str = 'dict'):
        """
        计算维度或领域得分
        :param answers: 由 final answers 中取出的部分数据，属于某一主体
        :param item_code: dimension/field
        :param res_format: dict/list
        :return:
        """
        keys, values, mapping = [], [], {}
        for code, code_group in answers.groupby(item_code):
            score = Util.format_num(code_group.score.mean() * 100, project.precision)
            keys.append(code)
            values.append(score)
            mapping[code] = score
        match res_format:
            case 'dict':
                return mapping
            case 'list':
                code_map = self.get_dim_field_order(key=item_code)
                keys = sorted(keys, key=lambda x: code_map[x])
                values = [mapping[k] for k in keys]
                return keys, values

    def get_grade_focus(self, limit: int = 60, step: int = 5, mode: str = 'all'):
        """
        获取所有年级的优先关注点
        mode:all/dimension/field
        """
        res = {}
        for grade, grade_answers in self.final_answers.groupby('grade'):

            dimensions = self.count_dim_or_field_scores_by_answers(
                answers=grade_answers, item_code='dimension', res_format='dict'
            )
            fields = self.count_dim_or_field_scores_by_answers(
                answers=grade_answers, item_code='field', res_format='dict'
            )
            match mode:
                case 'all':
                    grade_res = self.get_limit_focus_recu_res(data=dimensions | fields, limit=limit, step=step)
                case 'dimension':
                    grade_res = self.get_limit_focus_recu_res(data=dimensions, limit=limit, step=step)
                case 'field':
                    grade_res = self.get_limit_focus_recu_res(data=fields, limit=limit, step=step)
                case _:
                    raise
            res[grade] = grade_res
        return res

    def get_limit_focus_recu_res(self, data: dict, limit: int, step: int = 2):
        res = [k for k, v in data.items() if v < limit]
        if res:
            return res
        if not res:
            return self.get_limit_focus_recu_res(data, limit + step, step)
        return res

    @staticmethod
    def count_mean_score_by_final_scores(scores: pd.DataFrame):
        return round(scores.score.mean(), 1)

    def count_11scores_by_answers(self, ans: pd.DataFrame):
        """通过传入的 answers 计算 11 个得分 6f 4d 1total"""
        res = {
            "total": self.count_mean_score_by_final_scores(scores=self.count_final_score(answers=ans))
        }
        for f, field_ans in ans.groupby('field'):
            field_score = self.count_mean_score_by_final_scores(scores=self.count_final_score(answers=field_ans))
            res[f] = field_score
        for dim, dim_ans in ans.groupby('dimension'):
            dim_score = self.count_mean_score_by_final_scores(scores=self.count_final_score(answers=dim_ans))
            res[dim] = dim_score
        return res

    def count_gender_scores33(self, ans: pd.DataFrame, grade: Optional[int] = None, cls: Optional[int] = None):
        """计算 total/M/F 11 共 33 个得分"""
        res = {
            "total": self.count_11scores_by_answers(ans=ans) | {
                'gender': 'total', 'grade': grade, 'cls': cls,
                'group': self.count_group_name(cls=cls, gender='total')
            }
        }
        for gender, gender_ans in ans.groupby('gender'):
            res[gender] = self.count_11scores_by_answers(gender_ans) | {
                'gender': gender, 'grade': grade, 'cls': cls,
                'group': self.count_group_name(cls=cls, gender=str(gender))
            }
        return res

    @staticmethod
    def count_group_name(cls: int, gender: str = 'total'):
        """计算 11 33 组别名称"""
        prefix = f'{cls}班' if cls else ''
        suffix_map = {'total': '全体', 'M': '男生', 'F': '女生'}
        return f'{prefix}{suffix_map[gender]}'

    def count_class_detail_scores11(self):
        """
        计算学校的全部年级、班级维度领域得分 每单位 11 3组 共33个
        列：年级 组别 班级（无/年级 有/具体班级）性别（total/M/F） 6领域列 4维度列 总分列
        """
        rows33 = []
        for grade, grade_ans in self.final_answers.groupby('grade'):
            grade_gender_scores = self.count_gender_scores33(ans=grade_ans, grade=int(str(grade)), cls=None)
            rows33.append(grade_gender_scores)
            for cls, grade_cls_ans in grade_ans.groupby('cls'):
                grade_cls_gender_scores = self.count_gender_scores33(
                    ans=grade_cls_ans, grade=int(str(grade)), cls=cls)
                rows33.append(grade_cls_gender_scores)
        base_res = []
        for row33 in rows33:
            for k, v in row33.items():
                base_res.append(v)
        return base_res

    @staticmethod
    def _count_point_name(row, point_map):
        return point_map.get(row['code'].rsplit('.', 1)[0].replace('target1', 'point'), '')

    @staticmethod
    def _count_field_name(row, field_map):
        return field_map.get(row['code'].rsplit('.', 2)[0].replace("target1", "domain"), '')

    @staticmethod
    def _retain_prec(n: float, prec: int = 1):
        n = n * 100
        return int(n) if n in (0, 0.0, 100.0, 100) else round(n, prec)

    @staticmethod
    def _count_reverse_sorted_rank(rank_data: dict):
        base = [(v, k) for k, v in rank_data.items()]
        res = [b for b in sorted(base, key=lambda x: x[0], reverse=True)]
        return res

    def count_rank_dis_by_final_scores(self, scores: pd.DataFrame):
        """计算 scores 的 rank 分布比例"""
        base = dict(
            zip(project.ranks['FEEDBACK_LEVEL'].values(),
                [0] * len(project.ranks['FEEDBACK_LEVEL'])))
        count = base | scores.level.value_counts().to_dict()
        count = {k: v / sum(count.values()) for k, v in count.items()}
        return {k: self._retain_prec(v) for k, v in count.items()}

    def count_field_point_target(self, page_limit: int = 38):
        periods = tuple(self.grade_util.grade_periods + ['-'])
        codes_sql = f"select * from code_guide where period in {periods} or category in ('G.domain','G.point');"
        codes = self.query.raw_query(codes_sql)
        targets = codes.loc[codes['category'] == 'G.target1', :]
        targets['target'] = targets['name']
        target1_points = codes.loc[codes['category'] == 'G.point', :]
        target1_points_map = {i['code']: i['name'] for _, i in target1_points.iterrows()}
        fields = codes.loc[codes['category'] == 'G.domain', :]
        fields_map = {i['code']: i['name'] for _, i in fields.iterrows()}
        targets['point'] = targets.apply(lambda x: self._count_point_name(x, target1_points_map), axis=1)
        targets['field'] = targets.apply(lambda x: self._count_field_name(x, fields_map), axis=1)
        field_count_map = targets['field'].value_counts().to_dict()
        point_count_map = targets['point'].value_counts().to_dict()
        targets['field_count'] = targets['field'].apply(lambda x: field_count_map.get(x, 0))
        targets['point_count'] = targets['point'].apply(lambda x: point_count_map.get(x, 0))
        targets['field_prefix'] = targets['code'].apply(lambda x: x.split('.')[2])
        targets['point_prefix'] = targets['code'].apply(lambda x: f"{x.split('.')[2]}.{x.split('.')[3]}")
        cols = ['field', 'point', 'target', 'field_count', 'point_count', 'field_prefix', 'point_prefix', 'field_extra']

        new_target_counts = {row['target']: row['field_count'] for _, row in targets.iterrows()}
        new_target_field_extra = {row['target']: row['field'] for _, row in targets.iterrows()}
        target_counts = []
        for the_field, field_group in targets.groupby('field'):
            field_count = field_group['field_count'].values[0]
            if field_count < page_limit:
                continue

            the_target_count = TargetsCount(field_extra=the_field)

            for point_prefix, point_group in field_group.groupby('point_prefix'):
                point_count = point_group['point_count'].values[0]

                # 单段终止条件
                if the_target_count.count + point_count > page_limit:
                    target_counts.append(the_target_count)
                    new_extra_count = the_target_count.field_extra_count + 1
                    the_target_count = TargetsCount(
                        field_extra=f'{the_field}extra{new_extra_count}', field_extra_count=new_extra_count)

                the_target_count.count += point_count
                the_target_count.targets |= set(point_group['target'].tolist())
            else:
                target_counts.append(the_target_count)

        for the_tc in target_counts:
            new_target_counts |= {k: the_tc.count for k in the_tc.targets}
            new_target_field_extra |= {k: the_tc.field_extra for k in the_tc.targets}

        targets['field_count'] = targets.apply(lambda x: new_target_counts.get(x['target'], 0), axis=1)
        targets['field_extra'] = targets.apply(lambda x: new_target_field_extra.get(x['target'], ''), axis=1)

        res = targets.loc[:, cols]
        return res.to_dict(orient='records')

    @staticmethod
    def count_rank_by_score(score: float):
        if score >= 90:
            level = 'A'
        elif score >= 80:
            level = 'B'
        elif score >= 60:
            level = 'C'
        else:
            level = 'D'
        return project.ranks['FEEDBACK_LEVEL'][level]

    @staticmethod
    def _count_item_targets(percent_item_id_map, all_item_codes: pd.DataFrame, all_code_guides: pd.DataFrame,
                            category: str = 'G.target1'):
        res = []
        for percent, item_ids in percent_item_id_map.items():
            conditions = (all_item_codes['item_id'].isin(item_ids) &
                          (all_item_codes['category'] == category))
            item_targets = all_item_codes.loc[conditions, :]
            merge_targets = all_code_guides.merge(item_targets, on='code', how='inner', suffixes=('', '_y'))
            merge_targets['percent'] = percent
            record = {
                "name": '，'.join(merge_targets['name'].unique().tolist()),
                "percent": percent,
            }
            res.append(record)
        df = pd.DataFrame.from_records(res)
        return df

    @staticmethod
    def _count_top_last_item_ids(item_scores: pd.DataFrame, ascending: bool = True):
        res = defaultdict(list)
        score_filter = set()
        for _, row in item_scores.sort_values(by='score', ascending=ascending).iterrows():
            decimal_number = Decimal(row['score']).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP) * 100
            if len(score_filter) < 3:
                score_filter.add(decimal_number)
                res[decimal_number].append(row['item_id'])
            else:
                break
        return res

    def count_grade_class_item_target(self):
        """计算各年级各班级 top3/last3 item target 相对优势/优先关注点"""
        all_item_codes = self.query.query_item_codes(item_ids=self.item_ids, categories=None)
        item_target2_map_data = all_item_codes.loc[all_item_codes['category'] == 'G.target2', ['code', 'item_id']]
        item_target2_map = {r['item_id']: r['code'] for _, r in item_target2_map_data.iterrows()}
        all_code_guides = self.query.query_code_guides()
        res = {}
        for grade, grade_ans in self.final_answers.groupby('grade'):
            grade_data = []
            for cls, grade_cls_ans in grade_ans.groupby('cls'):

                # 计算正常的相对优势、优先关注点
                dimensions = self.count_dim_or_field_scores_by_answers(
                    answers=grade_cls_ans, item_code='dimension', res_format='dict'
                )
                fields = self.count_dim_or_field_scores_by_answers(
                    answers=grade_cls_ans, item_code='field', res_format='dict'
                )
                upper_codes, lower_codes = [], []
                for k, v in (dimensions | fields).items():
                    if v >= 80:
                        upper_codes.append(k)
                    elif v <= 60:
                        lower_codes.append(k)

                cls_score = self.count_mean_score_by_final_scores(scores=self.count_final_score(answers=grade_cls_ans))
                cls_rank = self.count_rank_by_score(score=cls_score)
                item_scores = grade_cls_ans.groupby('item_id').score.mean().to_frame().reset_index()
                item_scores['target2'] = item_scores.item_id.map(item_target2_map)
                item_scores.dropna(subset=['target2'], inplace=True)

                # get top3/last3 item_ids
                top3_item_ids = self._count_top_last_item_ids(item_scores=item_scores, ascending=False)
                last3_item_ids = self._count_top_last_item_ids(item_scores=item_scores, ascending=True)

                record = {
                    "cls": cls, "grade": grade, "score": cls_score, "rank": cls_rank,
                    "upper_codes": upper_codes, "lower_codes": lower_codes,
                    # "top3_item_ids": top3_item_ids, "last3_item_ids": last3_item_ids
                }

                categories = ['G.target1', 'G.point', 'G.target2']
                use_item_ids = {
                    "top3": top3_item_ids, "last3": last3_item_ids
                }

                for c, uk in itertools.product(categories, use_item_ids.keys()):
                    the_code_guide = self._count_item_targets(
                        percent_item_id_map=use_item_ids[uk],
                        all_item_codes=all_item_codes, all_code_guides=all_code_guides, category=c
                    )

                    match uk:
                        case 'top3':
                            record[f"{c}_{uk}_data"] = the_code_guide.to_dict(orient='records')
                        case 'last3':
                            record[f"{c}_{uk}_data"] = list(reversed(the_code_guide.to_dict(orient='records')))
                    record[f"{c}_{uk}_names"] = the_code_guide['name'].unique().tolist()[:3]

                grade_data.append(record)
            res[grade] = grade_data
        return res

    @staticmethod
    def count_str_rank(rank: dict):
        """"""
        rank = deepcopy(rank)
        level_score = round(rank['优秀'] + rank['良好'], 1)
        rank['素养'] = level_score
        rank['基础'] = round(100 - level_score, 1)
        res = {k: str(Decimal(v).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)) for k, v in rank.items()}
        return res

    @property
    def grade_class_map(self):
        """生成年级/班级映射"""
        res = {}
        max_min_score_class = defaultdict(list)
        for grade, grade_ans in self.final_answers.groupby('grade'):
            res[grade] = {"cls": []}
            max_cls, min_cls = grade_ans['cls'].max(), grade_ans['cls'].min()
            for cls, cls_ans in grade_ans.groupby('cls'):
                student_scores = self.count_final_score(answers=cls_ans)
                gc_score = self.count_mean_score_by_final_scores(scores=student_scores)
                max_min_score_class[grade].append((cls, gc_score))
                cls_student_count = len(cls_ans['student_id'].unique())
                boy_ans = cls_ans.loc[cls_ans['gender'] == 'M', :]
                girl_ans = cls_ans.loc[cls_ans['gender'] == 'F', :]
                cls_boy_count = len(boy_ans['student_id'].unique())
                cls_girl_count = len(girl_ans['student_id'].unique())
                cls_rank = self.count_rank_dis_by_final_scores(scores=student_scores)
                cls_reverse_rank = self._count_reverse_sorted_rank(cls_rank)
                cls_11_scores = self.count_11scores_by_answers(cls_ans)
                del cls_11_scores['total']
                reverse_dim_field_scores = self._count_reverse_sorted_rank(cls_11_scores)
                cls_record = {
                    "cls": cls, "student_count": cls_student_count,
                    "boy_count": cls_boy_count, "girl_count": cls_girl_count,
                    "avg_score": gc_score, "max_score": round(student_scores['score'].max(), 1),
                    "boy_score": self.count_mean_score_by_final_scores(scores=self.count_final_score(boy_ans)),
                    "girl_score": self.count_mean_score_by_final_scores(scores=self.count_final_score(girl_ans)),

                    "min_score": round(student_scores['score'].min(), 1),
                    "rank": cls_rank,
                    "str_rank": {},
                    "boy_rank": self.count_rank_dis_by_final_scores(scores=self.count_final_score(answers=boy_ans)),
                    "girl_rank": self.count_rank_dis_by_final_scores(scores=self.count_final_score(answers=girl_ans)),
                    "reverse_rank": cls_reverse_rank, "reverse_dim_fields": reverse_dim_field_scores,
                    "gender_codes_score": self.count_gender_scores33(ans=cls_ans),
                }
                for k in ('rank', 'boy_rank', 'girl_rank'):
                    cls_record['str_rank'][k] = self.count_str_rank(rank=cls_record[k])
                res[grade]["cls"].append(cls_record)
            sort_cls_scores = sorted(max_min_score_class[grade], key=lambda x: x[1])
            res[grade] |= {
                # 班级顺序的最大最小值
                "max_cls": max_cls, "min_cls": min_cls,
                # 得分最高最低的班级
                "high": sort_cls_scores[-1][0], "low": sort_cls_scores[0][0]
            }
        return res

    def temp_school_grade_class_data(self):
        """学校、年级、班级、答对率、题干、选项a、选项b、选项c、选项d、答案、健康领域、健康维度、一级目标内容、二级目标内容"""
        all_item_codes = self.query.query_item_codes(item_ids=self.item_ids, categories=None)
        all_code_guides = self.query.query_code_guides()
        all_code_book = self.codebook
        codebook_name_map = {i['code']: i['name'] for _, i in all_code_book.iterrows()}
        code_guide_name_map = {i['code']: i['name'] for _, i in all_code_guides.iterrows()}
        all_code_name_map = codebook_name_map | code_guide_name_map

        res = []
        for grade, grade_ans in self.final_answers.groupby('grade'):
            for cls, grade_cls_ans in grade_ans.groupby('cls'):
                item_scores = grade_cls_ans.groupby('item_id').score.mean()
                item_score_map = item_scores.to_dict()
                self._count_top_last_item_ids(item_scores=item_scores)
                # get top3/last3 item_ids
                top3_item_ids = self._count_top_last_item_ids(item_scores=item_scores, ascending=False)
                last3_item_ids = self._count_top_last_item_ids(item_scores=item_scores, ascending=True)
                this_item_ids = list(top3_item_ids.values()) + list(last3_item_ids.values())
                that_item_ids = []
                for i in this_item_ids:
                    that_item_ids.extend(i)
                this_items = self.items.loc[self.items['id'].isin(that_item_ids), :]
                codebook_codes = ['dimension', 'field', 'G.target1', 'G.target2']
                base = {'学校': self.meta_unit.name, '年级': grade, '班级': f"{cls}班"}
                for _, item in this_items.iterrows():
                    item_id = item['id']
                    item_code_map = {
                        "题干": item['item_text'], "答案": item['item_key'],
                        "答对率": round(item_score_map.get(item_id, 0) * 100, 1)
                    }
                    choices = item['choices'].split(";")
                    for c, t in zip(string.ascii_uppercase, choices):
                        item_code_map[f"选项{c}"] = t[3:]
                    for code in codebook_codes:
                        conditions = (all_item_codes['item_id'] == item_id) & (all_item_codes['category'] == code)
                        local_record = all_item_codes.loc[conditions, :]
                        item_code_code = local_record['code'].values[0] if len(local_record) else ''
                        if item_code_code:
                            item_code_map[code] = all_code_name_map.get(item_code_code, '')
                        else:
                            item_code_map[code] = ''
                    row = base | item_code_map
                    res.append(row)
        df_res = pd.DataFrame.from_records(res)
        df_res.sort_values(by=['学校', '年级', '班级', '答对率'], ascending=[True, True, True, False], inplace=True)
        index1 = ['学校', '年级', '班级', '答对率', '题干']
        index2 = [i for i in df_res.columns if '选项' in i]
        index3 = ['答案', 'field', 'dimension', 'G.target1', 'G.target2']
        res = df_res.loc[:, index1 + index2 + index3]
        res = res.rename(columns={
            "field": "健康领域", "dimension": "健康维度", "G.target1": "一级目标内容", "G.target2": "二级目标内容"
        }).set_index("学校")
        res.to_excel(f'{self.meta_unit.name}_0425数据.xlsx')
        return res
