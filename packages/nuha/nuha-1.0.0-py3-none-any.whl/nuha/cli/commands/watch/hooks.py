"""Shell hook generation for watch command."""

import sys
from pathlib import Path


def generate_bash_hooks(watch_jsonl_file: Path) -> str:
    """Generate bash shell hooks."""
    python_path = sys.executable
    return f"""
# Nuha watch hooks for Bash
export NUHA_WATCH_ACTIVE=1
export NUHA_WATCH_LOG="{str(watch_jsonl_file)}"
export NUHA_WATCH_ORIG_PROMPT_COMMAND="$PROMPT_COMMAND"

__nuha_preexec() {{
    [ "$BASH_COMMAND" != "$PROMPT_COMMAND" ] && {python_path} -c "from nuha.core.capture import capture_event; capture_event('cmd', '$BASH_COMMAND')" 2>/dev/null
}}

__nuha_postcmd() {{
    {python_path} -c "from nuha.core.capture import capture_event; capture_event('result', '$?')" 2>/dev/null
    $NUHA_WATCH_ORIG_PROMPT_COMMAND
}}

trap '__nuha_preexec' DEBUG
PROMPT_COMMAND='__nuha_postcmd'
echo "✓ Nuha watch monitoring started (eval mode)"
"""


def generate_zsh_hooks(watch_jsonl_file: Path) -> str:
    """Generate zsh shell hooks."""
    python_path = sys.executable
    return f"""
# Nuha watch hooks for Zsh
export NUHA_WATCH_ACTIVE=1
export NUHA_WATCH_LOG="{str(watch_jsonl_file)}"

preexec() {{
    {python_path} -c "from nuha.core.capture import capture_event; capture_event('cmd', '$1')" 2>/dev/null
}}

precmd() {{
    {python_path} -c "from nuha.core.capture import capture_event; capture_event('result', '$?')" 2>/dev/null
}}

echo "✓ Nuha watch monitoring started (eval mode)"
"""


def generate_bash_stop_hooks() -> str:
    """Generate bash stop hooks."""
    return """
trap - DEBUG
PROMPT_COMMAND="$NUHA_WATCH_ORIG_PROMPT_COMMAND"
unset NUHA_WATCH_ACTIVE NUHA_WATCH_LOG NUHA_WATCH_ORIG_PROMPT_COMMAND
unset -f __nuha_preexec __nuha_postcmd
echo "✓ Nuha watch monitoring stopped"
"""


def generate_zsh_stop_hooks() -> str:
    """Generate zsh stop hooks."""
    return """
unfunction preexec precmd
unset NUHA_WATCH_ACTIVE NUHA_WATCH_LOG
echo "✓ Nuha watch monitoring stopped"
"""


def generate_shell_hooks(shell: str, watch_jsonl_file: Path, stop: bool = False) -> str:
    """Generate appropriate shell hooks."""
    if stop:
        if "bash" in shell:
            return generate_bash_stop_hooks()
        elif "zsh" in shell:
            return generate_zsh_stop_hooks()
        else:
            return f"# Unsupported shell: {shell}"
    else:
        if "bash" in shell:
            return generate_bash_hooks(watch_jsonl_file)
        elif "zsh" in shell:
            return generate_zsh_hooks(watch_jsonl_file)
        else:
            return f"# Unsupported shell: {shell}"
