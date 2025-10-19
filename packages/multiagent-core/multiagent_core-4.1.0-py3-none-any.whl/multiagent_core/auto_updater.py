"""Auto-update all deployed projects when multiagent-core is built."""

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Single source of truth: ~/.multiagent.json
REGISTRY_FILE = Path.home() / ".multiagent.json"
CORE_PROJECT = Path(__file__).parent.parent

def register_deployment(project_path):
    """Register a project for automatic updates (called by multiagent init)."""
    if isinstance(project_path, str):
        project_path = Path(project_path)
    project_path = project_path.resolve()

    # Skip /tmp projects - they're temporary test projects
    if str(project_path).startswith('/tmp/'):
        print(f"[SKIP] Not registering temporary project: {project_path.name}")
        return

    # Load or create registry file
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            data = json.load(f)
    else:
        # Create new registry with standard format
        data = {
            "version": "1.0.0",
            "framework_version": "3.8.0",
            "projects": [],
            "settings": {"auto_update": True}
        }

    # Add project if not already tracked
    project_str = str(project_path)
    project_name = project_path.name

    # Check if already exists
    existing = next((p for p in data["projects"] if p.get("path") == project_str), None)

    if not existing:
        data["projects"].append({
            "name": project_name,
            "path": project_str,
            "autoUpdate": True,
            "registered_at": datetime.now().isoformat(),
            "last_updated": None
        })

        # Save registry file
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"[OK] Registered for automatic updates: {project_path.name}")


def sync_directory_recursively(src_dir, dst_dir, exclude_dirs=None):
    """Recursively sync directory structure and files."""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.DS_Store'}

    if not src_dir.exists():
        return

    # Create destination directory if it doesn't exist
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Protected directories - never delete custom files from these
    PROTECTED_DIRS = {'agents', 'commands', 'hooks', 'scripts'}

    # Protected file patterns - preserve user customizations
    PROTECTED_PATTERNS = {
        # Custom agents (not from multiagent-core templates)
        'memory-agent.md', 'outreach-agent.md', 'pipeline-agent.md',
        'qualification-agent.md', 'scheduling-agent.md', 'sourcing-agent.md',
        # User settings and customizations
        'settings.local.json', 'settings.user.json',
        # Project-specific configs
        '.mcp.json', 'mcp-config.json'
    }

    # Clean up deprecated files and directories ONLY for non-protected areas
    if dst_dir.name == 'prompts':
        cleanup_deprecated_prompts(dst_dir)
        cleanup_extra_files(src_dir, dst_dir)
    elif dst_dir.name == 'docs':
        cleanup_deprecated_docs(src_dir, dst_dir)

    # CLEANUP: Remove directories and files that don't exist in source
    # BUT skip protected directories to preserve custom user files
    if dst_dir.name not in PROTECTED_DIRS:
        # Get list of items that should exist (from source)
        src_items = {item.name for item in src_dir.iterdir() if item.name not in exclude_dirs}

        # Remove items in destination that don't exist in source
        for dst_item in list(dst_dir.iterdir()):
            if dst_item.name in exclude_dirs:
                continue

            # Skip protected files/patterns
            if dst_item.name in PROTECTED_PATTERNS:
                continue

            if dst_item.name not in src_items:
                # This item doesn't exist in source - remove it
                if dst_item.is_dir():
                    shutil.rmtree(dst_item)
                    print(f"     ✗ Removed obsolete directory: {dst_item.name}")
                else:
                    dst_item.unlink()
                    print(f"     ✗ Removed obsolete file: {dst_item.name}")

    # Sync all files and subdirectories from source
    for src_item in src_dir.iterdir():
        if src_item.name in exclude_dirs:
            continue

        dst_item = dst_dir / src_item.name

        if src_item.is_file():
            # For template files, always copy to ensure they're up to date
            # For other files, only copy if newer or different
            should_copy = (
                not dst_item.exists() or
                src_dir.name == 'templates' or  # Always sync template files
                src_item.stat().st_mtime > dst_item.stat().st_mtime
            )

            if should_copy:
                shutil.copy2(src_item, dst_item)
                print(f"     → {src_item.relative_to(src_dir)}")
        elif src_item.is_dir():
            # Recursively sync subdirectory
            sync_directory_recursively(src_item, dst_item, exclude_dirs)

def cleanup_deprecated_prompts(prompts_dir):
    """Remove deprecated .md prompt files when .txt equivalents exist."""
    if not prompts_dir.exists():
        return
    
    # Find all .txt files to understand what agents we have
    txt_files = {f.stem for f in prompts_dir.glob("*.txt")}
    agent_names = {stem.split('-')[0] for stem in txt_files if '-' in stem}
    
    for md_file in prompts_dir.glob("*.md"):
        # Skip README.md and task-related documentation files
        if md_file.stem in ['README', 'TASK_CHECKLIST', 'TASK_TRIGGER']:
            continue
        
        should_remove = False
        
        # If there's a corresponding .txt file with exact same stem, remove the .md file
        if md_file.stem in txt_files:
            should_remove = True
            reason = f"replaced by {md_file.stem}.txt"
        
        # If this is an old agent prompt file and we have a new .txt file for that agent
        elif '-' in md_file.stem:
            agent_name = md_file.stem.split('-')[0]
            if agent_name in agent_names:
                should_remove = True
                reason = f"replaced by {agent_name}-startup.txt"
        
        if should_remove:
            print(f"     ✗ Removing deprecated {md_file.name} ({reason})")
            md_file.unlink()

def cleanup_extra_files(src_dir, dst_dir):
    """Remove files from destination that don't exist in source."""
    if not src_dir.exists() or not dst_dir.exists():
        return
    
    # Get list of files that should exist (from source)
    src_files = {item.name for item in src_dir.iterdir() if item.is_file()}
    
    # Remove files from destination that don't exist in source
    for dst_file in dst_dir.iterdir():
        if dst_file.is_file() and dst_file.name not in src_files:
            print(f"     ✗ Removing extra file {dst_file.name} (not in source)")
            dst_file.unlink()

def cleanup_deprecated_docs(src_docs, dst_docs):
    """Remove directories in docs that no longer exist in the template."""
    if not src_docs.exists() or not dst_docs.exists():
        return
    
    # Get list of directories that should exist (from source)
    src_dirs = {item.name for item in src_docs.iterdir() if item.is_dir()}
    
    # Remove directories that no longer exist in the source
    for dst_item in dst_docs.iterdir():
        if dst_item.is_dir() and dst_item.name not in src_dirs:
            print(f"     ✗ Removing deprecated docs directory: {dst_item.name}/")
            shutil.rmtree(dst_item)

def update_all_deployments():
    """Update all tracked deployments with latest templates."""

    if not REGISTRY_FILE.exists():
        print("[WARNING] No registry file found at ~/.multiagent.json")
        return

    with open(REGISTRY_FILE) as f:
        data = json.load(f)

    templates_dir = CORE_PROJECT / "multiagent_core" / "templates"

    # Standard format: {version, framework_version, projects: [...], settings}
    if 'projects' not in data or not isinstance(data['projects'], list):
        print("[ERROR] Invalid registry format - expected 'projects' array")
        return

    # Filter projects by autoUpdate preference
    projects = []
    for proj in data['projects']:
        if 'path' in proj and proj['path']:
            path = Path(proj['path'])
            if path.exists():
                # Only auto-update if explicitly enabled (respects user choice)
                if proj.get('autoUpdate', False):
                    projects.append(str(path))
                else:
                    print(f"[SKIP] {proj.get('name', 'unknown')} (autoUpdate: false)")
            else:
                print(f"[WARNING] Project path not found: {proj.get('name', 'unknown')} at {proj['path']}")

    if not projects:
        print("[INFO] No projects with autoUpdate enabled")
        return

    print(f"[UPDATE] Auto-updating {len(projects)} project(s) with autoUpdate enabled...")

    # ARCHITECTURE: Projects get specific files, not full .multiagent/
    # - Templates stay in ~/.multiagent/ (global)
    # - Projects get: .github/ configs, git hooks
    # - NOT: workflows (generated by agents), NOT: full .multiagent/ templates

    global_multiagent = Path.home() / ".multiagent"

    for project_path in projects:
        project = Path(project_path)

        if not project.exists():
            print(f"[WARNING]  Skipping {project_path} (not found)")
            continue

        print(f"[PACKAGE] Updating: {project.name}")

        # 1. Update .github/ISSUE_TEMPLATE/ (from core/templates/github-config/)
        # Only update if directory exists (user hasn't removed it)
        src_issue_templates = global_multiagent / "core" / "templates" / "github-config" / "ISSUE_TEMPLATE"
        dst_issue_templates = project / ".github" / "ISSUE_TEMPLATE"
        if src_issue_templates.exists() and dst_issue_templates.exists():
            for template_file in src_issue_templates.glob("*.yml"):
                shutil.copy2(template_file, dst_issue_templates / template_file.name)
            print(f"   [SYNC] .github/ISSUE_TEMPLATE/ (5 templates)")

        # 2. Update .github/copilot-instructions.md (from core/templates/github-config/)
        # Only update if file exists (user hasn't removed it)
        src_copilot = global_multiagent / "core" / "templates" / "github-config" / "copilot-instructions.md"
        dst_copilot = project / ".github" / "copilot-instructions.md"
        if src_copilot.exists() and dst_copilot.exists():
            shutil.copy2(src_copilot, dst_copilot)
            print(f"   [SYNC] .github/copilot-instructions.md")

        # 3. Update git hooks (from agents/hooks/ and security/hooks/)
        git_hooks_dir = project / ".git" / "hooks"
        if git_hooks_dir.exists():
            # Post-commit hook
            src_post_commit = global_multiagent / "agents" / "hooks" / "post-commit"
            if src_post_commit.exists():
                shutil.copy2(src_post_commit, git_hooks_dir / "post-commit")
                (git_hooks_dir / "post-commit").chmod(0o755)
                print(f"   [SYNC] .git/hooks/post-commit")

            # Pre-push hook
            src_pre_push = global_multiagent / "security" / "hooks" / "pre-push"
            if src_pre_push.exists():
                shutil.copy2(src_pre_push, git_hooks_dir / "pre-push")
                (git_hooks_dir / "pre-push").chmod(0o755)
                print(f"   [SYNC] .git/hooks/pre-push")

        # NOTE: .github/workflows/ are NOT synced - generated by agents from templates

        print(f"   [OK] Updated {project.name}")
    
    # Update timestamps for all projects
    current_time = datetime.now().isoformat()
    for proj in data['projects']:
        proj['last_updated'] = current_time

    # Save updated registry
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] All deployments updated at {current_time}")

def hook_into_build():
    """Called after build to update all deployments."""
    print("\n" + "="*50)
    print("[AUTO-UPDATE] MULTIAGENT-CORE AUTO-UPDATE SYSTEM")
    print("="*50)
    update_all_deployments()
    print("="*50 + "\n")

if __name__ == "__main__":
    # Test the auto-updater
    update_all_deployments()