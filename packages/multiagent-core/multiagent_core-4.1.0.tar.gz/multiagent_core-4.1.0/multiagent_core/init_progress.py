"""Visual progress tracker for multiagent initialization.

Displays real-time checklist with emojis showing initialization progress across 8 phases.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class InitProgress:
    """Visual progress tracker for initialization process."""

    def __init__(self, console: Console, log_dir: Optional[Path] = None):
        """Initialize progress tracker.

        Args:
            console: Rich console instance for output
            log_dir: Directory to save completion log (default: .multiagent/logs/)
        """
        self.console = console
        self.log_dir = log_dir
        self.phases: Dict[str, Dict] = {}
        self.current_phase: Optional[str] = None
        self.start_time = datetime.now()
        self.log_entries: List[str] = []

    def add_phase(self, name: str, steps: List[str]):
        """Add a phase with its steps.

        Args:
            name: Phase name (e.g., "Phase 1: Prerequisites")
            steps: List of step descriptions
        """
        self.phases[name] = {
            'steps': steps,
            'completed': set(),
            'started': False,
            'start_time': None,
            'end_time': None
        }

    def start_phase(self, name: str):
        """Start a phase (mark as in progress).

        Args:
            name: Phase name
        """
        if name not in self.phases:
            return

        self.current_phase = name
        self.phases[name]['started'] = True
        self.phases[name]['start_time'] = datetime.now()
        self._display_progress()

    def complete_step(self, phase: str, step: str):
        """Mark a step as completed.

        Args:
            phase: Phase name
            step: Step description (must match one from add_phase)
        """
        if phase not in self.phases:
            return

        if step in self.phases[phase]['steps']:
            self.phases[phase]['completed'].add(step)

            # Log the completion
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_entries.append(f"[{timestamp}] ✅ {step}")

            # Check if phase is complete
            if len(self.phases[phase]['completed']) == len(self.phases[phase]['steps']):
                self.phases[phase]['end_time'] = datetime.now()

            self._display_progress()

    def _display_progress(self):
        """Display current progress in console."""
        self.console.clear()

        # Title
        title = Text()
        title.append("🚀 MultiAgent Framework Initialization\n", style="bold blue")

        # Build progress display
        lines = []
        for phase_name, phase_data in self.phases.items():
            # Phase header
            if not phase_data['started']:
                phase_icon = "⏳"
                phase_style = "dim"
            elif phase_data['end_time']:
                phase_icon = "✅"
                phase_style = "green"
            else:
                phase_icon = "⚙️"
                phase_style = "cyan"

            lines.append(f"\n{phase_icon} [bold {phase_style}]{phase_name}[/bold {phase_style}]")

            # Steps
            for step in phase_data['steps']:
                if step in phase_data['completed']:
                    lines.append(f"  ✅ {step}")
                elif phase_data['started'] and phase_name == self.current_phase:
                    lines.append(f"  ⚙️ [cyan]{step}[/cyan]")
                else:
                    lines.append(f"  ⏳ [dim]{step}[/dim]")

        content = "\n".join(lines)
        panel = Panel(content, title="[bold]Initialization Progress[/bold]", border_style="blue")
        self.console.print(panel)

    def save_log(self, project_path: Path):
        """Save initialization log to file.

        Args:
            project_path: Project directory path
        """
        # Determine log directory
        if self.log_dir:
            log_dir = self.log_dir
        else:
            log_dir = project_path / ".multiagent" / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log filename with timestamp
        timestamp = self.start_time.strftime("%Y%m%d-%H%M%S")
        log_file = log_dir / f"init-{timestamp}.log"

        # Build log content
        log_content = []
        log_content.append("=" * 80)
        log_content.append("MultiAgent Framework Initialization Log")
        log_content.append("=" * 80)
        log_content.append(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f}s")
        log_content.append("=" * 80)
        log_content.append("")

        # Add all phases and steps
        for phase_name, phase_data in self.phases.items():
            phase_status = "✅ COMPLETED" if phase_data['end_time'] else "⚠️ PARTIAL"
            log_content.append(f"\n{phase_name} - {phase_status}")
            log_content.append("-" * 80)

            for step in phase_data['steps']:
                if step in phase_data['completed']:
                    log_content.append(f"  ✅ {step}")
                else:
                    log_content.append(f"  ⏳ {step} (NOT COMPLETED)")

            if phase_data['start_time'] and phase_data['end_time']:
                duration = (phase_data['end_time'] - phase_data['start_time']).total_seconds()
                log_content.append(f"  Duration: {duration:.2f}s")

        log_content.append("\n" + "=" * 80)
        log_content.append("Detailed Timeline")
        log_content.append("=" * 80)
        for entry in self.log_entries:
            log_content.append(entry)

        log_content.append("\n" + "=" * 80)
        log_content.append("Initialization Complete")
        log_content.append("=" * 80)

        # Write to file
        log_file.write_text("\n".join(log_content))

        return log_file


def create_init_phases() -> List[tuple]:
    """Create standard initialization phases.

    Returns:
        List of (phase_name, steps) tuples
    """
    return [
        ("Phase 1: Prerequisites", [
            "Check spec-kit installation",
            "Verify package installation",
            "Validate target directory"
        ]),
        ("Phase 2: Global Framework Setup", [
            "Create ~/.multiagent/ (or detect existing)",
            "Install framework templates",
            "Create global registry ~/.multiagent.json",
            "Backup existing customizations (if applicable)"
        ]),
        ("Phase 3: Git Repository Setup", [
            "Initialize or use existing git repository",
            "Configure git ownership (WSL/Windows safety)",
            "Create initial commit"
        ]),
        ("Phase 4: MCP Configuration", [
            "Create .mcp.json (Claude Code)",
            "Create .vscode/mcp.json (VS Code Copilot)"
        ]),
        ("Phase 5: Project Structure", [
            "Generate project directories (docs/, scripts/)",
            "Install git hooks (pre-commit, pre-push, post-commit)",
            "Create components registry"
        ]),
        ("Phase 6: GitHub Integration", [
            "Create GitHub repository (if enabled)",
            "Configure origin remote (if enabled)",
            "Install issue templates (if enabled)",
            "Install GitHub workflows (if enabled)"
        ]),
        ("Phase 7: Environment Detection", [
            "Detect project type (Python, Node.js, etc.)",
            "Identify frameworks",
            "Generate smart configurations"
        ]),
        ("Phase 8: Registration & Finalization", [
            "Register project in ~/.multiagent.json",
            "Update last_updated timestamp",
            "Save initialization log",
            "Display completion summary"
        ])
    ]
