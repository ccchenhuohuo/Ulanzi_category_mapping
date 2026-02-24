# 日本灯光类分类引擎

**数据量**: 387,722 条 | **类目数**: 11个 | **架构**: 五层解耦向量化

---

## 架构

```
输入: 商品标题
  ↓ normalize_text()   # 文本预处理
  ↓ extract_signals()  # 布尔特征
  ↓ extract_specs()   # 数值特征
  ↓ calculate_scores() # 向量化评分
  ↓ arbitrate()        # 冲突裁决
输出: 类目分类
```

---

## 11个类目

COB补光灯、平板灯、环形灯、闪光灯、口袋灯、棒灯、摄影手电、充气灯、手机便携补光灯、运动相机补光灯、灯光类-其他

---

## 配置文件

`config/signals.json` - 布尔标签关键词词典

`config/scoring_models.json` - 11类目评分权重

`config/hard_filters.json` - 硬拦截规则

---

## 文件结构

```
├── config/
├── data/raw/
├── data/processed/
├── src/
│   ├── classifier.py
│   └── utils.py
├── tests/
├── main.py
└── requirements.txt
```

---

## Feishu Operations & MCP Rules

### 认证原则 (Authentication)
- **强制使用 UAT**: 飞书 API 调用必须显式设置 `useUAT=true`。
- **权限边界**: 
  - 所有文件的创建、修改、删除均须通过 `user_access_token` (UAT)。
  - 应用创建的文件也必须通过 UAT 进行后续操作。
- **tenant_access_token 限制**:
  - **仅用于**: 发现 UAT 权限不足以给用户开放文档权限时的特殊补救。
  - **禁止事项**: 绝不允许以 tenant 身份创建任何新文件。

### 关键身份信息 (Identities)
- **主要用户**: 陈煜 (Open ID: `ou_93584ea0074a8000c86012b4ea3b308d` | Phone: `15837138830`)
- **通知群组**: Claude助手群 (Chat ID: `oc_55283addb22b6e3cbb50d2d04ce5c53e`)

### 操作同步流程 (Sync Workflow)
- **增删改记录**: 任何飞书文档的增删改操作完成后，必须立即在 **Claude助手群** 发布：`操作说明 + 链接`。
- **批量处理**: 涉及多项操作时，必须在群内逐一列出明细。
