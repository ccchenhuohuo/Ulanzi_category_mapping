"""
工具函数模块
包含文本预处理和规格提取功能
"""
import re
import unicodedata


def normalize_text(text):
    """
    第一层：基础预处理
    将原始商品标题处理为统一的、干净的基础文本

    处理逻辑：
    1. 全角→半角转换
    2. 大小写归一化
    3. 噪声去除（保留字母、数字、连字符、空格）
    4. 不翻译

    Args:
        text: 原始商品标题

    Returns:
        清洗后的统一格式文本
    """
    if not isinstance(text, str):
        return ""

    # 全角→半角
    text = unicodedata.normalize('NFKC', text)

    # 大小写归一化
    text = text.lower()

    # 噪声去除（保留字母、数字、连字符、空格、全角空格）
    text = re.sub(r'[^\w\s\.\-ー]', ' ', text)

    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def extract_specs(text):
    """
    第三层：规格数字化提取
    将商品标题中的技术参数提取出来，并归一化到[0, 1]区间

    提取的规格参数：
    - f_wattage: 功率 (W)，阈值300W
    - f_lux: 照度 (lux)，阈值20000lux
    - f_kelvin: 色温 (K)，阈值10000K
    - f_cri: 显色指数，阈值100

    Args:
        text: 清洗后的商品标题

    Returns:
        规格参数字典，每个值都在[0, 1]区间
    """
    specs = {}

    # 功率提取 (Watt)
    # 匹配模式：120W、120w、120ワット、120ｗ
    watt_match = re.search(r'(\d+)\s*(w|watt|ワット|ｗ)', text, re.IGNORECASE)
    if watt_match:
        watt_val = float(watt_match.group(1))
        # 归一化：300W为饱和阈值
        specs['f_wattage'] = min(watt_val / 300.0, 1.0)
    else:
        specs['f_wattage'] = 0.0

    # 照度提取 (Lux)
    # 匹配模式：5000 lux、5000ルクス
    lux_match = re.search(r'(\d+[,\s]*\d*)\s*(lux|ルクス)', text, re.IGNORECASE)
    if lux_match:
        lux_val = float(lux_match.group(1).replace(',', '').replace(' ', ''))
        # 归一化：20000lux为饱和阈值
        specs['f_lux'] = min(lux_val / 20000.0, 1.0)
    else:
        specs['f_lux'] = 0.0

    # 色温提取 (K)
    # 匹配模式：5600K、5600ケルビン
    kelvin_match = re.search(r'(\d+)\s*(k|kelvin|ケルビン)', text, re.IGNORECASE)
    if kelvin_match:
        kelvin_val = float(kelvin_match.group(1))
        # 归一化：10000K为饱和阈值
        specs['f_kelvin'] = min(kelvin_val / 10000.0, 1.0)
    else:
        specs['f_kelvin'] = 0.0

    # CRI/TLCI 提取
    # 匹配模式：CRI:96、CRI 96、tlci 95
    cri_match = re.search(r'(cri|tlci)\s*:?\s*(\d+)', text, re.IGNORECASE)
    if cri_match:
        cri_val = float(cri_match.group(2))
        # 归一化：100为满分
        specs['f_cri'] = cri_val / 100.0
    else:
        specs['f_cri'] = 0.0

    return specs
