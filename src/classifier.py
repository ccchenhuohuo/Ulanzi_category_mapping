"""
分类器核心模块
实现五层解耦向量化分类引擎
"""
import json
import pandas as pd
from .utils import normalize_text, extract_specs


class GlobalLightClassifier:
    """
    全球灯光类目分类器

    采用五层解耦向量化分类架构：
    1. 文本预处理层
    2. 布尔特征感知层
    3. 规格数值归一化层
    4. 向量化评分引擎
    5. 冲突裁决层
    """

    def __init__(self, signals_path, scoring_path, filters_path):
        """
        初始化：加载配置文件

        Args:
            signals_path: 信号词典JSON文件路径
            scoring_path: 评分模型JSON文件路径
            filters_path: 硬拦截规则JSON文件路径
        """
        with open(signals_path, 'r', encoding='utf-8') as f:
            self.signals = json.load(f)
        with open(scoring_path, 'r', encoding='utf-8') as f:
            self.scoring_models = json.load(f)
        with open(filters_path, 'r', encoding='utf-8') as f:
            self.hard_filters = json.load(f)

    def extract_signals(self, text, country='US'):
        """
        第二层：信号感知层
        通过关键词匹配，将清洗后的标题转换为布尔特征向量（0/1）

        Args:
            text: 清洗后的商品标题
            country: 国家代码（CN/US/JP），默认US

        Returns:
            布尔特征向量字典
        """
        bool_signals = {}

        for tag, lang_map in self.signals.items():
            # 获取对应语言的关键词（降级使用US作为通用）
            keywords = lang_map.get(country, []) + lang_map.get('US', [])

            # 检查标题中是否包含任一关键词
            # 使用部分匹配（kw in text）而非精确匹配
            has_keyword = 0
            for kw in keywords:
                if kw in text:
                    has_keyword = 1
                    break

            bool_signals[tag] = float(has_keyword)

        return bool_signals

    def calculate_scores(self, feature_vector):
        """
        第四层：向量化评分引擎
        对11个品类同时计算得分，通过点积公式快速得到每个品类的总分

        数学原理：
        Score(品类i) = BaseScore(i) + Σ(特征值 × 权重)

        Args:
            feature_vector: 完整的特征向量（布尔+数值）

        Returns:
            11个品类的得分字典
        """
        scores = {}

        for category, model in self.scoring_models.items():
            base_score = model['base_score']
            weights = model['weights']
            total_score = base_score

            for feature, weight in weights.items():
                feature_val = feature_vector.get(feature, 0.0)
                total_score += feature_val * weight

            scores[category] = round(total_score, 2)

        return scores

    def arbitrate(self, scores, feature_vector, title):
        """
        第五层：冲突裁决层
        通过硬规则解决评分引擎无法处理的边界情况，输出最终分类结果

        裁决规则优先级（从高到低）：
        1. 配件拦截 → 灯光类-其他
        2. 形态锁定 → 强制归为对应品类
        3. 最低分过滤 → 灯光类-其他
        4. 最高分归档 → 得分最高的品类

        Args:
            scores: 11个品类的得分字典
            feature_vector: 完整的特征向量
            title: 清洗后的商品标题

        Returns:
            (final_category, reason): 最终分类和裁决原因
        """
        # 1. 配件一票否决
        for acc in self.hard_filters['accessories']:
            if acc.lower() in title.lower():
                return '灯光类-其他', f'Accessory Kill: {acc}'

        # 2. 形态锁定
        form_lock = self.hard_filters.get('form_factor_lock', {})
        for tag, forced_category in form_lock.items():
            if feature_vector.get(tag, 0) == 1.0:
                return forced_category, f'Form Lock: {tag}'

        # 3. 最高分归属
        winner = max(scores, key=scores.get)
        max_score = scores[winner]

        # 4. 门限过滤
        min_threshold = self.hard_filters.get('min_score_threshold', 30)
        if max_score < min_threshold:
            return '灯光类-其他', f'Low Score: {max_score} < {min_threshold}'

        return winner, f'High Score: {winner} ({max_score})'

    def process_row(self, row):
        """
        处理单条数据

        Args:
            row: pandas DataFrame的一行数据

        Returns:
            包含分类结果的字典
        """
        # 获取标题（优先使用SKU标题，fallback到产品标题）
        title = row.get('SKU标题', row.get('产品标题', ''))
        if pd.isna(title):
            title = ''

        # 第一层：标准化
        clean_title = normalize_text(title)

        # 第二层：信号提取
        # 根据站点判断国家代码
        site = row.get('site', '').upper()
        if site == 'JP':
            country = 'JP'
        elif site == 'CN':
            country = 'CN'
        else:
            country = 'US'

        bool_signals = self.extract_signals(clean_title, country)

        # 第三层：规格提取
        spec_signals = extract_specs(clean_title)

        # 合并特征向量
        feature_vector = {**bool_signals, **spec_signals}

        # 第四层：计算得分
        scores = self.calculate_scores(feature_vector)

        # 第五层：裁决
        category, audit = self.arbitrate(scores, feature_vector, clean_title)

        return {
            'clean_title': clean_title,
            'predicted_category': category,
            'decision_reason': audit,
            'scores_all': scores,
            'features_bool': bool_signals,
            'features_num': spec_signals
        }

    def process(self, df, progress_callback=None):
        """
        批量处理

        Args:
            df: pandas DataFrame
            progress_callback: 进度回调函数

        Returns:
            合并结果后的DataFrame
        """
        results = []

        for idx, row in df.iterrows():
            result = self.process_row(row.to_dict())
            results.append(result)

            # 进度显示
            if progress_callback and (idx + 1) % 100 == 0:
                progress_callback(idx + 1, len(df))

        # 合并结果
        df_result = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), df_result], axis=1)
