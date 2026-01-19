#!/usr/bin/env python3
"""
Error Parsing Module for Swarm-IOSM (v1.2)

Parses error sections from subagent reports and generates diagnoses.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Import error classes
try:
    from .errors import ErrorDiagnosis
    from .error_patterns import diagnose_error
except ImportError:
    # For standalone testing
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from errors import ErrorDiagnosis
    from error_patterns import diagnose_error


def parse_subagent_errors(report_path: Path, task_id: str) -> List[ErrorDiagnosis]:
    """Extract errors from subagent report and diagnose them.

    Args:
        report_path: Path to subagent_report.md
        task_id: Task identifier (e.g., "T04")

    Returns:
        List of ErrorDiagnosis objects (empty if no errors)
    """
    if not report_path.exists():
        return []

    try:
        content = report_path.read_text(encoding='utf-8')
    except Exception:
        return []

    # Find "Errors Encountered section (capture until end or next header)
    errors_section = re.search(
        r'## Errors Encountered\s*\n([\s\S]*?)(?=\n##[^\n]|$)',
        content,
        re.DOTALL
    )

    if not errors_section:
        return []

    section_text = errors_section.group(1)

    # Check for "No errors"
    if re.search(r'no errors? encountered', section_text, re.IGNORECASE):
        return []

    # Extract individual errors by splitting on E-XX headers
    errors_list = []
    for error_match in re.finditer(r'### (E-\d+):', section_text, re.MULTILINE):
        errors_list.append(error_match.start())

    # Now extract each error block
    diagnoses = []
    for i, start_pos in enumerate(errors_list):
        # End position is either next error start or end of section
        end_pos = errors_list[i + 1] if i + 1 < len(errors_list) else len(section_text)

        error_content = section_text[start_pos:end_pos]

        # Extract components
        header = re.search(r'### (E-\d+): ([^\n]+)', error_content)
        if not header:
            continue

        error_id = header.group(1)
        error_title = header.group(2).strip()

        # Extract error message from code block
        error_msg_match = re.search(
            r'```\n(.*?)\n```',
            error_content,
            re.DOTALL
        )
        error_msg = error_msg_match.group(1) if error_msg_match else error_content

        # Extract file if present
        file_match = re.search(r'\*\*File:\*\*\s*`([^`]+)`', error_content)
        file = file_match.group(1) if file_match else None

        # Diagnose the error
        diagnosis = diagnose_error(error_msg, task_id)

        # Override file if found
        if file:
            diagnosis.file = file

        diagnoses.append(diagnosis)

    return diagnoses


def generate_error_summary(diagnoses: List[ErrorDiagnosis], task_id: str) -> str:
    """Generate markdown summary of all errors for a task.

    Args:
        diagnoses: List of error diagnoses
        task_id: Task identifier

    Returns:
        Markdown formatted error summary
    """
    if not diagnoses:
        return f"✅ Task {task_id}: No errors\n"

    lines = [
        f"❌ Task {task_id}: {len(diagnoses)} error(s)",
        "",
    ]

    for i, diag in enumerate(diagnoses, 1):
        lines.append(f"### Error {i}: {diag.error_type.value.replace('_', ' ').title()}")
        if diag.file:
            lines.append(f"**File:** `{diag.file}`")
        lines.append(f"**Reason:** {diag.reason}")
        lines.append("")
        lines.append("**Suggested fixes:**")
        for fix in diag.suggested_fixes:
            lines.append(f"- {fix}")
        lines.append("")
        lines.append("**Retry:**")
        lines.append(f"```")
        lines.append(diag.retry_command)
        lines.append(f"```")
        if i < len(diagnoses):
            lines.append("")

    return '\n'.join(lines)


def parse_all_track_errors(track_path: Path) -> Dict[str, List[ErrorDiagnosis]]:
    """Parse errors from all task reports in a track.

    Args:
        track_path: Path to track directory

    Returns:
        Dict mapping task_id to list of diagnoses
    """
    reports_dir = track_path / "reports"
    if not reports_dir.exists():
        return {}

    errors_by_task = {}

    for report_file in reports_dir.glob("*.md"):
        # Extract task ID from filename (T01.md -> T01)
        task_id = report_file.stem.upper()
        diagnoses = parse_subagent_errors(report_file, task_id)

        if diagnoses:
            errors_by_task[task_id] = diagnoses

    return errors_by_task


def generate_track_error_summary(track_path: Path) -> str:
    """Generate summary of all errors in a track.

    Args:
        track_path: Path to track directory

    Returns:
        Markdown formatted summary
    """
    errors_by_task = parse_all_track_errors(track_path)

    if not errors_by_task:
        return "✅ No errors in track\n"

    lines = [
        f"# Track Error Summary",
        f"**Track:** {track_path.name}",
        f"**Tasks with errors:** {len(errors_by_task)}",
        f"**Total errors:** {sum(len(d) for d in errors_by_task.values())}",
        "",
        "---",
        "",
    ]

    # Sort by task ID
    for task_id in sorted(errors_by_task.keys()):
        diagnoses = errors_by_task[task_id]
        lines.append(generate_error_summary(diagnoses, task_id))
        lines.append("")

    return '\n'.join(lines)


def main():
    """CLI for error parsing."""
    if len(sys.argv) < 2:
        print("Usage: python parse_errors.py <report_path|track_path> [--summary]")
        sys.exit(1)

    path = Path(sys.argv[1])
    summary_only = '--summary' in sys.argv

    if not path.exists():
        print(f"Error: Path not found: {path}")
        sys.exit(1)

    # Check if it's a track directory (has reports/ subfolder)
    if (path / "reports").exists():
        if summary_only:
            print(generate_track_error_summary(path))
        else:
            errors = parse_all_track_errors(path)
            for task_id in sorted(errors.keys()):
                print(f"\n{task_id}:")
                for diag in errors[task_id]:
                    print(f"  - {diag.error_type.value}: {diag.reason}")
    # Otherwise treat as single report
    elif path.is_file():
        task_id = path.stem.upper()
        diagnoses = parse_subagent_errors(path, task_id)
        print(generate_error_summary(diagnoses, task_id))
    else:
        print(f"Error: Not a valid track or report path: {path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
