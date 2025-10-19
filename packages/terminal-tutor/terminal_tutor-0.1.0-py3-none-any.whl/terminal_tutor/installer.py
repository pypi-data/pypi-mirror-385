"""Shell integration installer."""

import os
import shutil
from pathlib import Path


class ShellInstaller:
    """Install and manage shell integration."""

    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".config" / "terminal-tutor"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_shell_config_file(self):
        """Detect and return the appropriate shell config file."""
        shell = os.environ.get('SHELL', '').lower()

        if 'zsh' in shell:
            return self.home / '.zshrc'
        elif 'fish' in shell:
            return self.home / '.config' / 'fish' / 'config.fish'
        else:  # Default to bash
            bashrc = self.home / '.bashrc'
            bash_profile = self.home / '.bash_profile'
            return bashrc if bashrc.exists() else bash_profile

    def get_shell_integration_code(self):
        """Get the shell integration code."""
        shell = os.environ.get('SHELL', '').lower()

        if 'zsh' in shell:
            return self._get_zsh_realtime_integration()
        else:
            return self._get_bash_integration()

    def _get_zsh_realtime_integration(self):
        """Get advanced Zsh real-time integration."""
        zsh_file = Path(__file__).parent / "zsh_integration.zsh"
        if zsh_file.exists():
            return '\n# Terminal Tutor Integration - Start\n' + zsh_file.read_text() + '\n# Terminal Tutor Integration - End\n'
        else:
            # Fallback to basic integration if file not found
            return self._get_bash_integration()

    def _get_bash_integration(self):
        """Get basic Bash/universal integration."""
        return '''
# Terminal Tutor Integration - Start

# Simple real-time prediction via trap DEBUG
function tt_predict_live() {
    local cmd="$BASH_COMMAND"

    # Skip our internal commands
    [[ "$cmd" =~ ^(tt_|terminal-tutor) ]] && return

    # Only show predictions for commands we recognize, silently ignore others
    if [[ "$TT_LIVE_MODE" == "enabled" ]]; then
        local prediction=""
        if command -v terminal-tutor >/dev/null 2>&1; then
            prediction=$(terminal-tutor explain --no-confirm "$cmd" 2>/dev/null)
        fi

        # Only show if we have a real match (not "not found")
        if [[ -n "$prediction" && "$prediction" != *"not found"* ]]; then
            echo -e "\\033[90m$prediction\\033[0m"
        fi
    fi
}

function tt_explain() {
    local cmd="$1"
    shift
    local full_cmd="$cmd $@"

    # Show live prediction if enabled
    if [[ "$TT_LIVE_MODE" == "enabled" ]]; then
        local prediction=""
        if command -v terminal-tutor >/dev/null 2>&1; then
            prediction=$(terminal-tutor explain --no-confirm "$full_cmd" 2>/dev/null)
        fi

        if [[ -n "$prediction" ]]; then
            echo -e "\\033[90m$prediction\\033[0m"
        fi
    fi

    # Use the installed terminal-tutor command directly (cleaner than python -m)
    if command -v terminal-tutor >/dev/null 2>&1; then
        terminal-tutor explain --no-confirm "$cmd" "$@"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m terminal_tutor.cli explain --no-confirm "$cmd" "$@"
    elif command -v python >/dev/null 2>&1; then
        python -m terminal_tutor.cli explain --no-confirm "$cmd" "$@"
    else
        echo "Error: terminal-tutor not found and no python interpreter available"
        return 1
    fi

    # Check exit status for dangerous commands
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Command explanation failed or cancelled."
        return 1
    fi

    # Ask for confirmation
    echo -n "Execute command? [Y/n]: "
    read -r response
    case "$response" in
        [nN][oO]|[nN])
            echo "Command cancelled."
            return 1
            ;;
        *)
            "$cmd" "$@"
            ;;
    esac
}

# Create aliases for common commands
alias kubectl='tt_explain kubectl'
alias docker='tt_explain docker'
alias git='tt_explain git'
alias systemctl='tt_explain systemctl'
alias rm='tt_explain rm'
alias chmod='tt_explain chmod'
alias chown='tt_explain chown'
alias iptables='tt_explain iptables'
alias ufw='tt_explain ufw'

# Note: Use 'terminal-tutor enable/disable/toggle' to control Terminal Tutor
# Terminal Tutor Integration - End
'''

    def install(self):
        """Install shell integration."""
        config_file = self.get_shell_config_file()
        integration_code = self.get_shell_integration_code()

        # Check if already installed
        if config_file.exists():
            content = config_file.read_text()
            if "Terminal Tutor Integration" in content:
                print("✅ Terminal Tutor is already installed!")
                return

        # Append integration code
        with open(config_file, 'a') as f:
            f.write('\n')
            f.write(integration_code)

        print("✅ Terminal Tutor installed successfully!")
        print("🔄 Restart terminal with: source ~/.zshrc or exec zsh")

    def uninstall(self):
        """Uninstall shell integration."""
        config_file = self.get_shell_config_file()

        if not config_file.exists():
            print("❌ No shell configuration file found.")
            return

        content = config_file.read_text()

        # Remove integration code
        lines = content.split('\n')
        filtered_lines = []
        skip = False

        for line in lines:
            if "Terminal Tutor Integration - Start" in line:
                skip = True
                continue
            elif "Terminal Tutor Integration - End" in line:
                skip = False
                continue

            if not skip:
                filtered_lines.append(line)

        # Write back the filtered content
        config_file.write_text('\n'.join(filtered_lines))

        print("✅ Terminal Tutor uninstalled successfully!")
        print("🔄 Restart your terminal for changes to take effect.")