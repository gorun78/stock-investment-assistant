# find-skills 技能

技能检索与匹配技能，根据当前任务自动调用最合适的 Skill 组合。

## 触发条件

- 任务开始时自动调用
- 需要确定执行策略时
- 复杂任务分解时

## 技能匹配矩阵

### 按任务类型匹配

| 任务类型 | 推荐技能组合 | 优先级 |
|----------|--------------|--------|
| 新功能开发 | spec-rfc → frontend-design → code-reviewer → update-docs | 高 |
| Bug 修复 | code-reviewer → update-docs → self-improvement | 高 |
| 重构任务 | spec-rfc → code-reviewer → update-docs | 中 |
| 文档更新 | update-docs | 低 |
| 前端开发 | frontend-design → ui-ux-pro-max → code-reviewer | 高 |
| API 开发 | spec-rfc → code-reviewer → update-docs | 高 |

### 按模块匹配

| 模块 | 推荐技能 | 原因 |
|------|----------|------|
| Sys-Man | spec-rfc + code-reviewer | 系统管理涉及权限安全 |
| Bus-Zhi | spec-rfc + update-docs | 业务逻辑复杂需文档同步 |
| Dc-Cheng | spec-rfc + code-reviewer | 数据治理需严格审查 |
| Datanet-Ge | spec-rfc + update-docs | EDC 集成需文档记录 |
| AIMod-Ming | spec-rfc + self-improvement | AI 模块需持续学习 |
| Runtime | code-reviewer + update-docs | 基础设施需稳定可靠 |

## 匹配算法

```python
def find_skills(task):
    skills = []
    
    # 1. 所有开发任务以 spec-rfc 开始
    if task.type in ['feature', 'refactor', 'api']:
        skills.append('spec-rfc')
    
    # 2. 前端任务添加设计技能
    if task.domain == 'frontend':
        skills.append('frontend-design')
        if task.complexity == 'high':
            skills.append('ui-ux-pro-max')
    
    # 3. 编码完成后执行审查
    if task.type != 'docs':
        skills.append('code-reviewer')
    
    # 4. 任务完成后同步文档
    skills.append('update-docs')
    
    # 5. 复杂任务添加自学习
    if task.complexity == 'high' or task.has_errors:
        skills.append('self-improvement')
    
    return skills
```

## 执行流程

```
┌─────────────────────────────────────────┐
│            任务输入                      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         find-skills 匹配                 │
│  ┌─────────┬─────────┬─────────┐       │
│  │任务类型 │ 模块    │ 复杂度  │       │
│  └────┬────┴────┬────┴────┬────┘       │
│       │         │         │            │
│       └─────────┼─────────┘            │
│                 │                      │
│                 ▼                      │
│       ┌─────────────────┐              │
│       │  技能组合输出    │              │
│       └─────────────────┘              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         按顺序执行技能                   │
│  spec-rfc → code-reviewer → update-docs │
└─────────────────────────────────────────┘
```

## 技能依赖关系

```
spec-rfc (需求分析)
    │
    ├──→ frontend-design (前端设计)
    │        │
    │        └──→ ui-ux-pro-max (交互优化)
    │
    ├──→ code-reviewer (代码审查)
    │        │
    │        └──→ self-improvement (自学习)
    │
    └──→ update-docs (文档同步)
```

## 使用示例

### 示例 1: 新功能开发

```
任务: 为用户管理模块添加批量导入功能

find-skills 分析:
1. 任务类型: feature → 添加 spec-rfc
2. 模块: Sys-Man → 添加 code-reviewer
3. 涉及前端 → 添加 frontend-design
4. 复杂度: 中等 → 添加 update-docs

输出技能组合:
[spec-rfc] → [frontend-design] → [code-reviewer] → [update-docs]
```

### 示例 2: Bug 修复

```
任务: 修复数据血缘查询超时问题

find-skills 分析:
1. 任务类型: fix → 添加 code-reviewer
2. 模块: Dc-Cheng → 添加 update-docs
3. 复杂度: 高 → 添加 self-improvement

输出技能组合:
[code-reviewer] → [update-docs] → [self-improvement]
```

### 示例 3: 前端优化

```
任务: 优化系统管理页面响应式布局

find-skills 分析:
1. 任务类型: refactor → 添加 spec-rfc
2. 领域: frontend → 添加 frontend-design
3. 复杂度: 中等 → 添加 ui-ux-pro-max
4. 添加 code-reviewer 和 update-docs

输出技能组合:
[spec-rfc] → [frontend-design] → [ui-ux-pro-max] → [code-reviewer] → [update-docs]
```

## 技能调用时机

| 阶段 | 调用技能 | 说明 |
|------|----------|------|
| 任务开始 | spec-rfc | 分析需求，制定规格 |
| 设计阶段 | frontend-design | 设计前端方案 |
| 开发阶段 | - | 执行编码 |
| 开发完成 | code-reviewer | 审查代码质量 |
| 任务完成 | update-docs | 同步更新文档 |
| 复盘阶段 | self-improvement | 总结学习 |

## 相关技能

- [spec-rfc](./spec-rfc.md) - 需求分析
- [code-reviewer](./code-reviewer.md) - 代码审查
- [update-docs](./update-docs.md) - 文档同步
- [frontend-design](./frontend-design.md) - 前端设计
- [self-improvement](./self-improvement.md) - 自学习
