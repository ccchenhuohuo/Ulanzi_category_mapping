"""
规则概览页面
展示11个品类的分类规则
"""
import streamlit as st
import pandas as pd
from utils.rules_loader import RulesLoader
from frontend.components.charts import render_weights_bar_chart

# 标签名称中英文映射
TAG_NAMES_CN = {
    'tag_is_flash': '闪光灯',
    'tag_is_cob': 'COB灯',
    'tag_is_panel': '平板灯',
    'tag_is_ring': '环形灯',
    'tag_is_tube': '棒灯',
    'tag_is_pocket': '口袋灯',
    'tag_is_video_light': '视频灯',
    'tag_is_inflatable': '充气灯',
    'tag_is_phone_light': '手机补光灯',
    'tag_is_action_cam_light': '运动相机灯',
    'tag_is_torch': '手电筒',
    'tag_has_bowens': '保荣口',
    'tag_has_magnetic': '磁吸',
    'tag_has_ttl': 'TTL',
    'tag_has_hss': 'HSS高速同步',
    'tag_has_rgb': 'RGB彩色',
    'tag_has_battery': '内置电池',
    'tag_is_small': '小型便携',
}


def get_tag_name_cn(tag: str) -> str:
    """获取标签的中文名称"""
    return TAG_NAMES_CN.get(tag, tag.replace('tag_', '').replace('_', ' ').title())


def show():
    """显示规则概览页面"""
    # 加载规则
    loader = RulesLoader()
    categories = loader.get_all_categories()
    summary = loader.get_rules_summary()

    # 概览统计
    st.markdown("### 系统统计")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("品类数量", summary['categories_count'])
    with col2:
        st.metric("信号标签数", summary['signals_count'])
    with col3:
        st.metric("配件拦截词", summary['accessories_count'])
    with col4:
        st.metric("最低分阈值", summary['min_score_threshold'])

    st.markdown("---")

    # 搜索框
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("搜索品类", placeholder="输入品类名称...")
    with search_col2:
        show_details = st.checkbox("显示详情", value=True)

    # 筛选品类
    filtered_categories = [c for c in categories if search_term.lower() in c.lower()] if search_term else categories

    st.markdown(f"**{len(filtered_categories)} 个品类**")

    for category in filtered_categories:
        render_category_card(loader, category, show_details)


def render_category_card(loader: RulesLoader, category: str, show_details: bool):
    """渲染品类卡片"""
    info = loader.get_category_info(category)

    base_score = info.get('base_score', 0)
    positive_weights = info.get('positive_weights', {})
    negative_weights = info.get('negative_weights', {})
    keywords = info.get('keywords', {})
    hard_rules = info.get('hard_rules', {})

    # 按权重值排序（从大到小）
    sorted_positive = sorted(positive_weights.items(), key=lambda x: x[1], reverse=True)
    sorted_negative = sorted(negative_weights.items(), key=lambda x: x[1])

    # 卡片容器
    with st.expander(f"【{category}】 基础分: {base_score} 分", expanded=show_details):
        col1, col2 = st.columns(2)

        # 正向权重（全部展示）
        with col1:
            st.markdown("**正向权重（加分项）**")
            if sorted_positive:
                for tag, weight in sorted_positive:
                    tag_cn = get_tag_name_cn(tag)
                    st.markdown(f"<span style='color: #2E7D32;'>[{tag_cn}] {tag}</span> <b>+{weight}</b>", unsafe_allow_html=True)
            else:
                st.info("无正向权重配置")

        # 负向权重（全部展示）
        with col2:
            st.markdown("**负向权重（扣分项）**")
            if sorted_negative:
                for tag, weight in sorted_negative:
                    tag_cn = get_tag_name_cn(tag)
                    st.markdown(f"<span style='color: #C62828;'>[{tag_cn}] {tag}</span> <b>{weight}</b>", unsafe_allow_html=True)
            else:
                st.info("无负向权重配置")

        # 关键词展示
        if show_details and keywords:
            st.markdown("---")
            st.markdown("**相关关键词**")
            keyword_cols = st.columns(3)

            lang_names = {'CN': '中文', 'US': '英文', 'JP': '日文'}
            lang_keys = ['CN', 'US', 'JP']

            for idx, lang in enumerate(lang_keys):
                with keyword_cols[idx]:
                    st.markdown(f"**{lang_names[lang]}**")
                    lang_keywords = []
                    for tag, lang_map in keywords.items():
                        kw_list = lang_map.get(lang, [])
                        lang_keywords.extend(kw_list)
                    unique_kw = list(set(lang_keywords))
                    if unique_kw:
                        # 使用标签样式展示
                        tags_html = " ".join([f":blue[`{kw}`]" for kw in unique_kw])
                        st.markdown(tags_html)
                    else:
                        st.markdown("-")

        # 形态锁定规则
        if hard_rules:
            st.markdown("---")
            st.markdown("**形态锁定规则**")
            for rule_type, rule_value in hard_rules.items():
                rule_cn = get_tag_name_cn(rule_type)
                st.warning(f"[{rule_cn}] {rule_type} → {rule_value}")

        # 权重分布图表
        if show_details:
            st.markdown("---")
            st.markdown("**权重分布可视化**")
            fig = render_weights_bar_chart(info)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
