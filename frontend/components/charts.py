"""
可视化图表组件
提供 Plotly 图表渲染功能
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import pandas as pd


def render_weights_bar_chart(category_info: dict) -> Optional[go.Figure]:
    """
    渲染品类权重横向柱状图

    Args:
        category_info: 品类信息字典，包含 base_score, positive_weights, negative_weights

    Returns:
        Plotly Figure 对象，失败返回 None
    """
    try:
        positive_weights = category_info.get('positive_weights', {})
        negative_weights = category_info.get('negative_weights', {})

        if not positive_weights and not negative_weights:
            return None

        # 准备数据
        features = []
        weights = []
        colors = []

        for tag, weight in positive_weights.items():
            features.append(tag)
            weights.append(abs(weight))
            colors.append('#2E7D32')  # 绿色表示正向

        for tag, weight in negative_weights.items():
            features.append(tag)
            weights.append(abs(weight))
            colors.append('#C62828')  # 红色表示负向

        if not features:
            return None

        # 创建横向柱状图
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=features,
            x=weights,
            orientation='h',
            marker_color=colors,
            text=[f"+{w}" if c == '#2E7D32' else str(w) for w, c in zip(weights, colors)],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>权重: %{x}<extra></extra>'
        ))

        base_score = category_info.get('base_score', 0)

        fig.update_layout(
            title={
                'text': f"品类权重分布 (基础分: {base_score})",
                'x': 0.5,
                'font': {'size': 16}
            },
            xaxis_title="权重值",
            yaxis_title="特征标签",
            height=max(300, len(features) * 40),
            margin=dict(l=150, r=50, t=60, b=50),
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='#f0f0f0',
                zeroline=True,
                zerolinecolor='#ccc'
            ),
            yaxis=dict(
                showgrid=False
            )
        )

        return fig

    except Exception:
        return None


def render_score_ranking_chart(score_ranking: List[Dict]) -> Optional[go.Figure]:
    """
    渲染得分排行榜柱状图

    Args:
        score_ranking: 得分排行列表，每个元素包含 rank, category, score

    Returns:
        Plotly Figure 对象，失败返回 None
    """
    try:
        if not score_ranking:
            return None

        # 转换为 DataFrame 便于处理
        df = pd.DataFrame(score_ranking)

        if df.empty:
            return None

        # 按得分排序
        df = df.sort_values('score', ascending=True)

        # 根据得分设置颜色
        def get_color(score):
            if score >= 200:
                return '#4CAF50'  # 绿色 - 高分
            elif score >= 100:
                return '#FF9800'  # 橙色 - 中分
            else:
                return '#9E9E9E'  # 灰色 - 低分

        colors = [get_color(s) for s in df['score']]

        # 创建横向柱状图
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df['category'],
            x=df['score'],
            orientation='h',
            marker_color=colors,
            text=[f"{s:.1f}" for s in df['score']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>得分: %{x}<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': "品类得分排行",
                'x': 0.5,
                'font': {'size': 16}
            },
            xaxis_title="得分",
            yaxis_title="品类",
            height=max(300, len(df) * 40),
            margin=dict(l=120, r=50, t=60, b=50),
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='#f0f0f0',
                zeroline=True,
                zerolinecolor='#ccc'
            ),
            yaxis=dict(
                showgrid=False
            )
        )

        return fig

    except Exception:
        return None


def render_categories_distribution(stats: Dict) -> Optional[go.Figure]:
    """
    渲染分类分布饼图

    Args:
        stats: 统计字典，包含 total 和 by_category

    Returns:
        Plotly Figure 对象，失败返回 None
    """
    try:
        by_category = stats.get('by_category', {})

        if not by_category:
            return None

        # 准备数据
        labels = list(by_category.keys())
        values = list(by_category.values())

        # 创建饼图
        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>',
            marker=dict(
                colors=px.colors.qualitative.Set3[:len(labels)]
            )
        ))

        fig.update_layout(
            title={
                'text': f"分类分布 (总数: {sum(values)})",
                'x': 0.5,
                'font': {'size': 16}
            },
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )

        return fig

    except Exception:
        return None


def render_score_comparison_chart(scores_all: Dict, predicted: str) -> Optional[go.Figure]:
    """
    渲染得分对比柱状图

    Args:
        scores_all: 所有品类得分字典
        predicted: 预测的品类

    Returns:
        Plotly Figure 对象，失败返回 None
    """
    try:
        if not scores_all:
            return None

        # 准备数据
        categories = list(scores_all.keys())
        scores = list(scores_all.values())

        # 按得分排序
        sorted_data = sorted(zip(categories, scores), key=lambda x: x[1], reverse=True)
        categories = [d[0] for d in sorted_data]
        scores = [d[1] for d in sorted_data]

        # 根据是否预测品类设置颜色
        colors = ['#4CAF50' if c == predicted else '#2196F3' for c in categories]

        # 创建柱状图
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=categories,
            y=scores,
            marker_color=colors,
            text=[f"{s:.0f}" for s in scores],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>得分: %{y:.1f}<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': "各品类得分对比",
                'x': 0.5,
                'font': {'size': 16}
            },
            xaxis_title="品类",
            yaxis_title="得分",
            height=350,
            margin=dict(l=50, r=50, t=60, b=100),
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                tickangle=45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f0f0f0',
                zeroline=True,
                zerolinecolor='#ccc'
            )
        )

        return fig

    except Exception:
        return None
