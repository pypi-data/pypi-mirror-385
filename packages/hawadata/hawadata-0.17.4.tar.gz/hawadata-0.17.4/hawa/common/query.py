from dataclasses import dataclass

import pandas as pd
from sqlalchemy import text

from hawa.base.db import DbUtil
from hawa.base.decos import singleton


@dataclass
class MetaUnit:
    id: int
    name: str
    short_name: str
    client_id: int = 0


@singleton
class DataQuery:
    db = DbUtil()

    def raw_query(self, sql: str):
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_unit(self, meta_unit_type: str, meta_unit_id: str):
        match meta_unit_type:
            case 'student':
                sql = f"select id,nickname,client_id from users where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(id=data['id'], name=data['nickname'], short_name=data['nickname'],
                                     client_id=data['client_id'])
            case 'school' | 'class':
                sql = f"select id,name,short_name from schools where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(**data)
            case 'group':
                sql = f"select id,name,short_name from `groups` where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(**data)
            case 'district' | 'city' | 'province':
                sql = f"select id,name from locations where id={meta_unit_id};"
                data = self.db.query_by_sql(sql=sql, mode='one')
                meta_unit = MetaUnit(**data, short_name=data['name'])
            case _:
                meta_unit = MetaUnit(id=0, name='全国', short_name='全国')
        return meta_unit

    def query_schools_all(self):
        sql = f"select id, name, short_name, created from schools;"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_schools_by_ids(self, school_ids: list[int]):
        if len(school_ids) == 0:
            return []
        elif len(school_ids) == 1:
            sql = f"select id, name, short_name, created from schools where id={school_ids[0]};"
        else:
            sql = f"select id, name, short_name, created from schools where id in {tuple(school_ids)};"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_schools_by_startwith(self, startwith: int):
        param_len = len(str(startwith))
        sql = f"select id, name, short_name, created from schools where left(id,{param_len})={startwith};"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_schools_by_group_id(self, group_id: int):
        sql = (f"select id, name, short_name from schools where id in "
               f"(select school_id from group_schools where group_id = {group_id});")
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_papers(self, test_type: str = '', test_types: list[str] = None):
        """优先 test_types"""
        if test_types:
            sql = f"select id, name, grade, test_type, created from papers where test_type in {tuple(test_types)};"
        elif test_type:
            sql = f"select id, name, grade, test_type, created from papers where test_type='{test_type}';"
        else:
            raise
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_cases(
            self, school_ids: list[int], paper_ids: list[int],
            valid_to_start: str, valid_to_end: str, is_cleared: bool = True
    ):
        """

        :param school_ids:
        :param paper_ids:
        :param valid_to_start:
        :param valid_to_end:
        :param is_cleared: True 仅查询已清洗的测评，other 查询所有
        :return:
        """
        if len(paper_ids) == 0:
            return pd.DataFrame()
        elif len(paper_ids) == 1:
            paper_sql = f"and c.paper_id={paper_ids[0]}"
        else:
            paper_sql = f"and c.paper_id in {tuple(paper_ids)}"

        match is_cleared:
            case True:
                is_cleared_sql = f"c.is_cleared={is_cleared} and "
            case _:
                is_cleared_sql = ''

        if len(school_ids) == 0:
            return pd.DataFrame()
        elif len(school_ids) == 1:
            school_sql = f"and cs.school_id={school_ids[0]}"
        else:
            school_sql = f"and cs.school_id in {tuple(school_ids)}"

        sql = f"select c.id,c.name,c.valid_from,c.valid_to,c.client_id,c.created," \
              f"c.paper_id,c.is_cleared, cs.school_id " \
              f"from cases c " \
              f"inner join case_schools cs on c.id=cs.case_id " \
              f"where {is_cleared_sql} valid_to between '{valid_to_start}' and '{valid_to_end}'" \
              f" {school_sql} {paper_sql};"
        with self.db.engine_conn() as conn:
            cases = pd.read_sql(text(sql), conn).drop_duplicates(subset=['id'])
        return cases

    def query_answers(self, case_ids: list[int], student_id: int = None):
        answer_cols = "id, student_id, item_id, case_id, answer, score, created, valid"
        if len(case_ids) == 0:
            return []
        elif len(case_ids) == 1:
            sql = f"select {answer_cols} from answers where case_id={case_ids[0]} and valid=1"
        else:
            sql = f"select {answer_cols} from answers where case_id in {tuple(case_ids)} and valid=1"
        if student_id:
            sql += f" and student_id={student_id};"
        with self.db.engine_conn() as conn:
            answers = pd.read_sql(text(sql), conn).drop_duplicates(
                subset=['case_id', 'student_id', 'item_id'])
        return answers

    def query_students(self, student_ids: list[int], mode: str = 'default'):
        user_cols = "id, username, first_name, last_name, nickname, gender, role, source, created, " \
                    "unit_id, client_id, extra"
        student_ids.append(0)
        match mode:
            case 'default':
                sql = f"select {user_cols} from users where id in {tuple(student_ids)} and length(id)>=18"
            case 'xx':
                sql = f"select {user_cols} from users where id in {tuple(student_ids)} and client_id=10"
            case _:
                raise ValueError(f"mode {mode} not support")

        with self.db.engine_conn() as conn:
            students = pd.read_sql(text(sql), conn).drop_duplicates(subset=['id'])
        return students

    def query_items(self, item_ids: set[int], is_hawa: bool = False):
        item_cols = "id, item_text, choices, item_key, item_type, grade, test_type, pattern, " \
                    "`source`, created"
        sql = f"select {item_cols} from items where id in {tuple(item_ids)};"
        if is_hawa:
            sql = sql.replace(';', " and test_type=1;")
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_paper_items(self, paper_ids: list[int]):
        if len(paper_ids) == 0:
            return []
        elif len(paper_ids) == 1:
            sql = f"select * from paper_items where paper_id={paper_ids[0]};"
        else:
            sql = f"select * from paper_items where paper_id in {tuple(paper_ids)};"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_phq_items(self):
        sql = f"select * from items where source='2021浙江心理';"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_mgarbage_items(self):
        sql = f"select * from items where source='mgarbage';"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_item_codes(self, item_ids: set[int], categories: list[str] = None):
        item_code_sql = f'select ic.item_id,ic.code,ic.category,c.name ' \
                        f'from item_codes ic left join codebook c on ic.code = c.code ' \
                        f'where ic.item_id in {tuple(item_ids)}'
        if categories:
            item_code_sql += f' and ic.category in {tuple(categories)};'
        with self.db.engine_conn() as conn:
            item_codes = pd.read_sql(text(item_code_sql), conn)
        return item_codes

    def query_locations(self, location_ids: list[int]):
        location_sql = f'select id, name, level from locations where id in {tuple(location_ids)};'
        with self.db.engine_conn() as conn:
            locations = pd.read_sql(text(location_sql), conn)
        return locations

    def query_codebook(self):
        sql = f"select code,category,name,`order` from codebook;"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)

    def query_code_guides(self):
        sql = f"select code,category,name,`period` from code_guide;"
        with self.db.engine_conn() as conn:
            return pd.read_sql(text(sql), conn)
