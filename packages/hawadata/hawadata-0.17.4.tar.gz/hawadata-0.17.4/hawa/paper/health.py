"""健康测评数据"""

import itertools
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Union, Set

import pandas as pd
from munch import Munch
from pingouin import cronbach_alpha

from hawa.common.data import CommonData
from hawa.common.utils import Util
from hawa.config import project


@dataclass
class HealthData(CommonData):
    """健康测评数据，不应直接使用，应向下继承 city/district/school 等"""

    test_types: list[str] = field(
        default_factory=lambda: [
            "publicWelfare",
            "ZjpublicWelfare",
            "XxPublicWelfareQus",
            "publicWelfareZZ"
        ]
    )
    code_word_list: Set[str] = field(default_factory=lambda: {"dimension", "field"})

    @staticmethod
    def replace_hai(text: str, condition: list):
        if condition:
            return text
        else:
            return text.replace("还", "")


@dataclass
class HealthApiData(HealthData):
    """为 yingde api 项目提供基类"""

    def score_rank(self, grade: int, gender: str = ""):
        """
        某年级 健康素养水平各等级占比
        :param grade: 年级
        :param gender: 性别 '' 全部 'M' 男 'F' 女
        """
        base = {"优秀": 0, "良好": 0, "中等": 0, "待提高": 0}
        fs = final_scores = self.__get_grade_final_scores(grade=grade)
        if gender:
            final_scores = fs.loc[fs.gender == gender, :]
        raw = final_scores.level.value_counts().to_dict()
        data = base | raw
        sum_data = sum(data.values())
        if not sum_data:
            raise ValueError(f"grade {grade} score rank is empty")
        percent = {
            k: Util.format_num(v * 100 / sum_data, project.precision)
            for k, v in data.items()
        }
        return percent

    def gender_compare(self, grade: int):
        """某年级学生健康素养水平及性别比较图"""
        final_scores = self.__get_grade_final_scores(grade=grade)
        total_score = final_scores.score.mean()
        m_score = final_scores.loc[final_scores.gender == "M"].score.mean()
        f_score = final_scores.loc[final_scores.gender == "F"].score.mean()
        return {
            "total": Util.format_num(total_score, project.precision),
            "M": Util.format_num(m_score, project.precision),
            "F": Util.format_num(f_score, project.precision),
        }

    def dim_field_gender_compare(
        self, grade: int, item_code: str, key_format: str = "en"
    ):
        """某年级六大领域/四大维度测评得分及性别比较图"""
        final_answers = self.__get_grade_final_answers(grade=grade)
        answers = final_answers.loc[~final_answers[item_code].isnull(), :]
        raw_data = {
            "total": answers,
            "M": answers.loc[answers.gender == "M", :],
            "F": answers.loc[answers.gender == "F", :],
        }
        res = {}
        for gender_k, gender_v in raw_data.items():
            res[gender_k] = self.count_dim_or_field_scores_by_answers(
                answers=gender_v, item_code=item_code, res_format="dict"
            )
        map_order = self.get_dim_field_order(key=item_code)
        codes = answers[item_code].unique().tolist()
        codes = sorted(codes, key=lambda x: map_order[x])
        gender_box = []
        for gender_k, gender_data in res.items():
            row_data = {
                "name": gender_k
                if key_format == "en"
                else project.total_gender_map[gender_k],
                "value": [],
            }
            for c in codes:
                row_data["value"].append(res[gender_k][c])
            gender_box.append(row_data)

        return {
            "category": codes,
            "values": gender_box,
        }

    def count_student_grade(self, student_id: int):
        """计算指定学生的年级"""
        fa = self.final_answers
        student_answers = fa.loc[fa["student_id"] == int(student_id), :]
        case_ids = student_answers["case_id"].unique().tolist()
        return case_ids[0] % 100

    def __get_grade_final_answers(self, grade: int):
        return self.final_answers[self.final_answers["grade"] == grade]

    def __get_grade_final_scores(self, grade: int):
        return self.final_scores[self.final_scores["grade"] == grade]

    def get_class_scores(self):
        """获取年级各班级的分数 仅可在 school/assemble 中使用"""
        scores = self.final_scores
        scores["cls"] = scores["student_id"].apply(lambda x: f"{int(str(x)[13:15])}班")
        res = scores.groupby("cls").score.mean().to_dict()
        sorted_keys = sorted(res.keys(), key=lambda x: int(x[:-1]))
        sorted_res = {k: res[k] for k in sorted_keys}
        keys, values = (
            sorted_res.keys(),
            [Util.format_num(i) for i in sorted_res.values()],
        )
        return {"keys": list(keys), "values": list(values)}


@dataclass
class HealthReportData(HealthData):
    # 计算数据
    code_scores: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary_scores: dict = field(default_factory=dict)
    grade_good_bad = None  # 优势 优先关注点

    grade_rank_dis = None  # 年级、性别、水平学生分布占比
    grade_str_rank_dis = None  # 年级、性别、水平学生分布占比
    grade_reverse_rank_dis = None  # 占比由高到低的年级分布水平
    grade_gender_distribution = None
    grade_score = None  # 年级最高、最低、平均分
    grade_code_score = None  # 健康素养水平 所需数据
    compare_grade_year_school = None  # 比较学校与去年维度领域
    compare_all_total = None  # 比照去年数据和学校数据的全年级平均数

    def _to_count_a0_last_year_data(self):
        if not self.is_load_last:
            return
        key = f"{project.REDIS_PREFIX}{self.last_year_num}:data"
        if not self.redis.conn.exists(key):
            raise ValueError(f"last year data not exists: {key}")
        self.last_year = json.loads(self.redis.conn.get(key))
        res = []
        for grade in self.grade.grades:
            grade_data = self.get_last_year_miss(grade=grade)
            year_code_score = pd.DataFrame(grade_data["code"]).T
            year_code_score["grade"] = int(grade)
            year_code_score["i"] = [int(grade) * 10 + i for i in range(1, 11)]
            year_code_score.set_index("i", inplace=True)
            res.append(year_code_score)
        self.last_year_code_scores = pd.concat(res)

    def _to_count_c_code_scores(self):
        records = []
        for grade in self.grade.grades:
            for code in self.measurement.dimensions:
                record = self._count_grade_code_score(
                    grade=grade, code=code, category="dimension"
                )
                records.append(record)
            for code in self.measurement.fields:
                record = self._count_grade_code_score(
                    grade=grade, code=code, category="field"
                )
                records.append(record)
        self.code_scores = pd.DataFrame.from_records(records)

    def _to_count_d_summary_scores(self):
        records = defaultdict(dict)
        for grade, group in self.code_scores.groupby("grade"):
            for gender in project.gender_map.keys():
                records[grade][gender] = Util.format_num(
                    self._count_school_score(group, key=gender), project.precision
                )
        self.summary_scores = records

    def _to_count_e_grade_good_bad(self):
        records = defaultdict(dict)
        for g, group in self.code_scores.groupby("grade"):
            for gender in project.gender_map.keys():
                records[g][gender] = {
                    "dimension": {"good": [], "bad": []},
                    "field": {"good": [], "bad": []},
                }
            for _, row in group.iterrows():
                for gender in project.gender_map.keys():
                    if row[gender] >= 80:
                        if row["category"] == "dimension":
                            records[g][gender]["dimension"]["good"].append(row["code"])
                        if row["category"] == "field":
                            records[g][gender]["field"]["good"].append(row["code"])
                    elif row[gender] < 60:
                        if row["category"] == "dimension":
                            records[g][gender]["dimension"]["bad"].append(row["code"])
                        if row["category"] == "field":
                            records[g][gender]["field"]["bad"].append(row["code"])
                    else:
                        pass
                else:
                    for code in itertools.chain(
                        self.measurement.dimensions, self.measurement.fields
                    ):
                        for ccc in ["dimension", "field"]:
                            if code in records[g]["total"][ccc]["bad"]:
                                for ggg in "MF":
                                    try:
                                        records[g][ggg][ccc]["bad"].remove(code)
                                    except ValueError:
                                        pass

        self.grade_good_bad = records

    def _to_count_f_case_gender_counts(self):
        """单年级，各班级性别数据；多年级，各年级性别数据。"""
        ans = self.final_answers.drop_duplicates(subset=["student_id"])
        data = ans.loc[:, ["grade", "cls", "gender", "student_id"]]
        # 年级 班级 男生数 女生数 总人数
        # 班级 男生数 女生数 总人数
        records = []
        for grade, grade_group in data.groupby(by="grade"):
            for cls, cls_group in grade_group.groupby("cls"):
                grade_cls = Munch(grade=grade, cls=cls)
                cls_total = Munch(total=len(cls_group))
                cls_gender = cls_group.gender.value_counts().to_dict()
                records.append(grade_cls | cls_total | cls_gender)
            grade_total = Munch(total=len(grade_group))
            grade_gender = grade_group.gender.value_counts().to_dict()
            records.append(
                {"grade": grade, "cls": 0, "F": 0, "M": 0} | grade_total | grade_gender
            )
        records = pd.DataFrame.from_records(records).fillna(0)
        records["M"] = records.M.astype("int")
        records["F"] = records.F.astype("int")
        records["grade"] = records.grade.apply(
            lambda x: f"{project.grade_simple[x]}年级"
        )
        records = records.loc[records.cls == 0, :]
        self.case_gender_counts = records.to_dict(orient="records")

    def _to_count_g_cronbach_alpha(self):
        cols = ["student_id", "item_id", "score"]
        res = []
        for grade, group in self.final_answers.groupby("grade"):
            base = group.loc[:, cols]
            data = pd.pivot_table(
                base, index="student_id", columns="item_id", values="score"
            )
            c = cronbach_alpha(data)
            res.append(c[0])
        self.cronbach_alpha = [round(i, 3) for i in res]

    def _to_count_h_grade_gender_distribution(self):
        """年级性别分布"""
        data = self.case_gender_counts
        records = {}
        for row in data:
            records[row["grade"]] = Munch(row)
        self.grade_gender_distribution = records

    def _to_count_i_grade_score(self):
        """年级最高、最低、平均分"""
        records = Munch()
        for grade in self.grade.grades:
            ans = self.final_answers.loc[self.final_answers.grade == grade, :]
            score = ans.groupby("student_id").score
            record = Munch(
                avg=self._retain_prec(score.mean().mean()),
                min=self._retain_prec(score.mean().min()),
                max=self._retain_prec(score.mean().max()),
                rank=self.count_rank_by_score(score.mean().mean() * 100),
            )
            records[grade] = record
        self.grade_score = records

    def _to_count_j_grade_rank_dis(self):
        records = {}
        str_records = {}
        for grade, group in self.final_scores.groupby("grade"):
            count = self.count_rank_dis_by_final_scores(scores=group)
            records[grade] = Munch()
            str_records[grade] = Munch()
            for gender, g in group.groupby("gender"):
                gender_count = self.count_rank_dis_by_final_scores(scores=g)
                records[grade][gender] = gender_count
                str_records[grade][gender] = self.count_str_rank(rank=gender_count)
            records[grade].total = count
            str_records[grade].total = self.count_str_rank(rank=count)

        self.grade_rank_dis = records
        self.grade_str_rank_dis = str_records

    def _to_count_k_grade_reverse_rank_dis(self):
        records = {}
        rank_dis = self.grade_rank_dis
        for g in self.grade.grades:
            try:
                here = rank_dis[g].total
            except KeyError:
                continue
            records[g] = self._count_reverse_sorted_rank(rank_data=here)
        self.grade_reverse_rank_dis = records

    def _to_count_l_grade_code_score(self):
        """健康素养水平 所需数据"""
        records = {}
        scores = self.code_scores
        for grade in self.grade.grades:
            base: pd.DataFrame = scores.loc[scores.grade == grade, :]
            base_dimensions = base.loc[base.category == "dimension", ["code", "total"]]
            base_fields = base.loc[base.category == "field", ["code", "total"]]

            dimensions = self._count_df_reverse(
                first_col="code", second_col="total", data=base_dimensions
            )
            fields = self._count_df_reverse(
                first_col="code", second_col="total", data=base_fields
            )
            a = base.loc[base.category == "field", ["F"]].mean().mean()
            b = base.loc[base.category == "field", ["M"]].mean().mean()
            a = 0 if math.isnan(a) else a
            b = 0 if math.isnan(b) else b
            records[grade] = {
                "dimension": dimensions,
                "field": fields,
                "cond": self.count_cond(a, b, target="男生"),
            }
        self.grade_code_score = records

    def _to_count_n_compare_grade_year_school(self):
        if not self.is_load_last:
            return
        res = defaultdict(dict)
        cols = ["total", "M", "F"]
        for grade in self.grade.grades:
            for col in cols:
                res[grade][col] = self._count_dim_field_diff(grade=grade, key=col)
        self.compare_grade_year_school = res

    def _to_count_o_compare_all_total(self):
        if not self.is_load_last:
            return
        data = []
        for grade in self.grade.grades:
            sch = self.grade_score[grade].avg
            last_year_grade_data = self.get_last_year_miss(grade=grade)
            year = last_year_grade_data["score"]["total"]
            data.append(sch - year)
        self.compare_all_total = self.count_cond(a=sum(data) / len(data), b=0)

    @classmethod
    def cache_year_data(cls, year: int):
        """缓存年数据"""
        key = f"{project.REDIS_PREFIX}{year}:data"

        res = defaultdict(dict)
        tool = cls(
            meta_unit_type="country",
            meta_unit_id=0,
            target_year=year,
            last_year_num=year - 1,
            is_load_last=False,
        )

        for grade, value in zip(
            tool.grade.grades, tool.grade_gender_distribution.values()
        ):
            res[grade]["people"] = value
        for grade, group in tool.code_scores.groupby("grade"):
            res[grade]["code"] = {}
            for r in group.to_dict(orient="records"):
                res[grade]["code"][r["code"]] = r
        for grade, value in tool.grade_rank_dis.items():
            res[grade]["rank"] = value
        score_dict = defaultdict(dict)
        # 计算年级、性别 平均分
        for grade, first_value in res.items():
            for second_key, second_value in first_value.items():
                if second_key == "code":
                    total_score = cls._count_year_score("total", second_value)
                    f_score = cls._count_year_score("F", second_value)
                    m_score = cls._count_year_score("M", second_value)
                    score_dict[grade] = {
                        "total": total_score,
                        "F": f_score,
                        "M": m_score,
                    }
        for grade, value in score_dict.items():
            res[grade]["score"] = value
        # 计算总人数
        res["total"] = defaultdict(dict)
        res["total"]["total"] = sum([cls._get_value(v, "total") for v in res.values()])
        res["total"]["M"] = sum([cls._get_value(v, "M") for v in res.values()])
        res["total"]["F"] = sum([cls._get_value(v, "F") for v in res.values()])
        cls.redis.conn.set(key, json.dumps(res, ensure_ascii=False))

    def _count_grade_code_score(self, code: str, grade: int, category: str):
        """计算指定年级、指定维度、领域的分数"""
        ans = self.final_answers
        local_ans = ans.loc[(ans.grade == grade) & (ans[category] == code), :]
        student_score = local_ans.groupby("student_id").score.mean().mean() * 100
        gender_score = (
            local_ans.groupby(["gender", "student_id"])
            .score.mean()
            .reset_index()
            .groupby("gender")
            .score.mean()
            * 100
        )
        res = Munch(
            total=student_score,
            grade=grade,
            code=code,
            category=category,
            **gender_score.to_dict(),
        )
        return res

    @staticmethod
    def _count_school_score(group, key: str):
        """计算学校的维度、领域性别分数"""
        dim_score = group.loc[group.category == "dimension", :][key].mean()
        field_score = group.loc[group.category == "field", :][key].mean()
        return (dim_score + field_score) / 2

    @staticmethod
    def _count_cls(row):
        if row["cls"]:
            return f"{project.grade_simple[row['grade']]}({int(row['cls'])})班"
        else:
            return f"{project.grade_simple[row['grade']]}年级"

    @staticmethod
    def _get_value(v, k):
        """计算去年数据中的总人数"""
        base: Union[dict, int] = dict(v).get("people", 0)
        if base:
            return base[k]
        else:
            return 0

    @staticmethod
    def _count_year_score(category: str, data: dict):
        """
        :param category: total/M/F
        :param data: 需计算数据
        """
        dim_score = (
            sum(
                [
                    dict(v)[category]
                    for v in list(data.values())
                    if v["category"] == "dimension"
                ]
            )
            / 4
        )
        field_score = (
            sum(
                [
                    dict(v)[category]
                    for v in list(data.values())
                    if v["category"] == "field"
                ]
            )
            / 6
        )
        score = (dim_score + field_score) / 2
        return score

    @property
    def gender_count(self) -> Munch:
        r = self.students.gender.value_counts()
        return Munch({"M": 0, "F": 0} | r.to_dict())

    # 工具函数

    def _count_df_reverse(self, first_col: str, second_col: str, data: pd.DataFrame):
        base = data.to_dict(orient="records")
        middle = {d[first_col]: d[second_col] / 100 for d in base}
        reverse_middle = {v: k for k, v in middle.items()}
        res = [
            (self._retain_prec(k), reverse_middle[k])
            for k in sorted(reverse_middle.keys(), reverse=True)
        ]
        return res

    @staticmethod
    def count_cond(a: float, b: float, target: str = ""):
        a = 0 if math.isnan(a) else a
        b = 0 if math.isnan(b) else b
        if a == b:
            condition = f"等于{target}" if target else "等于"
        elif a - b >= 5:
            condition = f"明显高于{target}" if target else "明显高于"
        elif abs(a - b) < 5:
            condition = f"与{target}的差异不明显" if target else "差异不明显于"
        elif a - b <= -5:
            condition = f"明显低于{target}" if target else "明显低于"
        else:
            raise
        return condition

    def _count_dim_field_diff(self, grade: int, key: str):
        """计算学校与全国对比的维度、领域高低
        :param key: 比较的项：total/M/F
        """
        data = self._build_one_data(grade=grade)
        key_col = f"{key}_y_s"
        data[key_col] = data[f"{key}_sch"] - data[f"{key}_year"]
        cols = ["category_sch", "code", key_col, f"{key}_year", f"{key}_sch"]
        compare = data.sort_values(["category_sch", key_col]).loc[:, cols]
        dim_compare = compare.loc[compare.category_sch == "dimension", :]
        field_compare = compare.loc[compare.category_sch == "field", :]
        dim_low, dim_high = dim_compare.head(n=1), dim_compare.tail(n=1)
        field_low, field_high = field_compare.head(n=1), field_compare.tail(n=1)
        return {
            "dim_low": dim_low.code.values[0] if dim_low[key_col].values[0] < 0 else "",
            "field_low": field_low.code.values[0]
            if field_low[key_col].values[0] < 0
            else "",
            "dim_high": dim_high.code.values[0]
            if dim_high[key_col].values[0] > 0
            else "",
            "field_high": field_high.code.values[0]
            if field_high[key_col].values[0] > 0
            else "",
        }

    def _build_one_data(self, grade: int):
        """抽象某个构建数据的逻辑"""
        year_scores = self.last_year_code_scores
        sch_scores = self.code_scores
        year_code_score = year_scores.loc[year_scores.grade == grade, :]
        school_code_score = sch_scores.loc[sch_scores.grade == grade, :]
        data = pd.merge(
            year_code_score,
            school_code_score,
            left_on="code",
            right_on="code",
            suffixes=("_year", "_sch"),
        )
        return data

    def build_code_gender_data(self, category: str, g: int):
        data = self._build_one_data(grade=g)
        use_cols = [f"{category}_year", f"{category}_sch", "code", "category_sch"]
        data = data.loc[:, use_cols].sort_values(["category_sch", "code"])
        del data["category_sch"]
        return data

    def compare_gender_text(self, grade: int):
        grade_rank_dis_m = self.grade_rank_dis[grade].M
        grade_rank_dis_f = self.grade_rank_dis[grade].F
        level_m = Util.format_num(
            sum([grade_rank_dis_m["优秀"], grade_rank_dis_m["良好"]]), project.precision
        )
        level_f = Util.format_num(
            sum([grade_rank_dis_f["优秀"], grade_rank_dis_f["良好"]]), project.precision
        )
        if abs(level_m - level_f) >= 5:
            if level_m > level_f:
                return "男生明显高于女生"
            else:
                return "男生明显低于女生"
        elif abs(level_m - level_f) >= 3:
            if level_m > level_f:
                return "男生略高于女生"
            else:
                return "男生略低于女生"
        else:
            return "男生与女生不存在明显差异"

    def low_high_code_text(self, grade: int, gender: str):
        """相对最高、相对最低文本
        :param grade: total/M/F
        :param gender: total/M/F
        """
        if not self.is_load_last:
            return
        data = self.build_code_gender_data(category=gender, g=grade)
        data["diff"] = data[f"{gender}_sch"] - data[f"{gender}_year"]
        bigger = data.loc[data["diff"] >= 5, :].code.to_list()
        smaller = data.loc[data["diff"] <= -5, :].code.to_list()
        res = ""
        if bigger:
            local_codes = self._build_codes(bigger)
            res += (
                f"{local_codes}{project.category_map[gender]}分数"
                f"高于全国{project.grade_simple[grade]}年级{project.category_map[gender]}平均分数，"
            )
        if smaller:
            local_codes = self._build_codes(smaller)
            res += (
                f"{local_codes}{project.category_map[gender]}分数"
                f"低于全国{project.grade_simple[grade]}年级{project.category_map[gender]}平均分数，"
            )
        if len(bigger) + len(smaller) == 0:
            res += "所有维度/领域都没有明显差异。"
        elif len(bigger) + len(smaller) < 10:
            res += "其余维度/领域没有明显差异。"
        else:
            pass
        return res

    @staticmethod
    def _build_codes(codes: list[str]):
        if len(codes) == 1:
            return f"“{codes[0]}”"
        elif len(codes) > 1:
            code_text = "、".join([f"“{i}”" for i in codes[:-1]]) + f"和“{codes[-1]}”"
            return f"在{code_text}维度/领域，"
        else:
            return ""

    def compare_grade_gen_text(self):
        """生成整体分析标题及一句分析文本。"""
        data = {}
        for grade in self.grade.grades:
            sch = self.grade_score[grade].avg
            last_year_grade_data = self.get_last_year_miss(grade=grade)
            year = last_year_grade_data["score"]["total"]
            data[grade] = sch - year
        total_dif = sum(data.values()) / len(data)
        diff = []
        if total_dif > 0:
            for k, v in data.items():
                if v < 0:
                    diff.append(k)
        elif total_dif < 0:
            for k, v in data.items():
                if v > 0:
                    diff.append(k)
        else:
            pass
        cond = self.compare_all_total
        if diff:
            grade_text = (
                "除" + "、".join([project.grade_simple[g] for g in diff]) + "年级外，"
            )
        else:
            grade_text = ""
        title_text = f"{grade_text}各年级生命与健康素养{cond}全国平均水平"
        describe_text = f"{grade_text}各年级的健康素养水平{cond}{self.last_year_num}年的全国平均水平"
        return title_text, describe_text

    def describe_grade_text(self, category: str):
        """描述全年级对比情况
        :param category: total/gender  total：总体比全国 / gender：男生比女生。
        """
        bigger, smaller, others = [], [], []
        match category:
            case "total":
                subs = ["学生", "全国同年级学生", "学生分数与全国同年级学生", "学生"]
            case _:
                subs = ["男生", "女生", "男女生分数", "男女生"]
        for grade in self.grade.grades:
            if category == "total":
                first = self.grade_score[grade].avg
                last_year_grade_data = self.get_last_year_miss(grade=grade)
                second = last_year_grade_data["score"]["total"]
            else:
                first = self.summary_scores[grade]["M"]
                second = self.summary_scores[grade]["F"]
            if first - second >= 5:
                bigger.append(f"{project.grade_simple[grade]}年级")
            elif first - second <= -5:
                smaller.append(f"{project.grade_simple[grade]}年级")
            else:
                others.append(f"{project.grade_simple[grade]}年级")

        match len(self.grade.grades):
            case 1:
                if bigger or smaller:
                    grade_text = bigger[0] if bigger else smaller[0]
                    compare_text = "高于" if bigger else "低于"
                    res = f"{grade_text}{subs[0]}分数明显{compare_text}{subs[1]}。"
                else:
                    res = f"{others[0]}{subs[2]}对比没有明显差异。"
            case _:  # more than 1
                grades = []
                for grade in self.grade.grades:
                    chinese_grade_text = f"{project.grade_simple[grade]}年级"
                    if chinese_grade_text in bigger or chinese_grade_text in smaller:
                        grades.append(chinese_grade_text)
                if grades:
                    grades_text = "、".join(grades)
                    if len(grades) == len(self.grade.grades):
                        res = f"各年级{subs[0]}分数明显高于/低于{subs[1]}。"
                    else:
                        res = f"{grades_text}{subs[0]}分数明显高于/低于{subs[1]}，其他年级{subs[3]}分数对比没有明显差异。"
                else:
                    res = f"各年级{subs[2]}对比均没有明显差异。"
        return res

    @property
    def grade_class_student_table(self):
        scores = self.final_scores
        records = []
        grade_key, cls_key, gender_key = "grade", "cls", "gender"
        for grade, grade_group in scores.groupby(grade_key):
            grade_base = {
                grade_key: grade,
                f"{grade_key}_count": len(grade_group),
                f"{grade_key}_{cls_key}_count": len(grade_group.groupby(cls_key)),
            }
            for cls, grade_cls_group in grade_group.groupby(cls_key):
                class_count = len(grade_cls_group)
                class_base = {
                    cls_key: cls,
                    f"{cls_key}_count": class_count,
                }
                for gender, grade_cls_gender_group in grade_cls_group.groupby(
                    gender_key
                ):
                    gender_count = len(grade_cls_gender_group)
                    class_base[f"{gender}_count"] = gender_count
                    class_base[f"{gender}_percent"] = round(
                        gender_count / class_count * 100, 1
                    )
                records.append(class_base | grade_base)
        records.sort(key=lambda x: (int(x["grade"]) * 100 + int(x["cls"])))
        return records
