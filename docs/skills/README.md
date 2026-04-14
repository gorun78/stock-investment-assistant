# 技能库配置文档

本目录定义 DataBridge-GZCM 项目的核心技能库（Skill Library）。技能是封装了专业经验、规范与逻辑的闭环执行单元，是企业的核心数字资产。

## 目录结构

```
skills/
├── README.md                    # 本文件
├── spec-rfc.md                  # 最高优先级需求分析
├── code-reviewer.md             # 自动化质量守门员
├── update-docs.md               # 自动同步与自愈
├── frontend-design.md           # UI 逻辑封装
├── ui-ux-pro-max.md             # 交互体验优化
├── find-skills.md               # 技能检索与匹配
├── doc-gardener.md              # 文档园丁（架构垃圾回收）
└── self-improvement.md          # 闭环自学习
```

## 核心技能库定义

| 技能名称 | 核心职能 | 实施标准 |
|----------|----------|----------|
| spec-rfc | 最高优先级需求分析 | 从 7 个核心维度挖掘需求，生成结构化规格说明书 |
| code-reviewer | 自动化质量守门员 | 覆盖多语言规范、安全漏洞及可维护性审计 |
| update-docs | 自动同步与自愈 | 任务完成后强制执行，确保文档与代码同步更新 |
| frontend-design | UI 逻辑封装 | 指导 AI 遵循企业样式规范与组件选型逻辑 |
| ui-ux-pro-max | 交互体验优化 | 强化 UI 细节感知，提升 AI 对复杂交互实现的审美 |
| find-skills | 技能检索与匹配 | 根据当前任务自动调用最合适的 Skill 组合 |
| doc-gardener | 文档园丁 | 定期扫描文档与代码一致性，清理过期 ADR，修复语义冲突 |
| self-improvement | 闭环自学习 | 收集错误案例并更新跨会话的项目记忆 |

## 技能调用优先级

```
1. spec-rfc        # 所有开发任务必须以 spec-rfc 开始
2. find-skills     # 自动匹配相关技能
3. code-reviewer   # 编码完成后执行
4. update-docs     # 任务完成后强制执行
5. self-improvement # 复盘仪式
```

## 技能详细说明

### 1. spec-rfc - 需求分析

从以下 7 个维度生成规格说明书：

1. **System Context**: 系统边界、用户角色及外部系统依赖
2. **Capability Map**: 业务能力的分层拆解与模块归属
3. **Architecture Decision (ADR)**: 记录关键技术路径决策
4. **Technical Architecture**: 明确分层职责与技术栈选型
5. **API & Data Spec**: 定义结构化契约与核心数据模型
6. **Execution Plan**: 细化的原子化任务列表
7. **Quality Standards**: 明确测试覆盖要求与验收 Grade

### 2. code-reviewer - 代码审查

审查维度：

- **代码规范**: 命名、格式、注释
- **安全漏洞**: SQL 注入、XSS、敏感信息泄露
- **可维护性**: 复杂度、重复代码、依赖关系
- **性能问题**: N+1 查询、内存泄漏

### 3. update-docs - 文档同步

同步范围：

- API 文档更新
- 数据库变更记录
- 架构决策记录
- 功能清单更新

### 4. frontend-design - 前端设计

遵循规范：

- Ant Design 6.x 组件库
- 响应式布局设计
- 主题配置规范
- 国际化支持

### 5. ui-ux-pro-max - 交互优化

优化方向：

- 用户体验流程
- 交互反馈机制
- 错误处理友好性
- 加载状态展示

### 6. find-skills - 技能匹配

匹配逻辑：

```python
def find_skills(task_type, context):
    skills = []
    if task_type == "feature":
        skills.append("spec-rfc")
    if task_type == "frontend":
        skills.append("frontend-design")
    if task_type == "review":
        skills.append("code-reviewer")
    return skills
```

### 7. self-improvement - 自学习

学习闭环：

```
1. 收集错误案例
2. 分析根因
3. 更新项目记忆
4. 生成新 Skill（如需要）
```

## 相关文档

- [MCP 服务配置](../mcp-config.md)
- [质量标准](../quality-standards/README.md)
- [架构设计](../architecture/README.md)
