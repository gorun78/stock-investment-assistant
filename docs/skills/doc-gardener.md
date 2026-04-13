# doc-gardener 技能

文档园丁技能，执行"架构垃圾回收"任务，定期扫描文档与代码的一致性，清理过期 ADR，并修复因迭代导致的语义冲突，确保"地图"不误导智能体。

## 触发条件

- 定期执行（每周/每月）
- 重大重构后
- 版本发布前
- 发现文档与代码不一致时

## 核心职责

### 1. 文档一致性检查

| 检查项 | 检查内容 | 处理方式 |
|--------|----------|----------|
| API 文档 | 接口定义与实现是否一致 | 标记不一致项，生成修复建议 |
| 数据库文档 | 表结构与 SQL 脚本是否一致 | 同步更新文档 |
| 架构图 | 模块依赖与实际代码是否一致 | 更新架构图 |
| 功能清单 | 功能描述与实现是否一致 | 更新功能清单 |

### 2. ADR 清理

```markdown
## ADR 状态检查

| ADR 编号 | 标题 | 状态 | 最后更新 | 处理建议 |
|----------|------|------|----------|----------|
| ADR-001 | 多数据库架构 | 已采纳 | 2026-01-15 | 保留 |
| ADR-002 | EDC 集成方案 | 已废弃 | 2025-06-01 | 标记废弃，关联新 ADR |
| ADR-003 | 新 EDC 集成 | 已采纳 | 2026-02-01 | 保留 |
```

### 3. 语义冲突修复

```
检测到语义冲突:
- 文档描述: "用户管理模块使用 JWT 认证"
- 代码实现: 使用 Session 认证
- 处理: 更新文档以反映当前实现
```

## 执行流程

```
┌─────────────────────────────────────────┐
│           启动 Doc-gardener              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         1. 扫描文档目录                   │
│  docs/ + 各模块 docs/                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         2. 分析代码现状                   │
│  Controller/Service/DAO 结构             │
│  API 接口定义                            │
│  数据库表结构                            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         3. 对比检测不一致                 │
│  文档 vs 代码                            │
│  ADR 状态 vs 实际情况                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         4. 生成修复报告                   │
│  不一致项列表                            │
│  修复建议                                │
│  优先级排序                              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         5. 执行自动修复                   │
│  更新过期文档                            │
│  标记废弃 ADR                            │
│  同步功能清单                            │
└─────────────────────────────────────────┘
```

## 检查规则

### API 一致性检查

```python
def check_api_consistency():
    # 1. 扫描所有 Controller
    controllers = scan_controllers()
    
    # 2. 提取 API 定义
    apis = extract_api_definitions(controllers)
    
    # 3. 对比文档
    doc_apis = parse_api_docs()
    
    # 4. 找出差异
    differences = compare(apis, doc_apis)
    
    # 5. 生成报告
    return generate_report(differences)
```

### 数据库一致性检查

```sql
-- 检查表结构
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'sys-man';

-- 对比文档中的表定义
```

### ADR 生命周期管理

```
ADR 状态流转:
提议 → 已采纳 → 已废弃
         ↓
      已替代
```

## 输出报告模板

```markdown
# Doc-gardener 扫描报告

## 扫描时间
2026-03-19 10:00:00

## 扫描范围
- docs/architecture/
- docs/api-specs/
- docs/business-rules/
- 各模块 docs/

## 发现问题

### 高优先级
| 问题 | 位置 | 影响 | 建议 |
|------|------|------|------|
| API 文档缺失 | docs/api-specs/sys-man/ | 新接口未记录 | 立即补充 |
| 架构图过期 | docs/architecture/README.md | 误导开发 | 更新架构图 |

### 中优先级
| 问题 | 位置 | 影响 | 建议 |
|------|------|------|------|
| ADR-002 已废弃 | docs/architecture/adr/ | 可能被误用 | 标记废弃 |

### 低优先级
| 问题 | 位置 | 影响 | 建议 |
|------|------|------|------|
| 注释过期 | Bus-Zhi/docs/ | 文档可读性 | 更新注释 |

## 自动修复项
- [x] 更新 API 文档: /api/user/list
- [x] 标记 ADR-002 为已废弃
- [x] 同步功能清单: Bus-Zhi

## 需人工确认项
- [ ] 架构图更新: 需架构师确认
- [ ] 数据库文档: 需 DBA 确认
```

## 定期执行计划

```yaml
# .github/workflows/doc-gardener.yml
name: Doc-gardener
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日执行
  workflow_dispatch:      # 手动触发

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Doc-gardener
        run: |
          echo "🔍 Scanning documentation consistency..."
          # 执行文档一致性检查
      - name: Generate Report
        run: |
          echo "📊 Generating report..."
          # 生成报告
      - name: Create Issue
        if: steps.scan.outputs.issues > 0
        uses: actions/create-issue@v1
        with:
          title: "Doc-gardener 发现文档不一致"
          body: ${{ steps.scan.outputs.report }}
```

## 与其他技能协作

```
Doc-gardener
    │
    ├──→ update-docs (触发文档更新)
    │
    ├──→ self-improvement (记录发现的问题模式)
    │
    └──→ code-reviewer (检查代码注释一致性)
```

## 配置文件

```json
// .doc-gardener.json
{
  "scanPaths": [
    "docs/",
    "*/docs/"
  ],
  "excludePaths": [
    "docs/migration-logs/",
    "docs/session-learning/"
  ],
  "checkRules": {
    "apiConsistency": true,
    "dbConsistency": true,
    "adrLifecycle": true,
    "archDiagramSync": true
  },
  "autoFix": {
    "enabled": true,
    "safeMode": true
  },
  "report": {
    "format": "markdown",
    "output": "docs/session-learning/doc-gardener-report.md"
  }
}
```

## 相关技能

- [update-docs](./update-docs.md) - 文档同步
- [self-improvement](./self-improvement.md) - 自学习
- [code-reviewer](./code-reviewer.md) - 代码审查
