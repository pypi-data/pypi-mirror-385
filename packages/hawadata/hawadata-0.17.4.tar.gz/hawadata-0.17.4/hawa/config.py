import platform

from pydantic import BaseSettings


def is_debug():
    system = platform.system()
    dev_system = ('Windows', 'Darwin')
    return True if system in dev_system else False


class Settings(BaseSettings):
    # mode
    DEBUG = is_debug()
    COMPLETED = False  # 配置是否加载完成

    PROJECT = 'HawaData'
    client_id = 6

    # db
    DB_MODE = 'mysql'
    DB_HOST = '' if not DEBUG else 'localhost'
    DB_PORT = 3306
    DB_NAME = '' if not DEBUG else 'yass'
    DB_USER = '' if not DEBUG else 'test'
    DB_PSWD = '' if not DEBUG else 'test'

    # redis
    REDIS_HOST = '' if not DEBUG else 'localhost'
    REDIS_DB = 5
    REDIS_PREFIX = 'report:'

    # time
    utc = 'UTC'
    timezone = 'Asia/Shanghai'
    format = 'YYYY-MM-DD HH:mm:ss'

    # case
    time_distribution_minutes = 30
    min_join_number = 10
    min_alone_numger = 5

    gender_map = {
        'total': '总体', 'M': '男生', "F": "女生"
    }

    total_gender_map = {
        'total': '全部', 'M': '男生', "F": "女生"
    }

    # rank
    ranks = {
        'RANK_LABEL': {'A': '优秀', 'B': '良好', 'C': '达标', 'D': '待达标'},
        'FEEDBACK_LEVEL': {'A': '优秀', 'B': '良好', 'C': '中等', 'D': '待提高'}
    }
    reverse_ranks = {
        'RANK_LABEL': {k: v for v, k in ranks['RANK_LABEL'].items()},
        'FEEDBACK_LEVEL': {k: v for v, k in ranks['FEEDBACK_LEVEL'].items()},
    }

    # grades
    grade_map = {
        1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '初中一',
        8: '初中二', 9: '初中三', 10: '高中一', 11: '高中二',
        12: '高中三'
    }

    grade_simple = {**dict(zip(range(1, 11), '一二三四五六七八九十')), **{11: '十一', 12: '十二'}}

    # number
    number_map = dict(zip(range(1, 11), '一二三四五六七八九十'))
    precision = 1

    category_map = {
        'total': "学生", 'M': '男生', "F": "女生"
    }

    # other
    municipality = {11, 12, 31, 50}
    municipality_ids = {110000, 120000, 310000, 500000}

    class Config:
        env_prefix = 'No_Env_'  # 不使用环境变量

    @property
    def grade_mapping(self):
        mappings = dict(zip(range(0, 13), '无 一 二 三 四 五 六 七 八 九 十 十一 十二'.split(' ')))
        return mappings


project = Settings()
