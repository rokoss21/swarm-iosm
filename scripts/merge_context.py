#!/usr/bin/env python3
"""
Shared Context Manager (v2.0 Feature #5).

Merges updates from subagent reports into shared_context.md.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

def merge_context_updates(track_path: Path):
    """Scan reports and update shared_context.md."""
    reports_dir = track_path / 'reports'
    context_path = track_path / 'shared_context.md'
    
    if not reports_dir.exists():
        print("No reports directory found.")
        return

    # Initialize context if missing
    if not context_path.exists():
        template_path = Path(__file__).parent.parent / 'templates' / 'shared_context.md'
        if template_path.exists():
            context_path.write_text(template_path.read_text(encoding='utf-8'), encoding='utf-8')
        else:
            print("Template not found, skipping context creation.")
            return

    current_context = context_path.read_text(encoding='utf-8')
    
    # Track what we've already merged to avoid duplicates (naive check)
    # Ideally we'd use a more structured format, but appending is safe for now
    
    updates_found = False
    
    for report in reports_dir.glob('T*.md'):
        content = report.read_text(encoding='utf-8')
        task_id = report.stem
        
        # Extract Shared Context Updates section
        match = re.search(r'## Shared Context Updates.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if not match:
            continue
            
        updates = match.group(1).strip()
        if not updates or "None" in updates or "No updates" in updates:
            continue
            
        # Parse patterns
        patterns = re.findall(r'- \[(.*?)\]: (.*)', updates)
        for name, desc in patterns:
            if name not in current_context:
                current_context += f"\n\n### {name}\n- **Description:** {desc}\n- **Discovered by:** {task_id}"
                updates_found = True
                print(f"в• Merged pattern '{name}' from {task_id}")

    if updates_found:
        current_context = re.sub(r'\*\*Last Updated:\*\* .*', f'**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}', current_context)
        context_path.write_text(current_context, encoding='utf-8')
        print(f"вњ… Updated shared_context.md")
    else:
        print("No new context updates found.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python merge_context.py <track_dir>")
        sys.exit(1)
    
    merge_context_updates(Path(sys.argv[1]))
