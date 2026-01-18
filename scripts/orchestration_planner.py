#!/usr/bin/env python3
"""
Orchestration Planner for Swarm Workflow.

Analyzes plan.md and generates orchestration_plan.md with:
- Dependency graph
- Critical path
- Execution waves (parallel grouping)
- File conflict detection
- Background/foreground mode selection
- Time estimates (serial vs parallel)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: str
    title: str
    owner_role: str
    depends_on: List[str]
    touches: List[str]
    needs_user_input: bool
    effort: str
    status: str
    iosm_checks: str
    acceptance: str
    artifacts: str
    # v1.1 fields
    concurrency_class: str = 'write-local'  # read-only, write-local, write-shared
    discoveries_expected: str = ''
    auto_spawn_allowed: str = 'safe-only'


class OrchestrationPlanner:
    def __init__(self, plan_path: str):
        self.plan_path = Path(plan_path)
        self.tasks: Dict[str, Task] = {}
        self.graph: Dict[str, List[str]] = {}
        self.waves: List[List[str]] = []
        self.critical_path: List[str] = []

    def parse_plan(self):
        """Parse plan.md and extract tasks with new fields."""
        content = self.plan_path.read_text(encoding='utf-8')

        # Pattern for task sections: - [ ] **T##**: Title
        task_pattern = re.compile(
            r'- \[ \] \*\*([T\d]+)\*\*: (.+?)$\n(.*?)(?=- \[ \]|\Z)',
            re.MULTILINE | re.DOTALL
        )

        for match in task_pattern.finditer(content):
            task_id = match.group(1)
            title = match.group(2).strip()
            body = match.group(3)

            self.tasks[task_id] = Task(
                id=task_id,
                title=title,
                owner_role=self._extract_field(body, 'Owner role'),
                depends_on=self._extract_dependencies(body),
                touches=self._extract_list_field(body, 'Touches'),
                needs_user_input=self._extract_bool_field(body, 'Needs user input'),
                effort=self._extract_field(body, 'Effort'),
                status=self._extract_field(body, 'Status'),
                iosm_checks=self._extract_field(body, 'IOSM checks'),
                acceptance=self._extract_field(body, 'Acceptance'),
                artifacts=self._extract_field(body, 'Artifacts'),
                # v1.1 fields
                concurrency_class=self._extract_field(body, 'Concurrency class') or 'write-local',
                discoveries_expected=self._extract_field(body, 'Discoveries expected'),
                auto_spawn_allowed=self._extract_field(body, 'Auto-spawn allowed') or 'safe-only',
            )

    def _extract_field(self, text: str, field: str) -> str:
        """Extract single-value field."""
        pattern = re.compile(rf'- \*\*{field}:\*\* (.+?)$', re.MULTILINE)
        match = pattern.search(text)
        return match.group(1).strip() if match else ''

    def _extract_list_field(self, text: str, field: str) -> List[str]:
        """Extract list field (comma-separated)."""
        value = self._extract_field(text, field)
        if not value or value.lower() in ['none', 'n/a', '-']:
            return []
        # Split by comma, strip backticks and spaces
        items = [item.strip().strip('`').strip('[').strip(']') for item in value.split(',')]
        return [item for item in items if item and 'read-only' not in item.lower()]

    def _extract_bool_field(self, text: str, field: str) -> bool:
        """Extract boolean field."""
        value = self._extract_field(text, field).lower()
        return value in ['true', 'yes', '1']

    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract dependency task IDs."""
        deps_text = self._extract_field(text, 'Depends on')
        if deps_text.lower() in ['none', 'n/a', '-']:
            return []
        return re.findall(r'T\d+', deps_text)

    def build_dependency_graph(self):
        """Build adjacency list for task dependencies."""
        for task_id, task in self.tasks.items():
            self.graph[task_id] = task.depends_on

    def find_critical_path(self) -> Tuple[List[str], int]:
        """
        Find critical path (longest path by effort).
        Returns: (path as list of task IDs, total effort in minutes)
        """
        def effort_to_minutes(effort: str) -> int:
            effort = effort.upper()
            if 'S' in effort:
                return 30  # <1h
            elif 'M' in effort and 'MIN' not in effort:
                return 150  # 1-4h avg
            elif 'XL' in effort:
                return 720  # >12h avg
            elif 'L' in effort:
                return 480  # 4-12h avg
            # Try parse numbers
            if 'H' in effort:
                hours_match = re.search(r'(\d+)', effort)
                if hours_match:
                    return int(hours_match.group(1)) * 60
            if 'MIN' in effort:
                mins_match = re.search(r'(\d+)', effort)
                if mins_match:
                    return int(mins_match.group(1))
            return 120  # default

        # Topological sort + longest path
        def dfs_longest_path(task_id: str, memo: dict) -> Tuple[List[str], int]:
            if task_id in memo:
                return memo[task_id]

            task = self.tasks[task_id]
            task_effort = effort_to_minutes(task.effort)

            if not task.depends_on:
                result = ([task_id], task_effort)
            else:
                longest_subpath = ([], 0)
                for dep in task.depends_on:
                    if dep in self.tasks:  # Safety check
                        subpath, subeffort = dfs_longest_path(dep, memo)
                        if subeffort > longest_subpath[1]:
                            longest_subpath = (subpath, subeffort)

                result = (longest_subpath[0] + [task_id],
                         longest_subpath[1] + task_effort)

            memo[task_id] = result
            return result

        memo = {}
        all_paths = [dfs_longest_path(tid, memo) for tid in self.tasks]
        critical = max(all_paths, key=lambda x: x[1]) if all_paths else ([], 0)

        self.critical_path = critical[0]
        return critical

    def detect_file_conflicts(self, task_ids: List[str]) -> bool:
        """Check if any tasks in list have overlapping 'touches'."""
        all_touches = []
        for tid in task_ids:
            all_touches.extend(self.tasks[tid].touches)

        # Check for duplicates (simple exact match)
        return len(all_touches) != len(set(all_touches))

    def group_into_waves(self):
        """
        Group tasks into parallel execution waves.
        Wave N contains tasks where:
        - All dependencies are in waves 1..N-1
        - No file conflicts within the wave
        """
        remaining = set(self.tasks.keys())
        completed = set()

        while remaining:
            # Candidates: tasks with all deps satisfied
            candidates = [
                tid for tid in remaining
                if all(dep in completed or dep not in self.tasks for dep in self.tasks[tid].depends_on)
            ]

            if not candidates:
                # Circular dependency or error
                print(f"WARNING: Cannot schedule remaining tasks: {remaining}")
                break

            # Build wave without conflicts
            wave = []
            for tid in candidates:
                # Check if adding this task creates conflict
                if not self.detect_file_conflicts(wave + [tid]):
                    wave.append(tid)

            if not wave:
                # All candidates conflict, must do sequential
                wave = [candidates[0]]

            self.waves.append(wave)
            completed.update(wave)
            remaining -= set(wave)

    def choose_execution_mode(self, task_id: str) -> str:
        """Choose foreground or background based on task properties."""
        task = self.tasks[task_id]

        # Foreground if needs user input
        if task.needs_user_input:
            return "foreground"

        # Foreground if effort is Small (not worth backgrounding)
        if task.effort.upper().startswith('S'):
            return "foreground"

        # Background for M/L/XL without user input
        return "background"

    def estimate_times(self) -> Tuple[int, int]:
        """
        Estimate total time (minutes): serial vs parallel.
        Returns: (serial_time, parallel_time)
        """
        def effort_to_minutes(effort: str) -> int:
            effort = effort.upper()
            if 'S' in effort:
                return 30
            elif 'M' in effort and 'MIN' not in effort:
                return 150
            elif 'XL' in effort:
                return 720
            elif 'L' in effort:
                return 480
            if 'H' in effort:
                h_match = re.search(r'(\d+)', effort)
                if h_match:
                    return int(h_match.group(1)) * 60
            return 120

        # Serial: sum of all efforts
        serial = sum(effort_to_minutes(t.effort) for t in self.tasks.values())

        # Parallel: sum of max effort per wave
        parallel = 0
        for wave in self.waves:
            wave_efforts = [effort_to_minutes(self.tasks[tid].effort) for tid in wave]
            parallel += max(wave_efforts) if wave_efforts else 0

        return serial, parallel

    def classify_task_mode(self, task_id: str) -> str:
        """Classify task as background/foreground based on v1.1 rules."""
        task = self.tasks[task_id]

        # Foreground if needs user input
        if task.needs_user_input:
            return "foreground"

        # Foreground if effort is Small (not worth backgrounding)
        if task.effort.upper().startswith('S'):
            return "foreground"

        # read-only always safe for background
        if task.concurrency_class == 'read-only':
            return "background"

        # write-shared needs foreground for safety
        if task.concurrency_class == 'write-shared':
            return "foreground"

        # write-local with no user input -> background
        return "background"

    def get_ready_tasks(self, completed: Set[str], running: Set[str]) -> List[str]:
        """Get tasks ready to run (deps satisfied, not running/completed)."""
        ready = []
        for tid, task in self.tasks.items():
            if tid in completed or tid in running:
                continue
            deps_satisfied = all(
                dep in completed or dep not in self.tasks
                for dep in task.depends_on
            )
            if deps_satisfied:
                ready.append(tid)
        return ready

    def check_conflicts(self, task_id: str, locked_paths: Set[str]) -> bool:
        """Check if task conflicts with currently locked paths."""
        task = self.tasks[task_id]

        # read-only never conflicts
        if task.concurrency_class == 'read-only':
            return False

        # Check overlap with locked paths
        for touch in task.touches:
            if touch in locked_paths:
                return True
        return False

    def generate_continuous_dispatch_plan(self, output_path: str):
        """Generate continuous dispatch plan (v1.1 mode)."""
        self.parse_plan()
        self.build_dependency_graph()
        critical_path, critical_effort = self.find_critical_path()
        serial_time, parallel_time = self.estimate_times()

        lines = []
        track_id = self.plan_path.parent.name
        lines.append(f"# Continuous Dispatch Plan — {track_id}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("**Mode:** Continuous Scheduling (v1.1)")
        lines.append("**Strategy:** Dispatch immediately when READY, no wave barriers")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**Total tasks:** {len(self.tasks)}")
        lines.append(f"**Estimated time (serial):** {serial_time//60}h {serial_time%60}m")
        lines.append(f"**Estimated time (parallel):** {parallel_time//60}h {parallel_time%60}m")
        lines.append(f"**Critical path:** {' → '.join(critical_path)}")
        speedup = serial_time / parallel_time if parallel_time > 0 else 1
        lines.append(f"**Expected speedup:** ~{speedup:.1f}x")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Continuous Dispatch Rules
        lines.append("## Continuous Dispatch Rules")
        lines.append("")
        lines.append("1. **CollectReady:** Find tasks with all deps completed")
        lines.append("2. **ConflictCheck:** Verify no touches overlap with running tasks")
        lines.append("3. **Classify:** Determine background vs foreground")
        lines.append("4. **DispatchBatch:** Launch ALL ready tasks in SINGLE message")
        lines.append("5. **Monitor:** Check outputs, collect SpawnCandidates")
        lines.append("6. **AutoSpawn:** Create new tasks from discoveries")
        lines.append("7. **GateCheck:** Continue until Gate targets met")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Task Registry
        lines.append("## Task Registry")
        lines.append("")
        lines.append("| Task | Role | Concurrency | Mode | Effort | Deps | Touches |")
        lines.append("|------|------|-------------|------|--------|------|---------|")

        for tid in sorted(self.tasks.keys(), key=lambda x: int(x[1:])):
            task = self.tasks[tid]
            mode = self.classify_task_mode(tid)
            touches_display = ', '.join([f"`{t}`" for t in task.touches[:2]])
            if len(task.touches) > 2:
                touches_display += f" +{len(task.touches)-2}"
            deps_display = ', '.join(task.depends_on) if task.depends_on else '-'

            lines.append(
                f"| {tid} | {task.owner_role} | {task.concurrency_class} | "
                f"{'**FG**' if mode=='foreground' else 'BG'} | "
                f"{task.effort} | {deps_display} | {touches_display or '-'} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("")

        # Initial Ready Set
        lines.append("## Initial Ready Set")
        lines.append("")
        lines.append("Tasks ready at start (no dependencies):")
        lines.append("")

        initial_ready = self.get_ready_tasks(completed=set(), running=set())
        for tid in initial_ready:
            task = self.tasks[tid]
            mode = self.classify_task_mode(tid)
            lines.append(f"- **{tid}**: {task.title} ({mode})")

        lines.append("")
        lines.append("**Action:** Launch all in single message")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Lock Plan
        lines.append("## Lock Plan (Touches Conflict Matrix)")
        lines.append("")

        # Find tasks that share touches
        touches_to_tasks: Dict[str, List[str]] = {}
        for tid, task in self.tasks.items():
            if task.concurrency_class != 'read-only':
                for touch in task.touches:
                    if touch not in touches_to_tasks:
                        touches_to_tasks[touch] = []
                    touches_to_tasks[touch].append(tid)

        conflicts_found = False
        for touch, task_ids in touches_to_tasks.items():
            if len(task_ids) > 1:
                conflicts_found = True
                lines.append(f"- `{touch}`: {', '.join(task_ids)} — **sequential only**")

        if not conflicts_found:
            lines.append("No file conflicts detected. All write tasks can run in parallel.")

        lines.append("")
        lines.append("---")
        lines.append("")

        # SpawnCandidates Expectations
        lines.append("## Expected Discoveries (auto-spawn candidates)")
        lines.append("")
        lines.append("Based on `discoveries_expected` fields:")
        lines.append("")

        for tid, task in self.tasks.items():
            if task.discoveries_expected:
                lines.append(f"- **{tid}**: {task.discoveries_expected}")

        lines.append("")
        lines.append("**Auto-spawn rules:**")
        for tid, task in self.tasks.items():
            if task.auto_spawn_allowed:
                lines.append(f"- **{tid}**: {task.auto_spawn_allowed}")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Gate-Driven Continuation
        lines.append("## Gate-Driven Continuation")
        lines.append("")
        lines.append("Loop continues until Gate targets met (see plan.md).")
        lines.append("")
        lines.append("**Auto-spawn triggers:**")
        lines.append("- Gate-I gap → spawn clarity/duplication fixes")
        lines.append("- Gate-M gap → spawn module boundary fixes")
        lines.append("- Gate-O gap → spawn test/perf fixes")
        lines.append("")
        lines.append("**Stop conditions:**")
        lines.append("- All remaining tasks need user input")
        lines.append("- Critical SpawnCandidate found")
        lines.append("- Scope creep detected")
        lines.append("- Contradiction without policy")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Instructions
        lines.append("## Orchestrator Instructions")
        lines.append("")
        lines.append("```")
        lines.append("1. Initialize iosm_state.md")
        lines.append("2. Dispatch initial ready set (single message, parallel)")
        lines.append("3. LOOP:")
        lines.append("   a. Monitor running tasks (/bashes)")
        lines.append("   b. On task completion:")
        lines.append("      - Update iosm_state.md")
        lines.append("      - Read SpawnCandidates from report")
        lines.append("      - Auto-spawn eligible candidates")
        lines.append("      - Release touches locks")
        lines.append("      - Recalculate ready queue")
        lines.append("   c. Dispatch new ready tasks immediately")
        lines.append("   d. Check Gate targets")
        lines.append("   e. If gates met → exit loop")
        lines.append("   f. If all blocked on user → ask questions")
        lines.append("4. Generate final iosm_report.md")
        lines.append("```")
        lines.append("")

        # Write to file
        output = Path(output_path)
        output.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✅ Generated continuous dispatch plan: {output}")

    def generate_orchestration_plan(self, output_path: str):
        """Generate orchestration_plan.md file (wave-based, legacy mode)."""
        # Run all analysis
        self.parse_plan()
        self.build_dependency_graph()
        critical_path, critical_effort = self.find_critical_path()
        self.group_into_waves()
        serial_time, parallel_time = self.estimate_times()

        # Generate markdown
        lines = []
        track_id = self.plan_path.parent.name
        lines.append(f"# Orchestration Plan — {track_id}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("**Strategy:** Parallel waves with automatic conflict resolution")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"**Total tasks:** {len(self.tasks)}")
        lines.append(f"**Total waves:** {len(self.waves)}")
        lines.append(f"**Estimated time (serial):** {serial_time//60}h {serial_time%60}m")
        lines.append(f"**Estimated time (parallel):** {parallel_time//60}h {parallel_time%60}m")
        lines.append(f"**Critical path:** {' → '.join(critical_path)} ({critical_effort//60}h {critical_effort%60}m)")
        speedup = serial_time / parallel_time if parallel_time > 0 else 1
        lines.append(f"**Speedup factor:** ~{speedup:.1f}x")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Critical Path
        lines.append("## Critical Path")
        lines.append("")
        lines.append("```")
        if critical_path:
            path_str = " → ".join([
                f"{tid} ({self.tasks[tid].effort})"
                for tid in critical_path
            ])
            lines.append(path_str)
        lines.append(f"Total: {critical_effort//60}h {critical_effort%60}m (longest path)")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Waves
        for i, wave in enumerate(self.waves, 1):
            lines.append(f"### Wave {i}")
            lines.append("")

            # Determine if parallel
            if len(wave) > 1:
                lines.append(f"**Launch mode:** Parallel ({len(wave)} tasks, **launch in single message**)")
            else:
                lines.append("**Launch mode:** Sequential (single task)")
            lines.append("")

            # Table
            lines.append("| Task | Role | Mode | Effort | Touches | Conflicts |")
            lines.append("|------|------|------|--------|---------|-----------|")

            for tid in wave:
                task = self.tasks[tid]
                mode = self.choose_execution_mode(tid)
                touches_display = ', '.join([f"`{t}`" for t in task.touches[:2]])
                if len(task.touches) > 2:
                    touches_display += f" (+{len(task.touches)-2} more)"
                if not touches_display:
                    touches_display = "(none)"

                lines.append(
                    f"| {tid} | {task.owner_role} | "
                    f"{'**Foreground**' if mode=='foreground' else 'Background'} | "
                    f"{task.effort} | {touches_display} | None |"
                )

            lines.append("")
            lines.append("**Exit criteria:** All tasks complete or BLOCKED")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Write to file
        output = Path(output_path)
        output.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✅ Generated: {output}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python orchestration_planner.py <path/to/plan.md> [--validate|--generate|--continuous]")
        sys.exit(1)

    plan_path = sys.argv[1]

    if '--validate' in sys.argv:
        # Just validate fields
        planner = OrchestrationPlanner(plan_path)
        planner.parse_plan()

        missing = []
        warnings = []
        for tid, task in planner.tasks.items():
            if not task.touches:
                missing.append(f"{tid}: missing 'Touches'")
            if not task.effort:
                missing.append(f"{tid}: missing 'Effort'")
            # v1.1 warnings (not blocking)
            if not task.concurrency_class or task.concurrency_class == 'write-local':
                warnings.append(f"{tid}: using default concurrency_class='write-local'")

        if missing:
            print("❌ Validation failed:")
            for m in missing:
                print(f"  - {m}")
            sys.exit(1)
        else:
            print(f"✅ All {len(planner.tasks)} tasks have required fields (Touches, Needs user input, Effort)")
            if warnings:
                print(f"\n⚠️  Warnings (v1.1 fields):")
                for w in warnings[:5]:  # Limit to first 5
                    print(f"  - {w}")
                if len(warnings) > 5:
                    print(f"  ... and {len(warnings) - 5} more")

    elif '--continuous' in sys.argv:
        # Generate continuous dispatch plan (v1.1)
        planner = OrchestrationPlanner(plan_path)
        output_path = Path(plan_path).parent / "continuous_dispatch_plan.md"
        planner.generate_continuous_dispatch_plan(str(output_path))
        # Also generate iosm_state.md template
        iosm_state_path = Path(plan_path).parent / "iosm_state.md"
        if not iosm_state_path.exists():
            # Copy template
            template_dir = Path(__file__).parent.parent / "templates"
            template_path = template_dir / "iosm_state.md"
            if template_path.exists():
                import shutil
                shutil.copy(template_path, iosm_state_path)
                print(f"✅ Created iosm_state.md from template")
            else:
                print(f"⚠️  iosm_state.md template not found, create manually")

    elif '--generate' in sys.argv:
        # Generate wave-based orchestration plan (legacy mode)
        planner = OrchestrationPlanner(plan_path)
        output_path = Path(plan_path).parent / "orchestration_plan.md"
        planner.generate_orchestration_plan(str(output_path))
        print("ℹ️  Note: Consider using --continuous for v1.1 continuous dispatch mode")

    else:
        print("Usage:")
        print("  --validate   : Check plan.md has required fields")
        print("  --generate   : Generate wave-based orchestration_plan.md (legacy)")
        print("  --continuous : Generate continuous_dispatch_plan.md (v1.1 recommended)")
        sys.exit(1)


if __name__ == '__main__':
    main()
