"""Core functionality for command description lookup."""

import json
import math
import os
import re
import requests
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, Tuple

from .openai_manager import OpenAIKeyManager


class ModeManager:
    """Manages command modes for context-aware filtering."""

    def __init__(self, commands_metadata: Dict[str, dict] = None):
        self.commands_metadata = commands_metadata or {}
        self.mode_file = Path.home() / ".terminal_tutor_mode"
        self.auto_detect_file = Path.home() / ".terminal_tutor_auto_detect"
        self.current_mode = self._load_current_mode()
        self.auto_detect_enabled = self._load_auto_detect_setting()
        self.mode_configs = self._get_mode_configs()

    def _get_mode_configs(self) -> Dict:
        """Define mode configurations with category-based filtering."""
        return {
            "full": {
                "name": "Full Mode",
                "description": "All commands available",
                "allowed_categories": ["*"],
                "suppress_categories": [],
                "context_files": [],
                "risk_multiplier": 1.0
            },
            "aws": {
                "name": "AWS Mode",
                "description": "Focus on AWS and cloud infrastructure commands",
                "allowed_categories": [
                    "aws-*",  # All AWS sub-categories
                    "git", "file-operations", "file-search", "network",
                    "text-processing", "utilities", "general", "editor",
                    "terminal", "compression"
                ],
                "suppress_categories": ["docker", "kubernetes", "nvidia-jetson"],
                "context_files": [".aws/", "terraform.tf", "cloudformation.yaml", "template.yaml"],
                "risk_multiplier": 1.5
            },
            "docker": {
                "name": "Docker Mode",
                "description": "Focus on Docker and containerization commands",
                "allowed_categories": [
                    "docker", "git", "file-operations", "file-search",
                    "network", "system", "system-info", "utilities",
                    "general", "editor", "terminal", "compression"
                ],
                "suppress_categories": ["kubernetes", "aws-*", "nvidia-jetson"],
                "context_files": ["Dockerfile", "docker-compose.yml", ".dockerignore", "docker-compose.yaml"],
                "risk_multiplier": 1.2
            },
            "k8s": {
                "name": "Kubernetes Mode",
                "description": "Focus on Kubernetes and orchestration commands",
                "allowed_categories": [
                    "kubernetes", "docker", "git", "network",
                    "system", "system-info", "utilities", "general",
                    "editor", "terminal", "compression", "file-operations"
                ],
                "suppress_categories": ["aws-*", "nvidia-jetson"],
                "context_files": ["*.yaml", "kustomization.yaml", ".kube/", "Chart.yaml"],
                "risk_multiplier": 2.0
            },
            "git": {
                "name": "Git Mode",
                "description": "Focus on Git version control commands",
                "allowed_categories": [
                    "git", "file-operations", "file-search", "text-processing",
                    "utilities", "general", "editor", "terminal", "compression"
                ],
                "suppress_categories": ["docker", "kubernetes", "aws-*", "nvidia-jetson", "system", "network"],
                "context_files": [".git/", ".gitignore", ".gitmodules"],
                "risk_multiplier": 0.8
            }
        }

    def _load_current_mode(self) -> str:
        """Load current mode from file."""
        if self.mode_file.exists():
            try:
                return self.mode_file.read_text().strip()
            except:
                pass
        return "full"

    def _load_auto_detect_setting(self) -> bool:
        """Load auto-detection setting."""
        return self.auto_detect_file.exists()

    def _save_current_mode(self, mode: str):
        """Save current mode to file."""
        try:
            self.mode_file.write_text(mode)
            self.current_mode = mode
        except Exception as e:
            print(f"Warning: Could not save mode setting: {e}")

    def _save_auto_detect_setting(self, enabled: bool):
        """Save auto-detection setting."""
        try:
            if enabled:
                self.auto_detect_file.touch()
            else:
                if self.auto_detect_file.exists():
                    self.auto_detect_file.unlink()
            self.auto_detect_enabled = enabled
        except Exception as e:
            print(f"Warning: Could not save auto-detect setting: {e}")

    def detect_project_context(self) -> str:
        """Auto-detect mode based on current directory context."""
        if not self.auto_detect_enabled:
            return self.current_mode

        cwd = Path.cwd()

        # Check each mode's context files
        for mode_name, config in self.mode_configs.items():
            if mode_name == "full":
                continue

            for pattern in config["context_files"]:
                if "*" in pattern:
                    # Handle glob patterns
                    if list(cwd.glob(pattern)):
                        return mode_name
                else:
                    # Handle direct file/directory checks
                    if (cwd / pattern).exists():
                        return mode_name

        return "full"

    def get_effective_mode(self) -> str:
        """Get the effective mode (considering auto-detection)."""
        if self.auto_detect_enabled:
            detected_mode = self.detect_project_context()
            if detected_mode != "full":
                return detected_mode
        return self.current_mode

    def set_mode(self, mode: str) -> bool:
        """Set the current mode."""
        if mode not in self.mode_configs:
            return False
        self._save_current_mode(mode)
        return True

    def enable_auto_detect(self):
        """Enable auto-detection."""
        self._save_auto_detect_setting(True)

    def disable_auto_detect(self):
        """Disable auto-detection."""
        self._save_auto_detect_setting(False)

    def should_suppress_command(self, command: str) -> bool:
        """Check if command should be suppressed based on category."""
        effective_mode = self.get_effective_mode()

        if effective_mode == "full":
            return False

        # Get command category from metadata
        if command not in self.commands_metadata:
            return False

        cmd_category = self.commands_metadata[command].get("category", "general")
        config = self.mode_configs.get(effective_mode, {})

        # Check suppress_categories (takes precedence)
        suppress_categories = config.get("suppress_categories", [])
        for suppress_cat in suppress_categories:
            if self._category_matches(cmd_category, suppress_cat):
                return True

        # Check allowed_categories
        allowed_categories = config.get("allowed_categories", ["*"])
        if "*" in allowed_categories:
            return False

        for allowed_cat in allowed_categories:
            if self._category_matches(cmd_category, allowed_cat):
                return False

        return True  # Not in allowed list, suppress it

    def _category_matches(self, cmd_category: str, pattern: str) -> bool:
        """Check if command category matches pattern (supports wildcards)."""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            # Wildcard: "aws-*" matches "aws-s3", "aws-ec2", etc.
            return cmd_category.startswith(pattern[:-1])
        return cmd_category == pattern

    def get_risk_multiplier(self) -> float:
        """Get risk multiplier for current mode."""
        effective_mode = self.get_effective_mode()
        config = self.mode_configs.get(effective_mode, {})
        return config.get("risk_multiplier", 1.0)

    def list_modes(self) -> Dict:
        """List all available modes with descriptions."""
        return {mode: config["description"] for mode, config in self.mode_configs.items()}


class CommandTutor:
    """Main class for command description lookup."""

    def __init__(self):
        self.commands, self.commands_metadata = self._load_commands()
        self.prefix_index = self._build_prefix_index()
        self.usage_file = Path.home() / ".terminal_tutor_usage"
        self.premium_file = Path.home() / ".terminal_tutor_premium"
        self.mode_manager = ModeManager(self.commands_metadata)
        self.openai_manager = OpenAIKeyManager()

    def _load_commands(self) -> tuple[Dict[str, str], Dict[str, dict]]:
        """Load command database from JSON file with metadata.

        Loads from two sources (user custom commands override defaults):
        1. Default commands: terminal_tutor/data/commands.json
        2. User custom commands: ~/.terminal_tutor_custom_commands.json
        """
        commands = {}
        metadata = {}

        # Load default commands first
        commands_file = Path(__file__).parent / "data" / "commands.json"
        if commands_file.exists() and commands_file.stat().st_size > 0:
            try:
                with open(commands_file, 'r') as f:
                    data = json.load(f)

                # New JSON structure with metadata
                if "commands" in data and isinstance(data["commands"], dict):
                    for cmd, cmd_data in data["commands"].items():
                        if isinstance(cmd_data, dict):
                            commands[cmd] = cmd_data.get("description", "")
                            metadata[cmd] = cmd_data
                        else:
                            # Old format: just description string
                            commands[cmd] = cmd_data
                            metadata[cmd] = {"description": cmd_data, "risk_level": "SAFE", "category": "general"}

            except (json.JSONDecodeError, KeyError):
                # Use hardcoded defaults if JSON fails
                commands = self._get_default_commands()
                metadata = {cmd: {"description": desc, "risk_level": "SAFE", "category": "general"}
                           for cmd, desc in commands.items()}
        else:
            # Fallback to hardcoded defaults if file doesn't exist
            commands = self._get_default_commands()
            metadata = {cmd: {"description": desc, "risk_level": "SAFE", "category": "general"}
                       for cmd, desc in commands.items()}

        # Load user custom commands (overrides defaults)
        user_commands_file = Path.home() / ".terminal_tutor_custom_commands.json"
        if user_commands_file.exists() and user_commands_file.stat().st_size > 0:
            try:
                with open(user_commands_file, 'r') as f:
                    user_data = json.load(f)

                if "commands" in user_data and isinstance(user_data["commands"], dict):
                    for cmd, cmd_data in user_data["commands"].items():
                        if isinstance(cmd_data, dict):
                            commands[cmd] = cmd_data.get("description", "")
                            metadata[cmd] = cmd_data
                        else:
                            # Old format: just description string
                            commands[cmd] = cmd_data
                            metadata[cmd] = {"description": cmd_data, "risk_level": "SAFE", "category": "custom"}

            except (json.JSONDecodeError, KeyError):
                # Silently ignore invalid user custom commands file
                pass

        return commands, metadata

    def _get_default_commands(self) -> Dict[str, str]:
        """Default command database."""
        return {
            # Git commands
            "git": "Distributed version control system - tracks changes in files",
            "git status": "Show the working tree status",
            "git add": "Add file contents to the index",
            "git commit": "Record changes to the repository",
            "git push": "Update remote refs along with associated objects",
            "git pull": "Fetch from and integrate with another repository",
            "git clone": "Clone a repository into a new directory",
            "git branch": "List, create, or delete branches",
            "git checkout": "Switch branches or restore working tree files",
            "git merge": "Join two or more development histories together",
            "git log": "Show commit logs",
            "git diff": "Show changes between commits, commit and working tree, etc",
            "git reset": "Reset current HEAD to the specified state",

            # Docker commands
            "docker": "Container platform for building, sharing, and running applications",
            "docker run": "Run a command in a new container",
            "docker build": "Build an image from a Dockerfile",
            "docker ps": "List containers",
            "docker images": "List images",
            "docker pull": "Pull an image or a repository from a registry",
            "docker push": "Push an image or a repository to a registry",
            "docker stop": "Stop one or more running containers",
            "docker start": "Start one or more stopped containers",
            "docker restart": "Restart one or more containers",
            "docker rm": "Remove one or more containers",
            "docker rmi": "Remove one or more images",
            "docker exec": "Run a command in a running container",
            "docker logs": "Fetch the logs of a container",
            "docker inspect": "Return low-level information on Docker objects",

            # Kubernetes commands
            "kubectl": "Kubernetes command-line tool for cluster management",
            "kubectl get": "Display one or many resources",
            "kubectl get pods": "List all pods in the current namespace",
            "kubectl get services": "List all services in the current namespace",
            "kubectl get deployments": "List all deployments in the current namespace",
            "kubectl get nodes": "List all nodes in the cluster",
            "kubectl describe": "Show details of a specific resource",
            "kubectl apply": "Apply a configuration to a resource by filename or stdin",
            "kubectl delete": "Delete resources by filenames, stdin, resources and names",
            "kubectl logs": "Print the logs for a container in a pod",
            "kubectl exec": "Execute a command in a container",
            "kubectl port-forward": "Forward one or more local ports to a pod",
            "kubectl scale": "Set a new size for a Deployment, ReplicaSet or Replication Controller",

            # System commands
            "ps aux": "Display information about running processes",
            "ps -ef": "Display full format listing of processes",
            "top": "Display Linux processes in real time",
            "htop": "Interactive process viewer",
            "kill": "Terminate processes by process ID",
            "killall": "Kill processes by name",
            "systemctl start": "Start a systemd service",
            "systemctl stop": "Stop a systemd service",
            "systemctl restart": "Restart a systemd service",
            "systemctl status": "Show status of a systemd service",
            "systemctl enable": "Enable a systemd service to start at boot",
            "systemctl disable": "Disable a systemd service from starting at boot",

            # File operations
            "ls -la": "List all files in long format including hidden files",
            "ls -l": "List files in long format",
            "find": "Search for files and directories",
            "grep": "Search text using patterns",
            "grep -r": "Search recursively through directories",
            "chmod": "Change file permissions",
            "chown": "Change file ownership",
            "cp -r": "Copy directories recursively",
            "mv": "Move/rename files and directories",
            "rm -rf": "Remove files and directories forcefully and recursively",
            "tar -xzf": "Extract gzipped tar archive",
            "tar -czf": "Create gzipped tar archive",

            # Network commands
            "netstat -tulpn": "Display network connections, routing tables, interface statistics",
            "ss -tulpn": "Display socket statistics (modern netstat replacement)",
            "iptables -L": "List all iptables rules",
            "ufw enable": "Enable uncomplicated firewall",
            "ufw disable": "Disable uncomplicated firewall",
            "ufw allow": "Allow traffic through firewall",
            "ufw deny": "Deny traffic through firewall",
            "ping": "Send ICMP echo requests to network hosts",
            "curl": "Transfer data from or to a server",
            "wget": "Download files from the web",
            "ssh": "Secure Shell remote login",
            "scp": "Secure copy files over SSH",

            # Basic shell commands
            "cd": "Change current directory",
            "pwd": "Print working directory path",
            "ls": "List directory contents",
            "ls -l": "List files in long format with details",
            "ls -la": "List all files in long format including hidden files",
            "ls -a": "List all files including hidden ones",
            "mkdir": "Create directories",
            "mkdir -p": "Create directories and parent directories as needed",
            "rmdir": "Remove empty directories",
            "touch": "Create empty files or update timestamps",
            "cp": "Copy files and directories",
            "mv": "Move/rename files and directories",
            "rm": "Remove files and directories",
            "cat": "Display file contents",
            "less": "View file contents page by page",
            "more": "View file contents page by page",
            "head": "Display first lines of a file",
            "tail": "Display last lines of a file",
            "wc": "Count lines, words, and characters in files",
            "sort": "Sort lines in text files",
            "uniq": "Report or omit repeated lines",
            "cut": "Extract columns from text",
            "awk": "Pattern scanning and text processing",
            "sed": "Stream editor for filtering and transforming text",
            "which": "Locate a command",
            "whereis": "Locate binary, source, manual for a command",
            "file": "Determine file type",
            "stat": "Display file or filesystem status",
            "du": "Display directory space usage",
            "df": "Display filesystem disk space usage",
            "free": "Display amount of free and used memory",
            "uptime": "Show how long system has been running",
            "whoami": "Display current username",
            "id": "Display user and group IDs",
            "date": "Display or set system date",
            "history": "Display command history",
            "alias": "Create command aliases",
            "unalias": "Remove command aliases",
            "export": "Set environment variables",
            "env": "Display environment variables",
            "echo": "Display text",
            "printf": "Format and print text",
            "clear": "Clear the terminal screen",
            "reset": "Reset terminal to default state",

            # AWS CLI commands
            "aws": "Amazon Web Services command line interface",

            # S3 commands
            "aws s3 ls": "List S3 buckets or objects",
            "aws s3 cp": "Copy files to/from S3",
            "aws s3 mv": "Move files to/from S3",
            "aws s3 sync": "Sync directories with S3",
            "aws s3 rm": "Remove S3 objects",
            "aws s3 mb": "Create S3 bucket",
            "aws s3 rb": "Remove S3 bucket",
            "aws s3api create-bucket": "Create S3 bucket with advanced options",
            "aws s3api delete-bucket": "Delete S3 bucket",
            "aws s3api put-object": "Upload object to S3",
            "aws s3api get-object": "Download object from S3",
            "aws s3api list-objects": "List objects in S3 bucket",
            "aws s3api put-bucket-policy": "Set bucket policy",
            "aws s3api get-bucket-policy": "Get bucket policy",

            # EC2 commands
            "aws ec2 describe-instances": "Describe EC2 instances",
            "aws ec2 start-instances": "Start EC2 instances",
            "aws ec2 stop-instances": "Stop EC2 instances",
            "aws ec2 terminate-instances": "Terminate EC2 instances",
            "aws ec2 reboot-instances": "Reboot EC2 instances",
            "aws ec2 run-instances": "Launch new EC2 instances",
            "aws ec2 describe-images": "Describe AMI images",
            "aws ec2 create-image": "Create AMI from instance",
            "aws ec2 describe-key-pairs": "List EC2 key pairs",
            "aws ec2 create-key-pair": "Create EC2 key pair",
            "aws ec2 delete-key-pair": "Delete EC2 key pair",
            "aws ec2 describe-security-groups": "List security groups",
            "aws ec2 create-security-group": "Create security group",
            "aws ec2 delete-security-group": "Delete security group",
            "aws ec2 authorize-security-group-ingress": "Add inbound rule to security group",
            "aws ec2 revoke-security-group-ingress": "Remove inbound rule from security group",
            "aws ec2 describe-volumes": "List EBS volumes",
            "aws ec2 create-volume": "Create EBS volume",
            "aws ec2 delete-volume": "Delete EBS volume",
            "aws ec2 attach-volume": "Attach EBS volume to instance",
            "aws ec2 detach-volume": "Detach EBS volume from instance",

            # IAM commands
            "aws iam list-users": "List IAM users",
            "aws iam create-user": "Create IAM user",
            "aws iam delete-user": "Delete IAM user",
            "aws iam list-groups": "List IAM groups",
            "aws iam create-group": "Create IAM group",
            "aws iam delete-group": "Delete IAM group",
            "aws iam list-roles": "List IAM roles",
            "aws iam create-role": "Create IAM role",
            "aws iam delete-role": "Delete IAM role",
            "aws iam list-policies": "List IAM policies",
            "aws iam create-policy": "Create IAM policy",
            "aws iam delete-policy": "Delete IAM policy",
            "aws iam attach-user-policy": "Attach policy to user",
            "aws iam detach-user-policy": "Detach policy from user",
            "aws iam list-access-keys": "List access keys for user",
            "aws iam create-access-key": "Create access key for user",
            "aws iam delete-access-key": "Delete access key",

            # Lambda commands
            "aws lambda list-functions": "List Lambda functions",
            "aws lambda create-function": "Create Lambda function",
            "aws lambda delete-function": "Delete Lambda function",
            "aws lambda invoke": "Invoke Lambda function",
            "aws lambda update-function-code": "Update Lambda function code",
            "aws lambda get-function": "Get Lambda function details",

            # CloudWatch commands
            "aws logs describe-log-groups": "List CloudWatch log groups",
            "aws logs describe-log-streams": "List log streams in log group",
            "aws logs get-log-events": "Get log events from log stream",
            "aws logs tail": "Tail CloudWatch logs",
            "aws logs create-log-group": "Create log group",
            "aws logs delete-log-group": "Delete log group",
            "aws cloudwatch list-metrics": "List CloudWatch metrics",
            "aws cloudwatch get-metric-statistics": "Get metric statistics",
            "aws cloudwatch put-metric-data": "Put custom metric data",

            # RDS commands
            "aws rds describe-db-instances": "List RDS database instances",
            "aws rds create-db-instance": "Create RDS database instance",
            "aws rds delete-db-instance": "Delete RDS database instance",
            "aws rds start-db-instance": "Start RDS database instance",
            "aws rds stop-db-instance": "Stop RDS database instance",
            "aws rds reboot-db-instance": "Reboot RDS database instance",

            # ECS commands
            "aws ecs list-clusters": "List ECS clusters",
            "aws ecs describe-clusters": "Describe ECS clusters",
            "aws ecs list-services": "List ECS services",
            "aws ecs describe-services": "Describe ECS services",
            "aws ecs list-tasks": "List ECS tasks",
            "aws ecs describe-tasks": "Describe ECS tasks",
            "aws ecs run-task": "Run ECS task",
            "aws ecs stop-task": "Stop ECS task",

            # EKS commands
            "aws eks list-clusters": "List EKS clusters",
            "aws eks describe-cluster": "Describe EKS cluster",
            "aws eks create-cluster": "Create EKS cluster",
            "aws eks delete-cluster": "Delete EKS cluster",
            "aws eks update-kubeconfig": "Update kubeconfig for EKS cluster",

            # CloudFormation commands
            "aws cloudformation list-stacks": "List CloudFormation stacks",
            "aws cloudformation describe-stacks": "Describe CloudFormation stacks",
            "aws cloudformation create-stack": "Create CloudFormation stack",
            "aws cloudformation update-stack": "Update CloudFormation stack",
            "aws cloudformation delete-stack": "Delete CloudFormation stack",
            "aws cloudformation validate-template": "Validate CloudFormation template",

            # Route53 commands
            "aws route53 list-hosted-zones": "List Route53 hosted zones",
            "aws route53 list-resource-record-sets": "List DNS records in hosted zone",
            "aws route53 change-resource-record-sets": "Modify DNS records",

            # Package managers
            "apt update": "Update package index",
            "apt upgrade": "Upgrade installed packages",
            "apt install": "Install packages",
            "apt remove": "Remove packages",
            "apt autoremove": "Remove automatically installed packages no longer needed",
            "snap install": "Install snap packages",
            "snap list": "List installed snap packages",
            "pip install": "Install Python packages",
            "pip list": "List installed Python packages",
            "npm install": "Install Node.js packages",
            "npm list": "List installed Node.js packages",
        }

    def get_description(self, command_line: str) -> Optional[str]:
        """Get description for a command line with progressive matching."""
        command_line = command_line.strip()
        if not command_line:
            return None

        # Check mode-based suppression first
        if self.mode_manager.should_suppress_command(command_line):
            return None

        # Progressive matching for real-time prediction
        # Find the best match for current input
        best_match = None
        best_score = 0

        for cmd_pattern, description in self.commands.items():
            # Exact match gets highest priority
            if command_line == cmd_pattern:
                return description

            # Partial match from beginning
            if cmd_pattern.startswith(command_line):
                score = len(command_line) / len(cmd_pattern)
                if score > best_score:
                    best_score = score
                    best_match = description

        # If we found a good partial match, return it
        if best_match and best_score > 0.3:  # At least 30% match
            return best_match

        # Fallback to original logic for exact matches
        parts = command_line.split()
        if parts and parts[0] in self.commands:
            return self.commands[parts[0]]

        return None

    def _build_prefix_index(self) -> Dict:
        """Build prefix tree for ultra-fast O(1) lookups."""
        prefix_index = {}

        for cmd, description in self.commands.items():
            parts = cmd.split()
            current = prefix_index

            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {'_commands': [], '_children': {}}

                # Store the full command for this prefix
                current[part]['_commands'].append({
                    'command': cmd,
                    'description': description,
                    'priority': len(parts)  # Shorter commands get higher priority (lower number)
                })

                current = current[part]['_children']

        # Sort commands by priority (shorter commands first - lower priority number)
        for node in self._flatten_index_nodes(prefix_index):
            node['_commands'].sort(key=lambda x: (x['priority'], x['command']))

        return prefix_index

    def _flatten_index_nodes(self, index_dict):
        """Helper to flatten all nodes in the prefix index."""
        nodes = []
        for key, value in index_dict.items():
            if isinstance(value, dict) and '_commands' in value:
                nodes.append(value)
                nodes.extend(self._flatten_index_nodes(value['_children']))
        return nodes

    def get_description_realtime(self, command_line: str) -> Optional[str]:
        """Ultra-fast O(1) lookup for real-time predictions with fuzzy suggestions."""
        command_line = command_line.strip()
        if not command_line:
            return None

        # Check mode-based suppression first
        if self.mode_manager.should_suppress_command(command_line):
            return None

        # Check for exact match first
        if command_line in self.commands:
            description = self.commands[command_line]
            risk_level = self.get_risk_level(command_line)

            return f"{risk_level} - {description}"

        # For partial matches, show top 3 suggestions
        suggestions = self.get_fuzzy_suggestions(command_line, max_results=3)

        if suggestions:
            if len(suggestions) == 1:
                # Single match - show it directly
                suggestion = suggestions[0]
                return f"{suggestion['risk_level']} - {suggestion['description']}"
            else:
                # Multiple matches - show numbered list (no extra formatting)
                lines = []
                for i, suggestion in enumerate(suggestions, 1):
                    lines.append(f"{i}. {suggestion['risk_level']} {suggestion['command']} - {suggestion['description']}")
                return "\n".join(lines)

        return None

    def _commands_match(self, user_cmd: str, pattern_cmd: str) -> bool:
        """Check if user command matches a pattern."""
        user_parts = user_cmd.split()
        pattern_parts = pattern_cmd.split()

        if len(user_parts) < len(pattern_parts):
            return False

        for i, pattern_part in enumerate(pattern_parts):
            if i >= len(user_parts):
                return False
            if user_parts[i] != pattern_part:
                return False

        return True

    def get_risk_level(self, command_line: str) -> str:
        """Get risk level - reads from metadata (JSON) or calculates for unknown commands."""
        # Check if command exists in metadata (from JSON)
        if command_line in self.commands_metadata:
            risk_level = self.commands_metadata[command_line].get("risk_level", "SAFE")
            # Add emoji prefix
            if risk_level == "DANGEROUS":
                return "🔴 DANGEROUS"
            elif risk_level == "CAUTION":
                return "🟡 CAUTION"
            else:
                return "🟢 SAFE"

        # Fallback: calculate for unknown commands (not in database)
        return self._calculate_risk_level(command_line)

    def _calculate_risk_level(self, command_line: str) -> str:
        """Calculate risk level for unknown commands - fallback only."""
        dangerous_patterns = [
            r'rm\s+.*-rf',
            r'rm\s+.*-fr',
            r'dd\s+.*of=',
            r'mkfs\.',
            r'fdisk',
            r'parted',
            r':(){ :|:& };:',  # Fork bomb
            r'chmod\s+777',
            r'chown\s+.*-R.*/',
            r'iptables\s+.*-F',
            r'ufw\s+--force-reset'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command_line, re.IGNORECASE):
                return "🔴 DANGEROUS"

        caution_patterns = [
            r'sudo',
            r'rm\s+',
            r'mv\s+.*/',
            r'chmod',
            r'chown',
            r'systemctl\s+(stop|disable|mask)',
            r'docker\s+rm',
            r'kubectl\s+delete'
        ]

        for pattern in caution_patterns:
            if re.search(pattern, command_line, re.IGNORECASE):
                return "🟡 CAUTION"

        return "🟢 SAFE"

    def _is_premium_user(self) -> bool:
        """Check if user has premium subscription."""
        return self.premium_file.exists()

    def _get_daily_usage(self) -> dict:
        """Get current daily usage stats."""
        today = date.today().isoformat()

        if not self.usage_file.exists():
            return {"date": today, "count": 0}

        try:
            with open(self.usage_file, 'r') as f:
                usage_data = json.load(f)

            # Reset counter if it's a new day
            if usage_data.get("date") != today:
                usage_data = {"date": today, "count": 0}

            return usage_data
        except (json.JSONDecodeError, KeyError):
            return {"date": today, "count": 0}

    def _increment_usage(self) -> dict:
        """Increment daily usage counter and return updated stats."""
        usage_data = self._get_daily_usage()
        usage_data["count"] += 1

        try:
            with open(self.usage_file, 'w') as f:
                json.dump(usage_data, f)
        except Exception:
            pass  # Silent fail to avoid breaking predictions

        return usage_data

    def _check_rate_limit(self) -> tuple[bool, dict]:
        """Check if user has exceeded rate limit. Returns (is_allowed, usage_info)."""
        # Temporarily disable rate limiting - unlimited usage for all users
        usage_data = self._get_daily_usage()

        usage_info = {
            "premium": False,
            "count": usage_data["count"],
            "limit": float('inf'),  # Unlimited
            "remaining": float('inf'),  # Unlimited
            "is_allowed": True
        }

        return True, usage_info

    def get_description_with_rate_limit(self, command_line: str) -> tuple[Optional[str], dict]:
        """Get description with rate limiting. Returns (description, usage_info)."""
        is_allowed, usage_info = self._check_rate_limit()

        if not is_allowed:
            return None, usage_info

        # For premium users, don't increment usage counter
        if usage_info.get("premium", False):
            description = self.get_description_realtime(command_line)
            return description, usage_info

        # Increment usage counter for free users
        updated_usage = self._increment_usage()
        usage_info["count"] = updated_usage["count"]
        usage_info["remaining"] = max(0, usage_info["limit"] - updated_usage["count"])

        # Get description
        description = self.get_description_realtime(command_line)
        return description, usage_info

    def get_fuzzy_suggestions(self, partial_command: str, max_results: int = 3) -> list:
        """Get top fuzzy matches using FZF-inspired smart scoring algorithm."""
        partial_command = partial_command.strip().lower()
        if not partial_command:
            return []

        # Special handling for multi-word input - only exact prefix matches
        if ' ' in partial_command:
            exact_matches = []
            for cmd, description in self.commands.items():
                # Check mode-based suppression
                if self.mode_manager.should_suppress_command(cmd):
                    continue

                if cmd.lower().startswith(partial_command):
                    score = self._calculate_smart_score(partial_command, cmd.lower(), description)
                    exact_matches.append({
                        'command': cmd,
                        'description': description,
                        'risk_level': self.get_risk_level(cmd),
                        'score': score
                    })
            if exact_matches:
                exact_matches.sort(key=lambda x: x['score'], reverse=True)
                return exact_matches[:max_results]
            else:
                return []

        matches = []

        for cmd, description in self.commands.items():
            # Check mode-based suppression
            if self.mode_manager.should_suppress_command(cmd):
                continue

            cmd_lower = cmd.lower()
            score = self._calculate_smart_score(partial_command, cmd_lower, description)

            if score > 0:
                matches.append({
                    'command': cmd,
                    'description': description,
                    'risk_level': self.get_risk_level(cmd),
                    'score': score
                })

        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)

        # Apply dynamic relevance threshold - only show results that are reasonably relevant
        if not matches:
            return []

        top_score = matches[0]['score']

        # Dynamic threshold based on top score and minimum absolute threshold
        dynamic_threshold = max(
            top_score * 0.3,  # At least 30% of the top score
            200  # Absolute minimum threshold for relevance
        )

        # Filter matches that meet the relevance threshold
        relevant_matches = [m for m in matches if m['score'] >= dynamic_threshold]

        return relevant_matches[:max_results]

    def _calculate_smart_score(self, partial: str, full_command: str, description: str) -> float:
        """FZF-inspired smart scoring algorithm with word boundary detection and relevance filtering."""
        if not partial or not full_command:
            return 0

        # Command frequency/priority weights
        command_priority = self._get_command_priority(full_command)

        # 1. Exact prefix match - highest priority
        if full_command.startswith(partial):
            base_score = (len(partial) / len(full_command)) * 1000
            return base_score + command_priority + 500

        # 2. Word boundary prefix match - prioritize matches at word starts
        words = full_command.split()
        for i, word in enumerate(words):
            if word.startswith(partial):
                base_score = (len(partial) / len(word)) * 500
                word_position_bonus = max(0, 100 - (i * 20))  # Earlier words get higher bonus

                # CRITICAL: Apply exponential position decay to word boundary matches too
                # Calculate the starting position of this word in the full command
                word_start_position = full_command.find(word)
                position_decay = self._calculate_position_decay(word_start_position)

                final_score = (base_score + word_position_bonus + 200) * position_decay + command_priority
                return final_score

        # 3. CRITICAL FIX: Word boundary fuzzy matching - heavily prefer matches at word starts
        for i, word in enumerate(words):
            if len(partial) >= 2:  # Only for meaningful partial inputs
                word_fuzzy_score = self._calculate_fuzzy_score(partial, word)
                if word_fuzzy_score > 0:
                    # Word start matches get massive bonus, later words get penalties
                    word_position_multiplier = 1.0 if i == 0 else 0.3 if i == 1 else 0.1
                    adjusted_score = word_fuzzy_score * word_position_multiplier

                    # Only return if it meets minimum relevance threshold
                    if adjusted_score > 30:  # Minimum relevance threshold
                        return adjusted_score + command_priority

        # 4. Full command fuzzy matching (with exponential position decay)
        if len(partial) >= 2:
            fuzzy_score = self._calculate_fuzzy_score(partial, full_command)
            if fuzzy_score > 0:
                # Apply exponential position decay and match quality assessment
                match_quality = self._assess_match_quality(partial, full_command)

                # CRITICAL: Apply exponential position decay
                # "cl" in "clear" (avg_pos=0.5) gets minimal penalty
                # "cl" in "cloudwatch" (avg_pos=4.5) gets heavy penalty
                position_penalty = match_quality['position_decay_multiplier']
                fuzzy_score *= position_penalty

                # Apply additional penalties for scattered matches
                if match_quality['is_scattered'] and len(full_command) > 10:
                    fuzzy_score *= 0.5  # Additional penalty for scattered matches

                # Calculate final score with command priority
                final_score = fuzzy_score + command_priority

                # Soft threshold - allow very low scores to be filtered naturally
                return final_score if final_score > 10 else 0

        return 0

    def _assess_match_quality(self, partial: str, full_command: str) -> dict:
        """Assess the quality of a fuzzy match to detect scattered vs coherent matches."""
        partial_idx = 0
        match_positions = []
        gaps = []

        # Find all character match positions
        for i, char in enumerate(full_command):
            if partial_idx < len(partial) and char == partial[partial_idx]:
                match_positions.append(i)
                partial_idx += 1

        if len(match_positions) < 2:
            return {'is_scattered': False, 'avg_gap': 0, 'max_gap': 0}

        # Calculate gaps between consecutive matches
        for i in range(1, len(match_positions)):
            gap = match_positions[i] - match_positions[i-1] - 1
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        max_gap = max(gaps) if gaps else 0

        # CRITICAL: Calculate average character position for exponential position decay
        avg_position = sum(match_positions) / len(match_positions) if match_positions else 0
        first_match_position = match_positions[0] if match_positions else 0

        # FZF-inspired exponential position decay function
        # Characters matching deeper in strings get exponentially lower relevance
        position_decay_multiplier = self._calculate_position_decay(avg_position)

        # Define scattered match criteria
        is_scattered = (
            avg_gap > 3 or  # Average gap > 3 characters
            max_gap > 8 or  # Any gap > 8 characters
            len(gaps) > 0 and sum(g > 2 for g in gaps) > len(gaps) * 0.5  # More than 50% of gaps > 2
        )

        return {
            'is_scattered': is_scattered,
            'avg_gap': avg_gap,
            'max_gap': max_gap,
            'avg_position': avg_position,
            'first_match_position': first_match_position,
            'position_decay_multiplier': position_decay_multiplier,
            'match_positions': match_positions,
            'gaps': gaps
        }

    def _calculate_position_decay(self, avg_position: float, decay_rate: float = 0.5) -> float:
        """
        FZF-inspired exponential position decay function.

        Characters matching deeper in strings get exponentially lower relevance.

        Examples:
        - "cl" in "clear" (avg_pos=0.5) -> multiplier = 0.86 (minimal penalty)
        - "cl" in "cloudwatch" (avg_pos=4.5) -> multiplier = 0.27 (heavy penalty)

        Args:
            avg_position: Average position of matched characters in the string
            decay_rate: Controls how aggressively scores decay (0.1=gentle, 0.5=aggressive)

        Returns:
            Multiplier between 0.0-1.0 to apply to the base score
        """
        return math.exp(-decay_rate * avg_position)

    def _get_command_priority(self, command: str) -> float:
        """Assign priority scores based on command category and frequency."""
        # Basic shell commands (highest priority)
        basic_commands = {
            'cd', 'ls', 'pwd', 'clear', 'cat', 'echo', 'mv', 'cp', 'rm', 'mkdir',
            'touch', 'grep', 'find', 'head', 'tail', 'sort', 'uniq', 'wc'
        }

        # Development tools (medium-high priority)
        dev_commands = {
            'git', 'docker', 'npm', 'pip', 'vim', 'nano', 'code'
        }

        # Get first word of command
        first_word = command.split()[0]

        if first_word in basic_commands:
            return 100  # Highest priority
        elif first_word in dev_commands or command.startswith('git '):
            return 50   # Medium-high priority
        elif command.startswith('aws '):
            return 10   # Lower priority for specialized tools
        else:
            return 25   # Default priority

    def _calculate_fuzzy_score(self, partial: str, full_command: str, debug: bool = False) -> float:
        """Calculate fuzzy match score with position bonuses and gap penalties."""
        partial_idx = 0
        score = 0
        last_match_pos = -1
        consecutive_matches = 0
        match_positions = []
        gaps = []

        for i, char in enumerate(full_command):
            if partial_idx < len(partial) and char == partial[partial_idx]:
                # Track match positions for debugging
                match_positions.append((partial[partial_idx], i))

                # Position bonuses (FZF-inspired)
                position_bonus = 0

                # Start of command bonus
                if i == 0:
                    position_bonus += 50
                # Start of word bonus
                elif i > 0 and full_command[i-1] in ' -_':
                    position_bonus += 30
                # CamelCase bonus
                elif char.isupper() and i > 0 and full_command[i-1].islower():
                    position_bonus += 20

                # Consecutive match bonus
                if last_match_pos == i - 1:
                    consecutive_matches += 1
                    position_bonus += consecutive_matches * 5
                else:
                    consecutive_matches = 0

                # Gap penalty
                gap = 0
                if last_match_pos >= 0:
                    gap = i - last_match_pos - 1
                    gaps.append(gap)
                    gap_penalty = min(gap * 2, 20)  # Cap penalty at 20
                    position_bonus = max(0, position_bonus - gap_penalty)

                score += 10 + position_bonus
                last_match_pos = i
                partial_idx += 1

        # Only return score if we matched all characters
        if partial_idx == len(partial):
            # Length penalty for very long commands
            length_penalty = max(0, len(full_command) - 20) * 0.5
            final_score = max(0, score - length_penalty)

            # Debug output
            if debug:
                total_gaps = sum(gaps)
                avg_gap = total_gaps / len(gaps) if gaps else 0
                print(f"DEBUG: '{partial}' in '{full_command}':")
                print(f"  Matches: {match_positions}")
                print(f"  Gaps: {gaps} (total: {total_gaps}, avg: {avg_gap:.1f})")
                print(f"  Score: {final_score:.1f}")
                print()

            return final_score

        return 0

    def get_premium_upgrade_message(self) -> str:
        """Get premium upgrade message when rate limit exceeded."""
        return """
🚫 Daily limit reached (100 predictions/day)

🌟 Upgrade to Premium for unlimited predictions!
   • Unlimited daily predictions
   • Priority support
   • Early access to new features
   • Custom command libraries

💳 Just $5/month - Cancel anytime
🔗 Upgrade: https://terminal-tutor.com/premium

Or wait until tomorrow for 100 free predictions to reset.
"""

    def natural_language_search(self, query: str) -> Optional[dict]:
        """
        Use OpenAI API to translate natural language queries into terminal commands.

        Args:
            query: Natural language query (e.g., "how to list files")

        Returns:
            Dict with command, risk_level, description or None if not found
        """
        try:
            # Query OpenAI for command translation
            command_name = self._query_openai(query)
            if not command_name:
                return None

            # Look up the command in our database
            if command_name in self.commands:
                return {
                    'command': command_name,
                    'description': self.commands[command_name],
                    'risk_level': self.get_risk_level(command_name)
                }

            # Try fuzzy matching as fallback
            fuzzy_suggestions = self.get_fuzzy_suggestions(command_name, 1)
            if fuzzy_suggestions:
                suggestion = fuzzy_suggestions[0]
                return {
                    'command': suggestion['command'],
                    'description': suggestion['description'],
                    'risk_level': suggestion['risk_level']
                }

            return None

        except Exception as e:
            # Graceful degradation - return None on any error
            return None

    def _query_openai(self, query: str) -> Optional[str]:
        """
        Query OpenAI API for natural language to command translation.

        Args:
            query: Natural language query

        Returns:
            Command name or None if failed
        """
        # Get API key from manager (prompts user if needed)
        api_key = self.openai_manager.get_api_key()
        if not api_key:
            return None

        try:
            import openai
        except ImportError:
            # OpenAI package not installed
            return None

        try:
            client = openai.OpenAI(api_key=api_key)

            # Optimized prompt for command translation
            system_prompt = """You are a terminal command expert. Convert natural language requests to terminal commands.

Respond with ONLY the command name (like 'ls', 'git status', 'docker ps'). No explanations, quotes, or additional text.

Examples:
- "how to list files" → ls
- "show git status" → git status
- "copy files" → cp
- "remove directory" → rm -r
- "search for text in files" → grep
- "check disk space" → df
- "show running processes" → ps"""

            # Make request to OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=50,
                temperature=0.3
            )

            command = response.choices[0].message.content.strip()

            # Clean up the response - remove any extra text
            command = command.split('\n')[0].strip()  # Take first line only
            command = command.strip('"\'`')  # Remove quotes

            # Validate it looks like a command (not empty, reasonable length)
            if command and len(command) < 50 and not command.startswith(('I ', 'The ', 'To ')):
                return command

            return None

        except Exception:
            # Any error (auth, network, etc.) - graceful degradation
            return None