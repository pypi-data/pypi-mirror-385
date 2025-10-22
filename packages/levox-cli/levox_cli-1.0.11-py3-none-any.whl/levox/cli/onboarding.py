"""
Levox Interactive Onboarding Wizard

Provides a guided first-run experience for new users, helping them set up
their workspace, configure preferences, and get started with their first scan.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box

from ..core.config import Config, LicenseTier, load_default_config
from ..core.user_config import UserConfig, UserPreferences


@dataclass
class OnboardingStep:
    """Represents a step in the onboarding process."""
    id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False


class OnboardingWizard:
    """Interactive onboarding wizard for first-time Levox users."""
    
    def __init__(self):
        """Initialize the onboarding wizard."""
        self.console = Console(emoji=(sys.platform != 'win32'))
        self.config = load_default_config()
        self.user_config = UserConfig()
        self.steps: List[OnboardingStep] = []
        self.results: Dict[str, Any] = {}
        
        # Initialize onboarding steps
        self._initialize_steps()
    
    def _initialize_steps(self):
        """Initialize the onboarding steps."""
        self.steps = [
            OnboardingStep(
                id="welcome",
                title="Welcome to Levox",
                description="Get started with enterprise-grade PII detection",
                required=True
            ),
            OnboardingStep(
                id="license",
                title="License Setup",
                description="Configure your license tier and registration",
                required=True
            ),
            OnboardingStep(
                id="workspace",
                title="Workspace Setup",
                description="Configure default scan paths and exclusions",
                required=True
            ),
            OnboardingStep(
                id="preferences",
                title="Output Preferences",
                description="Set up report formats and output directories",
                required=False
            ),
            OnboardingStep(
                id="git_credentials",
                title="Git Integration",
                description="Configure Git credentials for repository scanning",
                required=False
            ),
            OnboardingStep(
                id="ml_preferences",
                title="ML Model Preferences",
                description="Configure machine learning model settings",
                required=False
            ),
            OnboardingStep(
                id="tutorial",
                title="Quick Tutorial",
                description="Try your first scan with guided assistance",
                required=False
            )
        ]
    
    def _validate_path(self, path: str, create_if_missing: bool = False) -> bool:
        """Validate and optionally create path."""
        try:
            path_obj = Path(path)
            if path_obj.exists():
                return True
            elif create_if_missing:
                path_obj.mkdir(parents=True, exist_ok=True)
                return True
            else:
                return False
        except Exception:
            return False
    
    def _validate_yes_no(self, value: str) -> bool:
        """Validate yes/no input."""
        return value.lower().strip() in ['y', 'yes', 'n', 'no']
    
    def _validate_choice(self, value: str, valid_choices: List[str]) -> bool:
        """Validate choice from list."""
        return value.lower().strip() in [choice.lower() for choice in valid_choices]
    
    def _validate_license_key(self, key: str) -> bool:
        """Validate license key format."""
        if not key or len(key.strip()) < 10:
            return False
        # Basic format validation - alphanumeric with some special chars
        import re
        return bool(re.match(r'^[a-zA-Z0-9\-_]+$', key.strip()))
    
    def _validate_git_url(self, url: str) -> bool:
        """Validate Git URL format."""
        import re
        git_patterns = [
            r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^git@github\.com:[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^git@gitlab\.com:[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^git@bitbucket\.org:[\w\-\.]+/[\w\-\.]+(?:\.git)?$'
        ]
        return any(re.match(pattern, url.strip()) for pattern in git_patterns)
    
    def _prompt_with_validation(self, prompt: str, validator, default=None, max_retries=3, error_msg="Invalid input. Please try again."):
        """Generic prompt with validation and retry."""
        for attempt in range(max_retries):
            try:
                if default:
                    value = Prompt.ask(prompt, default=default)
                else:
                    value = Prompt.ask(prompt)
                
                if validator(value):
                    return value
                else:
                    if attempt < max_retries - 1:
                        self.console.print(f"[red]{error_msg}[/red]")
                    else:
                        self.console.print(f"[red]Maximum retries exceeded. Using default: {default}[/red]")
                        return default
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Setup cancelled by user.[/yellow]")
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    self.console.print(f"[red]Error: {e}[/red]")
                else:
                    self.console.print(f"[red]Maximum retries exceeded. Using default: {default}[/red]")
                    return default
        
        return default
    
    def run(self) -> bool:
        """
        Run the complete onboarding wizard.
        
        Returns:
            True if onboarding completed successfully, False if cancelled
        """
        try:
            self._show_welcome_banner()
            
            # Check if this is actually a first run
            if not self._is_first_run():
                if not Confirm.ask("It looks like you've used Levox before. Run setup again?"):
                    return False
            
            # Run each step
            for step in self.steps:
                if not self._run_step(step):
                    if step.required:
                        self.console.print("[red]❌ Required step cancelled. Onboarding incomplete.[/red]")
                        return False
                    else:
                        self.console.print(f"[yellow]⚠️ Skipping optional step: {step.title}[/yellow]")
                        continue
            
            # Save configuration
            self._save_configuration()
            
            # Show completion
            self._show_completion()
            
            return True
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Onboarding cancelled by user.[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Onboarding failed: {e}[/red]")
            return False
    
    def _is_first_run(self) -> bool:
        """Check if this is the first time running Levox."""
        first_run_marker = Path.home() / '.levox' / 'first_run'
        return not first_run_marker.exists()
    
    def _run_step(self, step: OnboardingStep) -> bool:
        """Run a single onboarding step."""
        self.console.print(f"\n[bold cyan]Step {self.steps.index(step) + 1}/{len(self.steps)}: {step.title}[/bold cyan]")
        self.console.print(f"[dim]{step.description}[/dim]")
        
        try:
            if step.id == "welcome":
                return self._step_welcome()
            elif step.id == "license":
                return self._step_license()
            elif step.id == "workspace":
                return self._step_workspace()
            elif step.id == "preferences":
                return self._step_preferences()
            elif step.id == "git_credentials":
                return self._step_git_credentials()
            elif step.id == "ml_preferences":
                return self._step_ml_preferences()
            elif step.id == "tutorial":
                return self._step_tutorial()
            else:
                self.console.print(f"[yellow]Unknown step: {step.id}[/yellow]")
                return True
        except Exception as e:
            self.console.print(f"[red]Error in step {step.title}: {e}[/red]")
            return False
    
    def _step_welcome(self) -> bool:
        """Welcome step with feature overview."""
        welcome_text = """
🔒 Welcome to Levox - Enterprise PII Detection CLI

Levox helps you find and secure Personally Identifiable Information (PII) 
in your codebase with a powerful 7-stage detection pipeline:

• Stage 1: Regex Detection (Basic patterns)
• Stage 2: AST Analysis (Code structure analysis) 
• Stage 3: Context Analysis (Semantic understanding)
• Stage 4: Dataflow Analysis (Variable tracking)
• Stage 5: CFG Analysis (Control flow analysis)
• Stage 6: ML Filtering (Machine learning filtering)
• Stage 7: GDPR Compliance (Regulatory compliance)

Key Features:
✓ Multi-language support (Python, JavaScript, Java)
✓ Local scanning (your code never leaves your machine)
✓ JSON/SARIF/HTML/PDF report generation
✓ CI/CD integration
✓ Enterprise-grade performance
✓ GDPR compliance checking
        """
        
        panel = Panel(
            welcome_text,
            title="🚀 Welcome to Levox",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(Align.center(panel))
        
        return Confirm.ask("\nReady to get started?", default=True)
    
    def _step_license(self) -> bool:
        """License setup step."""
        self.console.print("\n[bold]License Configuration[/bold]")
        
        # Check for existing license
        try:
            from ..core.license_client import get_license_client
            license_client = get_license_client()
            license_info = license_client.get_license_info()
            
            if license_info and license_info.is_valid():
                self.console.print(f"[green]✅ License found: {license_info.tier.value}[/green]")
                return True
        except Exception:
            pass
        
        # Show license options
        license_table = Table(title="Available License Tiers", show_header=True, header_style="bold magenta")
        license_table.add_column("Tier", style="cyan", no_wrap=True)
        license_table.add_column("Features", style="white")
        license_table.add_column("Price", style="green")
        
        license_table.add_row(
            "Free",
            "Basic regex detection, JSON reports",
            "Free"
        )
        license_table.add_row(
            "Premium",
            "AST + Context analysis, HTML/PDF reports",
            "$29/month"
        )
        license_table.add_row(
            "Enterprise",
            "Full pipeline + ML + GDPR compliance",
            "$99/month"
        )
        
        self.console.print(license_table)
        
        # License setup options
        self.console.print("\n[bold]License Setup Options:[/bold]")
        self.console.print("1. Continue with Free tier (limited features)")
        self.console.print("2. Register for Premium/Enterprise trial")
        self.console.print("3. Enter existing license key")
        self.console.print("4. Skip for now")
        
        choice = self._prompt_with_validation(
            "Choose an option",
            lambda x: self._validate_choice(x, ["1", "2", "3", "4"]),
            default="1",
            error_msg="Please choose 1, 2, 3, or 4"
        )
        
        if choice == "1":
            self.results["license_tier"] = "free"
            self.console.print("[green]✅ Using Free tier[/green]")
            return True
        elif choice == "2":
            self._handle_license_registration()
            return True
        elif choice == "3":
            return self._handle_license_key_entry()
        else:
            self.console.print("[yellow]⚠️ Skipping license setup[/yellow]")
            return True
    
    def _step_workspace(self) -> bool:
        """Workspace setup step."""
        self.console.print("\n[bold]Workspace Configuration[/bold]")
        
        # Default scan directory
        default_scan_dir = self._prompt_with_validation(
            "Default scan directory",
            lambda x: self._validate_path(x, create_if_missing=False),
            default=str(Path.cwd()),
            error_msg="Directory does not exist. Please enter a valid path."
        )
        
        # Smart exclusions
        self.console.print("\n[bold]Smart Exclusions[/bold]")
        self.console.print("Levox can automatically exclude common non-scannable directories:")
        
        exclusion_table = Table(show_header=True, header_style="bold magenta")
        exclusion_table.add_column("Pattern", style="cyan")
        exclusion_table.add_column("Description", style="white")
        
        exclusion_table.add_row("node_modules/", "Node.js dependencies")
        exclusion_table.add_row("venv/", "Python virtual environments")
        exclusion_table.add_row(".git/", "Git repository data")
        exclusion_table.add_row("__pycache__/", "Python bytecode cache")
        exclusion_table.add_row("dist/", "Build output directories")
        exclusion_table.add_row("build/", "Build output directories")
        exclusion_table.add_row("*.log", "Log files")
        exclusion_table.add_row("*.jpg, *.png", "Image files")
        
        self.console.print(exclusion_table)
        
        smart_exclusions = self._prompt_with_validation(
            "Enable smart exclusions?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if smart_exclusions and smart_exclusions.lower() in ['y', 'yes']:
            self.results["smart_exclusions"] = True
            self.console.print("[green]✅ Smart exclusions enabled[/green]")
        else:
            self.results["smart_exclusions"] = False
            self.console.print("[yellow]⚠️ Smart exclusions disabled[/yellow]")
        
        # Project type detection
        self.console.print("\n[bold]Project Type Detection[/bold]")
        auto_detect = self._prompt_with_validation(
            "Auto-detect project type (Python/JS/Java)?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if auto_detect and auto_detect.lower() in ['y', 'yes']:
            self.results["auto_detect_project"] = True
            self.console.print("[green]✅ Auto-detection enabled[/green]")
        else:
            self.results["auto_detect_project"] = False
        
        self.results["default_scan_dir"] = default_scan_dir
        return True
    
    def _step_preferences(self) -> bool:
        """Output preferences step."""
        self.console.print("\n[bold]Output Preferences[/bold]")
        
        # Report formats
        self.console.print("Select your preferred report formats:")
        formats = []
        
        json_reports = self._prompt_with_validation(
            "JSON reports (for CI/CD integration)?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        if json_reports and json_reports.lower() in ['y', 'yes']:
            formats.append("json")
            
        html_reports = self._prompt_with_validation(
            "HTML reports (for human reading)?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        if html_reports and html_reports.lower() in ['y', 'yes']:
            formats.append("html")
            
        pdf_reports = self._prompt_with_validation(
            "PDF reports (for documentation)?",
            self._validate_yes_no,
            default="n",
            error_msg="Please enter 'y' or 'n'"
        )
        if pdf_reports and pdf_reports.lower() in ['y', 'yes']:
            formats.append("pdf")
            
        sarif_reports = self._prompt_with_validation(
            "SARIF reports (for security tools)?",
            self._validate_yes_no,
            default="n",
            error_msg="Please enter 'y' or 'n'"
        )
        if sarif_reports and sarif_reports.lower() in ['y', 'yes']:
            formats.append("sarif")
        
        self.results["preferred_formats"] = formats
        
        # Report directory
        report_dir = self._prompt_with_validation(
            "Report output directory",
            lambda x: self._validate_path(x, create_if_missing=True),
            default=str(Path.home() / "levox_reports"),
            error_msg="Invalid directory path. Please enter a valid path."
        )
        self.results["report_directory"] = report_dir
        
        # Verbosity level
        self.console.print("\n[bold]Verbosity Level[/bold]")
        verbosity_choice = self._prompt_with_validation(
            "Default verbosity level",
            lambda x: self._validate_choice(x, ["quiet", "normal", "verbose"]),
            default="normal",
            error_msg="Please choose 'quiet', 'normal', or 'verbose'"
        )
        self.results["verbosity"] = verbosity_choice
        
        return True
    
    def _step_git_credentials(self) -> bool:
        """Git credentials setup step."""
        self.console.print("\n[bold]Git Integration[/bold]")
        
        configure_git = self._prompt_with_validation(
            "Configure Git credentials for repository scanning?",
            self._validate_yes_no,
            default="n",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if not configure_git or configure_git.lower() not in ['y', 'yes']:
            self.console.print("[yellow]Skipping Git setup[/yellow]")
            return True
        
        # GitHub token
        configure_github = self._prompt_with_validation(
            "Configure GitHub access?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if configure_github and configure_github.lower() in ['y', 'yes']:
            github_token = Prompt.ask("GitHub personal access token (optional)", password=True)
            if github_token:
                self.results["github_token"] = github_token
                self.console.print("[green]✅ GitHub token configured[/green]")
        
        # GitLab token
        configure_gitlab = self._prompt_with_validation(
            "Configure GitLab access?",
            self._validate_yes_no,
            default="n",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if configure_gitlab and configure_gitlab.lower() in ['y', 'yes']:
            gitlab_token = Prompt.ask("GitLab personal access token (optional)", password=True)
            if gitlab_token:
                self.results["gitlab_token"] = gitlab_token
                self.console.print("[green]✅ GitLab token configured[/green]")
        
        return True
    
    def _step_ml_preferences(self) -> bool:
        """ML model preferences step."""
        self.console.print("\n[bold]Machine Learning Preferences[/bold]")
        
        configure_ml = self._prompt_with_validation(
            "Configure ML model settings?",
            self._validate_yes_no,
            default="n",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if not configure_ml or configure_ml.lower() not in ['y', 'yes']:
            self.console.print("[yellow]Using default ML settings[/yellow]")
            return True
        
        # Model download
        auto_download = self._prompt_with_validation(
            "Auto-download ML models when needed?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if auto_download and auto_download.lower() in ['y', 'yes']:
            self.results["auto_download_models"] = True
            self.console.print("[green]✅ Auto-download enabled[/green]")
        else:
            self.results["auto_download_models"] = False
        
        # Model cache directory
        model_cache_dir = self._prompt_with_validation(
            "ML model cache directory",
            lambda x: self._validate_path(x, create_if_missing=True),
            default=str(Path.home() / ".levox" / "models"),
            error_msg="Invalid directory path. Please enter a valid path."
        )
        self.results["model_cache_dir"] = model_cache_dir
        
        return True
    
    def _step_tutorial(self) -> bool:
        """Tutorial step with guided first scan."""
        self.console.print("\n[bold]Quick Tutorial[/bold]")
        
        try_tutorial = self._prompt_with_validation(
            "Try a guided first scan?",
            self._validate_yes_no,
            default="y",
            error_msg="Please enter 'y' or 'n'"
        )
        
        if not try_tutorial or try_tutorial.lower() not in ['y', 'yes']:
            self.console.print("[yellow]Skipping tutorial[/yellow]")
            return True
        
        # Create sample directory for tutorial
        tutorial_dir = Path.cwd() / "levox_tutorial"
        if not tutorial_dir.exists():
            tutorial_dir.mkdir(exist_ok=True)
            
            # Create sample files
            sample_python = tutorial_dir / "sample.py"
            sample_python.write_text('''
# Sample Python file with potential PII
user_email = "john.doe@example.com"
phone_number = "+1-555-123-4567"
ssn = "123-45-6789"
credit_card = "4111-1111-1111-1111"

def process_user_data(name, email):
    # This function processes user data
    return f"Hello {name}, your email is {email}"
''')
            
            sample_js = tutorial_dir / "sample.js"
            sample_js.write_text('''
// Sample JavaScript file with potential PII
const userData = {
    email: "jane.smith@example.com",
    phone: "+1-555-987-6543",
    ssn: "987-65-4321"
};

function validateUser(user) {
    // Validate user information
    return user.email && user.phone;
}
''')
            
            self.console.print(f"[green]✅ Created tutorial directory: {tutorial_dir}[/green]")
        
        # Run tutorial scan
        self.console.print("\n[bold]Running Tutorial Scan[/bold]")
        self.console.print("This will demonstrate Levox's detection capabilities...")
        
        try:
            # Import and run scan
            from ..core.engine import DetectionEngine
            from ..utils.progress_manager import ProgressManager
            
            engine = DetectionEngine(self.config)
            progress_manager = ProgressManager(quiet=False, theme='smooth')
            
            with progress_manager.file_scanning(2, "Tutorial Scan") as progress_callback:
                result = engine.scan_directory(str(tutorial_dir))
            
            # Show results
            self._show_tutorial_results(result)
            
            # Cleanup
            if Confirm.ask("Delete tutorial files?", default=True):
                import shutil
                shutil.rmtree(tutorial_dir, ignore_errors=True)
                self.console.print("[green]✅ Tutorial files cleaned up[/green]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Tutorial scan failed: {e}[/red]")
            return False
    
    def _handle_license_registration(self):
        """Handle license registration process."""
        self.console.print("\n[bold]License Registration[/bold]")
        self.console.print("To register for a trial or purchase a license:")
        self.console.print("1. Visit: https://levox.security/pricing")
        self.console.print("2. Choose your plan")
        self.console.print("3. Complete registration")
        self.console.print("4. Return here with your license key")
        
        if Confirm.ask("Open pricing page in browser?", default=True):
            import webbrowser
            webbrowser.open("https://levox.security/pricing")
        
        self.console.print("[yellow]You can configure your license later with: levox license --register[/yellow]")
    
    def _handle_license_key_entry(self) -> bool:
        """Handle license key entry."""
        license_key = self._prompt_with_validation(
            "Enter your license key",
            self._validate_license_key,
            error_msg="License key must be at least 10 characters and contain only alphanumeric characters, hyphens, and underscores"
        )
        
        if not license_key:
            self.console.print("[yellow]No license key entered[/yellow]")
            return True
        
        try:
            # Validate license key
            from ..core.license_client import get_license_client
            license_client = get_license_client()
            
            # This would validate the license key
            # For now, just store it
            self.results["license_key"] = license_key
            self.console.print("[green]✅ License key stored[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]License validation failed: {e}[/red]")
            return False
    
    def _show_tutorial_results(self, result):
        """Show tutorial scan results."""
        self.console.print("\n[bold]Tutorial Scan Results[/bold]")
        
        if result.total_matches > 0:
            self.console.print(f"[green]✅ Found {result.total_matches} potential PII matches![/green]")
            
            # Show summary table
            summary_table = Table(title="Detection Summary", show_header=True, header_style="bold magenta")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="white")
            
            summary_table.add_row("Files Scanned", str(result.files_scanned))
            summary_table.add_row("Files with Matches", str(result.files_with_matches))
            summary_table.add_row("Total Matches", str(result.total_matches))
            summary_table.add_row("Scan Duration", f"{result.scan_duration:.2f}s")
            
            self.console.print(summary_table)
            
            # Show some example matches
            if result.file_results:
                self.console.print("\n[bold]Example Matches:[/bold]")
                for file_result in result.file_results[:3]:  # Show first 3 files
                    if file_result.matches:
                        self.console.print(f"[cyan]{file_result.file_path}:[/cyan] {len(file_result.matches)} matches")
                        for match in file_result.matches[:2]:  # Show first 2 matches per file
                            self.console.print(f"  • {match.match_type}: {match.matched_text[:50]}...")
        else:
            self.console.print("[yellow]No PII matches found in tutorial files[/yellow]")
    
    def _save_configuration(self):
        """Save the onboarding configuration."""
        try:
            # Create user preferences
            preferences = UserPreferences(
                default_scan_directory=self.results.get("default_scan_dir", str(Path.cwd())),
                preferred_formats=self.results.get("preferred_formats", ["json", "html"]),
                verbosity_level=self.results.get("verbosity", "normal"),
                smart_exclusions=self.results.get("smart_exclusions", True),
                auto_detect_project=self.results.get("auto_detect_project", True),
                auto_download_models=self.results.get("auto_download_models", True),
                model_cache_directory=self.results.get("model_cache_dir", str(Path.home() / ".levox" / "models")),
                report_directory=self.results.get("report_directory", str(Path.home() / "levox_reports"))
            )
            
            # Save user preferences
            self.user_config.save_preferences(preferences)
            
            # Set environment variables for Git credentials
            if "github_token" in self.results:
                os.environ["GITHUB_TOKEN"] = self.results["github_token"]
            if "gitlab_token" in self.results:
                os.environ["GITLAB_TOKEN"] = self.results["gitlab_token"]
            
            # Create first run marker
            first_run_marker = Path.home() / '.levox' / 'first_run'
            first_run_marker.parent.mkdir(exist_ok=True)
            first_run_marker.touch()
            
            self.console.print("[green]✅ Configuration saved[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Failed to save configuration: {e}[/red]")
    
    def _show_completion(self):
        """Show onboarding completion."""
        completion_text = """
🎉 Onboarding Complete!

You're all set to start using Levox. Here's what you can do next:

Quick Start:
• Scan current directory: levox scan
• Scan specific path: levox scan /path/to/code
• Generate report: levox scan --report html
• View help: levox --help

Advanced Usage:
• Interactive mode: levox interactive
• Company setup: levox company create --name "Your Company"
• Evidence generation: levox evidence generate
• CI/CD integration: levox init-ci

Need Help?
• Documentation: https://docs.levox.security
• Support: support@levox.security
• Examples: levox examples
        """
        
        panel = Panel(
            completion_text,
            title="🚀 Ready to Go!",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(Align.center(panel))
    
    def _show_welcome_banner(self):
        """Show the welcome banner."""
        banner_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗     ███████╗██╗   ██╗ ██████╗ ██╗  ██╗                ║
║    ██║     ██╔════╝╚██╗ ██╔╝██╔═══██╗╚██╗██╔╝                ║
║    ██║     █████╗   ╚████╔╝ ██║   ██║ ╚███╔╝                 ║
║    ██║     ██╔══╝    ╚██╔╝  ██║   ██║ ██╔██╗                 ║
║    ███████╗███████╗   ██║   ╚██████╔╝██╔╝ ██╗                ║
║    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝                ║
║                                                              ║
║              Enterprise PII Detection CLI                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(banner_text)
        self.console.print("[bold blue]Welcome to Levox Setup Wizard![/bold blue]")
        self.console.print("[dim]Let's get you started with enterprise-grade PII detection[/dim]\n")


def run_onboarding() -> bool:
    """Run the onboarding wizard."""
    wizard = OnboardingWizard()
    return wizard.run()


if __name__ == "__main__":
    run_onboarding()
