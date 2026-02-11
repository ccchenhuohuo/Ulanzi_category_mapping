"""
分类服务
封装核心分类器，提供在线分类功能
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.classifier import GlobalLightClassifier
from src.utils import normalize_text, extract_specs


class ClassificationService:
    """分类服务，封装核心分类器"""

    def __init__(self, config_dir: str = None):
        """
        初始化分类服务

        Args:
            config_dir: 配置文件目录
        """
        if config_dir is None:
            config_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        signals_path = os.path.join(config_dir, 'config', 'signals.json')
        scoring_path = os.path.join(config_dir, 'config', 'scoring_models.json')
        filters_path = os.path.join(config_dir, 'config', 'hard_filters.json')

        self.classifier = GlobalLightClassifier(signals_path, scoring_path, filters_path)

    def classify(self, title: str, site: str = 'JP') -> Dict:
        """
        对单个商品标题进行分类

        Args:
            title: 商品标题
            site: 站点代码 (JP/US/CN)

        Returns:
            分类结果字典
        """
        # 构建模拟行数据
        row = {
            'SKU标题': title,
            'site': site
        }

        # 使用分类器处理
        result = self.classifier.process_row(row)

        # 添加原始标题
        result['original_title'] = title

        # 格式化得分排名
        scores = result['scores_all']
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result['score_ranking'] = [
            {'rank': i + 1, 'category': cat, 'score': score}
            for i, (cat, score) in enumerate(sorted_scores)
        ]

        return result

    def get_features_summary(self, features_bool: Dict, features_num: Dict) -> List[Dict]:
        """
        获取特征摘要

        Args:
            features_bool: 布尔特征字典
            features_num: 数值特征字典

        Returns:
            特征摘要列表
        """
        summary = []

        # 添加启用的布尔特征
        for tag, val in features_bool.items():
            if val == 1.0:
                summary.append({
                    'name': tag,
                    'value': 1,
                    'type': 'bool',
                    'enabled': True
                })

        # 添加数值特征
        for tag, val in features_num.items():
            if val > 0:
                summary.append({
                    'name': tag,
                    'value': val,
                    'type': 'numeric',
                    'enabled': True
                })

        return summary

    def get_score_details(self, category: str, scores_all: Dict, features_bool: Dict,
                          features_num: Dict) -> Dict[str, float]:
        """
        获取特定品类的得分明细

        Args:
            category: 品类名称
            scores_all: 所有品类得分
            features_bool: 布尔特征
            features_num: 数值特征

        Returns:
            得分明细字典
        """
        model = self.classifier.scoring_models.get(category, {})
        weights = model.get('weights', {})
        base_score = model.get('base_score', 0)

        details = {'base_score': base_score, 'breakdown': []}

        feature_vector = {**features_bool, **features_num}

        for feature, weight in weights.items():
            if weight != 0:
                val = feature_vector.get(feature, 0)
                contribution = val * weight
                if contribution != 0:
                    details['breakdown'].append({
                        'feature': feature,
                        'value': val,
                        'weight': weight,
                        'contribution': round(contribution, 2)
                    })

        details['total'] = scores_all.get(category, 0)
        return details
