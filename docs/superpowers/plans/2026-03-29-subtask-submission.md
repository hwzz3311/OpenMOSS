# 子任务提交清单功能实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现子任务提交清单功能，Agent 执行完成后可提交产出物清单，Reviewer 可查看

**Architecture:** 在现有 SubTask 模型中新增 JSON 字段存储提交清单，扩展 submit API 接受提交数据，前端展示清单，CLI 支持带清单提交

**Tech Stack:** Python (FastAPI), Vue 3, TypeScript, SQLite

---

## 文件结构

| 组件 | 文件 | 操作 |
|------|------|------|
| 后端模型 | `app/models/sub_task.py` | 修改 |
| 后端 Schema | `app/schemas/sub_task.py` | 新建 |
| 后端 API | `app/routers/sub_tasks.py` | 修改 |
| 后端 Service | `app/services/sub_task_service.py` | 修改 |
| 前端类型 | `webui/src/api/client.ts` | 修改 |
| 前端页面 | `webui/src/views/TasksView.vue` | 修改 |
| CLI 工具 | `skills/task-cli.py` | 修改 |

---

## Chunk 1: 后端数据库模型和 Schema

### Task 1: 添加数据库字段

**Files:**
- Modify: `app/models/sub_task.py:27`

- [ ] **Step 1: 添加 submission 字段到 SubTask 模型**

在 `recurring_config` 字段后添加：
```python
submission = Column(JSON, nullable=True, comment="提交清单")
```

- [ ] **Step 2: 执行数据库迁移**

```bash
# 方式1: 手动 SQL（推荐开发环境）
sqlite3 data/tasks.db "ALTER TABLE sub_task ADD COLUMN submission JSON;"

# 或重启服务自动创建（如果使用 create_all）
# 注意：SQLAlchemy 的 create_all 不会为已有表添加新列
```

- [ ] **Step 3: 验证字段添加成功**

```bash
sqlite3 data/tasks.db ".schema sub_task" | grep submission
```

### Task 2: 创建 Submission Schema

**Files:**
- Create: `app/schemas/sub_task.py` (新建文件)

- [ ] **Step 1: 检查现有 schema 文件结构**

```bash
ls -la app/schemas/
```

- [ ] **Step 2: 创建 Schema 文件**

创建 `app/schemas/sub_task.py`：
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class SubTaskSubmissionItem(BaseModel):
    name: str = Field(..., description="产出物名称")
    path: str = Field(..., description="文件路径")
    type: Literal['file', 'directory', 'config', 'doc', 'other'] = Field(default='file', description="类型")
    description: str = Field(default="", description="简要说明")
    status: Literal['completed', 'pending'] = Field(default='completed', description="状态")


class SubTaskSubmission(BaseModel):
    items: List[SubTaskSubmissionItem] = Field(default_factory=list, description="产出物列表")
    summary: str = Field(default="", description="提交说明")
    submitted_at: Optional[str] = Field(default=None, description="提交时间")


class SubmissionRequest(BaseModel):
    submission: Optional[SubTaskSubmission] = Field(default=None, description="提交清单")
```

- [ ] **Step 3: 注册到 __init__.py**

检查并更新 `app/schemas/__init__.py`：
```bash
cat app/schemas/__init__.py
```

如果有内容，添加导出：
```python
# 在文件末尾添加
from app.schemas.sub_task import SubTaskSubmission, SubTaskSubmissionItem, SubmissionRequest

__all__ = [
    # ... existing exports
    "SubTaskSubmission",
    "SubTaskSubmissionItem",
    "SubmissionRequest",
]
```

如果没有内容，创建：
```python
from app.schemas.sub_task import SubTaskSubmission, SubTaskSubmissionItem, SubmissionRequest

__all__ = [
    "SubTaskSubmission",
    "SubTaskSubmissionItem",
    "SubmissionRequest",
]
```

---

## Chunk 2: 后端 API 和 Service

### Task 3: 修改 Service 层

**Files:**
- Modify: `app/services/sub_task_service.py:169-178`

- [ ] **Step 1: 查看现有 submit_sub_task 函数**

```bash
sed -n '169,180p' app/services/sub_task_service.py
```

- [ ] **Step 2: 修改 submit_sub_task 函数**

替换为：
```python
def submit_sub_task(db: Session, sub_task_id: str, submission: dict = None) -> SubTask:
    """提交成果：in_progress → review"""
    from datetime import datetime

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
        submission["submitted_at"] = datetime.now().isoformat()
        sub_task.submission = submission

    sub_task.status = "review"
    db.commit()
    db.refresh(sub_task)
    return sub_task
```

- [ ] **Step 3: 运行测试验证**

```bash
# 测试服务能正常启动
python -c "from app.services.sub_task_service import submit_sub_task; print('OK')"
```

### Task 4: 修改 API 路由

**Files:**
- Modify: `app/routers/sub_tasks.py:300-333`

- [ ] **Step 1: 查看现有 submit API**

```bash
sed -n '300,340p' app/routers/sub_tasks.py
```

- [ ] **Step 2: 修改 submit API 接受请求体**

找到 `async def submit_sub_task` 函数，修改参数：
```python
from app.schemas.sub_task import SubmissionRequest

@router.post("/{sub_task_id}/submit", response_model=SubTaskResponse, summary="提交成果")
async def submit_sub_task(
    sub_task_id: str,
    req: SubmissionRequest = SubmissionRequest(),  # 新增请求体
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    """提交成果：in_progress → review
    - 如果任务指定了 assigned_agent，则该 Agent 可以提交（不限角色）
    - 如果任务未指定 assigned_agent，则只有 executor 角色可以提交
    - 可选在请求体中携带 submission 提交清单
    """
    from app.models.sub_task import SubTask

    sub_task = db.query(SubTask).filter(SubTask.id == sub_task_id).first()
    if not sub_task:
        raise HTTPException(status_code=404, detail=f"子任务 {sub_task_id} 不存在")

    # 权限检查
    if sub_task.assigned_agent:
        if agent.id != sub_task.assigned_agent:
            raise HTTPException(
                status_code=403,
                detail="此任务已指定其他 Agent，你无权提交"
            )
    else:
        if agent.role != "executor":
            raise HTTPException(
                status_code=403,
                detail="只有 executor 角色可以提交未指定 Agent 的任务"
            )

    try:
        submission_data = req.submission.model_dump() if req.submission else None
        return sub_task_service.submit_sub_task(db, sub_task_id, submission=submission_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

- [ ] **Step 3: 验证 API 启动**

```bash
python -c "from app.routers import sub_tasks; print('OK')"
```

---

## Chunk 3: 前端实现

### Task 5: 扩展前端 API 类型

**Files:**
- Modify: `webui/src/api/client.ts`

- [ ] **Step 1: 查看 AdminSubTaskItem 定义位置**

```bash
grep -n "AdminSubTaskItem" webui/src/api/client.ts | head -5
```

- [ ] **Step 2: 在文件开头添加 Submission 类型定义**

在 import 语句后，添加：
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
```

- [ ] **Step 3: 扩展 AdminSubTaskItem**

找到 `export interface AdminSubTaskItem` 定义，添加：
```typescript
  // 现有字段...
  deliverable: string
  acceptance: string
  // 新增字段
  submission: SubTaskSubmission | null
```

- [ ] **Step 4: 检查现有 subTaskApi 的 submit 方法**

```bash
grep -n "submit:" webui/src/api/client.ts
```

- [ ] **Step 5: 扩展 subTaskApi 的 submit 方法**

找到 `const subTaskApi` 定义，修改或添加：
```typescript
submit: (subTaskId: string, submission?: SubTaskSubmission) =>
  api.post(`/sub-tasks/${subTaskId}/submit`, { submission }),
```

- [ ] **Step 5: 安装类型依赖**

```bash
cd webui && npm install
```

- [ ] **Step 6: 验证类型编译**

```bash
cd webui && npx vue-tsc --noEmit 2>&1 | head -20
```

### Task 6: 前端 UI 修改

**Files:**
- Modify: `webui/src/views/TasksView.vue`

- [ ] **Step 1: 查找子任务详情抽屉的实际位置**

```bash
grep -n "交付物要求\|验收标准\|Separator" webui/src/views/TasksView.vue | head -20
```

记录找到的行号，用于后续步骤。

- [ ] **Step 2: 在"验收标准"区块后添加"提交清单"展示区块**

在 `<Separator />` (line 1164) 之前，添加：
```vue
                            <!-- 提交清单（review/done 状态显示） -->
                            <div v-if="selectedSubTask && (selectedSubTask.status === 'review' || selectedSubTask.status === 'done') && selectedSubTask.submission" class="rounded-xl border border-border/50 p-3.5">
                                <div class="text-[11px] text-muted-foreground/60 uppercase tracking-wider">
                                    提交清单 · {{ selectedSubTask.submission.items?.length || 0 }}
                                </div>
                                <div v-if="selectedSubTask.submission.summary" class="mt-2 text-sm text-muted-foreground">
                                    {{ selectedSubTask.submission.summary }}
                                </div>
                                <div class="mt-3 space-y-2">
                                    <div v-for="(item, idx) in selectedSubTask.submission.items" :key="idx"
                                        class="flex items-start gap-2 text-xs p-2 rounded bg-muted/30">
                                        <span class="shrink-0 px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">
                                            {{ item.type }}
                                        </span>
                                        <div class="min-w-0 flex-1">
                                            <div class="font-medium">{{ item.name }}</div>
                                            <div class="text-muted-foreground truncate">{{ item.path }}</div>
                                            <div v-if="item.description" class="text-muted-foreground mt-0.5">
                                                {{ item.description }}
                                            </div>
                                        </div>
                                        <span v-if="item.status === 'completed'" class="shrink-0 text-green-500">✓</span>
                                        <span v-else class="shrink-0 text-amber-500">○</span>
                                    </div>
                                </div>
                                <div v-if="selectedSubTask.submission.submitted_at" class="mt-2 text-[10px] text-muted-foreground">
                                    提交于 {{ formatDate(selectedSubTask.submission.submitted_at) }}
                                </div>
                            </div>
```

- [ ] **Step 3: 在"交付物要求"区块前添加编辑区块（in_progress 状态）**

在 "交付物要求" 区块 (line 1144) 之前添加：
```vue
                            <!-- 提交清单编辑（in_progress 状态显示） -->
                            <div v-if="selectedSubTask && selectedSubTask.status === 'in_progress'" class="rounded-xl border border-primary/50 bg-primary/5 p-3.5 space-y-3">
                                <div class="text-[11px] text-primary uppercase tracking-wider">
                                    提交清单
                                </div>
                                <p class="text-xs text-muted-foreground">
                                    完成后可在此填写提交清单，列出产出物供 Reviewer 审查
                                </p>
                                <!-- 简化版：先实现直接填写 JSON -->
                                <div class="space-y-2">
                                    <Label for="submission-json">提交清单 (JSON)</Label>
                                    <textarea
                                        id="submission-json"
                                        v-model="submissionJson"
                                        class="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                                        placeholder='{"items":[{"name":"文件名","path":"/path","type":"file","description":"说明","status":"completed"}],"summary":"提交说明"}'
                                    />
                                </div>
                                <Button @click="handleSubmitWithJson" :disabled="!submissionJson">
                                    提交并携带清单
                                </Button>
                            </div>
```

- [ ] **Step 4: 验证 subTaskApi 已导入**

```bash
grep -n "subTaskApi" webui/src/views/TasksView.vue | head -5
```

应该已有 `import { subTaskApi } from '@/api/client'`。

- [ ] **Step 5: 添加相关的响应式变量和方法**

在 `<script setup>` 中添加：
```typescript
const submissionJson = ref('')

async function handleSubmitWithJson() {
    if (!submissionJson.value) return
    try {
        const submission = JSON.parse(submissionJson.value)
        // 校验格式
        if (!Array.isArray(submission.items)) {
            throw new Error("items 必须是数组")
        }
        if (submission.items.length > 50) {
            throw new Error("最多 50 项")
        }
        await subTaskApi.submit(selectedSubTask.value.id, submission)
        // 刷新详情
        await loadSubTaskDetail(selectedSubTask.value.id)
        submissionJson.value = ''
    } catch (e) {
        alert('JSON 格式错误: ' + e.message)
    }
}
```

- [ ] **Step 5: 验证前端编译**

```bash
cd webui && npm run build 2>&1 | tail -20
```

---

## Chunk 4: CLI 工具修改

### Task 7: 扩展 task-cli.py

**Files:**
- Modify: `skills/task-cli.py`

- [ ] **Step 1: 查看现有 submit 命令**

```bash
grep -n "def cmd_sub_task_submit" skills/task-cli.py
sed -n '391,400p' skills/task-cli.py
```

- [ ] **Step 2: 修改 submit 命令支持 --submission 参数**

替换 `cmd_sub_task_submit` 函数：
```python
def cmd_sub_task_submit(args):
    """提交成果（可选带提交清单）"""
    body = {}
    if args.submission:
        import json
        submission_data = args.submission
        if submission_data.startswith('@'):
            # 读取文件
            file_path = submission_data[1:]
            with open(file_path, 'r', encoding='utf-8') as f:
                body["submission"] = json.load(f)
        else:
            body["submission"] = json.loads(submission_data)

    data = _request("post", f"/sub-tasks/{args.id}/submit", args.key, json=body)
    if body.get("submission"):
        print(f"✅ 已提交: {data['name']}，含提交清单")
    else:
        print(f"✅ 已提交: {data['name']}，等待审查")
```

- [ ] **Step 3: 在 argparse 中添加 --submission 参数**

找到 `st submit` 子命令定义（约 line 817），修改：
```python
    p = st_sub.add_parser("submit", help="提交成果")
    p.add_argument("id", help="子任务 ID")
    p.add_argument("--submission", help="提交清单 JSON（可直接传入或 @文件路径）")
    p.set_defaults(func=cmd_sub_task_submit)
```

- [ ] **Step 4: 验证 CLI 语法**

```bash
python skills/task-cli.py --help 2>&1 | head -30
python skills/task-cli.py st submit --help 2>&1
```

---

## 执行顺序

1. Chunk 1: 后端数据库和 Schema
2. Chunk 2: 后端 API 和 Service
3. Chunk 3: 前端实现
4. Chunk 4: CLI 工具

每个 Chunk 完成后进行测试验证。
