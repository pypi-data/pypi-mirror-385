#!/usr/bin/env python3
"""
MCP Server for Flow Framework

Model Context Protocol server that provides Flow development methodology tools.

AUTO-GENERATED - DO NOT EDIT DIRECTLY
Generated from framework/SLASH_COMMANDS.md metadata
"""

import os
import shutil
from pathlib import Path
from typing import Any, cast
from fastmcp import FastMCP

from flow_core import (
    find_plan_file,
    read_plan,
    write_plan,
    extract_dashboard,
    update_dashboard_timestamp,
    find_current_phase,
    find_current_task,
    find_current_iteration,
    format_success_response,
    format_error_response,
    PlanNotFoundError,
    FlowError,
)

# ============== INITIALIZATION ==============

mcp = FastMCP("Flow")

# ============== SPECIAL MCP TOOL: flow_init ==============

@mcp.tool()
def flow_init(create_slash_commands: bool = True) -> dict[str, Any]:
    """
    Initialize Flow framework in current project.

    Creates .flow/ directory with framework documentation and optionally
    .claude/commands/ with slash commands for Claude Code users.

    Args:
        create_slash_commands: Create .claude/commands/ slash commands (default: True).
                              Set to False if not using Claude Code.

    Returns:
        Initialization status and next steps
    """
    try:
        # Get framework files from package installation
        package_dir = Path(__file__).parent
        framework_source = package_dir / "framework"

        # Verify framework files exist
        if not framework_source.exists():
            return format_error_response(
                "flow-init",
                "Framework files not found in package",
                f"Expected framework files at: {framework_source}"
            )

        # Create .flow/ directory
        flow_dir = Path(".flow")
        flow_dir.mkdir(exist_ok=True)

        # Copy framework documentation
        docs_copied = []
        for doc in ["DEVELOPMENT_FRAMEWORK.md", "EXAMPLE_PLAN.md"]:
            src = framework_source / doc
            dest = flow_dir / doc
            if src.exists():
                shutil.copy(src, dest)
                docs_copied.append(doc)

        # Optionally create slash commands
        commands_created = 0
        if create_slash_commands:
            commands_dir = Path(".claude/commands")
            commands_dir.mkdir(parents=True, exist_ok=True)

            # Extract commands from SLASH_COMMANDS.md
            slash_commands_file = framework_source / "SLASH_COMMANDS.md"
            if slash_commands_file.exists():
                commands_created = extract_slash_commands(
                    slash_commands_file,
                    commands_dir
                )

        # Generate output report
        output = f"""# Flow Framework Initialized ✅

## What was created:

### .flow/ Directory
"""
        for doc in docs_copied:
            output += f"- ✅ {doc}\n"

        if create_slash_commands:
            output += f"\n### .claude/commands/ Directory\n"
            output += f"- ✅ {commands_created} slash commands extracted\n"
        else:
            output += "\n### Slash Commands\n"
            output += "- ⏭️  Skipped (create_slash_commands=False)\n"

        output += """

## Next Steps

1. **Create your first plan**: Run `flow_blueprint()` to create .flow/PLAN.md
2. **Or migrate existing docs**: Run `flow_migrate()` if you have existing planning docs

## Available Tools

Run `flow_status()` anytime to see where you are in the development process.
"""

        return format_success_response(
            "flow-init",
            f"Flow framework initialized (.flow/ + {commands_created if create_slash_commands else 0} commands)",
            output,
            "Run flow_blueprint() to create your first development plan"
        )

    except Exception as e:
        return format_error_response(
            "flow-init",
            "Failed to initialize Flow framework",
            str(e)
        )


def extract_slash_commands(slash_commands_file: Path, output_dir: Path) -> int:
    """
    Extract slash commands from SLASH_COMMANDS.md to .claude/commands/

    Args:
        slash_commands_file: Path to SLASH_COMMANDS.md
        output_dir: Directory to write command files

    Returns:
        Number of commands extracted
    """
    content = slash_commands_file.read_text()

    # Find all command sections (## /flow-...)
    import re
    command_pattern = r"## (/flow-[\w-]+)\s*\n.*?\*\*File\*\*: `([\w-]+\.md)`\s*\n```markdown\n(.*?)```"
    matches = re.findall(command_pattern, content, re.DOTALL)

    count = 0
    for command_name, filename, command_content in matches:
        command_file = output_dir / filename
        command_file.write_text(command_content)
        count += 1

    return count


# ============== AUTO-GENERATED MCP TOOLS ==============

@mcp.tool()
def flow_blueprint(project_description: str) -> dict[str, Any]:
    """
    Create new .flow/PLAN.md for a feature/project from scratch

    Args:
        project_description: Rich description of the feature/project including requirements, constraints, references, and testing methodology

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-blueprint",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-blueprint\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-blueprint",
                "Command instructions not found",
                f"Could not find /flow-blueprint in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-blueprint

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-blueprint",
            "Instructions retrieved",
            output,
            ""
        )

    except Exception as e:
        return format_error_response(
            "/flow-blueprint",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_migrate(existing_file_path: str = "") -> dict[str, Any]:
    """
    Migrate existing PRD/PLAN/TODO to Flow's .flow/PLAN.md format

    Args:
        existing_file_path: Path to existing plan file (auto-discovers if not provided)

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-migrate",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-migrate\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-migrate",
                "Command instructions not found",
                f"Could not find /flow-migrate in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-migrate

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-migrate",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-migrate",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_plan_update() -> dict[str, Any]:
    """
    Update existing plan to match latest Flow framework structure

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-plan-update",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-plan-update\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-plan-update",
                "Command instructions not found",
                f"Could not find /flow-plan-update in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-plan-update

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-plan-update",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-plan-update",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_phase_add(phase_name: str, phase_description: str = "") -> dict[str, Any]:
    """
    Add a new phase to the development plan

    Args:
        phase_name: Name of the phase to add
        phase_description: Optional description of the phase

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-phase-add",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-phase-add\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-phase-add",
                "Command instructions not found",
                f"Could not find /flow-phase-add in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-phase-add

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-phase-add",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-phase-add",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_phase_start() -> dict[str, Any]:
    """
    Mark current phase as in progress

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-phase-start",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-phase-start\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-phase-start",
                "Command instructions not found",
                f"Could not find /flow-phase-start in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-phase-start

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-phase-start",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-phase-start",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_phase_complete() -> dict[str, Any]:
    """
    Mark current phase as complete

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-phase-complete",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-phase-complete\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-phase-complete",
                "Command instructions not found",
                f"Could not find /flow-phase-complete in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-phase-complete

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-phase-complete",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-phase-complete",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_task_add(task_name: str, task_description: str = "", task_purpose: str = "") -> dict[str, Any]:
    """
    Add a new task under the current phase

    Args:
        task_name: Name of the task to add
        task_description: Optional description of the task
        task_purpose: Optional purpose statement for the task

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-task-add",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-task-add\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-task-add",
                "Command instructions not found",
                f"Could not find /flow-task-add in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-task-add

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-task-add",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-task-add",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_task_start() -> dict[str, Any]:
    """
    Mark current task as in progress

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-task-start",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-task-start\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-task-start",
                "Command instructions not found",
                f"Could not find /flow-task-start in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-task-start

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-task-start",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-task-start",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_task_complete() -> dict[str, Any]:
    """
    Mark current task as complete

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-task-complete",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-task-complete\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-task-complete",
                "Command instructions not found",
                f"Could not find /flow-task-complete in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-task-complete

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-task-complete",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-task-complete",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_iteration_add(iteration_name: str, iteration_description: str = "") -> dict[str, Any]:
    """
    Add a new iteration under the current task

    Args:
        iteration_name: Name/goal of the iteration to add
        iteration_description: Optional description of the iteration

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-iteration-add",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-iteration-add\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-iteration-add",
                "Command instructions not found",
                f"Could not find /flow-iteration-add in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-iteration-add

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-iteration-add",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-iteration-add",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_brainstorm_start(topics: str = "") -> dict[str, Any]:
    """
    Start brainstorming session with user-provided topics

    Args:
        topics: Topics to discuss (prompts if not provided)

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-brainstorm-start",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-brainstorm-start\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-brainstorm-start",
                "Command instructions not found",
                f"Could not find /flow-brainstorm-start in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-brainstorm-start

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-brainstorm-start",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-brainstorm-start",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_brainstorm_subject(subject_text: str) -> dict[str, Any]:
    """
    Add a subject to discuss in brainstorming

    Args:
        subject_text: Subject to add to discussion

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-brainstorm-subject",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-brainstorm-subject\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-brainstorm-subject",
                "Command instructions not found",
                f"Could not find /flow-brainstorm-subject in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-brainstorm-subject

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-brainstorm-subject",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-brainstorm-subject",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_brainstorm_review() -> dict[str, Any]:
    """
    Review all resolved subjects, suggest follow-up work

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-brainstorm-review",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-brainstorm-review\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-brainstorm-review",
                "Command instructions not found",
                f"Could not find /flow-brainstorm-review in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-brainstorm-review

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-brainstorm-review",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-brainstorm-review",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_brainstorm_complete() -> dict[str, Any]:
    """
    Complete brainstorming and generate action items

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-brainstorm-complete",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-brainstorm-complete\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-brainstorm-complete",
                "Command instructions not found",
                f"Could not find /flow-brainstorm-complete in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-brainstorm-complete

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-brainstorm-complete",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-brainstorm-complete",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_implement_start() -> dict[str, Any]:
    """
    Begin implementation of current iteration

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-implement-start",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-implement-start\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-implement-start",
                "Command instructions not found",
                f"Could not find /flow-implement-start in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-implement-start

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-implement-start",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-implement-start",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_implement_complete() -> dict[str, Any]:
    """
    Mark current iteration as complete

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-implement-complete",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-implement-complete\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-implement-complete",
                "Command instructions not found",
                f"Could not find /flow-implement-complete in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-implement-complete

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-implement-complete",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-implement-complete",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_status() -> dict[str, Any]:
    """
    Show current position and verify plan consistency

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-status",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-status\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-status",
                "Command instructions not found",
                f"Could not find /flow-status in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-status

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-status",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-status",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_summarize() -> dict[str, Any]:
    """
    Generate summary of all phases/tasks/iterations

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-summarize",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-summarize\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-summarize",
                "Command instructions not found",
                f"Could not find /flow-summarize in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-summarize

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-summarize",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-summarize",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_next_subject() -> dict[str, Any]:
    """
    Discuss next subject, capture decision, and mark resolved

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-next-subject",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-next-subject\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-next-subject",
                "Command instructions not found",
                f"Could not find /flow-next-subject in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-next-subject

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-next-subject",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-next-subject",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_next_iteration() -> dict[str, Any]:
    """
    Show next iteration details

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-next-iteration",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-next-iteration\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-next-iteration",
                "Command instructions not found",
                f"Could not find /flow-next-iteration in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-next-iteration

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-next-iteration",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-next-iteration",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_next() -> dict[str, Any]:
    """
    Smart helper - suggests next action based on current context

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-next",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-next\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-next",
                "Command instructions not found",
                f"Could not find /flow-next in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-next

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-next",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-next",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_rollback() -> dict[str, Any]:
    """
    Undo last plan change

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-rollback",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-rollback\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-rollback",
                "Command instructions not found",
                f"Could not find /flow-rollback in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-rollback

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-rollback",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-rollback",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_verify_plan() -> dict[str, Any]:
    """
    Verify plan file matches actual codebase state

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-verify-plan",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-verify-plan\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-verify-plan",
                "Command instructions not found",
                f"Could not find /flow-verify-plan in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-verify-plan

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-verify-plan",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-verify-plan",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_compact() -> dict[str, Any]:
    """
    No description available

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-compact",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-compact\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-compact",
                "Command instructions not found",
                f"Could not find /flow-compact in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-compact

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-compact",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-compact",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_plan_split() -> dict[str, Any]:
    """
    Archive old completed tasks to reduce PLAN.md size

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-plan-split",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-plan-split\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-plan-split",
                "Command instructions not found",
                f"Could not find /flow-plan-split in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-plan-split

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-plan-split",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-plan-split",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_backlog_add(task_numbers: str) -> dict[str, Any]:
    """
    Move task(s) to backlog to reduce active plan clutter

    Args:
        task_numbers: Task number(s) to move to backlog (e.g. '14' or '14-22')

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-backlog-add",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-backlog-add\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-backlog-add",
                "Command instructions not found",
                f"Could not find /flow-backlog-add in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-backlog-add

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-backlog-add",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-backlog-add",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_backlog_view() -> dict[str, Any]:
    """
    Show backlog contents (tasks waiting)

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-backlog-view",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-backlog-view\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-backlog-view",
                "Command instructions not found",
                f"Could not find /flow-backlog-view in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-backlog-view

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-backlog-view",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-backlog-view",
            "Failed to retrieve command instructions",
            str(e)
        )


@mcp.tool()
def flow_backlog_pull(task_number: str, position: str = "") -> dict[str, Any]:
    """
    Pull task from backlog back into active plan

    Args:
        task_number: Task number to pull from backlog
        position: Optional positioning instruction

    Returns:
        Status response with operation result
    """
    try:
        # Read slash command instructions from bundled SLASH_COMMANDS.md
        package_dir = Path(__file__).parent
        slash_commands_file = package_dir / "framework" / "SLASH_COMMANDS.md"

        if not slash_commands_file.exists():
            return format_error_response(
                "/flow-backlog-pull",
                "SLASH_COMMANDS.md not found",
                f"Expected at: {slash_commands_file}"
            )

        # Extract command instructions
        content = slash_commands_file.read_text()
        import re
        pattern = r"## /flow-backlog-pull\s*\n.*?```markdown\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return format_error_response(
                "/flow-backlog-pull",
                "Command instructions not found",
                f"Could not find /flow-backlog-pull in SLASH_COMMANDS.md"
            )

        instructions = match.group(1).strip()

        # Extract dashboard if plan exists
        dashboard = None
        try:
            plan_path = find_plan_file()
            plan_content = read_plan(plan_path)
            dashboard = extract_dashboard(plan_content)
        except PlanNotFoundError:
            pass  # Dashboard optional for instruction-only commands

        # Return instructions as structured guidance for LLM to execute
        output = f"""# /flow-backlog-pull

## Instructions

{instructions}
        """

        return format_success_response(
            "/flow-backlog-pull",
            "Instructions retrieved",
            output,
            "",
            dashboard
        )

    except Exception as e:
        return format_error_response(
            "/flow-backlog-pull",
            "Failed to retrieve command instructions",
            str(e)
        )


# ============== ENTRY POINT ==============

def main():
    """Entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
