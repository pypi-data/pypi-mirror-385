"""Command parser and analyzer."""

import re
from typing import Any


class CommandParser:
    """Parse and analyze terminal commands."""

    # Common dangerous command patterns
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r":\s*\(\s*\)\s*{\s*:\s*\|\s*:\s*&\s*}\s*;\s*:",  # Fork bomb
        r"dd\s+if=/dev/zero",
        r"mkfs\.",
        r"chmod\s+-R\s+777",
    ]

    # Common error patterns
    ERROR_PATTERNS = {
        "permission_denied": r"permission denied",
        "command_not_found": r"command not found",
        "no_such_file": r"no such file or directory",
        "connection_refused": r"connection refused",
        "port_in_use": r"address already in use",
    }

    def __init__(self) -> None:
        """Initialize command parser."""
        pass

    def parse_command(self, command: str) -> dict[str, Any]:
        """Parse a command into its components."""
        parts = command.strip().split()
        if not parts:
            return {"raw": command, "base_command": "", "args": [], "flags": []}

        base_command = parts[0]
        args = []
        flags = []

        for part in parts[1:]:
            if part.startswith("-"):
                flags.append(part)
            else:
                args.append(part)

        return {
            "raw": command,
            "base_command": base_command,
            "args": args,
            "flags": flags,
            "is_sudo": command.strip().startswith("sudo"),
            "is_piped": "|" in command,
            "is_redirected": ">" in command or "<" in command,
        }

    def is_dangerous(self, command: str) -> tuple[bool, str | None]:
        """Check if a command is potentially dangerous."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True, f"Potentially dangerous pattern detected: {pattern}"
        return False, None

    def detect_error_type(self, error_output: str) -> str | None:
        """Detect the type of error from output."""
        error_lower = error_output.lower()

        for error_type, pattern in self.ERROR_PATTERNS.items():
            if re.search(pattern, error_lower):
                return error_type

        return None

    def extract_error_message(self, output: str) -> str | None:
        """Extract the main error message from command output."""
        lines = output.strip().split("\n")

        # Look for common error indicators
        error_lines = []
        for line in lines:
            lower_line = line.lower()
            if any(
                indicator in lower_line
                for indicator in ["error", "failed", "fatal", "exception", "denied"]
            ):
                error_lines.append(line.strip())

        return "\n".join(error_lines) if error_lines else None

    def suggest_alternatives(self, command: str) -> list[str]:
        """Suggest alternative commands or corrections."""
        parsed = self.parse_command(command)
        base_cmd = parsed["base_command"]

        # Common command alternatives
        alternatives_map = {
            "ls": ["exa", "lsd", "tree"],
            "cat": ["bat", "less", "more"],
            "grep": ["rg", "ag", "ack"],
            "find": ["fd", "locate"],
            "du": ["ncdu", "dust"],
            "top": ["htop", "btop", "glances"],
            "ps": ["procs", "htop"],
        }

        suggestions = []

        # Check for alternatives
        if base_cmd in alternatives_map:
            suggestions.extend(
                [
                    f"Consider using {alt} instead of {base_cmd}"
                    for alt in alternatives_map[base_cmd]
                ]
            )

        # Check for common typos
        if base_cmd == "sl":
            suggestions.append("Did you mean: ls")
        elif base_cmd == "cd..":
            suggestions.append("Did you mean: cd ..")
        elif base_cmd == "claer":
            suggestions.append("Did you mean: clear")

        return suggestions

    def analyze_command_chain(self, command: str) -> dict[str, Any]:
        """Analyze a command chain (with pipes, redirects, etc.)."""
        analysis = {
            "commands": [],
            "has_pipe": "|" in command,
            "has_redirect": ">" in command or "<" in command,
            "has_background": "&" in command and "&&" not in command,
            "has_logical_and": "&&" in command,
            "has_logical_or": "||" in command,
        }

        # Split by pipes
        if "|" in command:
            pipe_parts = command.split("|")
            analysis["commands"] = [part.strip() for part in pipe_parts]
        else:
            analysis["commands"] = [command.strip()]

        return analysis

    def get_command_category(self, command: str) -> str:
        """Categorize a command by its purpose."""
        parsed = self.parse_command(command)
        base_cmd = parsed["base_command"]

        categories = {
            "file_operations": [
                "ls",
                "cd",
                "cp",
                "mv",
                "rm",
                "mkdir",
                "touch",
                "chmod",
                "chown",
            ],
            "text_processing": [
                "cat",
                "grep",
                "sed",
                "awk",
                "cut",
                "sort",
                "uniq",
                "wc",
            ],
            "system_info": ["ps", "top", "htop", "free", "df", "du", "uptime", "uname"],
            "network": [
                "ping",
                "curl",
                "wget",
                "ssh",
                "scp",
                "netstat",
                "ifconfig",
                "ip",
            ],
            "package_management": ["apt", "yum", "dnf", "brew", "pip", "npm", "cargo"],
            "version_control": ["git", "svn", "hg"],
            "compression": ["tar", "zip", "unzip", "gzip", "bzip2"],
            "search": ["find", "locate", "which", "whereis"],
        }

        for category, commands in categories.items():
            if base_cmd in commands:
                return category

        return "other"
