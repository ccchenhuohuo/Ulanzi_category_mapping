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

    # 噪声去除（保留字母、数字、连字符、空格）
    text = re.sub(r'[^\w\s\.\-ー]', ' ', text)

    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def extract_kelvin_raw(text):
    """
    提取色温原始值，返回 (min, max) 或 (0, 0)

    支持格式：
    - 3000k-7200k → (3000, 7200)
    - 3000k~7200k → (3000, 7200)
    - 3000k/6000k → (3000, 6000)  支持斜杠
    - 3000k - 7200k → (3000, 7200) 支持空格+分隔符
    - 2500 - 8500k → (2500, 8500) 支持第一个数无k
    - 5600k → (5600, 5600)
    """
    # 范围匹配格式1: Xk-Yk (k紧跟数字)
    kelvin_range_match = re.search(r'(\d{3,5})\s*k\s*[-～~/]\s*(\d{3,5})\s*k', text, re.IGNORECASE)
    if kelvin_range_match:
        kelvin_min = float(kelvin_range_match.group(1))
        kelvin_max = float(kelvin_range_match.group(2))
        if kelvin_max >= 2000 and kelvin_max <= 10000 and kelvin_min >= 2000:
            return (kelvin_min, kelvin_max)

    # 范围匹配格式2: X - Yk (第一个数无k，第二个有k)
    kelvin_range_match2 = re.search(r'(\d{3,5})\s*[-～~]\s*(\d{3,5})\s*k', text, re.IGNORECASE)
    if kelvin_range_match2:
        kelvin_min = float(kelvin_range_match2.group(1))
        kelvin_max = float(kelvin_range_match2.group(2))
        if kelvin_max >= 2000 and kelvin_max <= 10000 and kelvin_min >= 2000:
            return (kelvin_min, kelvin_max)

    # 单个值匹配 - 必须有k后缀
    kelvin_match = re.search(r'(\d{3,5})\s*(k|kelvin|ケルビン)\b', text, re.IGNORECASE)
    if kelvin_match:
        kelvin_val = float(kelvin_match.group(1))
        if kelvin_val >= 2000 and kelvin_val <= 10000:
            return (kelvin_val, kelvin_val)
        else:
            return (0.0, 0.0)
    else:
        return (0.0, 0.0)


def extract_cri_raw(text):
    """
    提取CRI原始值

    支持格式：
    - CRI 97、CRI:96
    - 97 CRI、97cri（数字在前）
    - CRI 95-97 → 取上限97
    """
    # 范围匹配 (CRI 95-97)
    cri_range_match = re.search(r'(cri|tlci)\s*:?\s*(\d+)\s*[-~]\s*(\d+)', text, re.IGNORECASE)
    if cri_range_match:
        cri_val = float(cri_range_match.group(3))  # 取上限
        if 70 <= cri_val <= 100:
            return cri_val
        else:
            return 0.0

    # 格式: CRI 97 或 97 CRI 或 CRI97 或 97cri
    # 支持数字在前(cri)或在后(cri 97)
    cri_match = re.search(r'(\d+)\s*(cri|tlci)|(cri|tlci)\s*:?\s*(\d+)', text, re.IGNORECASE)
    if cri_match:
        # 数字在前
        if cri_match.group(1):
            cri_val = float(cri_match.group(1))
        else:
            cri_val = float(cri_match.group(4))
        if 70 <= cri_val <= 100:
            return cri_val
        else:
            return 0.0

    return 0.0


def extract_wattage_raw(text):
    """
    提取功率原始值

    支持格式：
    - 200W、200w、200Watt、200ワット、200ｗ（全角）
    """
    watt_match = re.search(r'(\d+)\s*(w|watt|ワット|ｗ)', text, re.IGNORECASE)
    if watt_match:
        return float(watt_match.group(1))
    return 0.0


def extract_lumens_raw(text):
    """
    流明值提取

    支持格式：
    - 10000lm、10000lumens、10000ルーメン
    - 12,500lm (带逗号)
    """
    # 匹配数字+单位，上限限制在500000流明
    # 工业级补光灯通常不超过500000流明，超过此值的通常为误匹配
    lumens_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d{3,6})\s*(?:lm|lumens|ルーメン)', text, re.IGNORECASE)
    if lumens_match:
        lumens_val = float(lumens_match.group(1).replace(',', ''))
        if lumens_val <= 500000:
            return lumens_val
    return 0.0


def extract_lux_raw(text):
    """
    照度值提取

    支持格式：
    - 5000 lux、5000ルクス、5000lx
    - 12,500lux (带逗号)
    """
    # 匹配数字+单位，上限限制在200000照度
    lux_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d{3,6})\s*(?:lux|ルクス|lx)', text, re.IGNORECASE)
    if lux_match:
        lux_val = float(lux_match.group(1).replace(',', ''))
        if lux_val <= 200000:
            return lux_val
    return 0.0


def extract_specs(text):
    """
    第三层：规格数字化提取

    保留指标（删除 f_levels、f_angle、f_battery）：
    - f_kelvin_min, f_kelvin_max: 色温范围（归一化）
    - f_kelvin_range: 色温覆盖度
    - f_cri: 显色指数
    - f_wattage: 功率
    - f_lumens: 流明值
    - f_lux: 照度

    Args:
        text: 清洗后的商品标题

    Returns:
        规格参数字典，每个值都在[0, 1]区间
    """
    specs = {}

    # 1. 色温范围 (min/max)
    kelvin_min, kelvin_max = extract_kelvin_raw(text)
    specs['f_kelvin_min'] = kelvin_min / 10000.0 if kelvin_min > 0 else 0.0
    specs['f_kelvin_max'] = kelvin_max / 10000.0 if kelvin_max > 0 else 0.0
    # 色温覆盖范围（归一化）
    if kelvin_max > kelvin_min > 0:
        specs['f_kelvin_range'] = (kelvin_max - kelvin_min) / 8000.0  # 最大8000K范围
    else:
        specs['f_kelvin_range'] = 0.0

    # 2. CRI
    cri_raw = extract_cri_raw(text)
    specs['f_cri'] = cri_raw / 100.0 if cri_raw > 0 else 0.0

    # 3. 功率
    watt_raw = extract_wattage_raw(text)
    specs['f_wattage'] = min(watt_raw / 300.0, 1.0) if watt_raw > 0 else 0.0

    # 4. 流明
    lumens_raw = extract_lumens_raw(text)
    specs['f_lumens'] = min(lumens_raw / 50000.0, 1.0) if lumens_raw > 0 else 0.0

    # 5. 照度
    lux_raw = extract_lux_raw(text)
    specs['f_lux'] = min(lux_raw / 20000.0, 1.0) if lux_raw > 0 else 0.0

    return specs


def extract_raw_specs(text):
    """
    提取未归一化的原始规格值

    用于第一阶段输出，方便验证正则匹配正确性

    Returns:
        包含原始值的字典
    """
    raw_specs = {}

    # 色温
    kelvin_min, kelvin_max = extract_kelvin_raw(text)
    raw_specs['raw_kelvin_min'] = int(kelvin_min) if kelvin_min > 0 else 0
    raw_specs['raw_kelvin_max'] = int(kelvin_max) if kelvin_max > 0 else 0

    # CRI
    raw_specs['raw_cri'] = int(extract_cri_raw(text))

    # 功率
    raw_specs['raw_wattage'] = int(extract_wattage_raw(text))

    # 流明
    raw_specs['raw_lumens'] = int(extract_lumens_raw(text))

    # 照度
    raw_specs['raw_lux'] = int(extract_lux_raw(text))

    return raw_specs
