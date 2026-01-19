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
from dataclasses import dataclass, field
from datetime import datetime


# Resource Constraints (v1.2)

@dataclass
class ResourceConstraints:
    """Resource limits for parallel execution (v1.2)"""
    max_parallel_background: int = 6
    max_parallel_foreground: int = 2
    max_total_parallel: int = 8
    token_budget_per_hour: int = 10_000_000  # 10M tokens/hour
    cost_limit_per_track: float = 10.00  # $10 USD


@dataclass
class Checkpoint:
    """Snapshot of orchestration state (v1.3)"""
    iteration: int
    timestamp: str
    completed_tasks: List[str]
    running_tasks: Dict[str, str]  # tid -> mode
    gate_scores: Dict[str, float]
    spawn_budget_remaining: int
    seen_dedup_keys: List[str]
    retry_counts: Dict[str, int]
    
    def save(self, path: Path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=2)
            
    @classmethod
    def load(cls, path: Path) -> 'Checkpoint':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(**data)


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
    # v1.2 fields
    model: str = 'auto'  # auto, haiku, sonnet, opus
    severity: str = 'medium'  # low, medium, high, critical
    is_on_critical_path: bool = False


# Model Selection & Cost Tracking (v1.2)

COST_TABLE = {
    'haiku': {
        'input': 0.25,   # $ per 1M tokens
        'output': 1.25,
    },
    'sonnet': {
        'input': 3.00,
        'output': 15.00,
    },
    'opus': {
        'input': 15.00,
        'output': 75.00,
    }
}

EFFORT_TO_TOKENS = {
    'S': 5000,    # Small tasks
    'M': 20000,   # Medium tasks
    'L': 50000,   # Large tasks
    'XL': 100000, # Extra large tasks
}

def select_model(task: Task) -> str:
    """
    Auto-select optimal model based on task properties.

    Rules:
    - read-only exploration → haiku (cheap)
    - needs user input (reasoning) → sonnet
    - security/critical → opus
    - default → sonnet
    """
    if task.model and task.model != 'auto':
        return task.model  # User-specified model

    # Read-only tasks → haiku (cheap exploration)
    if task.concurrency_class == 'read-only':
        return 'haiku'

    # Security-critical → opus
    if 'security' in task.owner_role.lower() or 'audit' in task.owner_role.lower():
        return 'opus'

    # Critical decisions → opus
    if 'architect' in task.owner_role.lower() and task.needs_user_input:
        return 'opus'

    # Background automation → sonnet (balanced)
    if not task.needs_user_input:
        return 'sonnet'

    # Default for interactive tasks → sonnet
    return 'sonnet'

def estimate_task_cost(task: Task, model: str = None) -> float:
    """
    Estimate cost for a task in USD.

    Assumptions:
    - Input tokens ≈ 70% of total
    - Output tokens ≈ 30% of total
    - Total tokens based on effort
    """
    if model is None:
        model = select_model(task)

    # Get token estimate
    effort_key = task.effort.upper()[0] if task.effort else 'M'
    if 'XL' in task.effort.upper():
        effort_key = 'XL'

    total_tokens = EFFORT_TO_TOKENS.get(effort_key, 20000)
    input_tokens = int(total_tokens * 0.7)
    output_tokens = int(total_tokens * 0.3)

    # Calculate cost
    cost = (
        (input_tokens / 1_000_000) * COST_TABLE[model]['input'] +
        (output_tokens / 1_000_000) * COST_TABLE[model]['output']
    )

    return round(cost, 3)

def estimate_track_cost(tasks: Dict[str, Task]) -> Dict[str, any]:
    """Estimate total cost for all tasks in track"""
    total_cost = 0.0
    breakdown = {}

    for task_id, task in tasks.items():
        model = select_model(task)
        cost = estimate_task_cost(task, model)
        total_cost += cost
        breakdown[task_id] = {
            'model': model,
            'cost': cost
        }

    return {
        'total': round(total_cost, 2),
        'breakdown': breakdown
    }


# Priority & Mode Selection (v1.2)

def calculate_priority_score(task: Task) -> float:
    """Calculate priority score for task selection (higher = more important)"""
    score = 0.0

    # Critical path tasks highest priority
    if task.is_on_critical_path:
        score += 100

    # Severity weighting
    severity_weights = {'critical': 50, 'high': 30, 'medium': 10, 'low': 5}
    score += severity_weights.get(task.severity.lower(), 10)

    # Read-only tasks are safer (can run in background)
    if task.concurrency_class == 'read-only':
        score += 20

    # Smaller tasks preferred for quick wins
    effort_weights = {'S': 30, 'M': 20, 'L': 10, 'XL': 5}
    effort_key = task.effort.upper()[0] if task.effort else 'M'
    if 'XL' in task.effort.upper():
        effort_key = 'XL'
    score += effort_weights.get(effort_key, 10)

    return score


def get_task_mode(task: Task) -> str:
    """Determine if task should run in background or foreground"""
    if task.needs_user_input:
        return 'foreground'
    if task.severity.lower() in ['critical', 'high']:
        return 'foreground'
    if task.concurrency_class == 'write-shared':
        return 'foreground'
    # Small effort tasks → foreground (not worth backgrounding)
    if task.effort.upper().startswith('S'):
        return 'foreground'
    return 'background'


def select_batch(
    ready_tasks: List[Task],
    constraints: ResourceConstraints,
    running_tasks: Dict[str, str],
    current_iteration: int
) -> List[Task]:
    """Select which tasks to launch in current iteration.

    Args:
        ready_tasks: Tasks whose dependencies are satisfied
        constraints: Resource limits
        running_tasks: Dict of task_id -> mode ('background' or 'foreground')
        current_iteration: Current dispatch iteration number

    Returns:
        List of tasks to launch (respecting constraints)
    """
    # Count current usage
    background_running = sum(1 for mode in running_tasks.values() if mode == 'background')
    foreground_running = sum(1 for mode in running_tasks.values() if mode == 'foreground')
    total_running = len(running_tasks)

    # Calculate available slots
    bg_slots = max(0, constraints.max_parallel_background - background_running)
    fg_slots = max(0, constraints.max_parallel_foreground - foreground_running)
    total_slots = max(0, constraints.max_total_parallel - total_running)

    # Score and sort tasks by priority
    scored_tasks = []
    for task in ready_tasks:
        # Skip if already running
        if task.id in running_tasks:
            continue

        score = calculate_priority_score(task)
        mode = get_task_mode(task)
        scored_tasks.append((score, task, mode))

    # Sort by score descending
    scored_tasks.sort(key=lambda x: x[0], reverse=True)

    # Select tasks respecting constraints
    selected = []
    bg_used = 0
    fg_used = 0
    total_used = 0

    for score, task, mode in scored_tasks:
        # Check total limit
        if total_used >= total_slots:
            break

        # Check mode-specific limits
        if mode == 'background':
            if bg_used >= bg_slots:
                continue
            bg_used += 1
        else:  # foreground
            if fg_used >= fg_slots:
                continue
            fg_used += 1

        selected.append(task)
        total_used += 1

    return selected


def simulate_batch_selection(
    all_tasks: List[Task],
    dependencies: Dict[str, List[str]],
    constraints: ResourceConstraints,
    max_iterations: int = 50
) -> List[Dict]:
    """Simulate dispatch to show batch allocation over time.

    Args:
        all_tasks: All tasks in track
        dependencies: Dict of task_id -> list of dependency task_ids
        constraints: Resource limits
        max_iterations: Max simulation iterations

    Returns:
        List of dicts with iteration stats
    """
    simulation = []

    completed = set()
    running = {}  # task_id -> mode
    iteration = 0

    # Build task lookup
    tasks_by_id = {t.id: t for t in all_tasks}

    while len(completed) < len(all_tasks) and iteration < max_iterations:
        # Find ready tasks
        ready = []
        for task in all_tasks:
            if task.id in completed or task.id in running:
                continue
            deps = dependencies.get(task.id, [])
            if all(d in completed for d in deps):
                ready.append(task)

        # Select batch
        batch = select_batch(ready, constraints, running, iteration)

        # Simulate execution (assume 1 iteration for demo)
        running_tasks = {t.id: get_task_mode(t) for t in batch}
        running.update(running_tasks)

        # Complete running tasks
        completed.update(running_tasks.keys())
        running = {}

        # Record iteration
        simulation.append({
            'iteration': iteration,
            'launched': [t.id for t in batch],
            'completed': list(completed),
            'remaining': len(all_tasks) - len(completed)
        })

        iteration += 1

    return simulation


def effort_to_minutes(effort: str) -> int:
    """Parse effort string into minutes."""
    effort = effort.upper()
    
    # Try parse numbers first (more specific)
    hours_match = re.search(r'(\d+)\s*H', effort)
    if hours_match:
        return int(hours_match.group(1)) * 60
    mins_match = re.search(r'(\d+)\s*MIN', effort)
    if mins_match:
        return int(mins_match.group(1))

    # Single letter shortcuts (must be careful with word boundaries)
    if re.search(r'\bXL\b', effort):
        return 720
    if re.search(r'\bL\b', effort):
        return 480
    if re.search(r'\bM\b', effort):
        return 150
    if re.search(r'\bS\b', effort):
        return 30
        
    return 120  # default

def simulate_track(
    tasks: Dict[str, Task],
    constraints: ResourceConstraints,
    max_iterations: int = 100
) -> Dict[str, any]:
    """
    Simulate full track execution with virtual time.
    Returns: Dict with timeline, bottleneck analysis, and stats.
    """
    completed = set()
    # task_id -> (start_time, end_time, mode)
    running: Dict[str, Tuple[int, int, str]] = {}
    current_time = 0
    events = []
    iteration = 0
    
    task_stats = {tid: {'start': 0, 'end': 0} for tid in tasks}

    while (len(completed) < len(tasks)) and (iteration < max_iterations):
        iteration += 1
        
        # 1. Update completed tasks based on current time
        finished_this_tick = [tid for tid, (_, end, _) in running.items() if end <= current_time]
        for tid in finished_this_tick:
            completed.add(tid)
            task_stats[tid]['end'] = running[tid][1]
            del running[tid]

        # 2. Find ready tasks (deps met, not running, not completed)
        ready_ids = [
            tid for tid, t in tasks.items()
            if tid not in completed and tid not in running and
            all(d in completed or d not in tasks for d in t.depends_on)
        ]
        ready_tasks = [tasks[tid] for tid in ready_ids]

        # 3. Select batch using standard logic
        current_running_modes = {tid: mode for tid, (_, _, mode) in running.items()}
        batch = select_batch(ready_tasks, constraints, current_running_modes, iteration)

        # 4. Start selected tasks
        for t in batch:
            mode = get_task_mode(t)
            duration = effort_to_minutes(t.effort)
            start_time = current_time
            end_time = current_time + duration
            running[t.id] = (start_time, end_time, mode)
            task_stats[t.id]['start'] = start_time
            
            events.append({
                'time': current_time,
                'type': 'start',
                'task': t.id,
                'mode': mode
            })

        # 5. Advance time to next event
        if running:
            # Next completion or next possible start if we have slots?
            # For simulation simplicity, we jump to next completion
            next_completion = min(end for _, end, _ in running.values())
            current_time = next_completion
        elif ready_ids and not batch:
            # Blocked by constraints or conflicts
            current_time += 30
        elif not ready_ids and len(completed) < len(tasks):
            # Potential circular dependency check
            break
        else:
            break

    # Bottleneck analysis
    dependency_counts = {}
    for tid, t in tasks.items():
        for dep in t.depends_on:
            dependency_counts[dep] = dependency_counts.get(dep, 0) + 1
    
    bottlenecks = sorted(
        [(tid, count) for tid, count in dependency_counts.items() if tid in tasks],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return {
        'total_time': current_time,
        'task_stats': task_stats,
        'events': events,
        'bottlenecks': bottlenecks,
        'completed_count': len(completed)
    }

def render_ascii_timeline(simulation_results: Dict[str, any], tasks: Dict[str, Task]) -> str:
    """Generate ASCII Gantт chart for simulation results"""
    stats = simulation_results['task_stats']
    total_time = simulation_results['total_time']
    if total_time == 0: return "No tasks executed."

    def format_t(m):
        return f"{int(m)//60}h{int(m)%60:02d}m"

    width = 50
    lines = ["## Execution Timeline (Simulated)", ""]
    
    sorted_tids = sorted(tasks.keys(), key=lambda x: (stats[x]['start'], x))

    for tid in sorted_tids:
        s = stats[tid]
        if s['end'] == 0 and not any(e['task'] == tid for e in simulation_results['events']):
            bar = ' ' * width
            label = "(never started)"
        else:
            start_pos = int((s['start'] / total_time) * (width - 1))
            end_pos = int((s['end'] / total_time) * (width - 1))
            duration_chars = max(1, end_pos - start_pos)
            
            bar = ' ' * start_pos + 'в–€' * duration_chars + 'в–‘' * (width - 1 - end_pos)
            label = f"{format_t(s['start'])} - {format_t(s['end'])}"

        mode_indicator = "FG" if get_task_mode(tasks[tid]) == 'foreground' else "BG"
        lines.append(f"{tid} [{mode_indicator}] {bar} {label}")

    lines.append("")
    lines.append(f"Total simulated time: {format_t(total_time)}")
    return "\n".join(lines)


def generate_simulation_report(planner: 'OrchestrationPlanner', constraints: ResourceConstraints) -> str:
    """Generate full markdown simulation report"""
    results = simulate_track(planner.tasks, constraints)
    
    lines = [
        f"# Simulation Report вЂ” {planner.plan_path.parent.name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Constraints used:",
        f"- Max BG: {constraints.max_parallel_background}",
        f"- Max FG: {constraints.max_parallel_foreground}",
        f"- Max Total: {constraints.max_total_parallel}",
        "",
        render_ascii_timeline(results, planner.tasks),
        "",
        "## Bottleneck Analysis",
        "Tasks that other tasks are waiting for most:",
        ""
    ]
    
    for tid, count in results['bottlenecks']:
        task = planner.tasks[tid]
        lines.append(f"- **{tid}**: {task.title} (blocks {count} tasks)")
        
    lines.append("")
    lines.append("## Resource Efficiency")
    serial_time, _ = planner.estimate_times()
    parallel_time = results['total_time']
    speedup = serial_time / parallel_time if parallel_time > 0 else 1
    
    lines.append(f"- Serial Time: {serial_time//60}h {serial_time%60}m")
    lines.append(f"- Simulated Parallel Time: {parallel_time//60}h {parallel_time%60}m")
    lines.append(f"- Efficiency Gain: {speedup:.1f}x speedup")
    
    return "\n".join(lines)


def render_progress_bar(percent: float, width: int = 20) -> str:
    """Generate ASCII progress bar."""
    filled = int(width * (percent / 100))
    return 'в–€' * filled + 'в–‘' * (width - filled)

def calculate_metrics(
    all_tasks: Dict[str, Task],
    completed_ids: List[str],
    start_time_iso: str
) -> Dict[str, any]:
    """Calculate execution metrics."""
    total = len(all_tasks)
    done = len(completed_ids)
    percent = (done / total * 100) if total > 0 else 0
    
    # Velocity (tasks per hour)
    start_dt = datetime.fromisoformat(start_time_iso)
    elapsed = (datetime.now() - start_dt).total_seconds() / 3600
    velocity = done / elapsed if elapsed > 0.01 else 0
    
    # Estimated completion
    remaining = total - done
    eta_hours = remaining / velocity if velocity > 0 else 0
    
    return {
        'percent': round(percent, 1),
        'done': done,
        'total': total,
        'velocity': round(velocity, 2),
        'eta_min': int(eta_hours * 60)
    }


def generate_mermaid_graph(planner: 'OrchestrationPlanner') -> str:
    """Generate Mermaid flowchart of the task graph."""
    lines = ["graph TD"]
    
    # Define styles
    lines.append("    classDef done fill:#d4edda,stroke:#28a745,color:black;")
    lines.append("    classDef running fill:#fff3cd,stroke:#ffc107,color:black;")
    lines.append("    classDef blocked fill:#f8d7da,stroke:#dc3545,color:black;")
    lines.append("    classDef todo fill:#f8f9fa,stroke:#6c757d,color:black;")
    lines.append("    classDef critical stroke:#000,stroke-width:3px;")

    # Nodes
    for tid, task in planner.tasks.items():
        # Determine status class
        status = task.status.upper()
        if status in ['DONE', 'COMPLETE', 'вњ…']:
            style = "done"
        elif status in ['DOING', 'IN PROGRESS', 'RUNNING']:
            style = "running"
        elif status in ['BLOCKED']:
            style = "blocked"
        else:
            style = "todo"
            
        # Format label: T01\nTitle (Effort)
        label = f"{tid}<br/>{task.title}<br/>({task.effort})"
        
        # Build node definition
        node_def = f"    {tid}(\"{label}\")"
        
        # Add class
        lines.append(f"{node_def}:::{style}")
        
        # Critical path highlighting
        if task.is_on_critical_path:
            lines.append(f"    class {tid} critical")

    # Edges
    for tid, task in planner.tasks.items():
        for dep in task.depends_on:
            if dep in planner.tasks:
                lines.append(f"    {dep} --> {tid}")

    return "\n".join(lines)


def detect_anti_patterns(planner: 'OrchestrationPlanner') -> List[str]:
    """Detect planning anti-patterns (v2.0 Feature #9)."""
    warnings = []
    
    # 1. Monolithic Tasks
    for tid, task in planner.tasks.items():
        if 'XL' in task.effort.upper() and len(task.touches) > 5:
            warnings.append(f"рџ›ЎпёЏ  {tid}: XL task touches many files. Consider decomposing into smaller tasks.")

    # 2. Sequential Chains (Low Parallelism)
    serial_time, parallel_time = planner.estimate_times()
    if parallel_time > 0:
        speedup = serial_time / parallel_time
        if speedup < 1.2 and len(planner.tasks) > 3:
            warnings.append(f"рџ›ЎпёЏ  Low parallelism ({speedup:.1f}x). Consider breaking dependencies or using more 'read-only' tasks.")

    # 3. Missing Gates
    tasks_with_gates = sum(1 for t in planner.tasks.values() if t.iosm_checks and t.iosm_checks.lower() != 'n/a')
    if tasks_with_gates < len(planner.tasks) / 3:
        warnings.append(f"рџ›ЎпёЏ  Few IOSM gates defined ({tasks_with_gates}/{len(planner.tasks)}). Quality risks.")

    # 4. Circular Dependencies (Basic Check)
    # (The graph builder doesn't strictly fail on cycles, but group_into_waves catches them)
    if not planner.waves and planner.tasks:
         warnings.append(f"рџ›ЎпёЏ  Possible circular dependency (cannot schedule waves).")

    return warnings


def load_template(name: str, track_path: Path = None) -> str:
    """
    Load a template by name with resolution order:
    1. swarm/templates/<name>
    2. .claude/skills/swarm-iosm/templates/<name>
    """
    # 1. Project-specific override
    if track_path:
        project_template = track_path.parents[1] / 'templates' / name
        if project_template.exists():
            return project_template.read_text(encoding='utf-8')
            
    # 2. Skill defaults
    skill_template = Path(__file__).parent.parent / 'templates' / name
    if skill_template.exists():
        return skill_template.read_text(encoding='utf-8')
        
    raise FileNotFoundError(f"Template '{name}' not found.")

def render_template(content: str, variables: Dict[str, str]) -> str:
    """Simple variable substitution."""
    for key, val in variables.items():
        content = content.replace(f"{{{{{key}}}}}", str(val))
    return content


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

        # Pattern for task sections: - [ ] **T##**: Title OR - [x] **T##**: Title
        task_pattern = re.compile(
            r'- \[[ xX]\] \*\*([T\d]+)\*\*: (.+?)\r?\n(.*?)(?=- \[[ xX]\]|\Z)',
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
                # v1.2 fields
                model=self._extract_field(body, 'Model') or 'auto',
                severity=self._extract_field(body, 'Severity') or 'medium',
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

        # Mark tasks on critical path (v1.2)
        for tid in self.tasks:
            self.tasks[tid].is_on_critical_path = (tid in self.critical_path)

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

        # Cost estimation (v1.2)
        cost_estimate = estimate_track_cost(self.tasks)
        lines.append(f"**Estimated cost:** ${cost_estimate['total']}")
        model_counts = {}
        for breakdown in cost_estimate['breakdown'].values():
            model = breakdown['model']
            model_counts[model] = model_counts.get(model, 0) + 1
        cost_breakdown_str = ', '.join([f"{count} {model}" for model, count in sorted(model_counts.items())])
        lines.append(f"**Cost breakdown:** {cost_breakdown_str}")

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
        lines.append("| Task | Role | Model | Concurrency | Mode | Effort | Deps | Touches |")
        lines.append("|------|------|-------|-------------|------|--------|------|---------|")

        for tid in sorted(self.tasks.keys(), key=lambda x: int(x[1:])):
            task = self.tasks[tid]
            mode = self.classify_task_mode(tid)
            model = select_model(task)
            cost = estimate_task_cost(task, model)
            touches_display = ', '.join([f"`{t}`" for t in task.touches[:2]])
            if len(task.touches) > 2:
                touches_display += f" +{len(task.touches)-2}"
            deps_display = ', '.join(task.depends_on) if task.depends_on else '-'

            lines.append(
                f"| {tid} | {task.owner_role} | {model} | {task.concurrency_class} | "
                f"{'**FG**' if mode=='foreground' else 'BG'} | "
                f"{task.effort} (${cost}) | {deps_display} | {touches_display or '-'} |"
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
        lines.append("- [v1.2] Cost limit exceeded (spent >= 100% of budget)")
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
        lines.append("      - Update iosm_state.md (including cost tracking)")
        lines.append("      - Check cost budget (v1.2):")
        lines.append("        * If spent >= 80% of budget → ⚠️ WARNING")
        lines.append("        * If spent >= 100% of budget → 🚨 STOP execution")
        lines.append("      - Read SpawnCandidates from report")
        lines.append("      - Auto-spawn eligible candidates")
        lines.append("      - Release touches locks")
        lines.append("      - Recalculate ready queue")
        lines.append("   c. Dispatch new ready tasks immediately")
        lines.append("   d. Check Gate targets")
        lines.append("   e. If gates met → exit loop")
        lines.append("   f. If all blocked on user → ask questions")
        lines.append("   g. [v1.2] If budget exhausted → STOP and notify user")
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


    def reconcile_state(self) -> Dict[str, any]:
        """
        Reconcile current state by reading reports and plan.md.
        Returns: Dict with completed tasks, running, etc.
        """
        self.parse_plan()
        
        # Check reports for completion
        reports_dir = self.plan_path.parent / 'reports'
        completed = []
        if reports_dir.exists():
            for report in reports_dir.glob('T*.md'):
                # Basic check: if report exists and has 'Complete' status
                content = report.read_text(encoding='utf-8')
                if 'Status:** вњ… Complete' in content or 'Status:** Complete' in content:
                    completed.append(report.stem.upper())
        
        # Merge with plan.md status
        for tid, task in self.tasks.items():
            if task.status.upper() in ['DONE', 'COMPLETE'] and tid not in completed:
                completed.append(tid)
                
        return {
            'completed': sorted(list(set(completed))),
            'timestamp': datetime.now().isoformat()
        }

    def save_checkpoint(self, iteration: int = 0):
        """Save current orchestration state to checkpoint file."""
        state = self.reconcile_state()
        
        cp = Checkpoint(
            iteration=iteration,
            timestamp=state['timestamp'],
            completed_tasks=state['completed'],
            running_tasks={}, # Orchestrator will fill this during loop
            gate_scores={},   # Will be filled from gate check
            spawn_budget_remaining=20, # Default or load from state
            seen_dedup_keys=[],
            retry_counts={}
        )
        
        checkpoint_dir = self.plan_path.parent / 'checkpoints'
        checkpoint_dir.mkdir(exist_ok=True)
        
        cp_path = checkpoint_dir / f"iter_{iteration:03d}.json"
        cp.save(cp_path)
        
        # Also symlink latest.json (manual copy for Windows compatibility)
        latest_path = checkpoint_dir / "latest.json"
        cp.save(latest_path)
        
        print(f"вњ… Saved checkpoint: {cp_path}")

    def load_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Load the most recent checkpoint."""
        latest_path = self.plan_path.parent / 'checkpoints' / 'latest.json'
        if latest_path.exists():
            return Checkpoint.load(latest_path)
        return None


    def retry_task(self, task_id: str) -> bool:
        """
        Record a retry attempt for a task and check limits.
        """
        cp = self.load_latest_checkpoint()
        if not cp:
            # Create fresh checkpoint
            state = self.reconcile_state()
            cp = Checkpoint(
                iteration=0,
                timestamp=state['timestamp'],
                completed_tasks=state['completed'],
                running_tasks={},
                gate_scores={},
                spawn_budget_remaining=20,
                seen_dedup_keys=[],
                retry_counts={}
            )
            
        count = cp.retry_counts.get(task_id, 0)
        if count >= 3:
            print(f"рџљЁ Task {task_id} reached max retry limit (3). Manual intervention required.")
            return False
            
        cp.retry_counts[task_id] = count + 1
        cp.save(self.plan_path.parent / 'checkpoints' / 'latest.json')
        print(f"вњ… Recorded retry #{count + 1} for {task_id}")
        return True


    def render_iosm_state(self, cp: Checkpoint) -> str:
        """Render iosm_state.md from checkpoint data."""
        metrics = calculate_metrics(self.tasks, cp.completed_tasks, cp.timestamp)
        
        # Calculate cost
        track_cost = estimate_track_cost(self.tasks)
        spent = 0.0
        for tid in cp.completed_tasks:
            # Use actual cost if we had it, currently using estimate
            task = self.tasks[tid]
            spent += estimate_task_cost(task, select_model(task))
            
        constraints = ResourceConstraints() # Load defaults or from config if available
        
        lines = [
            f"# IOSM State вЂ” {self.plan_path.parent.name}",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Status:** {'COMPLETE' if metrics['percent'] == 100 else 'IN_PROGRESS'}",
            f"**Iteration:** {cp.iteration}",
            "",
            "## Metrics",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Progress | {metrics['percent']}% ({metrics['done']}/{metrics['total']}) |",
            f"| Velocity | {metrics['velocity']} tasks/hr |",
            f"| ETA | {metrics['eta_min']//60}h {metrics['eta_min']%60}m |",
            "",
            "**Progress Bar:**",
            f"`[{render_progress_bar(metrics['percent'], 40)}]`",
            "",
            "---",
            "",
            "## Cost Tracking (v1.2)",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Budget Total | ${constraints.cost_limit_per_track:.2f} |",
            f"| Spent So Far | ${spent:.2f} |",
            f"| Remaining | ${max(0, constraints.cost_limit_per_track - spent):.2f} |",
            "",
            "---",
            "",
            "## Task Queues",
            "",
            "**Running:**",
        ]
        
        if cp.running_tasks:
            for tid, mode in cp.running_tasks.items():
                lines.append(f"- {tid}: {self.tasks[tid].title} ({mode})")
        else:
            lines.append("*(None)*")
            
        lines.append("")
        lines.append("**Next Ready:**")
        
        ready = self.get_ready_tasks(set(cp.completed_tasks), set(cp.running_tasks.keys()))
        for tid in ready[:5]:
            lines.append(f"- {tid}: {self.tasks[tid].title}")
        if len(ready) > 5:
            lines.append(f"... and {len(ready)-5} more")
            
        if not ready and not cp.running_tasks and metrics['percent'] < 100:
             lines.append("*(No ready tasks - check blockers or dependencies)*")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Note:** This file is auto-generated. Do not edit manually.")
        
        return "\n".join(lines)

    def update_task_state(self, task_id: str, status: str):
        """Update task status in checkpoint and regenerate state file."""
        cp = self.load_latest_checkpoint()
        if not cp:
            # Init checkpoint if missing
            state = self.reconcile_state()
            cp = Checkpoint(
                iteration=0,
                timestamp=state['timestamp'],
                completed_tasks=state['completed'],
                running_tasks={},
                gate_scores={},
                spawn_budget_remaining=20,
                seen_dedup_keys=[],
                retry_counts={}
            )
            
        status = status.upper()
        updated = False
        
        if status in ['DONE', 'COMPLETE', 'SUCCESS']:
            if task_id not in cp.completed_tasks:
                cp.completed_tasks.append(task_id)
                updated = True
            if task_id in cp.running_tasks:
                del cp.running_tasks[task_id]
                updated = True
                
        elif status in ['RUNNING', 'IN_PROGRESS']:
            # Assume background default if not specified, usually classification handles this
            if task_id not in cp.running_tasks:
                cp.running_tasks[task_id] = "background" 
                updated = True
                
        elif status in ['FAILED', 'BLOCKED']:
            if task_id in cp.running_tasks:
                del cp.running_tasks[task_id]
                updated = True
        
        if updated:
            cp.iteration += 1
            cp.save(self.plan_path.parent / 'checkpoints' / 'latest.json')
            
            # Regenerate iosm_state.md
            state_content = self.render_iosm_state(cp)
            (self.plan_path.parent / 'iosm_state.md').write_text(state_content, encoding='utf-8')
            print(f"вњ… Updated status for {task_id} to {status}. State regenerated.")
        else:
            print(f"No changes needed for {task_id}.")


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
            if not task.touches and task.concurrency_class != 'read-only':
                missing.append(f"{tid}: missing 'Touches'")
            if not task.effort:
                missing.append(f"{tid}: missing 'Effort'")
            # v1.1 warnings (not blocking)
            if not task.concurrency_class or task.concurrency_class == 'write-local':
                warnings.append(f"{tid}: using default concurrency_class='write-local'")

        if missing:
            print("вќЊ Validation failed:")
            for m in missing:
                print(f"  - {m}")
            sys.exit(1)
        else:
            print(f"вњ… All {len(planner.tasks)} tasks have required fields (Touches, Needs user input, Effort)")
            
            # Anti-pattern checks (v2.0)
            planner.build_dependency_graph()
            planner.group_into_waves()
            anti_patterns = detect_anti_patterns(planner)
            
            if warnings or anti_patterns:
                print(f"\nвљ пёЏ  Warnings & Anti-Patterns:")
                for w in warnings:
                    print(f"  - {w}")
                for ap in anti_patterns:
                    print(f"  - {ap}")

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

    elif '--simulate' in sys.argv:
        # Generate simulation report
        planner = OrchestrationPlanner(plan_path)
        planner.parse_plan()
        planner.build_dependency_graph()
        planner.find_critical_path()
        
        # Load constraints from plan if possible (basic logic for now)
        constraints = ResourceConstraints()
        
        report = generate_simulation_report(planner, constraints)
        output_path = Path(plan_path).parent / "simulation_report.md"
        output_path.write_text(report, encoding='utf-8')
        print(f"вњ… Generated simulation report: {output_path}")
        print("\n" + render_ascii_timeline(simulate_track(planner.tasks, constraints), planner.tasks))

    elif '--checkpoint' in sys.argv:
        # Save current state as checkpoint
        planner = OrchestrationPlanner(plan_path)
        iteration = int(sys.argv[sys.argv.index('--checkpoint') + 1]) if len(sys.argv) > sys.argv.index('--checkpoint') + 1 else 0
        planner.save_checkpoint(iteration)

    elif '--resume' in sys.argv:
        # Load latest checkpoint and show status
        planner = OrchestrationPlanner(plan_path)
        cp = planner.load_latest_checkpoint()
        if cp:
            print(f"вњ… Loaded checkpoint from {cp.timestamp}")
            print(f"Iteration: {cp.iteration}")
            print(f"Completed tasks: {', '.join(cp.completed_tasks)}")
            
            # Recalculate ready tasks
            planner.parse_plan()
            ready = planner.get_ready_tasks(set(cp.completed_tasks), set())
            print(f"Ready to dispatch: {', '.join(ready)}")
        else:
            print("вќЊ No checkpoint found. Reconciling from files...")
            state = planner.reconcile_state()
            print(f"Completed tasks: {', '.join(state['completed'])}")

    elif '--retry' in sys.argv:
        # Record retry attempt
        planner = OrchestrationPlanner(plan_path)
        task_id = sys.argv[sys.argv.index('--retry') + 1]
        if planner.retry_task(task_id):
            print(f"Proceeding with retry for {task_id}...")
        else:
            sys.exit(1)

    elif '--watch' in sys.argv:
        # Show live status dashboard
        planner = OrchestrationPlanner(plan_path)
        planner.parse_plan()
        state = planner.reconcile_state()
        metrics = calculate_metrics(planner.tasks, state['completed'], state['timestamp'])
        
        # Parallelism efficiency
        serial_min, _ = planner.estimate_times()
        elapsed_min = (datetime.now() - datetime.fromisoformat(state['timestamp'])).total_seconds() / 60
        # Efficiency = (serial time of completed work) / (actual elapsed time)
        # For simplicity, let's just show the multiplier
        efficiency = (serial_min / elapsed_min) if elapsed_min > 1 else 1.0
        
        print(f"\nрџ“Љ Swarm-IOSM Live Dashboard РІР‚вЂќ {planner.plan_path.parent.name}")
        print(f"{'='*60}")
        print(f"Progress: {render_progress_bar(metrics['percent'])} {metrics['percent']}%")
        print(f"Tasks:    {metrics['done']} / {metrics['total']} complete")
        print(f"Velocity: {metrics['velocity']} tasks/hour")
        print(f"Efficiency: {efficiency:.1f}x (parallel speedup)")
        if metrics['eta_min'] > 0:
            print(f"ETA:      {metrics['eta_min']//60}h {metrics['eta_min']%60}m remaining")
        else:
            print(f"ETA:      calculating...")
        print(f"{'-'*60}")
        
        # Show task statuses
        for tid in sorted(planner.tasks.keys()):
            status = "вњ…" if tid in state['completed'] else "вЏі"
            print(f"{status} {tid}: {planner.tasks[tid].title[:40]}")
        print(f"{'='*60}\n")

    elif '--update-task' in sys.argv:
        # Update task status and regenerate state
        # Usage: python script.py plan.md --update-task T01 --status DONE
        try:
            task_idx = sys.argv.index('--update-task')
            task_id = sys.argv[task_idx + 1]
            
            status_idx = sys.argv.index('--status')
            status = sys.argv[status_idx + 1]
            
            planner = OrchestrationPlanner(plan_path)
            planner.parse_plan()
            planner.build_dependency_graph()
            planner.update_task_state(task_id, status)
            
        except (ValueError, IndexError):
            print("Usage: --update-task <TID> --status <STATUS>")
            sys.exit(1)

    elif '--graph' in sys.argv:
        # Generate Mermaid graph
        planner = OrchestrationPlanner(plan_path)
        planner.parse_plan()
        planner.build_dependency_graph()
        planner.find_critical_path()
        
        graph = generate_mermaid_graph(planner)
        output_path = Path(plan_path).parent / "dependency_graph.mermaid"
        output_path.write_text(graph, encoding='utf-8')
        
        print(f"вњ… Generated Mermaid graph: {output_path}")
        print("To view: Install Mermaid extension or paste into mermaid.live")
        print("\n" + graph)

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
