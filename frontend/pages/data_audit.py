"""
数据审核工作台
浏览、审核和修正分类结果
"""
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime


def show():
    """显示数据审核页面"""
    st.markdown("### 数据审核工作台")

    # 初始化会话状态
    if 'audit_data' not in st.session_state:
        st.session_state.audit_data = None
    if 'audit_page' not in st.session_state:
        st.session_state.audit_page = 1

    # 侧边栏 - 数据连接
    with st.sidebar:
        st.markdown("### 数据源")
        data_source = st.selectbox("选择数据源", ["上传文件", "示例数据"])

        if data_source == "上传文件":
            uploaded_file = st.file_uploader("上传CSV/Excel文件", type=['csv', 'xlsx'])
            if uploaded_file:
                load_data(uploaded_file)
        else:
            if st.button("加载示例数据"):
                load_sample_data()

        st.markdown("---")

        # 筛选器（侧边栏）
        st.markdown("### 筛选条件")

        # 品类筛选
        if st.session_state.audit_data is not None:
            df = st.session_state.audit_data
            categories = df['predicted_category'].unique().tolist()
            category_filter = st.multiselect(
                "分类结果",
                options=categories,
                default=[]
            )

            min_score = st.number_input("最低得分", min_value=0, value=0)

            reason_options = ["全部", "高分归档", "形态锁定", "配件拦截", "低分过滤"]
            reason_filter = st.selectbox(
                "裁决类型",
                options=reason_options
            )
        else:
            category_filter = []
            min_score = 0
            reason_filter = "全部"

    # 主界面
    if st.session_state.audit_data is not None:
        df = st.session_state.audit_data

        # 应用筛选
        filtered_df = df.copy()
        if category_filter:
            filtered_df = filtered_df[filtered_df['predicted_category'].isin(category_filter)]
        filtered_df = filtered_df[filtered_df['max_score'] >= min_score]
        if reason_filter != "全部":
            filtered_df = filtered_df[filtered_df['decision_reason'].str.contains(reason_filter)]

        st.markdown(f"**共 {len(filtered_df)} 条记录**")

        # 分页
        page_size = st.selectbox("每页显示", [10, 20, 50], index=0)
        total_pages = (len(filtered_df) + page_size - 1) // page_size

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("上一页") and st.session_state.audit_page > 1:
                st.session_state.audit_page -= 1
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 5px;'>第 {st.session_state.audit_page} / {total_pages} 页</div>", unsafe_allow_html=True)
        with col3:
            if st.button("下一页") and st.session_state.audit_page < total_pages:
                st.session_state.audit_page += 1

        # 当前页数据
        start_idx = (st.session_state.audit_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        page_df = filtered_df.iloc[start_idx:end_idx]

        display_audit_table(page_df)

    else:
        st.info("请先加载数据以开始审核")


def load_data(uploaded_file):
    """加载上传的文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if 'predicted_category' not in df.columns:
            st.warning("文件中未找到 'predicted_category' 列，将使用示例分类结果")
            load_sample_data()
            return

        # 计算最高得分
        if 'scores_all' in df.columns:
            def get_max_score(x):
                try:
                    scores = json.loads(x) if isinstance(x, str) else x
                    if scores:
                        return max(scores.values())
                except:
                    return 0
                return 0
            df['max_score'] = df['scores_all'].apply(get_max_score)
        else:
            df['max_score'] = 0

        # 生成URL（如果没有）
        if 'product_url' not in df.columns:
            df['product_url'] = df.apply(
                lambda row: f"https://www.amazon.{row.get('site', 'com')}/dp/{row.get('sku_id', '')}",
                axis=1
            )

        st.session_state.audit_data = df
        st.session_state.audit_page = 1
        st.success(f"成功加载 {len(df)} 条记录")

    except Exception as e:
        st.error(f"加载文件失败: {e}")


def load_sample_data():
    """加载示例数据"""
    sample_data = [
        {
            'sku_id': 'SKU001',
            'sku_title': 'Godox AD300Pro 300W TTL HSS ストロボ',
            'site': 'JP',
            'product_url': 'https://www.amazon.co.jp/dp/SKU001',
            'clean_title': 'godox ad300pro 300w ttl hss strobo',
            'predicted_category': '闪光灯',
            'decision_reason': '高分归档',
            'max_score': 350,
            'scores_all': json.dumps({'闪光灯': 350, 'COB补光灯': 180, '平板灯': 100}),
            'features_bool': json.dumps({'tag_is_flash': 1, 'tag_has_ttl': 1, 'tag_has_hss': 1}),
            'features_num': json.dumps({'f_wattage': 1.0})
        },
        {
            'sku_id': 'SKU002',
            'sku_title': 'amaran Pano 120c 120W RGBWW パネルライト',
            'site': 'JP',
            'product_url': 'https://www.amazon.co.jp/dp/SKU002',
            'clean_title': 'amaran pano 120c 120w rgbww パネルライト',
            'predicted_category': '平板灯',
            'decision_reason': '高分归档',
            'max_score': 200,
            'scores_all': json.dumps({'平板灯': 200, 'COB补光灯': 150, '棒灯': 80}),
            'features_bool': json.dumps({'tag_is_panel': 1, 'tag_has_rgb': 1}),
            'features_num': json.dumps({'f_wattage': 0.4})
        },
        {
            'sku_id': 'SKU003',
            'sku_title': 'NiceVeedi Ring Light 10inch',
            'site': 'US',
            'product_url': 'https://www.amazon.com/dp/SKU003',
            'clean_title': 'niceveedi ring light 10inch',
            'predicted_category': '环形灯',
            'decision_reason': '形态锁定',
            'max_score': 210,
            'scores_all': json.dumps({'环形灯': 210, '手机便携补光灯': 120}),
            'features_bool': json.dumps({'tag_is_ring': 1}),
            'features_num': json.dumps({})
        },
        {
            'sku_id': 'SKU004',
            'sku_title': 'Aputure MT Pro 60cm RGBWW',
            'site': 'US',
            'product_url': 'https://www.amazon.com/dp/SKU004',
            'clean_title': 'aputure mt pro 60cm rgbww',
            'predicted_category': '棒灯',
            'decision_reason': '高分归档',
            'max_score': 230,
            'scores_all': json.dumps({'棒灯': 230, 'COB补光灯': 100, '平板灯': 80}),
            'features_bool': json.dumps({'tag_is_tube': 1, 'tag_has_rgb': 1}),
            'features_num': json.dumps({'f_wattage': 0.2})
        },
        {
            'sku_id': 'SKU005',
            'sku_title': 'Softbox Diffuser 60cm',
            'site': 'US',
            'product_url': 'https://www.amazon.com/dp/SKU005',
            'clean_title': 'softbox diffuser 60cm',
            'predicted_category': '灯光类-其他',
            'decision_reason': '配件拦截',
            'max_score': 20,
            'scores_all': json.dumps({'灯光类-其他': 50, '平板灯': 30}),
            'features_bool': json.dumps({}),
            'features_num': json.dumps({})
        }
    ]

    df = pd.DataFrame(sample_data)
    st.session_state.audit_data = df
    st.session_state.audit_page = 1
    st.success(f"加载了 {len(df)} 条示例数据")


def display_audit_table(page_df: pd.DataFrame):
    """显示审核表格"""
    for idx, row in page_df.iterrows():
        # 获取数据
        sku_id = row.get('sku_id', '')
        sku_title = row.get('sku_title', '')
        site = row.get('site', '')
        url = row.get('product_url', '')
        predicted = row.get('predicted_category', '')
        max_score = row.get('max_score', 0)
        reason = row.get('decision_reason', '')

        # 根据裁决类型显示不同颜色
        reason_colors = {
            '高分归档': ('#E8F5E9', 'green'),
            '形态锁定': ('#E3F2FD', 'blue'),
            '配件拦截': ('#FFEBEE', 'red'),
            '低分过滤': ('#FFF3E0', 'orange'),
        }
        bg_color, reason_color = reason_colors.get(reason, ('#F5F5F5', 'gray'))

        # 裁决类型显示
        reason_display = f":{reason_color}[{reason}]"

        # 卡片样式
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {reason_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 16px;">{sku_id}</strong>
                    <span style="color: #666; margin-left: 10px;">[{site}]</span>
                </div>
                <div>
                    <span style="background-color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">{predicted}</span>
                    <span style="color: #888; margin-left: 10px;">得分: {max_score}</span>
                    <span style="color: {reason_color}; margin-left: 10px;">{reason_display}</span>
                </div>
            </div>
            <div style="margin-top: 8px; color: #333;">{sku_title}</div>
        </div>
        """, unsafe_allow_html=True)

        # 操作区和详情
        with st.expander("查看详情 & 审核操作"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**商品信息**")
                st.markdown(f"- SKU: `{sku_id}`")
                st.markdown(f"- 站点: {site}")
                if url:
                    st.markdown(f"- 链接: [查看商品]({url})")
                st.markdown(f"- 标题: {sku_title}")

            with col2:
                st.markdown("**分类结果**")
                st.markdown(f"- 预测分类: **{predicted}**")
                st.markdown(f"- 最高得分: {max_score}")
                st.markdown(f"- 裁决原因: {reason}")

                # 品类选择
                categories = ['闪光灯', 'COB补光灯', '平板灯', '环形灯', '棒灯', '口袋灯',
                             '摄影手电', '充气灯', '手机便携补光灯', '运动相机补光灯', '灯光类-其他']
                default_idx = categories.index(predicted) if predicted in categories else 0
                new_category = st.selectbox(
                    "修正分类",
                    options=categories,
                    key=f"correct_{idx}",
                    index=default_idx
                )

            with col3:
                st.markdown("**审核操作**")
                if st.button("保存修正", key=f"save_{idx}"):
                    # 这里应该调用后端保存
                    st.success(f"已保存: {sku_id} -> {new_category}")
                    # 记录到日志
                    from frontend.utils.error_handler import execution_logger
                    execution_logger.log_audit(sku_id, 'correct', predicted, new_category)

            # 得分和特征详情
            st.markdown("---")
            st.markdown("**得分详情**")
            try:
                scores_all = json.loads(row['scores_all']) if isinstance(row['scores_all'], str) else row['scores_all']
                if scores_all:
                    scores_df = pd.DataFrame([
                        {'品类': k, '得分': v} for k, v in scores_all.items()
                    ]).sort_values('得分', ascending=False)
                    st.table(scores_df)
            except:
                pass

            st.markdown("**特征分析**")
            try:
                features_bool = json.loads(row['features_bool']) if isinstance(row['features_bool'], str) else row['features_bool']
                enabled = [(k, v) for k, v in features_bool.items() if v == 1.0]
                if enabled:
                    tags_html = " ".join([f":blue[`{k}`]" for k, v in enabled])
                    st.markdown(tags_html)
                else:
                    st.markdown("无匹配的布尔特征")
            except:
                pass
