# Agent 协作通知 - 团队模板实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在团队介绍默认模板中添加角色协作配置，使 Agent 能通过 agent-send 主动通知相关成员

**Architecture:** 仅修改 `TeamProfileTemplate.get_default_template()` 的默认模板字符串，添加角色协作配置章节

**Tech Stack:** Python, SQLAlchemy, FastAPI

---

## 任务概览

- 修改文件: `app/models/team.py`
- 测试: 无需单元测试（模板字符串更新），手动验证
- 风险: 低 - 仅更新默认模板，不影响现有数据

---

## 实现步骤

### Task 1: 更新默认团队模板

**Files:**
- Modify: `app/models/team.py:62-84`

- [ ] **Step 1: 读取当前 TeamProfileTemplate 默认模板**

  查看 `app/models/team.py` 中 `get_default_template()` 方法的当前实现

- [ ] **Step 2: 更新默认模板，添加角色协作配置章节**

  将以下内容添加到模板末尾：

  ```markdown

  ## 角色协作配置

  ### 规划师 (planner)
  - **职责**：分析数据、制定计划、拆分任务
  - **需要通知的执行者**：请根据团队配置指定
  - **通知模板**：
    ```
    【新任务通知】

    任务：{{task_name}}
    子任务：{{sub_task_name}}
    任务ID：{{task_id}}
    子任务ID：{{sub_task_id}}

    详情：{{description}}
    验收标准：{{acceptance}}

    请前往系统认领并执行：GET /api/sub-tasks/{{sub_task_id}}

    遇到问题时可通过消息渠道联系规划师。
    ```

  ### 执行者 (executor)
  - **职责**：根据计划创作内容并发布
  - **需要通知的审核者**：请根据团队配置指定
  - **通知模板**：
    ```
    【任务提交审核】

    任务：{{task_name}}
    子任务：{{sub_task_name}}
    任务ID：{{task_id}}
    子任务ID：{{sub_task_id}}

    交付物：{{deliverable}}
    状态：{{from_status}} → {{to_status}}

    请前往系统审核：GET /api/sub-tasks/{{sub_task_id}}

    遇到问题时可通过消息渠道联系执行者。
    ```

  ### 审核者 (reviewer)
  - **职责**：审核内容质量，通过或驳回
  - **审核通过时**：任务完成
  - **审核驳回时通知**：原执行者
  - **通知模板**：
    ```
    【任务需要返工】

    任务：{{task_name}}
    子任务：{{sub_task_name}}
    任务ID：{{task_id}}
    子任务ID：{{sub_task_id}}

    原因：{{rejection_reason}}

    请前往系统查看详情并修复：GET /api/sub-tasks/{{sub_task_id}}

    遇到问题时可通过消息渠道联系审核者。
    ```

  ### 巡查者 (patrol)
  - **职责**：监控系统状态、处理异常
  - **发现异常时通知**：相关角色（根据异常类型）
  - **通知模板**：
    ```
    【异常告警】

    任务：{{task_name}}
    子任务：{{sub_task_name}}
    问题：{{issue_description}}

    请及时处理：GET /api/sub-tasks/{{sub_task_id}}

    遇到问题时可通过消息渠道联系巡查者。
    ```
  ```

- [ ] **Step 3: 运行服务验证模板可正常加载**

  ```bash
  python -m uvicorn app.main:app --host 0.0.0.0 --port 6565
  ```

  验证启动无错误

- [ ] **Step 4: 提交代码**

  ```bash
  git add app/models/team.py
  git commit -m "feat: add agent collaboration config to team profile template"
  ```

---

## 验证步骤

1. 启动服务后，访问 `GET /api/teams/me/profile` 查看团队介绍
2. 确认响应中包含"角色协作配置"章节
3. 可以在管理后台创建新团队验证模板生效

---

## 实施完成

计划完成。是否需要执行此计划？
