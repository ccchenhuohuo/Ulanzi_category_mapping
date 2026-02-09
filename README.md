# Ulanzi Category Mapping

日本灯光类目分类引擎 - 五层解耦向量化分类架构

## 版本
v1.0.0

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行分类
python main.py --data 日本灯光类.csv --output data/processed/output.csv

# 快速测试
python main.py --data 日本灯光类.csv --sample 1000
```

## 项目结构

- `config/` - 配置文件（可调优）
- `src/` - 核心代码
- `tests/` - 测试用例
- `main.py` - 主程序入口

详细文档请查看 [CLAUDE.md](./CLAUDE.md)
