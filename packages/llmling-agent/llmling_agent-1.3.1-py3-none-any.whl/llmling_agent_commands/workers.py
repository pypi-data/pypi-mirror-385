"""Tool management commands."""

from __future__ import annotations

from slashed import Command, CommandContext, CommandError  # noqa: TC002
from slashed.completers import CallbackCompleter

from llmling_agent.agent.context import AgentContext  # noqa: TC001
from llmling_agent.log import get_logger
from llmling_agent_commands.completers import get_available_agents
from llmling_agent_commands.markdown_utils import format_table


logger = get_logger(__name__)


ADD_WORKER_HELP = """\
Add another agent as a worker tool.

Options:
  --reset-history    Clear worker's history before each run (default: true)
  --share-history   Pass current agent's message history (default: false)
  --share-context   Share context data between agents (default: false)

Examples:
  /add-worker specialist               # Basic worker
  /add-worker analyst --share-history  # Pass conversation history
  /add-worker helper --share-context   # Share context between agents
"""

REMOVE_WORKER_HELP = """\
Remove a worker tool from the current agent.

Examples:
  /remove-worker specialist  # Remove the specialist worker tool
"""

LIST_WORKERS_HELP = """\
List all registered worker tools and their settings.

Shows:
- Worker agent name
- Tool name
- Current settings (history/context sharing)
- Enabled/disabled status

Example: /list-workers
"""


async def add_worker_command(
    ctx: CommandContext[AgentContext],
    args: list[str],
    kwargs: dict[str, str],
):
    """Add another agent as a worker tool."""
    if not args:
        await ctx.output.print("**Usage:** `/add-worker <agent_name> [options]`")
        return

    worker_name = args[0]
    try:
        if not ctx.context.pool:
            msg = "No agent pool available"
            raise CommandError(msg)  # noqa: TRY301

        # Get worker agent from pool
        worker = ctx.context.pool.get_agent(worker_name)

        # Parse boolean flags with defaults
        reset_history = kwargs.get("reset_history", "true").lower() != "false"
        share_history = kwargs.get("share_history", "false").lower() == "true"
        share_context = kwargs.get("share_context", "false").lower() == "true"

        # Register worker
        tool_info = ctx.context.agent.tools.register_worker(
            worker,
            reset_history_on_run=reset_history,
            pass_message_history=share_history,
            share_context=share_context,
            parent=ctx.context.agent,
        )

        await ctx.output.print(
            f"✅ **Added agent** `{worker_name}` **as worker tool:** `{tool_info.name}`\n"
            f"🔧 **Tool enabled:** {tool_info.enabled}"
        )

    except KeyError as e:
        msg = f"Agent not found: {worker_name}"
        raise CommandError(msg) from e
    except Exception as e:
        msg = f"Failed to add worker: {e}"
        raise CommandError(msg) from e


async def remove_worker_command(
    ctx: CommandContext[AgentContext],
    args: list[str],
    kwargs: dict[str, str],
):
    """Remove a worker tool."""
    if not args:
        await ctx.output.print("**Usage:** `/remove-worker <worker_name>`")
        return

    worker_name = args[0]
    tool_name = f"ask_{worker_name}"  # Match the naming in to_tool

    try:
        if tool_name not in ctx.context.agent.tools:
            msg = f"No worker tool found for agent: {worker_name}"
            raise CommandError(msg)  # noqa: TRY301

        # Check if it's actually a worker tool
        tool_info = ctx.context.agent.tools[tool_name]
        if tool_info.source != "agent":
            msg = f"{tool_name} is not a worker tool"
            raise CommandError(msg)  # noqa: TRY301

        # Remove the tool
        del ctx.context.agent.tools[tool_name]
        await ctx.output.print(f"🗑️ **Removed worker tool:** `{tool_name}`")

    except Exception as e:
        msg = f"Failed to remove worker: {e}"
        raise CommandError(msg) from e


async def list_workers_command(
    ctx: CommandContext[AgentContext],
    args: list[str],
    kwargs: dict[str, str],
):
    """List all worker tools."""
    # Filter tools by source="agent"
    worker_tools = [i for i in ctx.context.agent.tools.values() if i.source == "agent"]

    if not worker_tools:
        await ctx.output.print("ℹ️ **No worker tools registered**")  #  noqa: RUF001
        return

    rows = []
    for tool_info in worker_tools:
        # Extract settings from metadata
        agent_name = tool_info.metadata.get("agent", "unknown")
        rows.append({
            "Status": "✅" if tool_info.enabled else "❌",
            "Agent": agent_name,
            "Tool": tool_info.name,
            "Description": tool_info.description or "",
        })

    headers = ["Status", "Agent", "Tool", "Description"]
    table = format_table(headers, rows)
    await ctx.output.print(f"## 👥 Registered Workers\n\n{table}")


list_workers_cmd = Command(
    name="list-workers",
    description="List registered worker tools",
    execute_func=list_workers_command,
    help_text=LIST_WORKERS_HELP,
    category="tools",
)

remove_worker_cmd = Command(
    name="remove-worker",
    description="Remove a worker tool",
    execute_func=remove_worker_command,
    usage="<worker_name>",
    help_text=REMOVE_WORKER_HELP,
    category="tools",
    completer=CallbackCompleter(get_available_agents),
)


add_worker_cmd = Command(
    name="add-worker",
    description="Add another agent as a worker tool",
    execute_func=add_worker_command,
    usage="<agent_name> [--reset-history false] [--share-history] [--share-context]",
    help_text=ADD_WORKER_HELP,
    category="tools",
    completer=CallbackCompleter(get_available_agents),
)
