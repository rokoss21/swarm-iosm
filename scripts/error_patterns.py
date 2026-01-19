import re
from typing import Optional
from errors import ErrorType, ErrorDiagnosis

ERROR_PATTERNS = [
    # Permission errors
    {
        'pattern': r'(permission denied|EACCES|not permitted)',
        'type': ErrorType.PERMISSION_DENIED,
        'extract_file': r'permission denied[:\s]+["\']?([^"\'\n]+)["\']?',
        'reason_template': "Permission denied accessing {file}",
        'fixes': [
            "Check file/directory permissions: ls -la {file}",
            "Run with elevated permissions (if safe): chmod +x {file}",
            "Mark task as foreground for manual approval",
        ]
    },

    # File not found
    {
        'pattern': r'(no such file|cannot find|ENOENT|FileNotFoundError)',
        'type': ErrorType.FILE_NOT_FOUND,
        'extract_file': r"['\"]([^'\"]+)['\"]",
        'reason_template': "File not found: {file}",
        'fixes': [
            "Verify file path exists",
            "Check if file was created by dependency task",
            "Review task 'Touches' field — may be missing",
        ]
    },

    # Module import errors
    {
        'pattern': r'(ModuleNotFoundError|ImportError|No module named)',
        'type': ErrorType.IMPORT_ERROR,
        'extract_file': r"No module named ['\"]([^'\"]+)['\"]",
        'reason_template': "Missing Python module: {file}",
        'fixes': [
            "Install module: pip install {file}",
            "Check if in requirements.txt",
            "Activate virtual environment",
        ]
    },

    # Test failures
    {
        'pattern': r'(\d+) failed.*tests?',
        'type': ErrorType.TEST_FAILED,
        'extract_file': r'(test_\w+\.py)',
        'reason_template': "Tests failing in {file}",
        'fixes': [
            "Review test output for specific failures",
            "Run tests locally: pytest {file} -v",
            "Decision needed: Fix code or update tests?",
        ]
    },

    # MCP tool unavailable (background mode)
    {
        'pattern': r'(MCP.*not available|tool not found.*background)',
        'type': ErrorType.MCP_TOOL_UNAVAILABLE,
        'extract_file': None,
        'reason_template': "MCP tools unavailable in background mode",
        'fixes': [
            "Mark task as foreground: needs_user_input: true",
            "Avoid MCP tools in background tasks",
            "Use standard tools only (Read, Write, Bash)",
        ]
    },

    # Timeout
    {
        'pattern': r'(timeout|timed out|TimeoutError)',
        'type': ErrorType.TIMEOUT,
        'extract_file': None,
        'reason_template': "Task exceeded time limit",
        'fixes': [
            "Increase effort estimate in plan.md",
            "Break into smaller subtasks",
            "Retry with --foreground (no timeout)",
        ]
    },
]

def diagnose_error(error_text: str, task_id: str) -> Optional[ErrorDiagnosis]:
    """Match error text against patterns and return diagnosis"""
    for pattern_def in ERROR_PATTERNS:
        match = re.search(pattern_def['pattern'], error_text, re.IGNORECASE)
        if match:
            # Extract file if pattern exists
            file = None
            if pattern_def['extract_file']:
                file_match = re.search(pattern_def['extract_file'], error_text, re.IGNORECASE)
                if file_match:
                    file = file_match.group(1)

            # Format reason
            reason = pattern_def['reason_template'].format(
                file=file or "(unknown)"
            )

            # Format fixes
            fixes = [
                fix.format(file=file or "(unknown)")
                for fix in pattern_def['fixes']
            ]

            # Generate retry command
            retry_cmd = f"/swarm-iosm retry {task_id}"
            if pattern_def['type'] in [ErrorType.MCP_TOOL_UNAVAILABLE, ErrorType.PERMISSION_DENIED]:
                retry_cmd += " --foreground"

            return ErrorDiagnosis(
                error_type=pattern_def['type'],
                file=file,
                reason=reason,
                suggested_fixes=fixes,
                retry_command=retry_cmd,
                severity='high' if 'critical' in error_text.lower() else 'medium'
            )

    # Unknown error
    return ErrorDiagnosis(
        error_type=ErrorType.UNKNOWN,
        file=None,
        reason="Unknown error occurred",
        suggested_fixes=[
            "Review full error output in task report",
            "Check subagent logs for details",
            "Retry with --foreground for interactive debugging",
        ],
        retry_command=f"/swarm-iosm retry {task_id} --foreground",
        severity='medium'
    )
