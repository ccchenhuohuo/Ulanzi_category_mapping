"""
分类测试页面
在线测试商品标题分类效果
"""
import streamlit as st
from utils.classifier import ClassificationService
import pandas as pd
from frontend.components.charts import render_score_ranking_chart, render_score_comparison_chart


def show():
    """显示分类测试页面"""
    st.markdown("## 分类测试工具")

    # 初始化分类服务
    if 'classifier_service' not in st.session_state:
        st.session_state.classifier_service = ClassificationService()

    service = st.session_state.classifier_service

    # 输入区域
    st.markdown("### 输入商品信息")
    col1, col2 = st.columns([3, 1])

    with col1:
        title_input = st.text_area(
            "商品标题",
            placeholder="输入商品标题，例如: Godox AD300Pro 300W TTL HSS ストロボ",
            height=100
        )
    with col2:
        site = st.selectbox("站点", ["JP", "US", "CN"], index=0)

    # 示例按钮
    st.markdown("**示例标题：**")
    example_titles = [
        "Godox AD300Pro 300W TTL HSS ストロボ",
        "amaran Pano 120c 120W RGBWW パネルライト",
        "Aputure MT Pro 60cm RGBWW チューブライト",
        "NiceVeedi Ring Light 10inch",
        "Ulanzi VL49 Mini Video Light",
        "Inflatable Balloon Light 60cm RGB"
    ]

    example_cols = st.columns(3)
    for idx, title in enumerate(example_titles):
        with example_cols[idx % 3]:
            if st.button(f"测试 {title[:20]}...", key=f"example_{idx}"):
                st.session_state.test_title = title
                st.session_state.test_site = "JP"

    # 显示选中的示例
    if 'test_title' in st.session_state:
        title_input = st.session_state.test_title
        if 'test_site' in st.session_state:
            site = st.session_state.test_site

    # 分析按钮
    if st.button("开始分析", type="primary"):
        if title_input.strip():
            result = service.classify(title_input, site)
            st.session_state.classification_result = result

    # 显示结果
    if 'classification_result' in st.session_state:
        result = st.session_state.classification_result
        display_result(result, service)


def display_result(result: dict, service: ClassificationService):
    """显示分类结果"""
    st.markdown("---")
    st.markdown("### 分类结果")

    # 清洗后的标题
    st.markdown("**清洗后的标题：**")
    st.code(result['clean_title'], language='text')

    # 特征匹配
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 匹配的布尔特征")
        features_bool = result.get('features_bool', {})
        enabled_features = [(k, v) for k, v in features_bool.items() if v == 1.0]

        if enabled_features:
            for tag, val in enabled_features:
                st.markdown(f"- **{tag}**: {int(val)}")
        else:
            st.info("无匹配的布尔特征")

    with col2:
        st.markdown("#### 数值规格")
        features_num = result.get('features_num', {})
        if features_num:
            for tag, val in features_num.items():
                if val > 0:
                    st.markdown(f"- **{tag}**: {val:.2f}")
        else:
            st.info("未提取到数值规格")

    # 得分排行
    st.markdown("---")
    st.markdown("#### 品类得分排行")

    score_ranking = result.get('score_ranking', [])

    # 使用图表展示
    fig = render_score_ranking_chart(score_ranking)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        # 降级到表格
        df_scores = pd.DataFrame(score_ranking)
        if not df_scores.empty:
            df_scores['score'] = df_scores['score'].apply(lambda x: f"{x:.1f}")
            st.table(df_scores.rename(columns={
                'rank': '排名',
                'category': '品类',
                'score': '得分'
            }))

    # 最终分类结果
    st.markdown("---")
    predicted = result.get('predicted_category', '未知')
    reason = result.get('decision_reason', '')
    max_score = result['scores_all'].get(predicted, 0)

    if max_score >= 200:
        color, icon = "green", "✓"
    elif max_score >= 100:
        color, icon = "orange", "⚠"
    else:
        color, icon = "gray", "?"

    st.markdown(f"""
    <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center;">
        <h2 style="color: {color}; margin: 0;">{icon} 预测分类: {predicted}</h2>
        <p style="color: #666;">裁决原因: {reason}</p>
    </div>
    """, unsafe_allow_html=True)

    # 得分明细
    with st.expander("得分明细"):
        # 得分对比图表
        score_comparison_fig = render_score_comparison_chart(result['scores_all'], result.get('predicted_category', ''))
        if score_comparison_fig:
            st.plotly_chart(score_comparison_fig, use_container_width=True)

        category = st.selectbox("选择品类查看得分明细", list(result['scores_all'].keys()))
        details = service.get_score_details(
            category,
            result['scores_all'],
            result['features_bool'],
            result['features_num']
        )

        st.markdown(f"**{category}** 得分明细")
        st.markdown(f"- 基础分: {details['base_score']}")
        st.markdown(f"- 总分: {details['total']}")

        if details['breakdown']:
            st.markdown("**权重贡献：**")
            for item in details['breakdown']:
                sign = "+" if item['contribution'] >= 0 else ""
                st.markdown(f"- {item['feature']}: 值={item['value']} × 权重={item['weight']} = {sign}{item['contribution']}")
