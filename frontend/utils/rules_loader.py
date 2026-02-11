"""
规则加载器
负责读取和解析JSON配置文件
"""
import json
import os
from typing import Dict, List, Any


class RulesLoader:
    """规则加载器，用于读取和解析分类规则配置"""

    def __init__(self, config_dir: str = None):
        """
        初始化规则加载器

        Args:
            config_dir: 配置文件目录，默认为项目根目录下的config文件夹
        """
        if config_dir is None:
            # 默认指向项目根目录的config文件夹
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_dir = os.path.join(current_dir, 'config')

        self.config_dir = config_dir
        self.signals_path = os.path.join(config_dir, 'signals.json')
        self.scoring_path = os.path.join(config_dir, 'scoring_models.json')
        self.filters_path = os.path.join(config_dir, 'hard_filters.json')

        # 加载配置
        self.signals = self._load_json(self.signals_path)
        self.scoring_models = self._load_json(self.scoring_path)
        self.hard_filters = self._load_json(self.filters_path)

    def _load_json(self, path: str) -> Dict:
        """加载JSON文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_categories(self) -> List[str]:
        """获取所有品类名称"""
        return list(self.scoring_models.keys())

    def get_category_info(self, category: str) -> Dict[str, Any]:
        """
        获取品类详细信息

        Returns:
            包含品类基础分、权重、关键词、硬规则的字典
        """
        if category not in self.scoring_models:
            return {}

        model = self.scoring_models[category]
        weights = model.get('weights', {})

        # 分离正负权重
        positive_weights = {k: v for k, v in weights.items() if v > 0}
        negative_weights = {k: v for k, v in weights.items() if v < 0}

        # 获取关键词信息
        keywords = self._get_category_keywords(category)

        # 获取硬拦截规则
        hard_rules = self._get_hard_rules(category)

        return {
            'name': category,
            'base_score': model.get('base_score', 0),
            'positive_weights': dict(sorted(positive_weights.items(), key=lambda x: x[1], reverse=True)),
            'negative_weights': dict(sorted(negative_weights.items(), key=lambda x: x[1])),
            'keywords': keywords,
            'hard_rules': hard_rules
        }

    def _get_category_keywords(self, category: str) -> Dict[str, Dict[str, List[str]]]:
        """获取品类相关的关键词"""
        relevant_keywords = {}

        # 遍历所有信号标签
        for tag, lang_map in self.signals.items():
            # 检查该标签是否在品类的权重中
            if tag in self.scoring_models.get(category, {}).get('weights', {}):
                relevant_keywords[tag] = lang_map

        return relevant_keywords

    def _get_hard_rules(self, category: str) -> Dict[str, Any]:
        """获取品类的硬规则"""
        rules = {}

        # 检查形态锁定
        form_lock = self.hard_filters.get('form_factor_lock', {})
        if category in form_lock.values():
            for tag, cat in form_lock.items():
                if cat == category:
                    rules['form_lock'] = tag
                    break

        return rules

    def get_signal_keywords(self, signal_tag: str) -> Dict[str, List[str]]:
        """获取特定信号标签的关键词"""
        return self.signals.get(signal_tag, {})

    def get_all_signals(self) -> List[str]:
        """获取所有信号标签"""
        return list(self.signals.keys())

    def get_accessories(self) -> List[str]:
        """获取配件拦截列表"""
        return self.hard_filters.get('accessories', [])

    def get_min_score_threshold(self) -> int:
        """获取最低分阈值"""
        return self.hard_filters.get('min_score_threshold', 30)

    def get_rules_summary(self) -> Dict[str, Any]:
        """获取规则概览"""
        return {
            'categories_count': len(self.scoring_models),
            'signals_count': len(self.signals),
            'accessories_count': len(self.get_accessories()),
            'min_score_threshold': self.get_min_score_threshold()
        }
