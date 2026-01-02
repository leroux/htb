#!/usr/bin/env python3
"""
Convert FlowCoder workflows to Claude Code skills

Translates FlowCoder JSON workflows into Claude skills (markdown)
with embedded flowchart structure that Claude can navigate autonomously.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_workflow(filepath: Path) -> Dict:
    """Load FlowCoder workflow JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_block_by_id(workflow: Dict, block_id: str) -> Optional[Dict]:
    """Get block from workflow by ID"""
    blocks = workflow.get("flowchart", {}).get("blocks", {})
    return blocks.get(block_id)


def get_outgoing_connections(workflow: Dict, block_id: str) -> List[Dict]:
    """Get all connections leaving a block"""
    connections = workflow.get("flowchart", {}).get("connections", [])
    return [c for c in connections if c.get("source_block_id") == block_id]


def build_flow_graph(workflow: Dict) -> str:
    """Build ASCII flowchart representation"""
    flowchart = workflow.get("flowchart", {})
    start_id = flowchart.get("start_block_id")
    blocks = flowchart.get("blocks", {})
    connections = flowchart.get("connections", [])

    if not start_id:
        return "No start block found"

    lines = []
    visited = set()

    def render_block(block_id: str, indent: int = 0):
        if block_id in visited:
            lines.append("  " * indent + "↑ (loop back)")
            return

        visited.add(block_id)
        block = blocks.get(block_id)
        if not block:
            return

        block_type = block.get("type", "unknown")
        block_name = block.get("name", "Unnamed")

        # Format block display
        if block_type == "start":
            lines.append("  " * indent + "START")
        elif block_type == "end":
            lines.append("  " * indent + "END")
        elif block_type == "branch":
            condition = block.get("condition", "?")
            lines.append("  " * indent + f"BRANCH: {block_name} ({condition})")
        else:
            lines.append("  " * indent + f"[{block_type.upper()}] {block_name}")

        # Get outgoing connections
        out_conns = [c for c in connections if c.get("source_block_id") == block_id]

        if len(out_conns) == 0:
            return
        elif len(out_conns) == 1:
            lines.append("  " * indent + "  ↓")
            render_block(out_conns[0]["target_block_id"], indent)
        else:
            # Multiple paths (branch)
            true_conn = next((c for c in out_conns if c.get("is_true_path")), None)
            false_conn = next((c for c in out_conns if not c.get("is_true_path")), None)

            if true_conn:
                lines.append("  " * indent + "  ├─ TRUE →")
                render_block(true_conn["target_block_id"], indent + 1)

            if false_conn:
                lines.append("  " * indent + "  └─ FALSE →")
                render_block(false_conn["target_block_id"], indent + 1)

    render_block(start_id)
    return "\n".join(lines)


def extract_step_details(block: Dict, workflow: Dict) -> str:
    """Extract detailed information about a block/step"""
    block_type = block.get("type")
    name = block.get("name", "Unnamed")

    details = [f"### Step: {name}\n"]
    details.append(f"**Type:** {block_type}\n")

    if block_type == "prompt":
        prompt = block.get("prompt", "")
        # Truncate long prompts
        if len(prompt) > 300:
            prompt = prompt[:300] + "...\n\n(See full prompt in original workflow)"
        details.append(f"**Prompt:**\n```\n{prompt}\n```\n")

        output_schema = block.get("output_schema")
        if output_schema:
            details.append(f"**Expected Output:** Structured (JSON schema defined)\n")

    elif block_type == "bash":
        command = block.get("command", "")
        details.append(f"**Command:** `{command}`\n")

        if block.get("capture_output"):
            output_var = block.get("output_variable", "output")
            details.append(f"**Captures output to:** `{output_var}`\n")

    elif block_type == "branch":
        condition = block.get("condition", "")
        details.append(f"**Condition:** `{condition}`\n")
        details.append(f"**Branches:** TRUE path / FALSE path\n")

    elif block_type == "command":
        cmd_name = block.get("command_name", "")
        args = block.get("arguments", "")
        details.append(f"**Calls workflow:** `{cmd_name}`\n")
        if args:
            details.append(f"**Arguments:** `{args}`\n")

        if block.get("inherit_variables"):
            details.append(f"**Inherits variables:** Yes\n")
        if block.get("merge_output"):
            details.append(f"**Merges output:** Yes\n")

    elif block_type == "variable":
        var_name = block.get("variable_name", "")
        var_value = block.get("variable_value", "")
        var_type = block.get("variable_type", "string")
        details.append(f"**Sets variable:** `{var_name}` = `{var_value}` (type: {var_type})\n")

    return "".join(details)


def generate_skill(workflow: Dict) -> str:
    """Generate Claude skill markdown from workflow"""
    name = workflow.get("name", "unnamed")
    description = workflow.get("description", "No description")
    arguments = workflow.get("arguments", [])

    # Build argument hint
    arg_hint = " ".join([f"<{arg['name']}>" for arg in arguments])

    lines = [
        "---",
        f"description: {description}",
        "allowed-tools: \"*\"",
        "model: sonnet",
        f"argument-hint: {arg_hint}",
        "---\n",
        f"# {name.replace('-', ' ').title()}\n",
    ]

    # Add arguments documentation
    if arguments:
        lines.append("## Arguments\n")
        for arg in arguments:
            arg_name = arg.get("name", "")
            arg_desc = arg.get("description", "")
            required = " (required)" if arg.get("required") else " (optional)"
            lines.append(f"- **${len(lines) - 6} ({arg_name})**: {arg_desc}{required}")
        lines.append("\n")

    # Add flowchart
    lines.append("## Workflow Graph (Reference)\n")
    lines.append("```")
    lines.append(build_flow_graph(workflow))
    lines.append("```\n")

    # Add step details
    lines.append("## Step Details\n")
    lines.append("Below are the blocks/steps from the original workflow. Use these as a **guide**, not rigid instructions.\n")

    flowchart = workflow.get("flowchart", {})
    start_id = flowchart.get("start_block_id")
    blocks = flowchart.get("blocks", {})

    # Walk through blocks in execution order
    visited = set()

    def document_block(block_id: str):
        if block_id in visited:
            return
        visited.add(block_id)

        block = blocks.get(block_id)
        if not block or block.get("type") in ["start", "end"]:
            # Skip start/end documentation
            out_conns = get_outgoing_connections(workflow, block_id)
            for conn in out_conns:
                document_block(conn["target_block_id"])
            return

        lines.append(extract_step_details(block, workflow))

        # Recurse to next blocks
        out_conns = get_outgoing_connections(workflow, block_id)
        for conn in out_conns:
            document_block(conn["target_block_id"])

    if start_id:
        document_block(start_id)

    # Add guidance
    lines.append("\n---\n")
    lines.append("## Orchestration Guidance\n")
    lines.append("**You have full autonomy to:**")
    lines.append("- Skip steps that aren't needed")
    lines.append("- Repeat steps that require iteration")
    lines.append("- Modify approach based on results")
    lines.append("- Make intelligent decisions about flow\n")
    lines.append("**Use the workflow above as a reference guide, not a rigid script.**\n")
    lines.append("**Your goal:** Complete the objective efficiently.\n")
    lines.append("**Your advantage:** Context awareness and intelligent decision-making.\n")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 flowcoder_to_skill.py <workflow.json> [output.md]")
        print()
        print("Converts a FlowCoder workflow to a Claude Code skill")
        print()
        print("Example:")
        print("  python3 flowcoder_to_skill.py flowcoder/commands/htb-recon.json .claude/commands/htb-recon-guided.md")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    # Load workflow
    workflow = load_workflow(input_file)

    # Determine output filename
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        # Default: same name with -guided suffix in .claude/commands/
        base_name = input_file.stem
        output_file = Path(f".claude/commands/{base_name}-guided.md")

    # Generate skill
    skill_content = generate_skill(workflow)

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(skill_content)

    print("=" * 70)
    print(f"Converted FlowCoder workflow to Claude skill")
    print("=" * 70)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    print("Usage:")
    print(f"  /htb-recon-guided <args>")
    print()
    print("The skill includes:")
    print("  - ASCII flowchart for reference")
    print("  - Step details from each block")
    print("  - Guidance for autonomous execution")
    print()
    print("Claude will use the workflow as a guide but make intelligent")
    print("decisions about execution order, skipping, and iteration.")
    print("=" * 70)


if __name__ == "__main__":
    main()
