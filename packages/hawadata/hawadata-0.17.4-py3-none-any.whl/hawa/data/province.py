from dataclasses import dataclass

from hawa.paper.health import HealthApiData


@dataclass
class ProvinceMixin:
    """为了在 __mro__ 中有更高的优先级， mixin 在继承时，应该放在最前"""
    meta_unit_type: str = 'province'


@dataclass
class ProvinceHealthApiDataLess(ProvinceMixin, HealthApiData):
    """加载更少数据的 province，用于计算 cascade"""

    def __post_init__(self):
        # 初始化数据
        init_functions = [i for i in dir(self) if i.startswith('_to_init_')]
        for func in init_functions:
            if '_to_init_e_' in func:
                break
            getattr(self, func)()

        # 构建辅助工具
        self._to_build_helper()
