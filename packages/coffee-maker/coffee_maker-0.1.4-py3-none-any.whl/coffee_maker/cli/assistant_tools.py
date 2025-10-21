"""Tools for LangChain-powered assistant in project-manager.

This module provides tools that the assistant can use to help answer
complex questions and perform technical analysis.

PRIORITY 2.9.5: Transparent Assistant Integration
+ Bug Ticket Creation for DoD Validation
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    """Input for ReadFileTool."""

    file_path: str = Field(description="Path to the file to read")
    start_line: Optional[int] = Field(default=None, description="Start line number (optional)")
    end_line: Optional[int] = Field(default=None, description="End line number (optional)")


class ReadFileTool(BaseTool):
    """Tool to read file contents."""

    name: str = "read_file"
    description: str = (
        "Read contents of a file. Use this to examine source code, documentation, or configuration files."
    )
    args_schema: type[BaseModel] = ReadFileInput

    def _run(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        """Read file contents."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File {file_path} does not exist"

            with open(path, "r") as f:
                lines = f.readlines()

            if start_line is not None and end_line is not None:
                lines = lines[start_line - 1 : end_line]
            elif start_line is not None:
                lines = lines[start_line - 1 :]

            return "".join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"


class SearchCodeInput(BaseModel):
    """Input for SearchCodeTool."""

    pattern: str = Field(description="Pattern to search for (regex supported)")
    file_pattern: Optional[str] = Field(default="*.py", description="File pattern to search in (e.g., *.py, *.md)")
    directory: Optional[str] = Field(default=".", description="Directory to search in")


class SearchCodeTool(BaseTool):
    """Tool to search code using grep."""

    name: str = "search_code"
    description: str = (
        "Search for patterns in code files. Use this to find function definitions, class names, or specific code patterns."
    )
    args_schema: type[BaseModel] = SearchCodeInput

    def _run(self, pattern: str, file_pattern: str = "*.py", directory: str = ".") -> str:
        """Search code using grep."""
        try:
            cmd = ["grep", "-r", "-n", "--include", file_pattern, pattern, directory]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No matches found"
            elif result.returncode == 1:
                return "No matches found"
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Search timed out"
        except Exception as e:
            return f"Error: {str(e)}"


class ListFilesInput(BaseModel):
    """Input for ListFilesTool."""

    pattern: str = Field(description="File pattern to match (e.g., **/*.py, *.md)")
    directory: Optional[str] = Field(default=".", description="Directory to search in")


class ListFilesTool(BaseTool):
    """Tool to list files matching a pattern."""

    name: str = "list_files"
    description: str = "List files matching a pattern. Use this to discover files in the codebase."
    args_schema: type[BaseModel] = ListFilesInput

    def _run(self, pattern: str, directory: str = ".") -> str:
        """List files using glob."""
        try:
            path = Path(directory)
            files = list(path.glob(pattern))

            if not files:
                return "No files found matching pattern"

            return "\n".join(str(f) for f in sorted(files)[:100])  # Limit to 100 files
        except Exception as e:
            return f"Error: {str(e)}"


class GitLogInput(BaseModel):
    """Input for GitLogTool."""

    max_commits: Optional[int] = Field(default=10, description="Maximum number of commits to show")
    file_path: Optional[str] = Field(default=None, description="Show commits for specific file (optional)")


class GitLogTool(BaseTool):
    """Tool to view git commit history."""

    name: str = "git_log"
    description: str = (
        "View recent git commit history. Use this to understand recent changes or find when something was modified."
    )
    args_schema: type[BaseModel] = GitLogInput

    def _run(self, max_commits: int = 10, file_path: Optional[str] = None) -> str:
        """Get git log."""
        try:
            cmd = ["git", "log", f"-{max_commits}", "--oneline"]
            if file_path:
                cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No commits found"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitDiffInput(BaseModel):
    """Input for GitDiffTool."""

    file_path: Optional[str] = Field(default=None, description="Show diff for specific file (optional)")
    commit: Optional[str] = Field(default=None, description="Compare with specific commit (optional)")


class GitDiffTool(BaseTool):
    """Tool to view git differences."""

    name: str = "git_diff"
    description: str = "View git differences. Use this to see what changed in files or between commits."
    args_schema: type[BaseModel] = GitDiffInput

    def _run(self, file_path: Optional[str] = None, commit: Optional[str] = None) -> str:
        """Get git diff."""
        try:
            cmd = ["git", "diff"]
            if commit:
                cmd.append(commit)
            if file_path:
                cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout if result.stdout else "No differences found"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class ExecuteBashInput(BaseModel):
    """Input for ExecuteBashTool."""

    command: str = Field(description="Bash command to execute")


class ExecuteBashTool(BaseTool):
    """Tool to execute bash commands (read-only operations)."""

    name: str = "execute_bash"
    description: str = (
        "Execute bash commands for read-only operations like ls, cat, ps, etc. "
        "DO NOT use for write operations. Use this to check system state or process info."
    )
    args_schema: type[BaseModel] = ExecuteBashInput

    def _run(self, command: str) -> str:
        """Execute bash command."""
        # Safety check - only allow read-only commands
        dangerous_commands = ["rm", "mv", "cp", "dd", ">", ">>", "chmod", "chown"]
        if any(cmd in command.lower() for cmd in dangerous_commands):
            return "Error: Write operations not allowed"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path.cwd(),
            )

            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command executed successfully (no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"


class CreateBugTicketInput(BaseModel):
    """Input for CreateBugTicketTool."""

    title: str = Field(description="Brief description of the bug (e.g., 'Tests failing in test_developer_status.py')")
    dod_criterion: str = Field(description="Which DoD criterion was being validated (e.g., 'All tests passing')")
    priority_name: str = Field(description="Priority or feature being tested (e.g., 'PRIORITY 4')")
    command_run: str = Field(description="Exact command that was run (e.g., 'pytest tests/ -v')")
    expected_behavior: str = Field(description="What should have happened")
    actual_behavior: str = Field(description="What actually happened")
    exit_code: Optional[int] = Field(default=None, description="Command exit code (if available)")
    error_output: Optional[str] = Field(default=None, description="Error output or relevant excerpts")
    error_analysis: Optional[str] = Field(default=None, description="Brief analysis of what went wrong")
    related_files: Optional[str] = Field(default=None, description="Comma-separated list of related files")
    suggested_actions: Optional[str] = Field(
        default=None, description="Suggested actions to fix (one per line, numbered)"
    )


class CreateBugTicketTool(BaseTool):
    """Tool to create bug tickets when DoD validation fails."""

    name: str = "create_bug_ticket"
    description: str = (
        "Create a bug ticket when DoD validation fails, tests crash, or unexpected behavior is discovered. "
        "Use this whenever a command fails (non-zero exit code) or produces unexpected results during validation."
    )
    args_schema: type[BaseModel] = CreateBugTicketInput

    def _run(
        self,
        title: str,
        dod_criterion: str,
        priority_name: str,
        command_run: str,
        expected_behavior: str,
        actual_behavior: str,
        exit_code: Optional[int] = None,
        error_output: Optional[str] = None,
        error_analysis: Optional[str] = None,
        related_files: Optional[str] = None,
        suggested_actions: Optional[str] = None,
    ) -> str:
        """Create bug ticket."""
        try:
            # Find next BUG number
            tickets_dir = Path("tickets")
            tickets_dir.mkdir(exist_ok=True)

            existing_bugs = list(tickets_dir.glob("BUG-*.md"))
            if existing_bugs:
                # Extract numbers and find max
                numbers = []
                for bug_file in existing_bugs:
                    try:
                        num = int(bug_file.stem.split("-")[1])
                        numbers.append(num)
                    except (IndexError, ValueError):
                        continue
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1

            bug_id = f"BUG-{next_num:03d}"
            bug_file = tickets_dir / f"{bug_id}.md"

            # Get current git commit
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                git_commit = result.stdout.strip() if result.returncode == 0 else "unknown"
            except Exception:
                git_commit = "unknown"

            # Build bug ticket content
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Determine priority based on keywords
            priority = "Critical"
            if "test" in title.lower() or "failing" in title.lower():
                priority = "Critical"
            elif "build" in title.lower():
                priority = "Critical"
            elif "crash" in title.lower():
                priority = "High"

            content = f"""# {bug_id}: {title}

**Status**: 🔴 Open
**Priority**: {priority}
**Created**: {timestamp}
**Reporter**: Assistant (DoD Validation)
**Assigned**: code_developer

## Description

Bug discovered during DoD validation for {priority_name}.

## What I Was Testing

**DoD Criterion**: {dod_criterion}

**Priority/Feature**: {priority_name}

## Steps to Reproduce

1. Run: `{command_run}`
2. Observe: {actual_behavior}

## Expected Behavior

{expected_behavior}

## Actual Behavior

"""

            if exit_code is not None:
                content += f"**Exit Code**: {exit_code} {'(failure)' if exit_code != 0 else '(success)'}\n\n"

            if error_output:
                content += f"""**Output**:
```
{error_output}
```

"""

            if error_analysis:
                content += f"""**Error Analysis**:
{error_analysis}

"""

            content += f"""## Impact on DoD

❌ DoD criterion "{dod_criterion}" is **NOT MET**

This blocks:
- [ ] Marking {priority_name} as complete
- [ ] Merging PR
- [ ] Moving to next priority

## Additional Context

**Environment**:
- Git commit: {git_commit}
- Timestamp: {timestamp}

"""

            if related_files:
                content += f"""**Related Files**:
{chr(10).join('- ' + f.strip() for f in related_files.split(','))}

"""

            if suggested_actions:
                content += f"""## Suggested Actions

{suggested_actions}

"""

            content += """## Definition of Done

- [ ] Bug reproduced locally
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Tests added (if needed)
- [ ] All tests passing
- [ ] DoD criterion validated
- [ ] Bug ticket updated with resolution
"""

            # Write bug ticket
            with open(bug_file, "w") as f:
                f.write(content)

            return f"✅ Created {bug_id}: {title}\nFile: {bug_file}\n\nBug ticket created successfully. PM should review and assign to code_developer."

        except Exception as e:
            return f"Error creating bug ticket: {str(e)}"


def get_assistant_tools() -> List[BaseTool]:
    """Get all tools available to the assistant.

    Returns:
        List of LangChain tools
    """
    return [
        ReadFileTool(),
        SearchCodeTool(),
        ListFilesTool(),
        GitLogTool(),
        GitDiffTool(),
        ExecuteBashTool(),
        CreateBugTicketTool(),
    ]
