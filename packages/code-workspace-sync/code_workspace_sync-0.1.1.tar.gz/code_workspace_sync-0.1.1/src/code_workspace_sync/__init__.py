"""
VS Code Workspace Synchronizer

A script to synchronize a VS Code workspace with directories in a source repositories folder.
It can add new directories and optionally remove directories that no longer exist.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def parse_jsonc(text: str) -> Dict[str, Any]:
    """
    Parse JSON with Comments (JSONC) format by removing comments and trailing commas.

    Args:
        text: The JSONC text to parse

    Returns:
        Parsed JSON object
    """
    # Remove single-line comments (// ...)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)

    # Remove multi-line comments (/* ... */)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    # Remove trailing commas before closing brackets/braces
    text = re.sub(r",\s*([}\]])", r"\1", text)

    return json.loads(text)


def format_jsonc(obj: Dict[str, Any], indent: str = "\t") -> str:
    """
    Format a JSON object as JSONC (preserving VS Code style).

    Args:
        obj: The object to format
        indent: Indentation to use

    Returns:
        Formatted JSONC string
    """
    return json.dumps(obj, indent=indent)


class WorkspaceSyncer:
    """Manages synchronization between src_repos directories and VS Code workspace."""

    def __init__(
        self, workspace_file: Path, src_repos_path: Path, verbose: bool = False
    ):
        self.workspace_file = workspace_file
        self.src_repos_path = src_repos_path
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")

    def get_current_workspace_folders(self) -> List[Dict[str, str]]:
        """Read and return the current workspace folder configuration."""
        try:
            with open(self.workspace_file, "r", encoding="utf-8") as f:
                content = f.read()
            workspace_config = parse_jsonc(content)
            return workspace_config.get("folders", [])
        except FileNotFoundError:
            self.log(f"Workspace file not found: {self.workspace_file}", "ERROR")
            return []
        except (json.JSONDecodeError, ValueError) as e:
            self.log(f"Invalid JSON in workspace file: {e}", "ERROR")
            return []

    def get_src_repos_directories(self) -> Set[str]:
        """Get all directory names in the src_repos path."""
        if not self.src_repos_path.exists():
            self.log(
                f"Source repos path does not exist: {self.src_repos_path}", "ERROR"
            )
            return set()

        directories = set()
        for item in self.src_repos_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                directories.add(item.name)
                self.log(f"Found directory: {item.name}")

        return directories

    def get_workspace_src_repos_folders(
        self, folders: List[Dict[str, str]]
    ) -> Set[str]:
        """Extract src_repos folder names from workspace configuration."""
        src_repos_folders = set()
        src_repos_prefix = "src_repos/"

        for folder in folders:
            path = folder.get("path", "")
            if path.startswith(src_repos_prefix):
                # Extract the directory name after src_repos/
                dir_name = path[len(src_repos_prefix) :]
                if "/" not in dir_name:  # Only direct subdirectories
                    src_repos_folders.add(dir_name)
                    self.log(f"Found workspace src_repos folder: {dir_name}")

        return src_repos_folders

    def create_folder_entry(self, dir_name: str) -> Dict[str, str]:
        """Create a folder entry for the workspace configuration."""
        return {"path": f"src_repos/{dir_name}"}

    def sync_workspace(
        self, remove_missing: bool = False, dry_run: bool = False
    ) -> bool:
        """
        Synchronize the workspace with src_repos directories.

        Args:
            remove_missing: Whether to remove folders from workspace that don't exist in src_repos
            dry_run: If True, only show what would be changed without making changes

        Returns:
            True if changes were made (or would be made in dry_run), False otherwise
        """
        self.log("Starting workspace synchronization...")

        # Get current state
        current_folders = self.get_current_workspace_folders()
        src_repos_dirs = self.get_src_repos_directories()
        workspace_src_repos = self.get_workspace_src_repos_folders(current_folders)

        # Calculate changes needed
        to_add = src_repos_dirs - workspace_src_repos
        to_remove = workspace_src_repos - src_repos_dirs if remove_missing else set()

        if not to_add and not to_remove:
            print("✅ Workspace is already in sync!")
            return False

        # Show what will be changed
        if to_add:
            print(f"📁 Directories to add: {', '.join(sorted(to_add))}")
        if to_remove:
            print(f"🗑️  Directories to remove: {', '.join(sorted(to_remove))}")

        if dry_run:
            print("🔍 Dry run mode - no changes will be made")
            return True

        # Create new folder list
        new_folders = []

        # Keep existing folders that aren't being removed
        for folder in current_folders:
            path = folder.get("path", "")
            if path.startswith("src_repos/"):
                dir_name = path[len("src_repos/") :]
                if "/" not in dir_name and dir_name in to_remove:
                    self.log(f"Removing folder: {dir_name}")
                    continue
            new_folders.append(folder)

        # Add new folders
        for dir_name in sorted(to_add):
            new_folder = self.create_folder_entry(dir_name)
            new_folders.append(new_folder)
            self.log(f"Adding folder: {dir_name}")

        # Update workspace file
        try:
            with open(self.workspace_file, "r", encoding="utf-8") as f:
                content = f.read()
            workspace_config = parse_jsonc(content)

            workspace_config["folders"] = new_folders

            with open(self.workspace_file, "w", encoding="utf-8") as f:
                formatted_content = format_jsonc(workspace_config, indent="\t")
                f.write(formatted_content)

            print("✅ Workspace updated successfully!")
            return True

        except Exception as e:
            self.log(f"Error updating workspace file: {e}", "ERROR")
            return False


def find_workspace_file() -> Optional[Path]:
    """
    Find a .code-workspace file in the current directory.

    Returns:
        Path to the workspace file if exactly one is found, None otherwise.
    """
    current_dir = Path.cwd()
    workspace_files = list(current_dir.glob("*.code-workspace"))

    if len(workspace_files) == 0:
        print("❌ No .code-workspace file found in the current directory.")
        print("   Please specify a workspace file with --workspace")
        return None
    elif len(workspace_files) == 1:
        return workspace_files[0]
    else:
        print("⚠️  Multiple .code-workspace files found:")
        for wf in workspace_files:
            print(f"   - {wf.name}")
        print("   Please specify which one to use with --workspace")
        return None


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Synchronize VS Code workspace with src_repos directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic sync (add missing directories)
  python sync_workspace.py

  # Sync with custom paths
  python sync_workspace.py --src-repos ./repositories --workspace my-workspace.code-workspace

  # Sync and remove missing directories
  python sync_workspace.py --remove-missing

  # Dry run to see what would change
  python sync_workspace.py --dry-run --verbose

  # Full sync with verbose output
  python sync_workspace.py --remove-missing --verbose
""",
    )

    parser.add_argument(
        "--src-repos",
        type=Path,
        default=Path("src_repos"),
        help="Path to the source repositories directory (default: src_repos)",
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Path to the VS Code workspace file (default: auto-detect in current directory)",
    )

    parser.add_argument(
        "--remove-missing",
        action="store_true",
        help="Remove directories from workspace that no longer exist in src_repos",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making any modifications",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Auto-detect workspace file if not specified
    if args.workspace is None:
        workspace_file = find_workspace_file()
        if workspace_file is None:
            sys.exit(1)
    else:
        workspace_file = args.workspace.resolve()

    # Convert src_repos to absolute path if it's relative
    src_repos_path = args.src_repos.resolve()

    # Validate inputs
    if not workspace_file.exists():
        print(f"❌ Workspace file not found: {workspace_file}")
        sys.exit(1)

    if not src_repos_path.exists():
        print(f"❌ Source repos directory not found: {src_repos_path}")
        sys.exit(1)

    if args.verbose:
        print(f"🔧 Workspace file: {workspace_file}")
        print(f"📂 Source repos path: {src_repos_path}")
        print(f"🗑️  Remove missing: {args.remove_missing}")
        print(f"🔍 Dry run: {args.dry_run}")
        print()

    # Create syncer and run
    syncer = WorkspaceSyncer(workspace_file, src_repos_path, args.verbose)

    try:
        changes_made = syncer.sync_workspace(
            remove_missing=args.remove_missing, dry_run=args.dry_run
        )

        if changes_made and not args.dry_run:
            print("\n💡 You may need to reload VS Code for changes to take effect.")

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
