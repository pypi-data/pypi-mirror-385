"""Legacy v3-style initialization for multiagent framework.

Provides backward-compatible sequential prompt interface for users who prefer
the classic initialization flow over the new progress tracker.

This module maintains the v3.x UX while fixing bugs (hanging prompts, incomplete flows).
"""

import click
from pathlib import Path
from rich.console import Console

console = Console()


def _init_legacy(path, dry_run, create_repo, interactive, backend_heavy):
    """Legacy v3-style initialization (sequential prompts, fixed bugs).

    Args:
        path: Target directory path
        dry_run: If True, don't make actual changes
        create_repo: Create GitHub repository
        interactive: Use interactive prompts
        backend_heavy: Backend-heavy mode

    Returns:
        None
    """
    # Placeholder - will implement in T024-T028
    console.print("[bold blue]MultiAgent Framework Initialization[/bold blue]")
    console.print("[dim]Using legacy interface (v3 compatible)[/dim]\n")

    # TODO: Implement sequential prompts
    # TODO: Fix hanging prompt bug
    # TODO: Complete initialization flow
    pass


def _execute_initialization(
    path,
    use_existing_git,
    create_github,
    install_git_hooks,
    install_issue_templates,
    project_type,
    use_docker
):
    """Execute initialization with collected parameters.

    Args:
        path: Target directory path
        use_existing_git: Use existing git repo
        create_github: Create GitHub repository
        install_git_hooks: Install git hooks
        install_issue_templates: Install issue templates
        project_type: Project type (web-app, api, cli, etc.)
        use_docker: Use Docker

    Returns:
        None
    """
    # Placeholder - will implement in T028
    # This will call the same underlying functions as the new init flow
    # but without the progress tracker
    pass
