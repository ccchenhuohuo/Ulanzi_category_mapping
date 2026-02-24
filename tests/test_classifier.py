"""
分类器单元测试
测试典型误判案例
"""
import unittest
import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classifier import GlobalLightClassifier


class TestLightClassifier(unittest.TestCase):
    """灯光分类器单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.classifier = GlobalLightClassifier(
            'config/signals.json',
            'config/scoring_models.json',
            'config/hard_filters.json'
        )

        # 加载测试用例
        with open('tests/test_cases.json', 'r', encoding='utf-8') as f:
            cls.test_cases = json.load(f)['test_cases']

    def test_pano_120c_panel(self):
        """测试 Pano 120c 不被误判为 COB，应归为平板灯"""
        row = {'SKU标题': 'amaran Pano 120c Kit 120W RGBWW パネルライト', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '平板灯',
                         f"期望: 平板灯, 实际: {result['predicted_category']}, 原因: {result['decision_reason']}")

    def test_ad300pro_flash(self):
        """测试 AD300Pro 正确归为闪光灯"""
        row = {'SKU标题': 'Godox AD300Pro 300W Speedlite ストロボ TTL HSS', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '闪光灯',
                         f"期望: 闪光灯, 实际: {result['predicted_category']}")

    def test_ring_light(self):
        """测试环形灯正确识别"""
        row = {'SKU标题': 'NiceVeedi Ring Light 10inch with Phone Stand リングライト', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '环形灯',
                         f"期望: 环形灯, 实际: {result['predicted_category']}")

    def test_tube_light(self):
        """测试棒灯正确识别"""
        row = {'SKU标题': 'Aputure MT Pro Tube Light 60cm RGBWW チューブライト', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '棒灯',
                         f"期望: 棒灯, 实际: {result['predicted_category']}")

    def test_inflatable(self):
        """测试充气灯正确识别"""
        row = {'SKU标题': 'Inflatable Balloon Light 60cm RGB エアライト', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '充气灯',
                         f"期望: 充气灯, 实际: {result['predicted_category']}")

    def test_pocket_light(self):
        """测试口袋灯正确识别"""
        row = {'SKU标题': 'Ulanzi VL49 Mini Video Light Pocket Light', 'site': 'US'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '口袋灯',
                         f"期望: 口袋灯, 实际: {result['predicted_category']}")

    def test_cob_light(self):
        """测试COB灯正确识别"""
        row = {'SKU标题': 'Aputure Amaran 200x Bowens Mount COB LED Light', 'site': 'US'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], 'COB补光灯',
                         f"期望: COB补光灯, 实际: {result['predicted_category']}")

    def test_action_camera_light(self):
        """测试运动相机补光灯"""
        row = {'SKU标题': 'Magnetic Video Light for Action Camera Gopro', 'site': 'US'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '运动相机补光灯',
                         f"期望: 运动相机补光灯, 实际: {result['predicted_category']}")

    def test_flashlight(self):
        """测试摄影手电"""
        row = {'SKU标题': 'Underwater Flashlight for Diving Photography', 'site': 'US'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '摄影手电',
                         f"期望: 摄影手电, 实际: {result['predicted_category']}")

    def test_phone_clip_light(self):
        """测试手机便携补光灯"""
        row = {'SKU标题': 'Portable Phone Clip LED Fill Light', 'site': 'JP'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '手机便携补光灯',
                         f"期望: 手机便携补光灯, 实际: {result['predicted_category']}")

    def test_accessory_softbox(self):
        """测试配件（柔光箱）应归为其他"""
        row = {'SKU标题': 'Softbox Diffuser for Photography Light', 'site': 'US'}
        result = self.classifier.process_row(row)
        self.assertEqual(result['predicted_category'], '灯光类-其他',
                         f"期望: 灯光类-其他, 实际: {result['predicted_category']}")

    def test_all_test_cases(self):
        """运行所有测试用例并报告通过率"""
        passed = 0
        failed = 0
        errors = []

        for case in self.test_cases:
            row = {'SKU标题': case['sku_title'], 'site': case['site']}
            result = self.classifier.process_row(row)

            if result['predicted_category'] == case['expected_category']:
                passed += 1
            else:
                failed += 1
                errors.append({
                    'title': case['sku_title'][:50],
                    'expected': case['expected_category'],
                    'actual': result['predicted_category'],
                    'reason': result['decision_reason']
                })

        # 打印报告
        total = passed + failed
        print(f'\n=== 测试用例执行报告 ===')
        print(f'总计: {total}, 通过: {passed}, 失败: {failed}')
        print(f'通过率: {passed*100//total}%')

        if failed > 0:
            print(f'\n失败用例详情:')
            for err in errors:
                print(f"  - {err['title']}")
                print(f"    期望: {err['expected']}")
                print(f"    实际: {err['actual']}")
                print(f"    原因: {err['reason']}")

        # 断言至少80%通过率
        self.assertGreaterEqual(passed * 100 / total, 80,
                            f"测试通过率过低: {passed*100//total}% < 80%")


if __name__ == '__main__':
    unittest.main(verbosity=2)
