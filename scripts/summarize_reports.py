#!/usr/bin/env python3
"""
Summarize all subagent reports in a track.

Generates a summary showing:
- Which tasks are complete
- What files were touched
- Open blockers
- IOSM scores
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


class ReportSummarizer:
    def __init__(self, track_dir: str):
        self.track_dir = Path(track_dir)
        self.reports_dir = self.track_dir / 'reports'
        self.reports: Dict[str, dict] = {}

    def load_reports(self):
        """Load all report markdown files."""
        if not self.reports_dir.exists():
            print(f"❌ Reports directory not found: {self.reports_dir}")
            return False

        for report_file in self.reports_dir.glob('T*.md'):
            task_id = report_file.stem  # e.g., 'T01'
            content = report_file.read_text(encoding='utf-8')

            self.reports[task_id] = {
                'file': report_file.name,
                'status': self._extract_status(content),
                'summary': self._extract_summary(content),
                'files_touched': self._extract_files(content),
                'blockers': self._extract_blockers(content),
                'iosm_score': self._extract_iosm_score(content),
            }

        return True

    def _extract_status(self, content: str) -> str:
        """Extract completion status from report."""
        pattern = re.compile(r'\*\*Status:\*\* (.+?)$', re.MULTILINE)
        match = pattern.search(content)
        if match:
            status_text = match.group(1).strip()
            if '✅' in status_text or 'Complete' in status_text:
                return 'Complete'
            elif '⚠️' in status_text or 'Partial' in status_text:
                return 'Partial'
            elif '❌' in status_text or 'Blocked' in status_text:
                return 'Blocked'
        return 'Unknown'

    def _extract_summary(self, content: str) -> str:
        """Extract summary section."""
        pattern = re.compile(
            r'## Summary.*?\n\n(.+?)(?=\n\n## |\Z)',
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(content)
        if match:
            summary = match.group(1).strip()
            # Take first paragraph
            first_para = summary.split('\n\n')[0]
            return first_para[:200] + '...' if len(first_para) > 200 else first_para
        return 'No summary found'

    def _extract_files(self, content: str) -> Dict[str, int]:
        """Extract file statistics."""
        files = {'created': 0, 'modified': 0, 'deleted': 0}

        # Find Files Touched section
        pattern = re.compile(
            r'## Files Touched.*?\n(.*?)(?=\n## |\Z)',
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(content)
        if not match:
            return files

        section = match.group(1)

        # Count created files
        created_pattern = re.compile(r'^- `(.+?)`', re.MULTILINE)
        created_section = re.search(r'### Created\n(.*?)(?=###|\Z)', section, re.DOTALL)
        if created_section:
            files['created'] = len(created_pattern.findall(created_section.group(1)))

        # Count modified files
        modified_section = re.search(r'### Modified\n(.*?)(?=###|\Z)', section, re.DOTALL)
        if modified_section:
            files['modified'] = len(created_pattern.findall(modified_section.group(1)))

        # Count deleted files
        deleted_section = re.search(r'### Deleted\n(.*?)(?=###|\Z)', section, re.DOTALL)
        if deleted_section:
            files['deleted'] = len(created_pattern.findall(deleted_section.group(1)))

        return files

    def _extract_blockers(self, content: str) -> List[str]:
        """Extract blocker list."""
        blockers = []

        pattern = re.compile(
            r'### Blockers.*?\n(.*?)(?=\n### |\n## |\Z)',
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(content)
        if not match:
            return blockers

        section = match.group(1)
        blocker_pattern = re.compile(r'- ❌ \*\*(.+?)\*\*', re.MULTILINE)

        for blocker_match in blocker_pattern.finditer(section):
            blockers.append(blocker_match.group(1))

        return blockers

    def _extract_iosm_score(self, content: str) -> float:
        """Extract overall IOSM score."""
        pattern = re.compile(
            r'\*\*Overall IOSM Score.*?:\*\* ([\d.]+)',
            re.MULTILINE
        )
        match = pattern.search(content)
        if match:
            return float(match.group(1))
        return 0.0

    def print_summary(self):
        """Print comprehensive summary."""
        print(f"\n{'='*70}")
        print(f"Track Summary: {self.track_dir.name}")
        print(f"{'='*70}\n")

        if not self.reports:
            print("❌ No reports found.")
            return

        # Overall stats
        total = len(self.reports)
        complete = sum(1 for r in self.reports.values() if r['status'] == 'Complete')
        partial = sum(1 for r in self.reports.values() if r['status'] == 'Partial')
        blocked = sum(1 for r in self.reports.values() if r['status'] == 'Blocked')

        print(f"📊 Overall Progress:")
        print(f"   Total tasks: {total}")
        print(f"   ✅ Complete: {complete} ({complete/total*100:.0f}%)")
        print(f"   ⚠️  Partial: {partial}")
        print(f"   ❌ Blocked: {blocked}")
        print()

        # File impact
        total_created = sum(r['files_touched']['created'] for r in self.reports.values())
        total_modified = sum(r['files_touched']['modified'] for r in self.reports.values())
        total_deleted = sum(r['files_touched']['deleted'] for r in self.reports.values())

        print(f"📁 File Impact:")
        print(f"   Created: {total_created}")
        print(f"   Modified: {total_modified}")
        print(f"   Deleted: {total_deleted}")
        print()

        # IOSM scores
        iosm_scores = [r['iosm_score'] for r in self.reports.values() if r['iosm_score'] > 0]
        if iosm_scores:
            avg_iosm = sum(iosm_scores) / len(iosm_scores)
            print(f"📈 IOSM Quality:")
            print(f"   Average score: {avg_iosm:.2f}")
            print(f"   Min score: {min(iosm_scores):.2f}")
            print(f"   Max score: {max(iosm_scores):.2f}")
            print()

        # Task details
        print(f"{'─'*70}")
        print("Task Details:")
        print(f"{'─'*70}\n")

        for task_id in sorted(self.reports.keys()):
            report = self.reports[task_id]

            status_icon = {
                'Complete': '✅',
                'Partial': '⚠️',
                'Blocked': '❌',
                'Unknown': '❓'
            }.get(report['status'], '❓')

            print(f"{status_icon} {task_id}: {report['file']}")
            print(f"   Status: {report['status']}")
            print(f"   Summary: {report['summary']}")

            files = report['files_touched']
            if any(files.values()):
                print(f"   Files: +{files['created']} ~{files['modified']} -{files['deleted']}")

            if report['iosm_score'] > 0:
                print(f"   IOSM: {report['iosm_score']:.2f}")

            if report['blockers']:
                print(f"   ❌ Blockers: {len(report['blockers'])}")
                for blocker in report['blockers']:
                    print(f"      • {blocker}")

            print()

        # All blockers
        all_blockers = []
        for task_id, report in self.reports.items():
            for blocker in report['blockers']:
                all_blockers.append((task_id, blocker))

        if all_blockers:
            print(f"{'─'*70}")
            print(f"⚠️  All Blockers ({len(all_blockers)}):")
            print(f"{'─'*70}\n")
            for task_id, blocker in all_blockers:
                print(f"  [{task_id}] {blocker}")
            print()

        print(f"{'='*70}\n")

    def generate_json_summary(self) -> dict:
        """Generate JSON summary for programmatic use."""
        total = len(self.reports)
        complete = sum(1 for r in self.reports.values() if r['status'] == 'Complete')

        return {
            'track': self.track_dir.name,
            'total_tasks': total,
            'completed_tasks': complete,
            'progress_percent': round(complete / total * 100, 1) if total > 0 else 0,
            'files_created': sum(r['files_touched']['created'] for r in self.reports.values()),
            'files_modified': sum(r['files_touched']['modified'] for r in self.reports.values()),
            'files_deleted': sum(r['files_touched']['deleted'] for r in self.reports.values()),
            'blockers': sum(len(r['blockers']) for r in self.reports.values()),
            'tasks': {
                task_id: {
                    'status': report['status'],
                    'iosm_score': report['iosm_score'],
                    'has_blockers': len(report['blockers']) > 0,
                }
                for task_id, report in self.reports.items()
            }
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize_reports.py <path/to/track/dir>")
        print("Example: python summarize_reports.py swarm/tracks/2026-01-17-001")
        sys.exit(1)

    track_dir = sys.argv[1]
    summarizer = ReportSummarizer(track_dir)

    if not summarizer.load_reports():
        sys.exit(1)

    if '--json' in sys.argv:
        summary = summarizer.generate_json_summary()
        print(json.dumps(summary, indent=2))
    else:
        summarizer.print_summary()


if __name__ == '__main__':
    main()
