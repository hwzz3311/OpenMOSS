# 子任务提交清单功能设计

## 概述

为子任务增加"提交清单"功能，记录 Agent 执行完成后提交的产出物信息，与现有的"交付物要求"区分开。

## 背景

现有系统中：
- `deliverable` - 规划师填写的交付物**要求**
- `acceptance` - 规划师填写的验收标准
- Agent 提交时仅标记状态变更（in_progress → review），不携带任何产出物信息
- 前端在子任务详情中显示要求，但无法查看实际提交的产出物

## 需求

1. Agent 调用 submit 时附带产出物清单（JSON 格式）
2. Reviewer 在审查时可以看到提交的产出物
3. 前端在子任务详情抽屉中显示提交清单

## 设计

### 1. 数据库结构

在 `SubTask` 模型中新增字段：

```python
# app/models/sub_task.py
submission = Column(JSON, nullable=True, comment="提交清单")
```

字段说明：
```typescript
interface SubTaskSubmission {
  items: SubTaskSubmissionItem[]
  summary: string          // 提交说明
  submitted_at: string     // 提交时间 ISO 格式
}

interface SubTaskSubmissionItem {
  name: string             // 产出物名称
  path: string             // 文件路径
  type: 'file' | 'directory' | 'config' | 'doc' | 'other'
  description: string     // 简要说明
  status: 'completed' | 'pending'  // 状态
}
```

### 2. API 扩展

**提交成果 API** - 扩展接受提交清单：

```
POST /api/sub-tasks/{sub_task_id}/submit
Body: {
  submission: {
    items: [
      {
        name: string,
        path: string,
        type: 'file' | 'directory' | 'config' | 'doc' | 'other',
        description: string,
        status: 'completed' | 'pending'
      }
    ],
    summary: string
  }
}
```

响应：返回更新后的 SubTask（包含 submission 字段）

### 3. 前端实现

#### 3.1 API Client

在 `webui/src/api/client.ts` 中：
- 扩展 `AdminSubTaskItem` 和 `AdminSubTaskDetail` 类型，增加 `submission` 字段

#### 3.2 提交表单

在子任务详情抽屉中，当 Agent 处于 `in_progress` 状态时：
- 显示"提交清单"编辑区域
- 支持动态添加/删除产出物项
- 支持选择类型、填写路径和描述

#### 3.3 提交清单展示

在子任务详情抽屉中：
- 在"交付物要求"下方新增"提交清单"区块
- 仅在 `status === 'review'` 或 `status === 'done'` 时显示
- 以列表形式展示产出物，显示名称、类型、路径、说明

### 4. 数据流

```
Agent 执行任务
    ↓
Agent 调用 POST /sub-tasks/{id}/submit
    Body: { submission: {...} }
    ↓
后端更新 sub_task.submission 字段
    状态变更为 review
    ↓
前端显示提交清单（供 Reviewer 审查）
```

## 改动范围

### 后端

1. **数据库迁移** (`app/models/sub_task.py`):
   ```python
   # 新增字段
   submission = Column(JSON, nullable=True, comment="提交清单")
   ```

2. **Schema 定义** (`app/schemas/sub_task.py` 或新建):
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Optional, Literal

   class SubTaskSubmissionItem(BaseModel):
       name: str
       path: str
       type: Literal['file', 'directory', 'config', 'doc', 'other']
       description: str
       status: Literal['completed', 'pending']

   class SubTaskSubmission(BaseModel):
       items: List[SubTaskSubmissionItem] = Field(default_factory=list)
       summary: str = ""

   class SubmissionRequest(BaseModel):
       submission: Optional[SubTaskSubmission] = None
   ```

3. **API 扩展** (`app/routers/sub_tasks.py`):
   ```python
   @router.post("/{sub_task_id}/submit", response_model=SubTaskResponse)
   async def submit_sub_task(
       sub_task_id: str,
       req: SubmissionRequest = SubmissionRequest(),  # 新增请求体
       agent: Agent = Depends(get_current_agent),
       db: Session = Depends(get_db),
   ):
       # ... 权限检查 ...
       # 新增：处理 submission
       return sub_task_service.submit_sub_task(
           db, sub_task_id,
           submission=req.submission.model_dump() if req.submission else None
       )
   ```

4. **Service 层** (`app/services/sub_task_service.py`):
   ```python
   def submit_sub_task(db: Session, sub_task_id: str, submission: dict = None) -> SubTask:
       sub_task = db.query(SubTask).filter(SubTask.id == sub_task_id).first()
       if not sub_task:
           raise ValueError(f"子任务 {sub_task_id} 不存在")

       # 校验：最多 50 项
       if submission and submission.get("items"):
           items = submission.get("items")
           if len(items) > 50:
               raise ValueError("提交清单最多 50 项")

       # 更新 submission 字段
       if submission:
           # 注入提交时间
           from datetime import datetime
           submission["submitted_at"] = datetime.now().isoformat()
           sub_task.submission = submission

       sub_task.status = "review"
       db.commit()
       db.refresh(sub_task)
       return sub_task
   ```

### 前端

1. **类型扩展** (`webui/src/api/client.ts`):
   ```typescript
   export interface SubTaskSubmissionItem {
     name: string
     path: string
     type: 'file' | 'directory' | 'config' | 'doc' | 'other'
     description: string
     status: 'completed' | 'pending'
   }

   export interface SubTaskSubmission {
     items: SubTaskSubmissionItem[]
     summary: string
     submitted_at?: string
   }

   // 扩展 AdminSubTaskItem
   export interface AdminSubTaskItem {
     // ... 现有字段
     submission: SubTaskSubmission | null
   }
   ```

2. **提交 API** (`webui/src/api/client.ts`):
   ```typescript
   submit: (subTaskId: string, submission?: SubTaskSubmission) =>
     api.post(`/sub-tasks/${subTaskId}/submit`, { submission }),
   ```

3. **UI 修改** (`webui/src/views/TasksView.vue`):
   - 在子任务详情抽屉中增加"提交清单"编辑区域（in_progress 状态）
   - 在子任务详情抽屉中增加"提交清单"展示区域（review/done 状态）

### task-cli.py CLI 工具

5. **CLI 命令扩展** (`skills/task-cli.py`):

新增 `--submission` 参数，支持 JSON 字符串或文件路径：

```python
def cmd_sub_task_submit(args):
    """提交成果（可选带提交清单）"""
    body = {}
    if args.submission:
        # 支持两种格式：
        # 1. 直接传入 JSON 字符串
        # 2. @文件路径 读取文件内容
        submission_data = args.submission
        if submission_data.startswith('@'):
            # 读取文件
            file_path = submission_data[1:]
            with open(file_path, 'r', encoding='utf-8') as f:
                import json
                body["submission"] = json.load(f)
        else:
            import json
            body["submission"] = json.loads(submission_data)

    data = _request("post", f"/sub-tasks/{args.id}/submit", args.key, json=body)
    if body.get("submission"):
        print(f"✅ 已提交: {data['name']}，含提交清单")
    else:
        print(f"✅ 已提交: {data['name']}，等待审查")
```

参数说明：
- `--submission` 支持直接传入 JSON 字符串
- `--submission @/path/to/file.json` 读取 JSON 文件内容

使用示例：
```bash
# 直接传入 JSON
python task-cli.py --key <KEY> st submit <id> --submission '{"items":[{"name":"README","path":"/docs/README.md","type":"doc","description":"项目说明文档","status":"completed"}],"summary":"完成文档编写"}'

# 从文件读取
python task-cli.py --key <KEY> st submit <id> --submission @submission.json
```

### task-cli.py 新增子命令（可选，便捷方式）

为了简化使用，可新增 `st submit-with` 子命令：

```python
def cmd_sub_task_submit_with(args):
    """带清单的提交（便捷命令）"""
    body = {
        "submission": {
            "items": [
                {
                    "name": args.name,
                    "path": args.path,
                    "type": args.type or "file",
                    "description": args.description or "",
                    "status": args.status or "completed"
                }
            ],
            "summary": args.summary or ""
        }
    }
    data = _request("post", f"/sub-tasks/{args.id}/submit", args.key, json=body)
    print(f"✅ 已提交: {data['name']}，含提交清单")
```

使用示例：
```bash
# 单个文件提交
python task-cli.py --key <KEY> st submit-with <id> --name "用户登录模块" --path "/src/auth/login.ts" --type "file" --desc "实现了用户登录功能"

# 多个文件提交（使用 --submission）
python task-cli.py --key <KEY> st submit <id> --submission @/path/to/submission.json
```

## 测试要点

1. Agent 提交时正确保存 submission 字段
2. 前端能正确显示提交清单
3. 不同状态的子任务正确显示/隐藏提交清单
4. 审查通过后数据持久化
5. 后端 50 项限制生效
6. submission 为 null 时前端正确处理
7. task-cli.py 提交命令正常工作

## 风险与约束

- JSON 字段存储有大小限制，需在接口层做校验（单次提交最多 50 项）
- 前端暂不实现文件浏览功能，仅手动填写路径
- 需要执行数据库迁移 ALTER TABLE
