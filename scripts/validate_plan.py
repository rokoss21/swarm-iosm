#!/usr/bin/env python3
"""
Validate a Swarm workflow plan for correctness.

Checks:
- All tasks have required fields
- Dependencies are valid (no cycles, no missing tasks)
- Phases are properly structured
- IOSM checks are assigned
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


class PlanValidator:
    def __init__(self, plan_path: str):
        self.plan_path = Path(plan_path)
        self.tasks: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        if not self.plan_path.exists():
            self.errors.append(f"Plan file not found: {self.plan_path}")
            return False

        content = self.plan_path.read_text(encoding='utf-8')

        self._parse_tasks(content)
        self._check_dependencies()
        self._check_required_fields()
        self._check_iosm_gates()
        self._detect_cycles()

        return len(self.errors) == 0

    def _parse_tasks(self, content: str):
        """Extract tasks from markdown plan."""
        # Pattern: ### Task T01: Title
        task_pattern = re.compile(
            r'### Task (T\d+): (.+?)$\n(.*?)(?=### Task|## |$)',
            re.MULTILINE | re.DOTALL
        )

        for match in task_pattern.finditer(content):
            task_id = match.group(1)
            title = match.group(2).strip()
            body = match.group(3)

            self.tasks[task_id] = {
                'id': task_id,
                'title': title,
                'body': body,
                'owner_role': self._extract_field(body, 'Owner role'),
                'depends_on': self._extract_dependencies(body),
                'status': self._extract_field(body, 'Status'),
                'iosm_checks': self._extract_field(body, 'IOSM checks'),
                'acceptance': self._extract_field(body, 'Acceptance'),
                'artifacts': self._extract_field(body, 'Artifacts'),
            }

    def _extract_field(self, text: str, field: str) -> str:
        """Extract a field value from task body."""
        pattern = re.compile(rf'- \*\*{field}:\*\* (.+?)$', re.MULTILINE)
        match = pattern.search(text)
        return match.group(1).strip() if match else ''

    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract dependency task IDs."""
        pattern = re.compile(r'- \*\*Depends on:\*\* (.+?)$', re.MULTILINE)
        match = pattern.search(text)
        if not match:
            return []

        deps_text = match.group(1).strip()
        if deps_text.lower() in ['none', 'n/a', '-']:
            return []

        # Extract task IDs like T01, T02
        return re.findall(r'T\d+', deps_text)

    def _check_dependencies(self):
        """Check that all dependencies reference valid tasks."""
        all_task_ids = set(self.tasks.keys())

        for task_id, task in self.tasks.items():
            for dep in task['depends_on']:
                if dep not in all_task_ids:
                    self.errors.append(
                        f"Task {task_id} depends on non-existent task {dep}"
                    )

    def _check_required_fields(self):
        """Check that all tasks have required fields."""
        required_fields = ['owner_role', 'status', 'acceptance', 'artifacts']

        for task_id, task in self.tasks.items():
            for field in required_fields:
                if not task.get(field):
                    self.errors.append(
                        f"Task {task_id} missing required field: {field}"
                    )

            # Check status is valid
            valid_statuses = ['TODO', 'DOING', 'DONE', 'BLOCKED']
            status = task.get('status', '').upper()
            if status not in valid_statuses:
                self.warnings.append(
                    f"Task {task_id} has invalid status '{status}'. "
                    f"Should be one of: {', '.join(valid_statuses)}"
                )

    def _check_iosm_gates(self):
        """Check that IOSM gates are assigned appropriately."""
        valid_gates = ['Gate-I', 'Gate-O', 'Gate-S', 'Gate-M', 'N/A']

        for task_id, task in self.tasks.items():
            iosm = task.get('iosm_checks', '')
            if not iosm:
                self.warnings.append(
                    f"Task {task_id} has no IOSM checks assigned"
                )
                continue

            # Extract gate names
            mentioned_gates = [g for g in valid_gates if g in iosm]
            if not mentioned_gates and 'N/A' not in iosm:
                self.warnings.append(
                    f"Task {task_id} IOSM checks don't reference valid gates: {iosm}"
                )

    def _detect_cycles(self):
        """Detect circular dependencies."""
        def has_cycle_util(task_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep in self.tasks[task_id]['depends_on']:
                if dep not in visited:
                    if has_cycle_util(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        visited = set()
        rec_stack = set()

        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle_util(task_id, visited, rec_stack):
                    self.errors.append(
                        f"Circular dependency detected involving task {task_id}"
                    )

    def print_report(self):
        """Print validation report."""
        print(f"\n{'='*60}")
        print(f"Plan Validation Report: {self.plan_path.name}")
        print(f"{'='*60}\n")

        print(f"Tasks found: {len(self.tasks)}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ Plan is valid! No errors or warnings.")

        print(f"\n{'='*60}\n")

    def generate_dependency_graph(self) -> str:
        """Generate a simple text dependency graph."""
        lines = ["Dependency Graph:", ""]

        for task_id in sorted(self.tasks.keys()):
            task = self.tasks[task_id]
            deps = task['depends_on']

            if deps:
                dep_str = ', '.join(deps)
                lines.append(f"{task_id} → depends on → {dep_str}")
            else:
                lines.append(f"{task_id} → (no dependencies)")

        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_plan.py <path/to/plan.md>")
        sys.exit(1)

    plan_path = sys.argv[1]
    validator = PlanValidator(plan_path)

    is_valid = validator.validate()
    validator.print_report()

    if '--graph' in sys.argv:
        print(validator.generate_dependency_graph())

    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
