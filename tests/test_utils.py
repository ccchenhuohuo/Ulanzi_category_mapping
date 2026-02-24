"""
工具函数单元测试
"""
import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import normalize_text, extract_specs, extract_raw_specs


class TestNormalizeText(unittest.TestCase):
    """测试文本预处理函数"""

    def test_fullwidth_to_halfwidth(self):
        """测试全角转半角"""
        text = "Ｌｅｄライト"
        result = normalize_text(text)
        self.assertIn("led", result)

    def test_lowercase(self):
        """测试大小写归一化"""
        text = "LED LIGHT Ring"
        result = normalize_text(text)
        self.assertEqual(result, "led light ring")

    def test_noise_removal(self):
        """测试噪声去除"""
        text = "LED!ライト@#"
        result = normalize_text(text)
        self.assertEqual(result, "led ライト")

    def test_whitespace_normalization(self):
        """测试空格归一化"""
        text = "LED  ライト    test"
        result = normalize_text(text)
        self.assertEqual(result, "led ライト test")

    def test_non_string_input(self):
        """测试非字符串输入"""
        self.assertEqual(normalize_text(123), "")
        self.assertEqual(normalize_text(None), "")


class TestExtractSpecs(unittest.TestCase):
    """测试规格提取函数（归一化）"""

    def test_wattage_extraction(self):
        """测试功率提取"""
        text = "120w led light"
        result = extract_specs(text)
        self.assertEqual(result['f_wattage'], 120.0 / 300.0)

        text_jp = "120ワット"
        result = extract_specs(text_jp)
        self.assertEqual(result['f_wattage'], 120.0 / 300.0)

    def test_wattage_saturation(self):
        """测试功率饱和"""
        text = "500w led light"
        result = extract_specs(text)
        self.assertEqual(result['f_wattage'], 1.0)  # 饱和到1

    def test_no_wattage(self):
        """测试无功率"""
        text = "led light"
        result = extract_specs(text)
        self.assertEqual(result['f_wattage'], 0.0)

    def test_lux_extraction(self):
        """测试照度提取"""
        text = "5000 lux led"
        result = extract_specs(text)
        self.assertEqual(result['f_lux'], 5000.0 / 20000.0)

        text_jp = "5000ルクス"
        result = extract_specs(text_jp)
        self.assertEqual(result['f_lux'], 5000.0 / 20000.0)

    def test_cri_extraction(self):
        """测试CRI提取"""
        text = "cri 96 led light"
        result = extract_specs(text)
        self.assertEqual(result['f_cri'], 0.96)

        text_colon = "cri:96"
        result = extract_specs(text_colon)
        self.assertEqual(result['f_cri'], 0.96)

        # 测试数字在前的格式
        text_number_first = "97 cri"
        result = extract_specs(text_number_first)
        self.assertEqual(result['f_cri'], 0.97)

    def test_kelvin_range_extraction(self):
        """测试色温范围提取"""
        # 单个值
        text = "5600k led light"
        result = extract_specs(text)
        self.assertEqual(result['f_kelvin_min'], 5600.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 5600.0 / 10000.0)

        # 范围值 k-格式
        text_range = "3000k-7200k"
        result = extract_specs(text_range)
        self.assertEqual(result['f_kelvin_min'], 3000.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 7200.0 / 10000.0)
        self.assertAlmostEqual(result['f_kelvin_range'], (7200 - 3000) / 8000.0, places=3)

        # 范围值 k~格式
        text_tilde = "3000k~7200k"
        result = extract_specs(text_tilde)
        self.assertEqual(result['f_kelvin_min'], 3000.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 7200.0 / 10000.0)

        # 范围值 斜杠分隔
        text_slash = "3200k/6000k led"
        result = extract_specs(text_slash)
        self.assertEqual(result['f_kelvin_min'], 3200.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 6000.0 / 10000.0)

        # 范围值 空格+分隔符
        text_space = "2500 - 8500k cob"
        result = extract_specs(text_space)
        self.assertEqual(result['f_kelvin_min'], 2500.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 8500.0 / 10000.0)

    def test_lumens_extraction(self):
        """测试流明提取"""
        text = "10000lm light"
        result = extract_specs(text)
        self.assertEqual(result['f_lumens'], 10000.0 / 50000.0)

        text_jp = "10000ルーメン"
        result = extract_specs(text_jp)
        self.assertEqual(result['f_lumens'], 10000.0 / 50000.0)

    def test_multiple_specs(self):
        """测试多规格同时提取"""
        text = "120w 5000lux cri 96 3000k-7200k"
        result = extract_specs(text)
        self.assertEqual(result['f_wattage'], 120.0 / 300.0)
        self.assertEqual(result['f_lux'], 5000.0 / 20000.0)
        self.assertEqual(result['f_cri'], 0.96)
        self.assertEqual(result['f_kelvin_min'], 3000.0 / 10000.0)
        self.assertEqual(result['f_kelvin_max'], 7200.0 / 10000.0)


class TestExtractRawSpecs(unittest.TestCase):
    """测试原始规格值提取（未归一化）"""

    def test_raw_wattage(self):
        """测试功率原始值提取"""
        text = "200W led light"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_wattage'], 200)

        text_jp = "120ワット"
        result = extract_raw_specs(text_jp)
        self.assertEqual(result['raw_wattage'], 120)

    def test_raw_kelvin(self):
        """测试色温原始值提取"""
        # 单值
        text = "5600k led"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_kelvin_min'], 5600)
        self.assertEqual(result['raw_kelvin_max'], 5600)

        # 范围值 k-格式
        text = "3000k-7200k cob"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_kelvin_min'], 3000)
        self.assertEqual(result['raw_kelvin_max'], 7200)

        # 范围值 斜杠分隔
        text = "3200k/6000k panel"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_kelvin_min'], 3200)
        self.assertEqual(result['raw_kelvin_max'], 6000)

        # 范围值 空格+分隔符（第一个数无k）
        text = "2500 - 8500k rgb light"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_kelvin_min'], 2500)
        self.assertEqual(result['raw_kelvin_max'], 8500)

        # 范围值 波浪号分隔
        text = "3000k~6500k light"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_kelvin_min'], 3000)
        self.assertEqual(result['raw_kelvin_max'], 6500)

    def test_raw_cri(self):
        """测试CRI原始值提取"""
        text = "cri 96 led"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_cri'], 96)

        text = "97 cri"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_cri'], 97)

    def test_raw_lumens(self):
        """测试流明原始值提取"""
        text = "10000lm light"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_lumens'], 10000)

        text_jp = "15000ルーメン"
        result = extract_raw_specs(text_jp)
        self.assertEqual(result['raw_lumens'], 15000)

        # 逗号分隔格式
        text_comma = "12,500lm bright"
        result = extract_raw_specs(text_comma)
        self.assertEqual(result['raw_lumens'], 12500)

        # IP68场景（正确匹配10000，不是IP后面的数字）
        text_ip = "ip68 10000lm waterproof"
        result = extract_raw_specs(text_ip)
        self.assertEqual(result['raw_lumens'], 10000)

        # 超大值拦截（超过500000流明视为误匹配）
        text_over = "light 810000lm"
        result = extract_raw_specs(text_over)
        self.assertEqual(result['raw_lumens'], 0)

    def test_raw_lux(self):
        """测试照度原始值提取"""
        text = "5000lux led"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_lux'], 5000)

        text_jp = "8000ルクス"
        result = extract_raw_specs(text_jp)
        self.assertEqual(result['raw_lux'], 8000)

    def test_raw_specs_all_zeros(self):
        """测试无规格时的原始值"""
        text = "led light"
        result = extract_raw_specs(text)
        self.assertEqual(result['raw_wattage'], 0)
        self.assertEqual(result['raw_kelvin_min'], 0)
        self.assertEqual(result['raw_kelvin_max'], 0)
        self.assertEqual(result['raw_cri'], 0)
        self.assertEqual(result['raw_lumens'], 0)
        self.assertEqual(result['raw_lux'], 0)


if __name__ == '__main__':
    unittest.main()
