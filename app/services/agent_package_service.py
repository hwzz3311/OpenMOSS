"""
Agent Package 导出服务 — 生成 OpenClaw agent workspace 压缩包
"""
import io
import zipfile
from pathlib import Path

from app.services import prompt_service
from app.config import config

# ── 目录常量 ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]  # app/services → app → 项目根目录
AGENT_BUILDER_DIR = BASE_DIR / "agent-builder"
REFERENCES_DIR = AGENT_BUILDER_DIR / "references"


# ======================================================================
#  模板内容生成
# ======================================================================

def _get_template_content(filename: str) -> str:
    """读取 agent-builder 模板文件内容"""
    path = REFERENCES_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _generate_identity(agent_data: dict) -> str:
    """生成 IDENTITY.md"""
    name = agent_data.get("name", "Agent")
    role = agent_data.get("role", "")

    template = _get_template_content("templates.md")
    if not template:
        # 默认模板
        return f"""# IDENTITY.md

- **Name:** {name}
- **Creature:** AI assistant
- **Vibe:** Professional, direct, calm.
- **Emoji:** 🤖
- **Avatar:**
"""

    # 使用模板结构
    return f"""# IDENTITY.md

- **Name:** {name}
- **Creature:** AI assistant
- **Vibe:** Professional, direct, calm.
- **Emoji:** 🤖
- **Avatar:**
"""


def _generate_soul(agent_data: dict) -> str:
    """生成 SOUL.md"""
    template = _get_template_content("templates.md")
    # 使用模板中的 SOUL.md 结构
    return """# SOUL.md

## Core Truths

- Be genuinely helpful; no filler.
- Prefer verified actions over speculation.
- When uncertain, ask crisp clarifying questions.

## Boundaries (hard rules)

- Ask the user for explicit permission before any destructive/state-changing action (write/edit/delete/move, installs/updates, restarts, config changes).
- Ask before any outbound messages/emails/posts.
- Do not reveal private workspace contents in shared/group chats.

## Vibe

- Professional, direct, calm.
- Output should be concise by default.

## Operating stance

- Tool-first when correctness matters; otherwise answer-first with explicit uncertainty.
- Never hallucinate tool output; cite observations or file paths.
"""


def _generate_agents(agent_data: dict, full_prompt: str) -> str:
    """生成 AGENTS.md (填入完整提示词内容)"""
    template = _get_template_content("templates.md")

    # 使用模板结构 + 完整的 prompt 内容
    return f"""# AGENTS.md

## Session start

- Read `SOUL.md` and `USER.md`.
- Read today + yesterday in `memory/YYYY-MM-DD.md` if present.
- In private main sessions only: read `MEMORY.md` if present.

## Safety

- Ask before destructive/state-changing actions.
- Ask before sending outbound messages.
- Prefer `trash` over `rm`.
- Stop on CLI usage errors; run `--help` and correct.

## Memory workflow

- Daily log: `memory/YYYY-MM-DD.md` (raw session notes)
- Long-term: `MEMORY.md` (decisions, preferences, durable facts)

## Group chats

- You are a participant, not the user's voice.
- Reply only when mentioned or when value is high.

## Delegation

- Sub-agents may not get full persona files; keep essential safety rules here.

---

## Agent Prompt

{full_prompt}
"""


def _generate_user(agent_data: dict) -> str:
    """生成 USER.md"""
    return """# USER.md

- **Name:** User
- **What to call them:** User
- **Timezone:** Local
- **Notes:** Default user profile
"""


def _generate_heartbeat() -> str:
    """生成 HEARTBEAT.md (空)"""
    return """# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat runs.
# Add 1-5 short checklist items when you explicitly want periodic checks.
"""


def _generate_bootstrap(agent_data: dict) -> str:
    """生成 BOOTSTRAP.md"""
    role = agent_data.get("role", "")
    name = agent_data.get("name", "Agent")

    return f"""# BOOTSTRAP.md

## Agent Initialization

This file contains bootstrap instructions for the {name} agent.

### Role
- **Role:** {role}
- **Platform:** OpenMOSS

### Initialization Steps

1. Read IDENTITY.md for agent identity
2. Read SOUL.md for core principles and boundaries
3. Read AGENTS.md for operating instructions
4. Read USER.md for user profile
5. Check HEARTBEAT.md for periodic tasks
6. Initialize memory system if needed
"""


def _generate_tools(agent_data: dict) -> str:
    """生成 TOOLS.md"""
    role = agent_data.get("role", "")

    return f"""# TOOLS.md

## Available Tools

This file contains tool configurations and environment-specific notes for the {role} agent.

### Default Tools

- Task CLI: Interact with OpenMOSS task system
- File operations: Read, write, edit files
- Command execution: Run shell commands safely

### Tool Guidelines

- Always verify destructive commands with user
- Use `trash` instead of `rm` for safety
- Check tool documentation before use
"""


# ======================================================================
#  主导出函数
# ======================================================================

def generate_agent_package(slug: str) -> io.BytesIO:
    """
    生成 Agent 压缩包 (ZIP)

    Args:
        slug: Agent 标识名

    Returns:
        BytesIO: ZIP 文件流
    """
    # 获取 Agent 数据
    agent_data = prompt_service.get_agent(slug)
    if not agent_data:
        raise ValueError(f"Agent 提示词 '{slug}' 不存在")

    # 获取完整的 prompt 内容
    full_prompt = prompt_service.compose_prompt(slug)

    # 生成各个文件内容
    files = {
        "IDENTITY.md": _generate_identity(agent_data),
        "SOUL.md": _generate_soul(agent_data),
        "AGENTS.md": _generate_agents(agent_data, full_prompt),
        "USER.md": _generate_user(agent_data),
        "HEARTBEAT.md": _generate_heartbeat(),
        "BOOTSTRAP.md": _generate_bootstrap(agent_data),
        "TOOLS.md": _generate_tools(agent_data),
    }

    # 创建内存 ZIP
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 使用 slug 作为目录名
        folder = slug

        for filename, content in files.items():
            # 文件路径: {slug}/{filename}
            arcname = f"{folder}/{filename}"
            zf.writestr(arcname, content)

    # 回到文件开头
    buffer.seek(0)
    return buffer
