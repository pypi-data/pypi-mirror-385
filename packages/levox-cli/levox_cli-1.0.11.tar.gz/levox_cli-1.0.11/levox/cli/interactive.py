"""
Levox Interactive CLI

This module provides an interactive command-line interface for Levox,
allowing users to run commands in a conversational manner.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align
from rich import box

from .commands import cli
from .output import OutputManager
from ..core.config import load_default_config, LicenseTier

class InteractiveCLI:
    """Interactive CLI interface for Levox."""
    
    def __init__(self):
        """Initialize the interactive CLI."""
        self.console = Console(emoji=(sys.platform != 'win32'))
        self.config = load_default_config()
        self.output_manager = OutputManager(self.config)
        self.running = True
        self.logging_enabled = False  # Track logging state
        self.current_company = None  # Track current company context
        
        # Enhanced features
        self.command_history = []  # Track command history
        self.recent_paths = []  # Track recent scan paths
        self.quick_actions = self._initialize_quick_actions()
        self.command_shortcuts = self._initialize_shortcuts()
        
        # Set default logging level to ERROR (quiet mode)
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    
    def run(self):
        """Run the interactive CLI."""
        try:
            # Show welcome screen
            self._show_welcome()
            
            # Main interactive loop
            while self.running:
                try:
                    user_input = Prompt.ask(f"\n{self._get_enhanced_prompt()}", default="help").strip()
                    if not user_input:
                        continue
                    
                    # Smart path handling: if user pasted a path, offer to scan it
                    maybe_path = user_input.strip('"').strip("'")
                    if self._looks_like_path(maybe_path):
                        path_obj = Path(self._normalize_windows_path(maybe_path)) if sys.platform == 'win32' else Path(maybe_path)
                        if path_obj.exists():
                            choice = Prompt.ask(
                                f"Detected path: [cyan]{path_obj}[/cyan]. Scan now?",
                                choices=["y", "n"],
                                default="y"
                            )
                            if choice.lower() == 'y':
                                # Execute scan directly and skip further parsing noise
                                self._execute_scan_command(f"scan {str(path_obj)}")
                                continue
                            else:
                                # Do not show an error; just continue the loop quietly
                                continue
                    
                    # Smart Git URL handling: if user pasted a Git URL, offer to scan it
                    if self._looks_like_git_url(maybe_path):
                        choice = Prompt.ask(
                            f"Detected Git repository: [cyan]{maybe_path}[/cyan]. Scan now?",
                            choices=["y", "n"],
                            default="y"
                        )
                        if choice.lower() == 'y':
                            # Execute repository scan
                            self._execute_repo_scan(maybe_path)
                            continue
                        else:
                            continue
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        self._show_goodbye()
                        break
                    
                    if user_input.lower() in ['help', 'h', '?']:
                        self._show_enhanced_help()
                        continue
                    
                    # Handle help <command> syntax
                    if user_input.lower().startswith('help '):
                        command = user_input[5:].strip()
                        self._show_enhanced_help(command)
                        continue
                    
                    if user_input.lower() in ['menu', 'm']:
                        self._show_quick_actions_menu()
                        continue
                    
                    if user_input.lower() in ['clear', 'cls']:
                        self.console.clear()
                        self._show_full_welcome()
                        continue
                    
                    # Handle command shortcuts
                    if user_input.lower() in self.command_shortcuts:
                        expanded_command = self.command_shortcuts[user_input.lower()]
                        self.console.print(f"[dim]Expanded: {expanded_command}[/dim]")
                        user_input = expanded_command
                    
                    # Handle log toggle command
                    if user_input.lower() in ['enable log', 'disable log', 'toggle log']:
                        self._toggle_logging(user_input.lower())
                        continue

                    
                    # Add to history and execute command
                    self._add_to_history(user_input)
                    self._execute_command(user_input)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]💡 Tip: Use 'exit' to quit the CLI[/yellow]")
                except SystemExit as e:
                    if e.code not in (0, None, 1):
                        self.console.print(f"[red]Command exited with code {e.code}[/red]")
                except Exception as e:
                    self.console.print(Panel(
                        f"[red]Error: {e}[/red]\n[dim]The command encountered an unexpected error[/dim]",
                        title="⚠️ Error",
                        border_style="red"
                    ))
                    
        except KeyboardInterrupt:
            self.console.print("\nOperation cancelled by user.")
            sys.exit(1)
    
    def _show_welcome(self):
        """Show the welcome screen."""
        self.output_manager.print_branding()
        
        # Compact welcome message
        self.console.print("[bold cyan]Welcome to Levox Interactive CLI![/bold cyan]")
        self.console.print("[dim]Type [bold]help[/bold] for commands • [bold]exit[/bold] to quit • [bold]clear[/bold] to clear screen[/dim]")
    
    def _show_full_welcome(self):
        """Show the full welcome screen with branding (for clear command)."""
        # Force display the branding by temporarily resetting the global flag
        import levox.cli.output
        original_flag = getattr(levox.cli.output, '_BRANDING_PRINTED', False)
        levox.cli.output._BRANDING_PRINTED = False
        
        # Show the full branding
        self.output_manager.print_branding()
        
        # Restore the original flag
        levox.cli.output._BRANDING_PRINTED = original_flag
        
        # Show welcome message
        self.console.print("[bold cyan]Welcome to Levox Interactive CLI![/bold cyan]")
        self.console.print("[dim]Type [bold]help[/bold] for commands • [bold]exit[/bold] to quit • [bold]clear[/bold] to clear screen[/dim]")
    
    def _show_help(self):
        """Show the help information."""
        help_table = Table(
            title="[bold cyan]Levox CLI Commands[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        help_table.add_column("Usage", style="dim")
        
        # Core Commands
        help_table.add_row("[bold]scan[/bold]", "Scan files/directories for PII/GDPR violations", "scan <path> [options]")
        help_table.add_row("[bold]status[/bold]", "Show capability status and license tiers", "status [--detailed]")
        help_table.add_row("[bold]report[/bold]", "Generate reports from saved results", "report <file> [options]")
        help_table.add_row("[bold]license[/bold]", "Manage license, register, or upgrade", "license [--register] [--upgrade]")
        help_table.add_row("[bold]feedback[/bold]", "Provide feedback to improve detection", "feedback <match_id> <verdict>")
        help_table.add_row("[bold]models[/bold]", "Manage and evaluate ML models", "models [options]")
        help_table.add_row("[bold]generate_report[/bold]", "Generate report from latest scan", "generate_report [options]")
        help_table.add_row("[bold]history[/bold]", "Show scan history and available results", "history [--detailed] [--limit N]")
        help_table.add_row("[bold]history[/bold]", "Clear all history: history --clear", "history --clear")
        help_table.add_row("[bold]history[/bold]", "Clear specific result: history --clear-id <id>", "history --clear-id <id>")
        help_table.add_row("[bold]history[/bold]", "Select specific result: history --select <id>", "history --select <id>")
        help_table.add_row("[bold]history[/bold]", "Export history: history --export <file>", "history --export <file>")
        
        # Compliance Evidence Commands
        help_table.add_row("[bold]company[/bold]", "Company profile management for compliance", "company create/list")
        help_table.add_row("[bold]evidence[/bold]", "Generate audit-ready evidence packages", "evidence generate <company_id>")
        help_table.add_row("[bold]evidence[/bold]", "View scan history for compliance", "evidence history --company <id>")
        help_table.add_row("[bold]evidence[/bold]", "Show violation trends and analytics", "evidence trends --company <id>")
        help_table.add_row("[bold]evidence[/bold]", "Export evidence data", "evidence export --company <id>")
        
        # Advanced Commands
        help_table.add_row("[bold]ml_health[/bold]", "Check ML system health and performance", "ml_health [options]")
        help_table.add_row("[bold]switch_model[/bold]", "Switch to a different ML model", "switch_model [options]")
        help_table.add_row("[bold]generate_report[/bold]", "Generate reports from last scan", "generate_report [options]")
        help_table.add_row("[bold]set-report-directory[/bold]", "Choose where reports are saved", "set-report-directory")
        
        # CI/CD Integration Commands
        help_table.add_row("[bold]init-ci[/bold]", "Interactive CI/CD setup wizard", "init-ci [--interactive]")
        help_table.add_row("[bold]generate-template[/bold]", "Generate CI/CD templates", "generate-template <platform> [options]")
        help_table.add_row("[bold]validate-ci[/bold]", "Validate CI/CD configurations", "validate-ci <file>")
        help_table.add_row("[bold]test-ci[/bold]", "Test CI/CD integration locally", "test-ci [options]")
        help_table.add_row("[bold]generate-config[/bold]", "Generate .levoxrc configuration", "generate-config [options]")
        help_table.add_row("[bold]install-precommit[/bold]", "Install Git pre-commit hooks", "install-precommit [options]")
        
        # Utility Commands
        help_table.add_row("[bold]clear[/bold]", "Clear the screen", "clear")
        help_table.add_row("[bold]enable log[/bold]", "Enable verbose logging output", "enable log")
        help_table.add_row("[bold]disable log[/bold]", "Disable verbose logging output", "disable log")
        help_table.add_row("[bold]toggle log[/bold]", "Toggle verbose logging on/off", "toggle log")
        help_table.add_row("[bold]exit[/bold]", "Exit the CLI application", "exit")
        
        self.console.print(help_table)
        
        # Show compact examples
        self.console.print("[bold yellow]💡 Quick Examples:[/bold yellow]")
        self.console.print("[cyan]•[/cyan] scan . --report json html  [cyan]•[/cyan] status --detailed  [cyan]•[/cyan] report --latest --format html")
        self.console.print("[cyan]•[/cyan] company create --name 'My Company'  [cyan]•[/cyan] evidence generate <company_id>  [cyan]•[/cyan] evidence trends")
        self.console.print("[cyan]•[/cyan] license --register  [cyan]•[/cyan] license --upgrade  [cyan]•[/cyan] history  [cyan]•[/cyan] set-report-directory")
        self.console.print("[cyan]•[/cyan] init-ci --interactive  [cyan]•[/cyan] generate-template github-actions  [cyan]•[/cyan] test-ci")
        
        # Repository scanning examples
        self.console.print("\n[bold yellow]🔗 Repository Scanning:[/bold yellow]")
        self.console.print("[cyan]•[/cyan] Paste any GitHub/GitLab/Bitbucket URL to scan")
        self.console.print("[cyan]•[/cyan] Example: https://github.com/user/repo")
        self.console.print("[cyan]•[/cyan] Example: https://gitlab.com/user/repo")
        self.console.print("[cyan]•[/cyan] Example: https://bitbucket.org/user/repo")
        self.console.print("[dim]💡 Large repositories use smart cloning strategies for efficiency[/dim]")
    
    def _show_goodbye(self):
        """Show the goodbye message."""
        self.console.print("\n[bold green]Thank you for using Levox! 👋[/bold green]")
        self.console.print("[dim]Stay secure, stay compliant![/dim]")
    
    def _toggle_logging(self, command: str):
        """Toggle logging state and provide feedback."""
        if command == 'enable log':
            self.logging_enabled = True
            self.console.print("[green]✅ Logging enabled - verbose output will be shown[/green]")
        elif command == 'disable log':
            self.logging_enabled = False
            self.console.print("[yellow]🔇 Logging disabled - only essential output will be shown[/yellow]")
        elif command == 'toggle log':
            self.logging_enabled = not self.logging_enabled
            status = "enabled" if self.logging_enabled else "disabled"
            color = "green" if self.logging_enabled else "yellow"
            self.console.print(f"[{color}]🔄 Logging {status}[/{color}]")
        
        # Update the global logging level
        import logging
        if self.logging_enabled:
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.getLogger().setLevel(logging.ERROR)
        
        # Show current status
        status_text = "ON" if self.logging_enabled else "OFF"
        status_color = "green" if self.logging_enabled else "red"
        self.console.print(f"[dim]Current logging status: [{status_color}]{status_text}[/{status_color}][/dim]")
    
    def _get_current_company(self):
        """Get the current company context."""
        if self.current_company:
            return self.current_company
        
        # Try to get default company
        try:
            from ..compliance.evidence_store import get_evidence_store
            evidence_store = get_evidence_store("local")
            companies = evidence_store.get_all_companies()
            if companies:
                self.current_company = companies[0].id
                return self.current_company
        except Exception:
            pass
        
        return None

    def _get_command_suggestions(self, user_input: str, error_msg: str, command_type: str = 'general'):
        """Generate helpful command suggestions based on the error and user input."""
        import difflib
        import re
        
        suggestions = []
        
        # Check for common evidence command issues
        if command_type == 'evidence':
            # Check if user tried to use --company syntax with old format
            if '--company' in user_input and 'generate' in user_input:
                # Extract company ID from the command
                match = re.search(r'--company\s+(\S+)', user_input)
                if match:
                    company_id = match.group(1)
                    suggestions.append(f"💡 Try: evidence generate {company_id}")
                    suggestions.append("   (Company ID is now a positional argument)")
            
            # Check for invalid option errors
            if "No such option" in error_msg:
                # Extract the invalid option
                match = re.search(r"No such option: '?([^']+)'?", error_msg)
                if match:
                    invalid_option = match.group(1)
                    # If it looks like a company ID (no -- prefix), suggest correct syntax
                    if not invalid_option.startswith('--') and not invalid_option.startswith('-'):
                        suggestions.append(f"💡 Did you mean: evidence generate {invalid_option}")
                        suggestions.append("   (Company ID should be a positional argument, not an option)")
            
            # Check for missing company ID
            if 'generate' in user_input and len(user_input.split()) < 3:
                suggestions.append("💡 Usage: evidence generate <company_id>")
                suggestions.append("   Example: evidence generate fenrix41")
        
        # Check for company command issues
        elif command_type == 'company':
            if 'create' in user_input and '--name' not in user_input:
                suggestions.append("💡 Usage: company create --name 'Company Name'")
                suggestions.append("   Example: company create --name 'My Company'")
            elif 'list' in user_input:
                suggestions.append("💡 Usage: company list")
            elif 'select' in user_input and len(user_input.split()) < 3:
                suggestions.append("💡 Usage: company select <company_id>")
                suggestions.append("   First run 'company list' to see available companies")
        
        # Check for CI/CD command issues
        elif command_type in ['cicd', 'general']:
            if any(cmd in user_input for cmd in ['init-ci', 'generate-template', 'validate-ci', 'test-ci', 'generate-config', 'install-precommit']):
                suggestions.append("💡 CI/CD commands are working! Check the syntax:")
                suggestions.append("   • init-ci --interactive")
                suggestions.append("   • generate-template github")
                suggestions.append("   • validate-ci .github/workflows/ci.yml")
        
        # General command suggestions using fuzzy matching
        if not suggestions:
            known_commands = [
                'evidence generate', 'evidence history', 'evidence trends', 'evidence export',
                'company create', 'company list', 'company select',
                'init-ci', 'generate-template', 'validate-ci', 'test-ci', 'generate-config', 'install-precommit',
                'scan', 'report', 'status', 'license', 'history'
            ]
            
            # Find similar commands
            similar = difflib.get_close_matches(user_input.lower(), known_commands, n=3, cutoff=0.6)
            if similar:
                suggestions.append("💡 Did you mean one of these?")
                for cmd in similar:
                    suggestions.append(f"   • {cmd}")
        
        # Add general help
        if not suggestions:
            suggestions.append("💡 Type 'help' for a list of available commands")
            suggestions.append("💡 Type 'menu' for quick actions")
        
        return "\n".join(suggestions)

    
    def _execute_command(self, user_input: str):
        """Execute a user command."""
        # Handle scan command with special path parsing
        if user_input.lower().startswith('scan '):
            self._execute_scan_command(user_input)
            return
        
        # Handle report command with special parsing
        if user_input.lower().startswith('report '):
            self._execute_report_command(user_input)
            return
        
        # Handle generate_report command
        if user_input.lower().startswith('generate_report'):
            self._execute_generate_report_command(user_input)
            return
        
        # Handle CI/CD commands with special parsing
        if user_input.lower().startswith('init-ci'):
            self._execute_cicd_command(user_input)
            return
        
        if user_input.lower().startswith('generate-template'):
            self._execute_cicd_command(user_input)
            return
        
        if user_input.lower().startswith('validate-ci'):
            self._execute_cicd_command(user_input)
            return
        
        if user_input.lower().startswith('test-ci'):
            self._execute_cicd_command(user_input)
            return
        
        if user_input.lower().startswith('generate-config'):
            self._execute_cicd_command(user_input)
            return
        
        if user_input.lower().startswith('install-precommit'):
            self._execute_cicd_command(user_input)
            return
        
        # Handle company commands
        if user_input.lower().startswith('company '):
            self._execute_company_command(user_input)
            return
        
        # Handle evidence commands
        if user_input.lower().startswith('evidence '):
            self._execute_evidence_command(user_input)
            return
        
        # Handle setup command
        if user_input.lower() == 'setup':
            self._execute_setup_command()
            return
        
        # Handle other commands
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in {'scan', 'status', 'report', 'license', 'feedback', 'models', 'history', 'ml_health', 'switch_model', 'generate_report', 'set-report-directory', 'init-ci', 'generate-template', 'validate-ci', 'test-ci', 'generate-config', 'install-precommit', 'company', 'evidence', 'setup'}:
            # Parse toggle flags for all commands
            parsed_args = [command]
            input_lower = user_input.lower()
            
            # Parse common toggle flags that work across commands
            if '--verbose' in input_lower or '-v' in input_lower:
                parsed_args.append('--verbose')
            elif self.logging_enabled:
                # Auto-add verbose flag if logging is enabled
                parsed_args.append('--verbose')
            if '--debug' in input_lower:
                parsed_args.append('--debug')
            if '--quiet' in input_lower or '-q' in input_lower:
                parsed_args.append('--quiet')
            if '--detailed' in input_lower:
                parsed_args.append('--detailed')
            if '--auto' in input_lower:
                parsed_args.append('--auto')
            if '--list' in input_lower:
                parsed_args.append('--list')
            if '--latest' in input_lower:
                parsed_args.append('--latest')
            if '--include-metadata' in input_lower:
                parsed_args.append('--include-metadata')
            if '--check-dependencies' in input_lower:
                parsed_args.append('--check-dependencies')
            
            # Special handling for license command to allow --register <KEY>
            if command == 'license':
                # Preserve the raw args to pass through to click parser
                raw_args = user_input.split()[1:]
                args = ['license'] + raw_args
                try:
                    exit_code = cli.main(args, standalone_mode=False)
                    if exit_code in (2, 3):
                        self.console.print(Panel(
                            f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                            title="⚠️ Command Warning",
                            border_style="yellow"
                        ))
                except Exception as e:
                    self.console.print(Panel(
                        f"[red]Error executing command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                        title="❌ Command Error",
                        border_style="red"
                    ))
                return

            # Parse format options
            if '--format' in input_lower:
                if 'json' in input_lower:
                    parsed_args.extend(['--format', 'json'])
                elif 'html' in input_lower:
                    parsed_args.extend(['--format', 'html'])
                elif 'pdf' in input_lower:
                    parsed_args.extend(['--format', 'pdf'])
                elif 'table' in input_lower:
                    parsed_args.extend(['--format', 'table'])
                elif 'markdown' in input_lower:
                    parsed_args.extend(['--format', 'markdown'])
            
            # Parse output options
            if '--output' in input_lower or '-o' in input_lower:
                import re
                match = re.search(r'--output\s+([^\s]+)', user_input)
                if match:
                    parsed_args.extend(['--output', match.group(1)])
                else:
                    match = re.search(r'-o\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--output', match.group(1)])
            
            # License tier is now automatically detected - no need to parse
            # Users should verify their license with: levox license --verify
            
            # Parse limit options
            if '--limit' in input_lower:
                import re
                match = re.search(r'--limit\s+(\d+)', user_input)
                if match:
                    parsed_args.extend(['--limit', match.group(1)])
            
            # Parse history-specific options
            if command == 'history':
                if '--clear' in input_lower:
                    parsed_args.append('--clear')
                if '--clear-id' in input_lower:
                    import re
                    match = re.search(r'--clear-id\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--clear-id', match.group(1)])
                if '--select' in input_lower:
                    import re
                    match = re.search(r'--select\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--select', match.group(1)])
                if '--export' in input_lower:
                    import re
                    match = re.search(r'--export\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--export', match.group(1)])
            
            # Execute command with parsed arguments
            try:
                exit_code = cli.main(parsed_args, standalone_mode=False)
                # Reduce noise: only show warning for actual errors (2/3)
                if exit_code in (2, 3):
                    self.console.print(Panel(
                        f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(parsed_args)}[/dim]",
                        title="⚠️ Command Warning",
                        border_style="yellow"
                    ))
            except Exception as e:
                self.console.print(Panel(
                    f"[red]Error executing command: {e}[/red]\n[dim]Command: {' '.join(parsed_args)}[/dim]",
                    title="❌ Command Error",
                    border_style="red"
                ))
        else:
            # If it's not a known command and not a path, keep feedback minimal
            self.console.print("[yellow]Unknown command. Type 'help' for a list of commands.[/yellow]")
    
    def _execute_scan_command(self, user_input: str):
        """Execute a scan command with proper path handling."""
        # Extract the scan command and path
        command = 'scan'
        input_parts = user_input[5:].strip()  # Remove 'scan ' prefix
        
        # Parse the input to separate path from flags
        # Handle Windows paths with spaces properly
        import re
        
        # Find all flags (starting with -- or -)
        flag_pattern = r'\s+(--[a-zA-Z0-9-]+(?:[=:]\S+)?|\-[a-zA-Z0-9])\s*'
        flags_found = re.findall(flag_pattern, input_parts)
        
        # Remove flags from the input to get the path
        path_part = re.sub(flag_pattern, '', input_parts).strip()
        
        # If no path found, try to extract from the original input
        if not path_part:
            # Split by spaces and find the first non-flag argument
            parts = input_parts.split()
            for part in parts:
                if not part.startswith('--') and not part.startswith('-'):
                    path_part = part
                    break
        
        # Build the parts list
        parts = [path_part] + flags_found if path_part else flags_found
        
        # Now we have the path and flags separated
        flags = flags_found
        
        # If no path found, error
        if path_part is None:
            self.console.print("[red]Error: No path specified for scan command[/red]")
            return
        
        # Build the parsed parts
        parsed_parts = [path_part] + flags
        
        # First part should be the path
        path_part = parsed_parts[0]
        
        # Handle quoted paths
        if path_part.startswith('"') and path_part.endswith('"'):
            path_part = path_part[1:-1]
        elif path_part.startswith("'") and path_part.endswith("'"):
            path_part = path_part[1:-1]
        
        # Handle Windows path normalization
        if sys.platform == 'win32':
            path_part = self._normalize_windows_path(path_part)
        
        # Build the complete command line arguments
        args = ['scan', path_part]
        
        # Auto-add company-id if available
        current_company = self._get_current_company()
        if current_company and '--company-id' not in user_input:
            args.extend(['--company-id', current_company])
            self.console.print(f"[dim]🔍 Auto-adding company: {current_company}[/dim]")
        
        # Parse all options from the parsed parts (skip the first part which is the path)
        remaining_parts = parsed_parts[1:] if len(parsed_parts) > 1 else []
        
        # Process each flag
        i = 0
        while i < len(remaining_parts):
            flag = remaining_parts[i]
            
            if flag == '--report':
                # Handle --report format
                if i + 1 < len(remaining_parts):
                    report_format = remaining_parts[i + 1]
                    args.extend(['--report', report_format])
                    i += 2
                else:
                    i += 1
            elif flag in ['--verbose', '-v']:
                args.append('--verbose')
                i += 1
            elif flag == '--debug':
                args.append('--debug')
                i += 1
            elif flag in ['--quiet', '-q']:
                args.append('--quiet')
                i += 1
            elif flag in ['--cfg', '--deep-scan']:
                args.append('--cfg')
                i += 1
            elif flag == '--cfg-confidence':
                # Handle --cfg-confidence value
                if i + 1 < len(remaining_parts):
                    confidence = remaining_parts[i + 1]
                    args.extend(['--cfg-confidence', confidence])
                    i += 2
                else:
                    i += 1
            elif flag == '--company-id':
                # Handle --company-id value
                if i + 1 < len(remaining_parts):
                    company_id = remaining_parts[i + 1]
                    args.extend(['--company-id', company_id])
                    i += 2
                else:
                    i += 1
            else:
                # Unknown flag, skip it
                i += 1
        
        # Add any remaining flags that weren't processed above
        for flag in remaining_parts:
            if flag not in ['--report', '--verbose', '-v', '--debug', '--quiet', '-q', '--cfg', '--deep-scan', '--cfg-confidence', '--company-id']:
                # Check if it's a format flag
                if flag == '--format' and remaining_parts.index(flag) + 1 < len(remaining_parts):
                    format_value = remaining_parts[remaining_parts.index(flag) + 1]
                    args.extend(['--format', format_value])
                # Check for other toggle flags
                elif flag in ['--telemetry', '--dev', '--scan-optional', '--no-scan-optional', 
                             '--allow-fallback-parsing', '--require-full-ast', '--no-report']:
                    args.append(flag)
        
        # Add verbose flag if logging is enabled and not already present
        if self.logging_enabled and '--verbose' not in args:
            args.append('--verbose')
        # Remove verbose flag if logging is disabled and present
        elif not self.logging_enabled and '--verbose' in args:
            args.remove('--verbose')
        
        # Debug output to see what's being executed
        self.console.print(f"[dim]Executing: {' '.join(args)}[/dim]")
        
        # Execute scan directly via service to avoid any CLI parsing conflicts
        try:
            from .services import ScanService, EXIT_SUCCESS, EXIT_VIOLATIONS_FOUND, EXIT_RUNTIME_ERROR, EXIT_CONFIG_ERROR
            scan_service = ScanService(self.config, self.output_manager)
            # Minimal options based on parsed flags; defaults mirror CLI
            scan_options = {
                'output_format': 'summary',
                'output_file': None,
                'max_file_size_mb': None,
                'exclude_patterns': None,
                'scan_optional': False,
                'strict_mode': False,
                'allow_fallback_parsing': True,
                'require_full_ast': False,
                'cfg_enabled': ('--cfg' in args),
                'cfg_confidence': None,
                'report_formats': None,
                'verbosity': 'summary',
                'telemetry': False,
                'secret_verify': True,
                'scan_path': path_part,
                'company_id': current_company,
                'compliance_mode': False,
                'compliance_alerts': 'detailed',
                'alert_threshold': 'low',
                'compliance_frameworks': ['gdpr'],
                'executive_summary': False
            }
            exit_code = scan_service.execute_scan(path_part, scan_options)
            if exit_code in (EXIT_SUCCESS, EXIT_VIOLATIONS_FOUND, EXIT_RUNTIME_ERROR, EXIT_CONFIG_ERROR):
                # Provide concise feedback consistent with CLI behavior
                if exit_code == EXIT_SUCCESS:
                    self.console.print("Completed successfully (exit code 0).")
                elif exit_code == EXIT_VIOLATIONS_FOUND:
                    self.console.print("Violations found (exit code 1).")
                elif exit_code == EXIT_RUNTIME_ERROR:
                    self.console.print("Runtime error (exit code 2).")
                elif exit_code == EXIT_CONFIG_ERROR:
                    self.console.print("Configuration error (exit code 3).")
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing scan: {e}[/red]",
                title="❌ Scan Error",
                border_style="red"
            ))
    
    def _execute_report_command(self, user_input: str):
        """Execute a report command with proper parsing."""
        # Extract the report command and arguments
        command = 'report'
        args_part = user_input[7:].strip()  # Remove 'report ' prefix
        
        # Parse arguments
        args = ['report']
        
        # Check for file path (first argument)
        parts = args_part.split()
        if parts:
            # First part should be the results file
            args.append(parts[0])
            
            # Parse remaining options
            remaining = ' '.join(parts[1:])
            remaining_lower = remaining.lower()
            
            # Check for output format
            if '--format' in remaining_lower:
                # Extract the format value properly
                import re
                format_match = re.search(r'--format\s+(\w+)', remaining)
                if format_match:
                    format_value = format_match.group(1)
                    args.extend(['--format', format_value])
            
            # Check for output file
            if '--output' in remaining_lower or '-o' in remaining_lower:
                import re
                match = re.search(r'--output\s+([^\s]+)', remaining)
                if match:
                    args.extend(['--output', match.group(1)])
                else:
                    match = re.search(r'-o\s+([^\s]+)', remaining)
                    if match:
                        args.extend(['--output', match.group(1)])
        
        # Check for all report toggle flags
        if '--latest' in remaining_lower:
            args.append('--latest')
        
        if '--list' in remaining_lower:
            args.append('--list')
        
        if '--include-metadata' in remaining_lower:
            args.append('--include-metadata')
        
        if '--template' in remaining_lower:
            import re
            match = re.search(r'--template\s+([^\s]+)', remaining)
            if match:
                args.extend(['--template', match.group(1)])
        
        # Execute the command
        try:
            exit_code = cli.main(args, standalone_mode=False)
            # Reduce noise: only show warning for actual errors (2/3)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing report command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                title="❌ Report Error",
                border_style="red"
            ))
    
    def _execute_generate_report_command(self, user_input: str):
        """Execute a generate_report command."""
        # Parse the command and options
        parts = user_input.split()
        command = 'generate-report'
        args = [command]
        
        # Parse format options
        input_lower = user_input.lower()
        if '--format' in input_lower:
            if 'json' in input_lower:
                args.extend(['--format', 'json'])
            elif 'html' in input_lower:
                args.extend(['--format', 'html'])
            elif 'pdf' in input_lower:
                args.extend(['--format', 'pdf'])
            elif 'table' in input_lower:
                args.extend(['--format', 'table'])
            elif 'markdown' in input_lower:
                args.extend(['--format', 'markdown'])
        
        # Parse output options
        if '--output' in input_lower or '-o' in input_lower:
            import re
            match = re.search(r'--output\s+([^\s]+)', user_input)
            if match:
                args.extend(['--output', match.group(1)])
            else:
                match = re.search(r'-o\s+([^\s]+)', user_input)
                if match:
                    args.extend(['--output', match.group(1)])
        
        # Parse other options
        if '--verbose' in input_lower or '-v' in input_lower:
            args.append('--verbose')
        if '--latest' in input_lower:
            args.append('--latest')
        
        try:
            # Execute the command
            from levox.cli.commands import cli
            exit_code = cli.main(args=args, standalone_mode=False)
            
            if exit_code == 0:
                self.console.print(Panel(
                    f"[green]Report generated successfully![/green]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="✅ Report Generated",
                    border_style="green"
                ))
            else:
                self.console.print(Panel(
                    f"[yellow]Report generation completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Report Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing generate_report command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                title="❌ Generate Report Error",
                border_style="red"
            ))
    
    def _normalize_windows_path(self, path_part: str) -> str:
        """Normalize Windows path for better compatibility."""
        # Convert forward slashes to backslashes for Windows
        path_part = path_part.replace('/', '\\')
        
        # Handle UNC paths and drive letters
        if path_part.startswith('\\\\'):
            # UNC path - leave as is
            pass
        elif len(path_part) >= 2 and path_part[1] == ':':
            # Drive letter path - ensure proper format
            path_part = path_part[0].upper() + path_part[1:]
        elif not path_part.startswith('\\\\') and not path_part.startswith('.') and not path_part.startswith('\\'):
            # Relative path - ensure it's properly formatted
            path_part = str(Path.cwd() / path_part)
        
        return path_part

    def _looks_like_path(self, text: str) -> bool:
        """Heuristic to detect if user pasted a filesystem path."""
        if not text:
            return False
        # Windows drive or UNC, absolute/relative paths, or contains path separators
        if sys.platform == 'win32':
            return (
                (len(text) >= 2 and text[1] == ':') or
                text.startswith('\\\\') or
                '\\' in text or '/' in text or
                text.startswith('.')
            )
        else:
            return text.startswith('/') or '/' in text or text.startswith('.')
    
    def _looks_like_git_url(self, text: str) -> bool:
        """Heuristic to detect if user pasted a Git repository URL."""
        if not text:
            return False
        
        # Check for common Git URL patterns
        git_patterns = [
            'github.com',
            'gitlab.com',
            'bitbucket.org',
            'git@',
            '.git'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in git_patterns) and (
            text.startswith('http://') or 
            text.startswith('https://') or 
            text.startswith('git@') or
            'github.com' in text_lower or
            'gitlab.com' in text_lower or
            'bitbucket.org' in text_lower
        )
    
    def _execute_repo_scan(self, repo_url: str):
        """Execute repository scan with interactive workflow."""
        try:
            from ..integrations.repo_scanner import GitRepoScanner
            from ..models.repo_info import RepoConfig
            from ..cli.services import ScanService
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
            
            # Initialize repository scanner
            repo_config = RepoConfig()
            scanner = GitRepoScanner(repo_config)
            
            # Validate URL and get metadata
            self.console.print(f"[bold cyan]🔍 Analyzing repository...[/bold cyan]")
            
            try:
                metadata = scanner.get_repo_metadata(repo_url)
            except Exception as e:
                self.console.print(f"[red]❌ Invalid repository URL: {e}[/red]")
                return
            
            # Display repository information
            repo_info = Panel(
                f"[bold]Platform:[/bold] {metadata.platform.value.title()}\n"
                f"[bold]Repository:[/bold] {metadata.full_name}\n"
                f"[bold]Size:[/bold] {metadata.size_mb:.1f} MB\n"
                f"[bold]Visibility:[/bold] {metadata.visibility.value.title()}\n"
                f"[bold]Default Branch:[/bold] {metadata.default_branch}",
                title="📋 Repository Information",
                border_style="cyan"
            )
            self.console.print(repo_info)
            
            # Check if repository is too large
            if metadata.size_mb > repo_config.max_repo_size_mb:
                self.console.print(f"[yellow]⚠️ Repository is large ({metadata.size_mb:.1f} MB). This may take a while.[/yellow]")
                proceed = Prompt.ask("Continue?", choices=["y", "n"], default="y")
                if proceed.lower() != 'y':
                    return
            
            # Select clone strategy
            strategy = scanner.select_clone_strategy(metadata.size_mb)
            self.console.print(f"[dim]📥 Clone strategy: {strategy.value}[/dim]")
            
            # Clone repository with progress
            self.console.print(f"[bold green]📥 Cloning repository...[/bold green]")
            
            from time import perf_counter
            clone_started_at = perf_counter()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True  # clear the progress display when done
            ) as progress:
                
                clone_task = progress.add_task("Cloning...", total=100)
                
                def progress_callback(progress_info):
                    progress.update(clone_task, completed=progress_info.progress_percent, 
                                  description=progress_info.message)
                
                cloned_repo = scanner.clone_with_strategy(repo_url, strategy, progress_callback)
            clone_elapsed = perf_counter() - clone_started_at
            # After progress closes (transient), print a concise one-line summary
            self.console.print(f"[green]✅ Repository cloned[/green] [dim]({metadata.full_name}, {metadata.size_mb:.1f} MB, {clone_elapsed:.1f}s)[/dim]")
            
            # Execute scan
            self.console.print(f"[bold green]🔍 Scanning repository...[/bold green]")
            
            # Initialize scan service
            scan_service = ScanService(self.config, self.output_manager)
            
            # Prepare scan options
            scan_options = {
                'output_format': 'summary',
                'verbosity': 'summary',
                'scan_path': str(cloned_repo.local_path),
                'repo_url': repo_url,
                'cloned_repo': cloned_repo,
                'compliance_mode': True,  # Enable by default for enterprise
                'alert_threshold': 'high',
                'compliance_frameworks': ['gdpr', 'ccpa'] if self.config.license.tier == LicenseTier.BUSINESS else ['gdpr']
            }
            
            # Execute scan
            exit_code = scan_service.execute_scan(str(cloned_repo.local_path), scan_options)
            
            # Handle cleanup
            self._handle_repo_cleanup(cloned_repo)
            
        except Exception as e:
            # Only show tier message if frameworks truly unavailable
            try:
                from ..compliance.framework_engine import ComplianceFrameworkEngine
                available = ComplianceFrameworkEngine(self.config)._get_available_frameworks()
            except Exception:
                available = []
            if not available:
                self.console.print("[dim]No compliance issues can be generated in this license tier[/dim]")
            else:
                # Suppress verbose tracebacks in interactive mode for known parser syntax errors
                err_text = str(e)
                if isinstance(e, SyntaxError) or 'SyntaxError' in err_text:
                    self.console.print("[yellow]⚠️ Skipped files with syntax errors during analysis (details in debug logs)[/yellow]")
                else:
                    self.console.print(f"[red]❌ Repository scan failed: {e}[/red]")
                import traceback
                if self.logging_enabled:
                    self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    def _handle_repo_cleanup(self, cloned_repo):
        """Handle repository cleanup with user prompts."""
        try:
            from ..models.repo_info import ClonedRepo
            
            self.console.print(f"\n[bold yellow]🗑️ Cleanup Options[/bold yellow]")
            self.console.print(f"Repository cloned to: [cyan]{cloned_repo.local_path}[/cyan]")
            self.console.print(f"Size: [dim]{cloned_repo.metadata.size_mb:.1f} MB[/dim]")
            
            # Check if auto cleanup is configured
            if self.config.repo_auto_cleanup:
                cleanup_choice = "y"
                self.console.print("[dim]Auto cleanup enabled - repository will be deleted[/dim]")
            else:
                cleanup_choice = Prompt.ask(
                    "Delete cloned repository?",
                    choices=["y", "n", "always", "never"],
                    default="n"
                )
            
            if cleanup_choice in ["y", "always"]:
                try:
                    if cloned_repo.cleanup():
                        self.console.print("[green]✅ Repository cleaned up successfully[/green]")
                    else:
                        self.console.print("[yellow]⚠️ Failed to clean up repository[/yellow]")
                        self.console.print(f"[dim]Repository location: {cloned_repo.local_path}[/dim]")
                        self.console.print("[dim]You may need to manually delete this directory[/dim]")
                except Exception as e:
                    self.console.print(f"[red]❌ Cleanup error: {e}[/red]")
                    self.console.print(f"[dim]Repository location: {cloned_repo.local_path}[/dim]")
            else:
                self.console.print(f"[yellow]📁 Repository kept at: {cloned_repo.local_path}[/yellow]")
            
            # Update config if user chose always/never
            if cleanup_choice == "always":
                self.config.repo_auto_cleanup = True
                self.console.print("[dim]Auto cleanup enabled for future scans[/dim]")
            elif cleanup_choice == "never":
                self.config.repo_auto_cleanup = False
                self.console.print("[dim]Auto cleanup disabled for future scans[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Cleanup error: {e}[/red]")
    
    def _execute_cicd_command(self, user_input: str):
        """Execute CI/CD commands with proper argument parsing."""
        # Parse the command and arguments
        parts = user_input.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Build the complete command line arguments
        full_args = [command] + args
        
        # Add verbose flag if logging is enabled and not already present
        if self.logging_enabled and '--verbose' not in full_args:
            full_args.append('--verbose')
        
        # Debug output to see what's being executed
        self.console.print(f"[dim]Executing: {' '.join(full_args)}[/dim]")
        
        # Execute the command
        try:
            exit_code = cli.main(full_args, standalone_mode=False)
            # Reduce noise: only show warning for actual errors (2/3)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(full_args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            # Enhanced error handling with suggestions
            error_msg = str(e)
            suggestions = self._get_command_suggestions(user_input, error_msg, 'cicd')
            
            self.console.print(Panel(
                f"[red]Error executing CI/CD command: {e}[/red]\n[dim]Command: {' '.join(full_args)}[/dim]\n\n{suggestions}",
                title="❌ CI/CD Command Error",
                border_style="red"
            ))
    
    def _execute_company_command(self, user_input: str):
        """Execute company management commands."""
        # Parse the command and arguments using shlex for proper quote handling
        import shlex
        try:
            parts = shlex.split(user_input)
        except ValueError:
            # Fallback to simple split if shlex fails
            parts = user_input.split()
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Build the complete command line arguments
        full_args = [command] + args
        
        # Add verbose flag if logging is enabled and not already present
        if self.logging_enabled and '--verbose' not in full_args:
            full_args.append('--verbose')
        
        # Debug output to see what's being executed
        self.console.print(f"[dim]Executing: {' '.join(full_args)}[/dim]")
        
        # Execute the command
        try:
            exit_code = cli.main(full_args, standalone_mode=False)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(full_args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
            
            # If this was a company create command, update current company
            if 'create' in full_args and exit_code == 0:
                # Try to extract company ID from output (this is a bit hacky)
                # In a real implementation, we'd get this from the command return value
                try:
                    from ..compliance.evidence_store import get_evidence_store
                    evidence_store = get_evidence_store("local")
                    companies = evidence_store.get_all_companies()
                    if companies:
                        self.current_company = companies[0].id
                        self.console.print(f"[green]✅ Company context set to: {self.current_company}[/green]")
                except Exception:
                    pass
                    
        except Exception as e:
            # Enhanced error handling with suggestions
            error_msg = str(e)
            suggestions = self._get_command_suggestions(user_input, error_msg, 'company')
            
            self.console.print(Panel(
                f"[red]Error executing company command: {e}[/red]\n[dim]Command: {' '.join(full_args)}[/dim]\n\n{suggestions}",
                title="❌ Company Command Error",
                border_style="red"
            ))
    
    def _execute_evidence_command(self, user_input: str):
        """Execute evidence generation commands."""
        # Parse the command and arguments using shlex for proper quote handling
        import shlex
        try:
            parts = shlex.split(user_input)
        except ValueError:
            # Fallback to simple split if shlex fails
            parts = user_input.split()
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Build the complete command line arguments
        full_args = [command] + args
        
        # Note: Company ID is now a required positional argument for evidence generate
        # No need to auto-add since it's mandatory
        
        # Add verbose flag if logging is enabled and not already present
        if self.logging_enabled and '--verbose' not in full_args:
            full_args.append('--verbose')
        
        # Debug output to see what's being executed
        self.console.print(f"[dim]Executing: {' '.join(full_args)}[/dim]")
        
        # Execute the command
        try:
            exit_code = cli.main(full_args, standalone_mode=False)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(full_args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            # Enhanced error handling with suggestions
            error_msg = str(e)
            suggestions = self._get_command_suggestions(user_input, error_msg, 'evidence')
            
            self.console.print(Panel(
                f"[red]Error executing evidence command: {e}[/red]\n[dim]Command: {' '.join(full_args)}[/dim]\n\n{suggestions}",
                title="❌ Evidence Command Error",
                border_style="red"
            ))
    
    def _execute_setup_command(self):
        """Execute the setup/configuration command."""
        try:
            args = ['setup']
            exit_code = cli.main(args, standalone_mode=False)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Setup completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Setup Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing setup command: {e}[/red]\n[dim]Command: setup[/dim]",
                title="❌ Setup Error",
                border_style="red"
            ))
    
    def _initialize_quick_actions(self) -> List[Dict[str, str]]:
        """Initialize quick actions menu."""
        return [
            {
                "id": "1",
                "title": "Quick Scan",
                "description": "Scan current directory with basic settings",
                "command": "scan . --format summary"
            },
            {
                "id": "2", 
                "title": "Deep Scan",
                "description": "Scan with full analysis (CFG + ML)",
                "command": "scan . --cfg --format json html"
            },
            {
                "id": "3",
                "title": "Generate Report",
                "description": "Generate report from last scan",
                "command": "generate-report --format html"
            },
            {
                "id": "4",
                "title": "View History",
                "description": "Show scan history and results",
                "command": "history --detailed"
            },
            {
                "id": "5",
                "title": "Manage License",
                "description": "Check license status and upgrade",
                "command": "license --status"
            },
            {
                "id": "6",
                "title": "Configure Settings",
                "description": "Run setup wizard",
                "command": "setup"
            },
            {
                "id": "7",
                "title": "View Documentation",
                "description": "Show help and examples",
                "command": "help"
            },
            {
                "id": "8",
                "title": "Company Setup",
                "description": "Create or manage company profile",
                "command": "company create"
            },
            {
                "id": "9",
                "title": "Evidence Package",
                "description": "Generate compliance evidence",
                "command": "evidence generate"
            },
            {
                "id": "0",
                "title": "Exit",
                "description": "Exit the interactive CLI",
                "command": "exit"
            }
        ]
    
    def _initialize_shortcuts(self) -> Dict[str, str]:
        """Initialize command shortcuts."""
        return {
            "s": "scan .",
            "r": "generate-report",
            "h": "help",
            "m": "menu",
            "q": "exit",
            "l": "history",
            "c": "company list",
            "e": "evidence generate",
            "d": "scan . --cfg",
            "f": "scan . --format json"
        }
    
    def _show_quick_actions_menu(self):
        """Show the quick actions menu."""
        self.console.print("\n[bold cyan]🚀 Quick Actions Menu[/bold cyan]")
        
        # Create menu table
        menu_table = Table(
            title="Select an action",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )
        menu_table.add_column("ID", style="cyan", width=4, justify="center")
        menu_table.add_column("Action", style="white", width=20)
        menu_table.add_column("Description", style="dim", width=40)
        
        for action in self.quick_actions:
            menu_table.add_row(
                action["id"],
                action["title"],
                action["description"]
            )
        
        self.console.print(menu_table)
        
        # Get user selection
        try:
            choice = Prompt.ask(
                "\n[bold]Select an action[/bold]",
                choices=[action["id"] for action in self.quick_actions],
                default="1"
            )
            
            # Find selected action
            selected_action = next(
                (action for action in self.quick_actions if action["id"] == choice),
                None
            )
            
            if selected_action:
                if selected_action["command"] == "exit":
                    self._show_goodbye()
                    self.running = False
                else:
                    self.console.print(f"\n[dim]Executing: {selected_action['command']}[/dim]")
                    self._execute_command(selected_action["command"])
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Menu cancelled[/yellow]")
    
    def _get_enhanced_prompt(self) -> str:
        """Get enhanced prompt with context information."""
        # Simple, clean prompt
        return "[bold blue]levox[/bold blue] > "
    
    def _show_enhanced_help(self, command: Optional[str] = None):
        """Show enhanced help with shortcuts and tips."""
        if command:
            self._show_command_help(command)
        else:
            self._show_all_commands_help()
    
    def _show_all_commands_help(self):
        """Show categorized help for all commands."""
        self.console.print("\n[bold cyan]📚 Levox Interactive CLI Help[/bold cyan]")
        
        # Command shortcuts
        shortcuts_table = Table(
            title="Command Shortcuts",
            show_header=True,
            header_style="bold magenta",
            border_style="green"
        )
        shortcuts_table.add_column("Shortcut", style="cyan", width=8)
        shortcuts_table.add_column("Command", style="white", width=20)
        shortcuts_table.add_column("Description", style="dim", width=30)
        
        for shortcut, command in self.command_shortcuts.items():
            description = {
                "s": "Quick scan current directory",
                "r": "Generate report from last scan",
                "h": "Show this help",
                "m": "Show quick actions menu",
                "q": "Exit the CLI",
                "l": "Show scan history",
                "c": "List companies",
                "e": "Generate evidence package",
                "d": "Deep scan with CFG analysis",
                "f": "Scan with JSON output"
            }.get(shortcut, "Custom command")
            
            shortcuts_table.add_row(shortcut, command, description)
        
        self.console.print(shortcuts_table)
        
        # Scanning Commands
        scan_table = Table(title="🔍 Scanning Commands", show_header=True, header_style="bold green")
        scan_table.add_column("Command", style="cyan", no_wrap=True)
        scan_table.add_column("Description", style="white")
        scan_table.add_column("Usage", style="dim")
        
        scan_table.add_row("scan", "Scan files/directories for PII violations", "scan [path] [options]")
        scan_table.add_row("", "  --cfg", "Enable Control Flow Graph analysis")
        scan_table.add_row("", "  --format json|html|pdf", "Output format")
        scan_table.add_row("", "  --report", "Generate reports after scan")
        scan_table.add_row("", "  --verbose", "Show detailed output")
        
        self.console.print(scan_table)
        
        # Reporting Commands
        report_table = Table(title="📊 Reporting Commands", show_header=True, header_style="bold blue")
        report_table.add_column("Command", style="cyan", no_wrap=True)
        report_table.add_column("Description", style="white")
        report_table.add_column("Usage", style="dim")
        
        report_table.add_row("report", "Generate reports from scan results", "report [options]")
        report_table.add_row("", "  --latest", "Use most recent scan")
        report_table.add_row("", "  --format json|html|pdf", "Output format")
        report_table.add_row("", "  --output <file>", "Save to specific file")
        report_table.add_row("generate-report", "Generate report from last scan", "generate-report [options]")
        report_table.add_row("set-report-directory", "Choose where reports are saved", "set-report-directory")
        
        self.console.print(report_table)
        
        # Compliance Commands
        compliance_table = Table(title="🏢 Compliance Commands", show_header=True, header_style="bold yellow")
        compliance_table.add_column("Command", style="cyan", no_wrap=True)
        compliance_table.add_column("Description", style="white")
        compliance_table.add_column("Usage", style="dim")
        
        compliance_table.add_row("company", "Manage company profiles", "company [create|list|select] [options]")
        compliance_table.add_row("", "  create --name 'Company'", "Create new company profile")
        compliance_table.add_row("", "  list", "List all companies")
        compliance_table.add_row("", "  select <id>", "Select active company")
        compliance_table.add_row("evidence", "Generate evidence packages", "evidence [generate|list] [options]")
        compliance_table.add_row("", "  generate --company <id>", "Generate evidence package")
        compliance_table.add_row("", "  trends", "Show compliance trends")
        
        self.console.print(compliance_table)
        
        # System Commands
        system_table = Table(title="⚙️ System Commands", show_header=True, header_style="bold magenta")
        system_table.add_column("Command", style="cyan", no_wrap=True)
        system_table.add_column("Description", style="white")
        system_table.add_column("Usage", style="dim")
        
        system_table.add_row("status", "Show system status and capabilities", "status [--detailed]")
        system_table.add_row("license", "Manage and validate license", "license [options]")
        system_table.add_row("", "  --register <key>", "Register license key")
        system_table.add_row("", "  --upgrade", "Open upgrade page")
        system_table.add_row("", "  --status", "Check license status")
        system_table.add_row("setup", "Run interactive setup wizard", "setup")
        system_table.add_row("history", "Show scan history and results", "history [options]")
        system_table.add_row("", "  --detailed", "Show detailed information")
        system_table.add_row("", "  --clear", "Clear all history")
        system_table.add_row("", "  --export <file>", "Export history to file")
        
        self.console.print(system_table)
        
        # Tips section
        tips_panel = Panel(
            "[bold]💡 Pro Tips:[/bold]\n"
            "• Type [cyan]help <command>[/cyan] for detailed help on specific commands\n"
            "• Type [cyan]menu[/cyan] or [cyan]m[/cyan] for quick actions\n"
            "• Paste any file path to scan it instantly\n"
            "• Paste Git URLs to scan repositories\n"
            "• Use [cyan]history[/cyan] to see past scans\n"
            "• Use [cyan]setup[/cyan] to configure preferences\n"
            "• Press [cyan]Ctrl+C[/cyan] to cancel any operation",
            title="Tips & Tricks",
            border_style="yellow"
        )
        self.console.print(tips_panel)
        
        # Show recent paths if available
        if self.recent_paths:
            self.console.print(f"\n[bold]Recent Scan Paths:[/bold]")
            for i, path in enumerate(self.recent_paths[:5], 1):
                self.console.print(f"  {i}. [cyan]{path}[/cyan]")
            self.console.print(f"[dim]Use: scan <number> to scan a recent path[/dim]")
    
    def _show_command_help(self, command: str):
        """Show detailed help for a specific command."""
        command = command.lower().strip()
        
        if command == 'scan':
            self.console.print("\n[bold cyan]🔍 Scan Command Help[/bold cyan]")
            self.console.print("Scan files and directories for PII violations and GDPR compliance.")
            self.console.print("\n[bold]Usage:[/bold] scan [path] [options]")
            self.console.print("\n[bold]Arguments:[/bold]")
            self.console.print("  path    Directory or file to scan (default: current directory)")
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  --cfg              Enable Control Flow Graph analysis")
            self.console.print("  --format FORMAT   Output format (json, html, pdf, table)")
            self.console.print("  --report           Generate reports after scan")
            self.console.print("  --verbose, -v      Show detailed output")
            self.console.print("  --quiet, -q        Suppress non-essential output")
            self.console.print("  --limit N          Limit number of results")
            self.console.print("\n[bold]Examples:[/bold]")
            self.console.print("  scan .                    # Scan current directory")
            self.console.print("  scan /path/to/code        # Scan specific directory")
            self.console.print("  scan . --cfg --format json # Deep scan with JSON output")
            self.console.print("  scan . --report html      # Scan and generate HTML report")
            
        elif command == 'report':
            self.console.print("\n[bold cyan]📊 Report Command Help[/bold cyan]")
            self.console.print("Generate reports from scan results.")
            self.console.print("\n[bold]Usage:[/bold] report [options]")
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  --latest              Use most recent scan results")
            self.console.print("  --format FORMAT       Output format (json, html, pdf)")
            self.console.print("  --output FILE         Save to specific file")
            self.console.print("  --template TEMPLATE    Use custom template")
            self.console.print("  --include-metadata    Include scan metadata")
            self.console.print("\n[bold]Examples:[/bold]")
            self.console.print("  report --latest --format html")
            self.console.print("  report --output scan_report.html")
            self.console.print("  report --template custom.html")
            
        elif command == 'company':
            self.console.print("\n[bold cyan]🏢 Company Command Help[/bold cyan]")
            self.console.print("Manage company profiles for compliance tracking.")
            self.console.print("\n[bold]Usage:[/bold] company [create|list|select] [options]")
            self.console.print("\n[bold]Subcommands:[/bold]")
            self.console.print("  create --name NAME    Create new company profile")
            self.console.print("  list                  List all companies")
            self.console.print("  select ID             Select active company")
            self.console.print("\n[bold]Examples:[/bold]")
            self.console.print("  company create --name 'My Company'")
            self.console.print("  company list")
            self.console.print("  company select company_123")
            
        elif command == 'history':
            self.console.print("\n[bold cyan]📜 History Command Help[/bold cyan]")
            self.console.print("Show scan history and available results.")
            self.console.print("\n[bold]Usage:[/bold] history [options]")
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  --detailed            Show detailed information")
            self.console.print("  --limit N             Limit number of results")
            self.console.print("  --clear               Clear all history")
            self.console.print("  --clear-id ID         Clear specific result")
            self.console.print("  --select ID           Show details for specific result")
            self.console.print("  --export FILE         Export history to file")
            self.console.print("\n[bold]Examples:[/bold]")
            self.console.print("  history                    # Show recent scans")
            self.console.print("  history --detailed         # Show detailed information")
            self.console.print("  history --clear            # Clear all history")
            self.console.print("  history --export history.json")
            
        elif command == 'license':
            self.console.print("\n[bold cyan]🔑 License Command Help[/bold cyan]")
            self.console.print("Manage and validate Levox license.")
            self.console.print("\n[bold]Usage:[/bold] license [options]")
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("  --register KEY         Register license key")
            self.console.print("  --upgrade              Open license upgrade page")
            self.console.print("  --status               Check license status")
            self.console.print("  --validate             Force license validation")
            self.console.print("  --refresh              Refresh license cache")
            self.console.print("\n[bold]Examples:[/bold]")
            self.console.print("  license --register abc123")
            self.console.print("  license --upgrade")
            self.console.print("  license --status")
            
        else:
            self.console.print(f"\n[bold red]❌ Unknown command: {command}[/bold red]")
            self.console.print("Type [bold]help[/bold] to see all available commands.")
            self.console.print("Type [bold]help <command>[/bold] for detailed help on specific commands.")
    
    def _add_to_history(self, command: str):
        """Add command to history."""
        self.command_history.append(command)
        if len(self.command_history) > 50:  # Keep last 50 commands
            self.command_history = self.command_history[-50:]
    
    def _add_to_recent_paths(self, path: str):
        """Add path to recent paths."""
        if path not in self.recent_paths:
            self.recent_paths.insert(0, path)
            if len(self.recent_paths) > 10:  # Keep last 10 paths
                self.recent_paths = self.recent_paths[:10]
