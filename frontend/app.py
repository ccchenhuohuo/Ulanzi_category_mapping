"""
Streamlit 主程序入口
Ulanzi 灯光类目分类可视化前端
"""
import streamlit as st
import sys
import os

# 设置页面配置
st.set_page_config(
    page_title="Ulanzi 灯光分类系统",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入页面模块（使用绝对导入）
from frontend.pages.rules_overview import show as rules_overview_show
from frontend.pages.classification_test import show as classification_test_show
from frontend.pages.data_audit import show as data_audit_show
from frontend.pages.rule_config import show as rule_config_show
from frontend.utils.error_handler import execution_logger

# CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E3A5F;
        padding: 10px 0;
        border-bottom: 2px solid #E8E8E8;
        margin-bottom: 20px;
    }
    .sidebar-info {
        position: fixed;
        bottom: 10px;
        left: 10px;
        font-size: 12px;
        color: #888;
    }
    .stRadio > div {
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    # 初始化会话状态
    if 'show_full_log' not in st.session_state:
        st.session_state.show_full_log = False

    # 主标题
    st.markdown('<div class="main-header">💡 Ulanzi 灯光类目分类系统</div>', unsafe_allow_html=True)

    # 侧边栏导航（子菜单结构）
    with st.sidebar:
        st.markdown("### 功能菜单")

        # 主功能区
        main_menu = st.radio(
            "选择功能",
            ["规则概览", "分类测试", "数据审核", "规则配置"]
        )

        st.markdown("---")

        # 展开/收起高级功能
        with st.expander("高级功能 ▾", expanded=False):
            show_log = st.checkbox("查看执行日志")
            st.caption("显示系统运行日志")

        st.markdown("---")

    # 完整日志视图
    if show_log:
        from frontend.components.log_viewer import render_log_viewer, read_log_file, get_log_file_path
        from frontend.components.log_viewer import clear_log_file

        # 日志统计
        log_lines = read_log_file(1000)
        stats = {'INFO': 0, 'WARNING': 0, 'ERROR': 0}
        for line in log_lines:
            for level in stats:
                if f'[{level}]' in line:
                    stats[level] += 1

        # 日志统计展示
        col1, col2, col3 = st.columns(3)
        col1.metric("INFO", stats['INFO'])
        col2.metric("WARNING", stats['WARNING'])
        col3.metric("ERROR", stats['ERROR'])

        # 清空日志按钮
        if st.button("清空日志"):
            if clear_log_file():
                st.success("日志已清空")
                st.rerun()

        # 日志内容
        render_log_viewer()
        st.markdown("---")

    # 根据选择显示不同页面
    if main_menu == "规则概览":
        rules_overview_show()
    elif main_menu == "分类测试":
        classification_test_show()
    elif main_menu == "数据审核":
        data_audit_show()
    elif main_menu == "规则配置":
        rule_config_show()

    # 右下角系统信息
    st.markdown("""
    <div class="sidebar-info">
        系统版本: 1.1.0 | 数据更新: 实时
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
