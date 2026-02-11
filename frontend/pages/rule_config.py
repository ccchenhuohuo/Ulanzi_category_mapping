"""
规则配置编辑器
可视化编辑分类规则配置
"""
import streamlit as st
import json
import os
from datetime import datetime


# 会话状态用于追踪变更
if 'config_changes' not in st.session_state:
    st.session_state.config_changes = []
if 'last_saved' not in st.session_state:
    st.session_state.last_saved = None


def render_tags_editor(label: str, current_values: list, key: str) -> list:
    """
    使用 Streamlit 组件模拟 tags 编辑器

    Args:
        label: 显示标签
        current_values: 当前标签列表
        key: 组件唯一键
        new_values: 已更新的标签列表（引用传递）

    Returns:
        更新后的标签列表
    """
    # 初始化会话状态
    if f'{key}_values' not in st.session_state:
        st.session_state[f'{key}_values'] = current_values.copy()

    values = st.session_state[f'{key}_values']

    # 显示当前标签
    if values:
        st.markdown(f"**{label}**")
        tags_html = " ".join([f":blue[{kw}]" for kw in values])
        st.markdown(tags_html)

    # 添加新标签
    col1, col2 = st.columns([4, 1])
    with col1:
        new_kw = st.text_input("添加新标签", key=f"{key}_input", placeholder="输入标签后按回车添加")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # 占位对齐
        if st.button("添加", key=f"{key}_add_btn"):
            if new_kw and new_kw.strip() and new_kw.strip() not in values:
                values.append(new_kw.strip())
                st.session_state[f'{key}_values'] = values
                st.rerun()

    # 删除标签
    if values:
        st.markdown("**删除标签:**")
        delete_cols = st.columns(5)
        for idx, kw in enumerate(values):
            with delete_cols[idx % 5]:
                if st.button(f"✕ {kw[:8]}", key=f"{key}_del_{idx}"):
                    values.pop(idx)
                    st.session_state[f'{key}_values'] = values
                    st.rerun()

    return values


def track_change(config_type: str, field: str, old_value: str, new_value: str):
    """追踪配置变更"""
    change = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': config_type,
        'field': field,
        'old': str(old_value)[:100],
        'new': str(new_value)[:100]
    }
    st.session_state.config_changes.append(change)
    # 只保留最近的50条变更记录
    if len(st.session_state.config_changes) > 50:
        st.session_state.config_changes = st.session_state.config_changes[-50:]


def show_change_history():
    """显示变更历史"""
    if not st.session_state.config_changes:
        st.info("暂无配置变更记录")
        return

    changes = list(reversed(st.session_state.config_changes[-20:]))  # 显示最近20条

    for change in changes:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 4px; margin: 5px 0;">
            <small style="color: #666;">{change['time']}</small><br>
            <strong>{change['type']}.{change['field']}</strong><br>
            <span style="color: #C62828;">{change['old']}</span> →
            <span style="color: #2E7D32;">{change['new']}</span>
        </div>
        """, unsafe_allow_html=True)

    # 清空历史按钮
    if st.button("清空变更历史"):
        st.session_state.config_changes = []
        st.rerun()


def show():
    """显示规则配置页面"""
    st.markdown("## 规则配置编辑器")

    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_dir = os.path.join(project_root, 'config')

    # 侧边栏：变更历史
    with st.sidebar:
        st.markdown("### 📜 变更历史")
        if st.session_state.get('last_saved'):
            st.caption(f"最后保存: {st.session_state.last_saved}")

        if st.button("显示变更历史"):
            st.session_state.show_changes = not st.session_state.get('show_changes', False)

        if st.session_state.get('show_changes', False):
            show_change_history()

    # 标签页选择
    tab1, tab2, tab3 = st.tabs(["📝 信号词典", "📊 评分模型", "🔒 硬拦截规则"])

    # 信号词典编辑
    with tab1:
        edit_signals(config_dir)

    # 评分模型编辑
    with tab2:
        edit_scoring_models(config_dir)

    # 硬拦截规则编辑
    with tab3:
        edit_hard_filters(config_dir)


def edit_signals(config_dir: str):
    """编辑信号词典"""
    st.markdown("### 信号词典 (signals.json)")
    st.info("配置各特征标签在不同语言下的关键词映射")

    signals_path = os.path.join(config_dir, 'signals.json')

    with open(signals_path, 'r', encoding='utf-8') as f:
        signals = json.load(f)

    selected_signal = st.selectbox("选择信号标签", list(signals.keys()))

    if selected_signal:
        signal_data = signals[selected_signal]
        st.markdown(f"**{selected_signal}** 的关键词配置")

        # 保存原始值用于追踪变更
        original_data = json.dumps(signal_data, ensure_ascii=False)

        updated_data = {}

        for lang in ['CN', 'US', 'JP']:
            current_kw = signal_data.get(lang, [])
            st.markdown(f"#### {lang} 关键词")
            updated_kw = render_tags_editor(
                f"{lang} 现有标签",
                current_kw,
                f"signal_{selected_signal}_{lang}"
            )
            updated_data[lang] = updated_kw

        # 更新信号数据
        signals[selected_signal] = updated_data

        # 检查是否有变更
        if json.dumps(updated_data, ensure_ascii=False) != original_data:
            track_change('signals', selected_signal, original_data, json.dumps(updated_data, ensure_ascii=False))

        st.markdown("---")

        if st.button("保存信号词典", type="primary"):
            save_signals(signals_path, signals)
            st.session_state.last_saved = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.success("信号词典已保存")


def edit_scoring_models(config_dir: str):
    """编辑评分模型"""
    st.markdown("### 评分模型 (scoring_models.json)")
    st.info("配置各品类的基础分和权重向量")

    scoring_path = os.path.join(config_dir, 'scoring_models.json')

    with open(scoring_path, 'r', encoding='utf-8') as f:
        scoring_models = json.load(f)

    selected_category = st.selectbox("选择品类", list(scoring_models.keys()))

    if selected_category:
        category_data = scoring_models[selected_category]
        weights = category_data.get('weights', {})

        # 保存原始值用于追踪变更
        original_base = category_data.get('base_score', 0)

        new_base = st.number_input(
            f"**{selected_category}** 基础分",
            value=int(category_data.get('base_score', 0)),
            step=5
        )

        if new_base != original_base:
            track_change('scoring', f'{selected_category}.base_score', original_base, new_base)

        category_data['base_score'] = new_base

        st.markdown("#### 权重配置")
        positive_weights = {k: v for k, v in weights.items() if v > 0}
        negative_weights = {k: v for k, v in weights.items() if v < 0}

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 正向权重")
            for tag in positive_weights:
                original_weight = positive_weights[tag]
                new_weight = st.number_input(
                    f"{tag}",
                    value=int(positive_weights[tag]),
                    key=f"pos_{selected_category}_{tag}"
                )
                if new_weight != original_weight:
                    track_change('scoring', f'{selected_category}.{tag}', original_weight, new_weight)
                weights[tag] = new_weight

        with col2:
            st.markdown("##### 负向权重")
            for tag in negative_weights:
                original_weight = negative_weights[tag]
                new_weight = st.number_input(
                    f"{tag}",
                    value=int(negative_weights[tag]),
                    key=f"neg_{selected_category}_{tag}"
                )
                if new_weight != original_weight:
                    track_change('scoring', f'{selected_category}.{tag}', original_weight, new_weight)
                weights[tag] = new_weight

        st.markdown("---")

        if st.button("保存评分模型", type="primary"):
            save_scoring_models(scoring_path, scoring_models)
            st.session_state.last_saved = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.success("评分模型已保存")


def edit_hard_filters(config_dir: str):
    """编辑硬拦截规则"""
    st.markdown("### 硬拦截规则 (hard_filters.json)")
    st.info("配置配件拦截词、形态锁定规则和最低分阈值")

    filters_path = os.path.join(config_dir, 'hard_filters.json')

    with open(filters_path, 'r', encoding='utf-8') as f:
        filters = json.load(f)

    # 保存原始值用于追踪变更
    original_acc = filters.get('accessories', [])
    original_threshold = filters.get('min_score_threshold', 30)

    # 配件拦截
    st.markdown("#### 配件拦截词")
    current_acc = filters.get('accessories', [])
    new_acc = st.text_area(
        "配件关键词（逗号分隔）",
        value=", ".join(current_acc),
        height=100
    )
    acc_list = [k.strip() for k in new_acc.split(",") if k.strip()]

    if acc_list != original_acc:
        track_change('hard_filters', 'accessories', original_acc, acc_list)

    # 形态锁定
    st.markdown("#### 形态锁定规则")
    form_lock = filters.get('form_factor_lock', {})

    st.markdown("当前形态锁定配置：")
    if form_lock:
        for tag, category in form_lock.items():
            st.markdown(f"- **{tag}** → **{category}**")
    else:
        st.info("未配置形态锁定规则")

    # 最低分阈值
    st.markdown("#### 最低分阈值")
    new_threshold = st.number_input(
        "低于此阈值归入'灯光类-其他'",
        value=int(filters.get('min_score_threshold', 30)),
        min_value=0,
        step=5
    )

    if new_threshold != original_threshold:
        track_change('hard_filters', 'min_score_threshold', original_threshold, new_threshold)

    st.markdown("---")

    if st.button("保存硬拦截规则", type="primary"):
        filters['accessories'] = acc_list
        filters['min_score_threshold'] = new_threshold
        save_hard_filters(filters_path, filters)
        st.session_state.last_saved = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.success("硬拦截规则已保存")


def save_signals(path: str, signals: dict):
    """保存信号词典"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        st.success("信号词典已保存")
    except Exception as e:
        st.error(f"保存失败: {e}")


def save_scoring_models(path: str, models: dict):
    """保存评分模型"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=2)
        st.success("评分模型已保存")
    except Exception as e:
        st.error(f"保存失败: {e}")


def save_hard_filters(path: str, filters: dict):
    """保存硬拦截规则"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(filters, f, ensure_ascii=False, indent=2)
        st.success("硬拦截规则已保存")
    except Exception as e:
        st.error(f"保存失败: {e}")
