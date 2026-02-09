"""
日本灯光类目分类引擎 - 主程序入口
支持命令行参数，支持CSV/Excel输入，支持采样模式
"""
import argparse
import pandas as pd
import json
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.classifier import GlobalLightClassifier


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='全球灯光类目分类引擎 - 五层解耦向量化分类架构',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基础分类
  python main.py --data 日本灯光类.csv --output data/processed/output.csv

  # 快速测试（只处理前1000条）
  python main.py --data 日本灯光类.csv --sample 1000

  # Excel输入
  python main.py --data data.xlsx --output output.csv
        '''
    )

    parser.add_argument('--data', required=True, help='输入数据文件路径 (CSV/Excel)')
    parser.add_argument('--config-dir', default='config', help='配置文件目录 (默认: config)')
    parser.add_argument('--output', default='data/processed/output.csv', help='输出文件路径 (默认: data/processed/output.csv)')
    parser.add_argument('--sample', type=int, help='只处理前N条数据（用于快速测试）')

    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.data):
        print(f"错误: 输入文件不存在: {args.data}")
        sys.exit(1)

    # 验证配置目录
    if not os.path.exists(args.config_dir):
        print(f"错误: 配置目录不存在: {args.config_dir}")
        sys.exit(1)

    # 构建配置文件路径
    signals_path = os.path.join(args.config_dir, 'signals.json')
    scoring_path = os.path.join(args.config_dir, 'scoring_models.json')
    filters_path = os.path.join(args.config_dir, 'hard_filters.json')

    # 验证配置文件
    for config_file, path in [
        ('signals.json', signals_path),
        ('scoring_models.json', scoring_path),
        ('hard_filters.json', filters_path)
    ]:
        if not os.path.exists(path):
            print(f"错误: 配置文件不存在: {path}")
            sys.exit(1)

    # 初始化分类器
    print('初始化分类器...')
    print(f'  - 信号词典: {signals_path}')
    print(f'  - 评分模型: {scoring_path}')
    print(f'  - 硬拦截规则: {filters_path}')

    try:
        classifier = GlobalLightClassifier(signals_path, scoring_path, filters_path)
    except Exception as e:
        print(f"错误: 分类器初始化失败: {e}")
        sys.exit(1)

    # 加载数据
    print(f'\n加载数据: {args.data}')
    try:
        if args.data.endswith('.xlsx') or args.data.endswith('.xls'):
            df = pd.read_excel(args.data)
        else:
            df = pd.read_csv(args.data)
    except Exception as e:
        print(f"错误: 数据加载失败: {e}")
        sys.exit(1)

    # 采样
    if args.sample:
        total_rows = len(df)
        df = df.head(args.sample)
        print(f'采样模式: {args.sample} / {total_rows} 条')

    print(f'数据总量: {len(df)} 条')

    # 执行分类
    print('\n开始分类...')

    def progress_callback(current, total):
        """进度回调函数"""
        print(f'  进度: {current}/{total} ({current*100//total}%)')

    try:
        df_result = classifier.process(df, progress_callback=progress_callback)
    except Exception as e:
        print(f"错误: 分类失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 保存结果
    print(f'\n保存结果: {args.output}')
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        df_result.to_csv(args.output, index=False, encoding='utf-8-sig')
        print('  结果已保存')
    except Exception as e:
        print(f"错误: 结果保存失败: {e}")
        sys.exit(1)

    # 输出分类统计
    print('\n=== 分类统计 ===')
    print(df_result['predicted_category'].value_counts().to_string())

    print('\n完成!')


if __name__ == '__main__':
    main()
