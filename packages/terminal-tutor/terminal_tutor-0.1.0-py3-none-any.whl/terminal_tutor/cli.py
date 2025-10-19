"""Command line interface for Terminal Tutor."""

import argparse
import os
import sys
import time
from pathlib import Path
from .core import CommandTutor
from .installer import ShellInstaller
from .openai_manager import OpenAIKeyManager


def format_output(command: str, description: str, risk_level: str) -> str:
    """Format the command description output - lightning fast format with emoji indicators."""
    # Keep the full risk level with emoji (🟢 SAFE, 🟡 CAUTION, 🔴 DANGEROUS)
    risk_display = risk_level if risk_level else "❓ UNKNOWN"
    return f"{risk_display} - {description}"


def debug_command(command: str):
    """Debug command with timing and stats."""
    start_time = time.perf_counter()
    tutor = CommandTutor()

    # Get fuzzy suggestions first (always shows top 3 if available)
    suggestions = tutor.get_fuzzy_suggestions(command, max_results=3)

    # Check if there's an exact match
    exact_match = tutor.get_description(command)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000

    if suggestions and len(suggestions) > 1:
        # Multiple matches - show all as fuzzy
        print("───────────────────────────────────")
        for suggestion in suggestions:
            risk_level = suggestion['risk_level']
            cmd = suggestion['command']
            desc = suggestion['description']
            print(f"{risk_level} {cmd} - {desc}")
        print("───────────────────────────────────")
        match_type = "🎯 exact (+ related)" if exact_match else "🔍 fuzzy"
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 {len(suggestions)} matches | {match_type}")
    elif exact_match and len(suggestions) == 1:
        # Single exact match only - use matched command from suggestion for risk level
        suggestion = suggestions[0]
        matched_command = suggestion['command']
        risk_level = tutor.get_risk_level(matched_command)
        print("───────────────────────────────────")
        print(format_output(command, exact_match, risk_level))
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 1 match | 🎯 exact")
    elif suggestions and len(suggestions) == 1:
        # Single fuzzy match
        suggestion = suggestions[0]
        print("───────────────────────────────────")
        print(f"{suggestion['risk_level']} {suggestion['command']} - {suggestion['description']}")
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 1 match | 🔍 fuzzy")
    else:
        # No matches
        print("───────────────────────────────────")
        print(f"❓ No matches found for '{command}'")
        print("───────────────────────────────────")
        print(f"⏱️  {elapsed_ms:.1f}ms | 📊 0 matches")


def explain_command():
    """Main function to explain a command."""
    if len(sys.argv) < 2:
        print("Usage: terminal-tutor explain <command>")
        sys.exit(1)

    # Join all arguments to form the complete command
    command = " ".join(sys.argv[2:])

    tutor = CommandTutor()
    description = tutor.get_description(command)
    risk_level = tutor.get_risk_level(command)

    if description:
        print(format_output(command, description, risk_level))
    else:
        print(f"❓ Command '{command}' not found in database.")
        print("Consider adding it or check the spelling.")

    # Ask for confirmation if it's a dangerous command
    if risk_level == "🔴 DANGEROUS":
        response = input("\nThis command is potentially dangerous. Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Command cancelled for safety.")
            sys.exit(1)
    elif risk_level == "🟡 CAUTION":
        input("\nPress Enter to continue or Ctrl+C to cancel...")


def install_shell_hooks():
    """Install shell hooks for automatic command explanation."""
    installer = ShellInstaller()
    installer.install()


def uninstall_shell_hooks():
    """Uninstall shell hooks."""
    installer = ShellInstaller()
    installer.uninstall()


def enable_terminal_tutor():
    """Enable Terminal Tutor."""
    disable_file = "/tmp/tt_disabled"
    if os.path.exists(disable_file):
        os.remove(disable_file)
    print("🟢 Enabled")


def disable_terminal_tutor():
    """Disable Terminal Tutor."""
    disable_file = "/tmp/tt_disabled"
    with open(disable_file, 'w') as f:
        f.write("disabled")
    print("🔴 Disabled")


def toggle_terminal_tutor():
    """Toggle Terminal Tutor on/off."""
    disable_file = "/tmp/tt_disabled"
    if os.path.exists(disable_file):
        enable_terminal_tutor()
    else:
        disable_terminal_tutor()


def status_terminal_tutor():
    """Show Terminal Tutor status."""
    disable_file = "/tmp/tt_disabled"
    if os.path.exists(disable_file):
        print("🔴 Disabled")
    else:
        print("🟢 Enabled")


def show_usage_stats():
    """Show daily usage statistics."""
    tutor = CommandTutor()
    is_allowed, usage_info = tutor._check_rate_limit()

    count = usage_info.get("count", 0)
    limit = usage_info.get("limit", float('inf'))

    if limit == float('inf'):
        print("🚀 Unlimited Usage Active")
        print(f"📊 Commands used today: {count}")
        print("⚡ No daily limits currently enforced")
    elif usage_info.get("premium", False):
        print("🌟 Premium User - Unlimited predictions")
        print("🔄 Status: No daily limits")
    else:
        remaining = usage_info.get("remaining", limit)
        print(f"📊 Daily Usage: {count}/{limit} predictions")
        print(f"⏳ Remaining: {remaining} predictions")

        if remaining <= 10:
            print(f"\n⚠️  Only {remaining} predictions left today!")
            print("🌟 Upgrade to Premium for unlimited predictions: terminal-tutor premium info")
        elif remaining <= 25:
            print(f"\n💡 {remaining} predictions remaining - consider upgrading to Premium")


def manage_premium(action: str):
    """Manage premium subscription."""
    tutor = CommandTutor()

    if action == "info":
        if tutor._is_premium_user():
            print("🌟 You have Terminal Tutor Premium!")
            print("✅ Unlimited daily predictions")
            print("✅ Priority support")
            print("✅ Early access to new features")
            print("✅ Custom command libraries")
            print("\n🔧 To deactivate: terminal-tutor premium deactivate")
        else:
            print("💎 Terminal Tutor Premium - $5/month")
            print("🚀 Features:")
            print("  • Unlimited daily predictions (vs 100/day free)")
            print("  • Priority support")
            print("  • Early access to new features")
            print("  • Custom command libraries")
            print("\n🔗 Subscribe: https://terminal-tutor.com/premium")
            print("🔧 After subscribing: terminal-tutor premium activate")

    elif action == "activate":
        if tutor._is_premium_user():
            print("🌟 Premium already activated!")
        else:
            try:
                tutor.premium_file.touch()
                print("🎉 Premium activated successfully!")
                print("🚀 You now have unlimited predictions")
            except Exception as e:
                print(f"❌ Failed to activate premium: {e}")

    elif action == "deactivate":
        if tutor._is_premium_user():
            try:
                tutor.premium_file.unlink()
                print("📴 Premium deactivated")
                print("🔄 Reverted to free tier (100 predictions/day)")
            except Exception as e:
                print(f"❌ Failed to deactivate premium: {e}")
        else:
            print("ℹ️  Premium not currently active")


def manage_config(action: str, config_type: str):
    """Manage configuration settings."""
    if config_type == 'api-key':
        key_manager = OpenAIKeyManager()

        if action == 'set':
            # Force prompt for new API key
            import getpass
            print("🔑 Enter your OpenAI API key")
            print("🔗 Get one here: https://platform.openai.com/api-keys\n")

            try:
                key = getpass.getpass("Enter your OpenAI API key (input hidden): ")
                key = key.strip()

                if not key:
                    print("❌ No key entered. Cancelled.")
                    return

                print("✅ Testing API key...", end=" ", flush=True)
                if key_manager._validate_key(key):
                    print("Valid!")
                    key_manager._save_key(key)
                else:
                    print("❌ Invalid!")
                    print("❌ API key validation failed. Please check your key and try again.")

            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled by user.")

        elif action == 'clear':
            key_manager.clear_key()

        elif action == 'status':
            if key_manager.key_file.exists():
                # Try to validate the stored key
                stored_key = key_manager._load_key_from_file()
                if stored_key:
                    print(f"🔑 API key stored at: {key_manager.key_file}")
                    print("✅ Testing stored key...", end=" ", flush=True)
                    if key_manager._validate_key(stored_key):
                        print("Valid!")
                    else:
                        print("❌ Invalid!")
                        print("💡 Run 'terminal-tutor config api-key set' to update")
                else:
                    print(f"⚠️  Key file exists but is empty: {key_manager.key_file}")
            else:
                print("ℹ️  No API key configured")
                print("💡 Run 'terminal-tutor config api-key set' to configure")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Terminal Tutor - Learn commands as you type")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Explain command (DEPRECATED)
    explain_parser = subparsers.add_parser('explain', help='[DEPRECATED] Explain a command (use debug instead)')
    explain_parser.add_argument('cmd', nargs='+', help='Command to explain')
    explain_parser.add_argument('--no-confirm', action='store_true', help='Show description only, no confirmation prompts')

    # Predict command (for predictions)
    predict_parser = subparsers.add_parser('predict', help='Get command prediction (optimized for speed)')
    predict_parser.add_argument('cmd', nargs='+', help='Command to predict')
    predict_parser.add_argument('--fast', action='store_true', help='Ultra-fast prediction mode (default)')
    predict_parser.add_argument('--realtime', action='store_true', help='Legacy alias for --fast')

    # Install command
    install_parser = subparsers.add_parser('install', help='Install shell integration')

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall shell integration')

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable Terminal Tutor predictions')

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable Terminal Tutor predictions')

    # Toggle command
    toggle_parser = subparsers.add_parser('toggle', help='Toggle Terminal Tutor predictions on/off')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show Terminal Tutor status')

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version')

    # Usage command
    usage_parser = subparsers.add_parser('usage', help='Show daily usage and limits')

    # Premium command
    premium_parser = subparsers.add_parser('premium', help='Manage premium subscription')
    premium_parser.add_argument('action', choices=['info', 'activate', 'deactivate'],
                               help='Premium action: info, activate, or deactivate')

    # Suggest command (DEPRECATED - fuzzy command suggestions)
    suggest_parser = subparsers.add_parser('suggest', help='[DEPRECATED] Get fuzzy command suggestions (use debug instead)')
    suggest_parser.add_argument('partial', help='Partial command to match')
    suggest_parser.add_argument('--count', '-c', type=int, default=3, help='Number of suggestions (default: 3)')

    # Ask command (natural language command search)
    ask_parser = subparsers.add_parser('ask', help='Natural language command search')
    ask_parser.add_argument('query', nargs='+', help='Natural language query (e.g., "how to list files")')

    # Debug command (unified command with timing and stats)
    debug_parser = subparsers.add_parser('debug', help='Debug command lookup with timing and stats')
    debug_parser.add_argument('cmd', nargs='+', help='Command to debug')

    # Mode command (mode management)
    mode_parser = subparsers.add_parser('mode', help='Manage command modes for context-aware filtering')
    mode_subparsers = mode_parser.add_subparsers(dest='mode_action', help='Mode actions')

    # Mode list subcommand
    mode_list_parser = mode_subparsers.add_parser('list', help='List available modes')

    # Mode current subcommand
    mode_current_parser = mode_subparsers.add_parser('current', help='Show current mode')

    # Mode set subcommand
    mode_set_parser = mode_subparsers.add_parser('set', help='Set current mode')
    mode_set_parser.add_argument('mode_name', help='Mode to set (full, aws, docker, k8s, git)')

    # Mode auto subcommand
    mode_auto_parser = mode_subparsers.add_parser('auto', help='Manage auto-detection')
    mode_auto_parser.add_argument('action', choices=['enable', 'disable', 'status'],
                                 help='Auto-detection action')

    # Config command (configuration management)
    config_parser = subparsers.add_parser('config', help='Manage Terminal Tutor configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_type', help='Configuration type')

    # Config api-key subcommand
    config_apikey_parser = config_subparsers.add_parser('api-key', help='Manage OpenAI API key')
    config_apikey_parser.add_argument('action', choices=['set', 'clear', 'status'],
                                     help='API key action: set (configure new key), clear (remove key), status (check key)')

    args = parser.parse_args()

    if args.command == 'explain':
        print("⚠️  DEPRECATED: 'explain' command is deprecated. Use 'debug' instead.")
        print("    Example: terminal-tutor debug <command>\n")
        command = " ".join(args.cmd)
        debug_command(command)

    elif args.command == 'predict':
        command = " ".join(args.cmd)
        tutor = CommandTutor()

        # Check rate limit and get description
        description, usage_info = tutor.get_description_with_rate_limit(command)

        if description:
            # For multi-line descriptions (fuzzy suggestions), print directly
            if '\n' in description:
                print(description)
            else:
                # For single descriptions that already include risk level, print directly
                if description.startswith(('🟢 SAFE', '🟡 CAUTION', '🔴 DANGEROUS')):
                    print(description)
                else:
                    # Single line descriptions without risk level get the standard format
                    risk_level = tutor.get_risk_level(command)
                    print(format_output(command, description, risk_level))
        elif not usage_info.get("is_allowed", True):
            # Rate limit exceeded
            print(tutor.get_premium_upgrade_message())
        # For no description found, stay silent (real-time predictions)

    elif args.command == 'install':
        install_shell_hooks()

    elif args.command == 'uninstall':
        uninstall_shell_hooks()

    elif args.command == 'enable':
        enable_terminal_tutor()

    elif args.command == 'disable':
        disable_terminal_tutor()

    elif args.command == 'toggle':
        toggle_terminal_tutor()

    elif args.command == 'status':
        status_terminal_tutor()

    elif args.command == 'version':
        from . import __version__
        print(f"Terminal Tutor v{__version__}")

    elif args.command == 'usage':
        show_usage_stats()

    elif args.command == 'premium':
        manage_premium(args.action)

    elif args.command == 'suggest':
        print("⚠️  DEPRECATED: 'suggest' command is deprecated. Use 'debug' instead.")
        print("    Example: terminal-tutor debug <command>\n")
        debug_command(args.partial)

    elif args.command == 'ask':
        query = " ".join(args.query)
        tutor = CommandTutor()
        result = tutor.natural_language_search(query)

        if result:
            command = result['command']
            risk_level = result['risk_level']
            description = result['description']
            print(f"{command} - {risk_level} - {description}")
        else:
            print(f"❓ Could not find a command for: '{query}'")
            print("💡 Try: 'terminal-tutor suggest <partial_command>' for fuzzy matching")

    elif args.command == 'debug':
        command = " ".join(args.cmd)
        debug_command(command)

    elif args.command == 'mode':
        tutor = CommandTutor()
        mode_manager = tutor.mode_manager

        if args.mode_action == 'list':
            print("📋 Available Modes:")
            modes = mode_manager.list_modes()
            current_mode = mode_manager.get_effective_mode()

            for mode_name, description in modes.items():
                indicator = "👉" if mode_name == current_mode else "  "
                print(f"{indicator} {mode_name}: {description}")

            if mode_manager.auto_detect_enabled:
                print(f"\n🤖 Auto-detection: Enabled (effective mode: {current_mode})")
            else:
                print(f"\n🤖 Auto-detection: Disabled")

        elif args.mode_action == 'current':
            current_mode = mode_manager.current_mode
            effective_mode = mode_manager.get_effective_mode()

            if mode_manager.auto_detect_enabled and current_mode != effective_mode:
                print(f"📌 Set mode: {current_mode}")
                print(f"🤖 Auto-detected mode: {effective_mode}")
                print(f"✅ Effective mode: {effective_mode}")
            else:
                print(f"✅ Current mode: {current_mode}")

        elif args.mode_action == 'set':
            mode_name = args.mode_name
            if mode_manager.set_mode(mode_name):
                print(f"✅ Mode set to: {mode_name}")
                config = mode_manager.mode_configs.get(mode_name, {})
                if config.get("suppress_commands"):
                    print(f"🚫 Suppressed: {', '.join(config['suppress_commands'])}")
            else:
                print(f"❌ Invalid mode: {mode_name}")
                print("💡 Use 'terminal-tutor mode list' to see available modes")

        elif args.mode_action == 'auto':
            action = args.action
            if action == 'enable':
                mode_manager.enable_auto_detect()
                print("🤖 Auto-detection enabled")
                detected_mode = mode_manager.detect_project_context()
                if detected_mode != "full":
                    print(f"📍 Detected context: {detected_mode} mode")
                else:
                    print("📍 No specific context detected, using full mode")

            elif action == 'disable':
                mode_manager.disable_auto_detect()
                print("🔒 Auto-detection disabled")
                print(f"📌 Using manual mode: {mode_manager.current_mode}")

            elif action == 'status':
                if mode_manager.auto_detect_enabled:
                    print("🤖 Auto-detection: Enabled")
                    detected_mode = mode_manager.detect_project_context()
                    print(f"📍 Current context: {detected_mode} mode")
                else:
                    print("🔒 Auto-detection: Disabled")
        else:
            print("Usage: terminal-tutor mode {list,current,set,auto}")

    elif args.command == 'config':
        if args.config_type == 'api-key':
            manage_config(args.action, 'api-key')
        else:
            print("Usage: terminal-tutor config {api-key}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()