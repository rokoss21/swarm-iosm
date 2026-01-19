from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ErrorType(Enum):
    """Common error types in subagent execution"""
    PERMISSION_DENIED = "permission_denied"
    FILE_NOT_FOUND = "file_not_found"
    DEPENDENCY_MISSING = "dependency_missing"
    TEST_FAILED = "test_failed"
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    TYPE_ERROR = "type_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    MCP_TOOL_UNAVAILABLE = "mcp_tool_unavailable"
    UNKNOWN = "unknown"

@dataclass
class ErrorDiagnosis:
    """Structured error diagnosis with actionable fixes"""
    error_type: ErrorType
    file: Optional[str]
    reason: str
    suggested_fixes: List[str]
    retry_command: str
    severity: str = "medium"  # low, medium, high, critical

    def to_markdown(self, task_id: str) -> str:
        """Render as markdown report"""
        severity_emoji = {
            'low': '⚠️',
            'medium': '❌',
            'high': '🚨',
            'critical': '💥'
        }

        lines = [
            f"## {severity_emoji[self.severity]} Task {task_id} Failed — {self.error_type.value.replace('_', ' ').title()}",
            "",
        ]

        if self.file:
            lines.append(f"**File:** `{self.file}`")

        lines.extend([
            f"**Reason:** {self.reason}",
            "",
            "**Suggested fixes:**",
        ])

        for i, fix in enumerate(self.suggested_fixes, 1):
            lines.append(f"{i}. {fix}")

        lines.extend([
            "",
            "**How to retry:**",
            f"```",
            self.retry_command,
            f"```",
        ])

        return '\n'.join(lines)
