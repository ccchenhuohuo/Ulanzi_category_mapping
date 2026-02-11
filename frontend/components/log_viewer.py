"""
日志查看器组件
提供日志文件读取和展示功能
"""
import streamlit as st
import os


def get_log_file_path() -> str:
    """获取日志文件路径"""
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    log_file = os.path.join(current_dir, 'log.txt')
    return log_file


def read_log_file(max_lines: int = 1000) -> list:
    """
    读取日志文件

    Args:
        max_lines: 最大读取行数

    Returns:
        日志行列表
    """
    log_file = get_log_file_path()

    if not os.path.exists(log_file):
        return []

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-max_lines:] if len(lines) > max_lines else lines
    except Exception:
        return []


def render_log_viewer():
    """渲染日志查看器"""
    st.markdown("### 📋 执行日志")

    # 读取日志文件
    log_lines = read_log_file()

    if not log_lines:
        st.info("暂无日志记录")
        return

    # 统计信息
    stats = {
        'INFO': 0,
        'WARNING': 0,
        'ERROR': 0
    }

    for line in log_lines:
        for level in stats.keys():
            if f'[{level}]' in line:
                stats[level] += 1
                break

    # 显示统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("INFO", stats['INFO'])
    with col2:
        st.metric("WARNING", stats['WARNING'])
    with col3:
        st.metric("ERROR", stats['ERROR'])

    # 筛选器
    st.markdown("#### 日志筛选")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        level_filter = st.multiselect(
            "日志级别",
            options=['INFO', 'WARNING', 'ERROR', 'DEBUG'],
            default=['INFO', 'WARNING', 'ERROR']
        )
    with filter_col2:
        search_term = st.text_input("搜索关键词", placeholder="输入搜索内容...")

    # 筛选日志
    filtered_lines = []
    for line in log_lines:
        # 级别筛选
        has_level = any(f'[{level}]' in line for level in level_filter)
        if not has_level:
            continue

        # 关键词筛选
        if search_term and search_term.lower() not in line.lower():
            continue

        filtered_lines.append(line)

    # 显示日志
    st.markdown(f"共 **{len(filtered_lines)}** 条日志")

    # 日志内容显示
    log_container = st.container(height=400)

    with log_container:
        for line in reversed(filtered_lines):
            # 根据级别设置颜色
            if '[ERROR]' in line:
                color = '#FFCDD2'
                icon = '❌'
            elif '[WARNING]' in line:
                color = '#FFF9C4'
                icon = '⚠️'
            elif '[DEBUG]' in line:
                color = '#E3F2FD'
                icon = '🐛'
            else:
                color = '#E8F5E9'
                icon = 'ℹ️'

            st.markdown(
                f'<div style="background-color: {color}; padding: 8px; border-radius: 4px; margin: 4px 0; font-family: monospace; font-size: 12px;">{icon} {line.strip()}</div>',
                unsafe_allow_html=True
            )

    # 刷新按钮
    if st.button("刷新日志", key="refresh_log"):
        st.rerun()


def show_log_in_sidebar():
    """在侧边栏显示日志统计"""
    log_file = get_log_file_path()

    if not os.path.exists(log_file):
        return

    # 读取统计
    stats = {
        'INFO': 0,
        'WARNING': 0,
        'ERROR': 0
    }

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                for level in stats.keys():
                    if f'[{level}]' in line:
                        stats[level] += 1
                        break
    except Exception:
        return

    # 显示统计
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 日志统计**")

    for level, count in stats.items():
        if count > 0:
            if level == 'ERROR':
                st.sidebar.error(f"{level}: {count}")
            elif level == 'WARNING':
                st.sidebar.warning(f"{level}: {count}")
            else:
                st.sidebar.info(f"{level}: {count}")
        else:
            st.sidebar.markdown(f"{level}: {count}")


def clear_log_file():
    """清空日志文件"""
    log_file = get_log_file_path()

    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('')
        return True
    except Exception:
        return False


def render_log_sidebar_panel():
    """渲染日志侧边栏面板"""
    """渲染日志侧边栏面板，包含统计和快捷操作"""
    show_log_in_sidebar()

    # 快捷操作
    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚡ 快捷操作**")

    if st.sidebar.button("清空日志", key="clear_log"):
        if clear_log_file():
            st.sidebar.success("日志已清空")
            st.rerun()
        else:
            st.sidebar.error("清空失败")

    if st.sidebar.button("查看完整日志", key="view_full_log"):
        st.session_state.show_full_log = True


def set_full_log_view(state: bool = True):
    """设置完整日志视图状态"""
    st.session_state.show_full_log = state
