"""
工具函数单元测试
"""
import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import normalize_text, extract_specs


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
    """测试规格提取函数"""

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

    def test_kelvin_extraction(self):
        """测试色温提取"""
        text = "5600k led light"
        result = extract_specs(text)
        self.assertEqual(result['f_kelvin'], 5600.0 / 10000.0)

    def test_cri_extraction(self):
        """测试CRI提取"""
        text = "cri 96 led light"
        result = extract_specs(text)
        self.assertEqual(result['f_cri'], 0.96)

        text_colon = "cri:96"
        result = extract_specs(text_colon)
        self.assertEqual(result['f_cri'], 0.96)

    def test_multiple_specs(self):
        """测试多规格同时提取"""
        text = "120w 5000lux cri 96"
        result = extract_specs(text)
        self.assertEqual(result['f_wattage'], 120.0 / 300.0)
        self.assertEqual(result['f_lux'], 5000.0 / 20000.0)
        self.assertEqual(result['f_cri'], 0.96)


if __name__ == '__main__':
    unittest.main()
