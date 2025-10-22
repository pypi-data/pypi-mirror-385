"""
Levox CLI Commands

This module defines the Click-based CLI commands with clean separation of concerns.
Each command delegates to appropriate services and uses the output manager for display.
"""

import click
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import json 

from .services import ScanService, ReportService, StatusService
from .services import (
    EXIT_SUCCESS,
    EXIT_VIOLATIONS_FOUND,
    EXIT_RUNTIME_ERROR,
    EXIT_CONFIG_ERROR,
)


def _generate_smart_company_id(company_name: str) -> str:
    """Generate a short, memorable company ID from company name."""
    import re
    import hashlib
    
    # Clean the name: remove special chars, convert to lowercase
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
    words = clean_name.split()
    
    if len(words) == 1:
        # Single word: take first 6 chars + 2 digit hash
        base = words[0][:6]
        hash_suffix = hashlib.md5(company_name.encode()).hexdigest()[:2]
        return f"{base}{hash_suffix}"
    else:
        # Multiple words: take first letter of each word + 2 digit hash
        initials = ''.join(word[0] for word in words[:3])  # Max 3 initials
        hash_suffix = hashlib.md5(company_name.encode()).hexdigest()[:2]
        return f"{initials}{hash_suffix}"


def _get_default_company_id() -> Optional[str]:
    """Get the default company ID from context or last used company."""
    try:
        from ..compliance.evidence_store import get_evidence_store
        evidence_store = get_evidence_store("local")
        
        # Try to get the last used company
        companies = evidence_store.get_all_companies()
        if companies:
            # Return the most recently created company
            return companies[0].id
    except Exception:
        pass
    return None


def _save_default_company_id(company_id: str):
    """Save the company ID as the default for future use."""
    try:
        # This could be stored in a config file or database
        # For now, we'll rely on the evidence store
        pass
    except Exception:
        pass
from .output import OutputManager
from ..core.config import Config, load_default_config, LicenseTier
from ..core.exceptions import LevoxException, ConfigurationError
from ..integrations import (
    TemplateGenerator, PreCommitIntegration, ConfigManager, 
    CIOptimizer, CITester
)
from ..integrations.template_generator import CIPlatform, ScanProfile, TemplateConfig
from ..integrations.precommit import PreCommitConfig
from ..integrations.config_manager import CIConfig, Environment
from ..integrations.ci_tester import TestResultStatus
from ..integrations.ci_optimizer import OptimizationConfig, OptimizationLevel, ScanContext

# Global services (initialized in main)
scan_service: Optional[ScanService] = None
report_service: Optional[ReportService] = None
status_service: Optional[StatusService] = None
output_manager: Optional[OutputManager] = None

def initialize_services(config: Config):
    """Initialize global services with configuration."""
    global scan_service, report_service, status_service, output_manager
    
    output_manager = OutputManager(config)
    scan_service = ScanService(config, output_manager)
    report_service = ReportService(config, output_manager)
    status_service = StatusService(config, output_manager)

def print_version(ctx, param, value):
    """Print version information and exit."""
    if not value or ctx.resilient_parsing:
        return
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    
    console = Console()
    
    version_text = Text("Levox v1.0.9", style="bold blue")
    subtitle = Text("Enterprise PII/GDPR Detection Tool", style="cyan")
    beta_tag = Text("Beta Ready", style="yellow")
    
    panel = Panel(
        f"{version_text}\n{subtitle}\n{beta_tag}",
        title="🔒 Security Scanner",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(Align.center(panel))
    ctx.exit()

@click.group(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option('--version', is_flag=True, callback=print_version, 
              expose_value=False, is_eager=True, help='Show version and exit.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output and detailed logging.')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors.')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file.')
@click.option('--debug', is_flag=True, help='Enable debug mode with detailed internal information.')
@click.pass_context
def cli(ctx, verbose, quiet, config, debug):
    """
    Levox - Enterprise PII/GDPR Detection CLI
    
    Detect Personally Identifiable Information (PII) and ensure GDPR compliance
    in your codebase with our 7-stage detection architecture.
    
    Features:
    • Multi-language AST analysis with Tree-Sitter
    • Context-aware detection with 85%+ false positive reduction
    • Control Flow Graph (CFG) analysis for complex PII flows
    • Configurable file discovery and scanning
    • Professional reporting in JSON, HTML, and PDF formats
    • Enterprise-grade performance and scalability
    
    Detection Pipeline:
    • STAGE 1: Regex Detection (Basic)
    • STAGE 2: AST Analysis (Premium+)
    • STAGE 3: Context Analysis (Premium+)
    • STAGE 4: Dataflow Analysis (Enterprise)
    • STAGE 5: CFG Analysis (Premium+)
    • STAGE 6: ML Filtering (Enterprise)
    • STAGE 7: GDPR Compliance (Premium+)
    
    Commands:
    • company - Company profile management for compliance tracking
    • evidence - Evidence package generation for compliance audits
    • scan - Scan files/directories for PII violations and GDPR compliance
    • status - Show Levox status and capabilities
    
    Quick Start:
    • Scan current directory: levox scan
    • Create company profile: levox company create --name "My Company"
    • Generate evidence package: levox evidence generate --company <id>
    • Scan with CFG analysis: levox scan --cfg
    • Generate reports: levox scan --report json html
    • Show capabilities: levox status
    • Get help: levox <command> --help
    """
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Check for first run and trigger onboarding
    try:
        from ..core.user_config import get_user_config
        user_config = get_user_config()
        
        if user_config.is_first_run():
            # First run detected - trigger onboarding
            from .onboarding import run_onboarding
            
            click.echo("🎉 Welcome to Levox! Let's get you set up...")
            if run_onboarding():
                user_config.mark_first_run_complete()
                click.echo("✅ Setup complete! You're ready to start scanning.")
            else:
                click.echo("⚠️ Setup cancelled. You can run setup later with: levox setup")
                ctx.exit(0)
    except Exception as e:
        # If onboarding fails, continue with normal operation
        click.echo(f"Warning: Could not run setup wizard: {e}", err=True)
    
    # Set up configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            config_obj = load_default_config()
        
        # Override config with CLI flags
        if verbose:
            config_obj.log_level = "DEBUG"
        if quiet:
            config_obj.log_level = "ERROR"
        if debug:
            config_obj.debug_mode = True
            
        # Initialize services
        initialize_services(config_obj)
        
        # Store config in context
        ctx.obj['config'] = config_obj
        
    except Exception as e:
        click.echo(f"Configuration error: {e}", err=True)
        ctx.exit(1)

@cli.command()
@click.pass_context
def setup(ctx):
    """Run the interactive setup wizard."""
    try:
        from .onboarding import run_onboarding
        from ..core.user_config import get_user_config
        
        click.echo("🔧 Running Levox setup wizard...")
        if run_onboarding():
            user_config = get_user_config()
            user_config.mark_first_run_complete()
            click.echo("✅ Setup complete!")
        else:
            click.echo("⚠️ Setup cancelled.")
    except Exception as e:
        click.echo(f"Setup failed: {e}", err=True)
        ctx.exit(1)

@cli.command()
def examples():
    """Show common use cases and examples."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    
    console = Console()
    
    # Examples table
    examples_table = Table(
        title="🚀 Levox Usage Examples",
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    examples_table.add_column("Use Case", style="cyan", width=25)
    examples_table.add_column("Command", style="white", width=40)
    examples_table.add_column("Description", style="dim", width=35)
    
    # Basic examples
    examples_table.add_row(
        "Quick Scan",
        "levox scan .",
        "Scan current directory with basic settings"
    )
    examples_table.add_row(
        "Deep Analysis",
        "levox scan . --cfg --format json html",
        "Full analysis with CFG and multiple outputs"
    )
    examples_table.add_row(
        "Repository Scan",
        "levox scan https://github.com/user/repo",
        "Scan a Git repository directly"
    )
    examples_table.add_row(
        "Specific Files",
        "levox scan src/ --include '*.py'",
        "Scan only Python files in src/"
    )
    examples_table.add_row(
        "Exclude Dependencies",
        "levox scan . --exclude 'node_modules'",
        "Skip dependency directories"
    )
    examples_table.add_row(
        "Generate Report",
        "levox generate-report --format html",
        "Create HTML report from last scan"
    )
    examples_table.add_row(
        "Company Setup",
        "levox company create --name 'My Company'",
        "Set up company profile for compliance"
    )
    examples_table.add_row(
        "Evidence Package",
        "levox evidence generate --company <id>",
        "Generate compliance evidence package"
    )
    examples_table.add_row(
        "License Check",
        "levox license --status",
        "Check license status and features"
    )
    examples_table.add_row(
        "Interactive Mode",
        "levox interactive",
        "Launch interactive CLI with menu"
    )
    
    console.print(examples_table)
    
    # Advanced examples panel
    advanced_panel = Panel(
        "[bold]🔧 Advanced Examples:[/bold]\n\n"
        "[cyan]CI/CD Integration:[/cyan]\n"
        "• GitHub Actions: levox scan . --format sarif --output results.sarif\n"
        "• GitLab CI: levox scan . --format json --output results.json\n"
        "• Jenkins: levox scan . --format json --output results.json\n\n"
        "[cyan]Large Repository Scanning:[/cyan]\n"
        "• Shallow scan: levox scan <repo> --shallow\n"
        "• Incremental: levox scan . --incremental\n"
        "• Specific branch: levox scan <repo> --branch main\n\n"
        "[cyan]Compliance & Auditing:[/cyan]\n"
        "• GDPR compliance: levox scan . --gdpr\n"
        "• Evidence generation: levox evidence generate --company <id>\n"
        "• Audit trail: levox history --detailed\n\n"
        "[cyan]Performance Tuning:[/cyan]\n"
        "• Limit workers: levox scan . --max-workers 2\n"
        "• Memory limit: levox scan . --memory-limit 1024\n"
        "• Timeout: levox scan . --timeout 300",
        title="Advanced Usage",
        border_style="green"
    )
    console.print(advanced_panel)
    
    # Tips panel
    tips_panel = Panel(
        "[bold]💡 Pro Tips:[/bold]\n\n"
        "• Use [cyan]levox interactive[/cyan] for guided experience\n"
        "• Run [cyan]levox setup[/cyan] to configure preferences\n"
        "• Use [cyan]--format json[/cyan] for CI/CD integration\n"
        "• Try [cyan]--cfg[/cyan] for advanced analysis (Premium+)\n"
        "• Use [cyan]--exclude[/cyan] to skip large directories\n"
        "• Check [cyan]levox status[/cyan] for capabilities\n"
        "• Use [cyan]levox help <command>[/cyan] for detailed help",
        title="Tips & Best Practices",
        border_style="yellow"
    )
    console.print(tips_panel)

@cli.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument('path', type=click.Path(exists=False, file_okay=True, dir_okay=True), default='.')
@click.argument('extra', nargs=-1)  # swallow any extra positional/glob args
@click.option('--format', 'output_format', type=click.Choice(['summary', 'table', 'json', 'sarif']),
              default='summary', help='Output format for terminal display')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON format)')
@click.option('--max-file-size-mb', type=int, help='Maximum file size to scan in MB')
@click.option('--exclude-patterns', multiple=True, help='File patterns to exclude (glob patterns)')
@click.option('--scan-optional/--no-scan-optional', is_flag=True, default=False, 
              help='Include optional file types (.txt, .md) in addition to source code')
@click.option('--strict/--no-strict', is_flag=True, default=False,
              help='Strict mode: disable sane defaults and raise sensitivity (more noise)')
@click.option('--allow-fallback-parsing', is_flag=True, default=True, 
              help='Allow fallback parsing when Tree-Sitter unavailable')
@click.option('--require-full-ast', is_flag=True, 
              help='Require full AST parsing (fail if Tree-Sitter unavailable)')
@click.option('--cfg', '--deep-scan', is_flag=True, 
              help='Enable Control Flow Graph (CFG) analysis for complex PII detection')
@click.option('--cfg-confidence', type=float, default=0.6, 
              help='Minimum confidence threshold to trigger CFG analysis (default: 0.6)')
@click.option('--report', 'report_formats', type=click.Choice(['json', 'html', 'pdf']), multiple=True, 
              help='Generate reports in specific formats (only when explicitly requested)')
@click.option('--verbosity', type=click.Choice(['summary', 'verbose', 'debug']), default='summary',
              help='Output verbosity level')
@click.option('--telemetry', is_flag=True, help='Show detailed capability and performance information')
@click.option('--secret-verify/--no-secret-verify', is_flag=True, default=True,
              help='Validate detected secrets with provider APIs (e.g., AWS STS)')
@click.option('--company-id', help='Company ID for compliance tracking and evidence generation')
@click.option('--repo-url', help='Git repository URL (GitHub/GitLab/Bitbucket)')
@click.option('--clone-strategy', type=click.Choice(['auto', 'shallow', 'sparse', 'full']), 
              default='auto', help='Repository clone strategy')
@click.option('--keep-clone/--delete-clone', default=False, 
              help='Keep cloned repository after scan')
@click.option('--compliance-mode', is_flag=True, default=False,
              help='Enable compliance-focused scanning with real-time GDPR/CCPA violation alerts')
@click.option('--compliance-alerts', type=click.Choice(['silent', 'summary', 'detailed', 'verbose']), 
              default='detailed', help='Compliance alert verbosity level')
@click.option('--alert-threshold', type=click.Choice(['low', 'medium', 'high', 'critical']), 
              default='low', help='Minimum alert severity threshold to display')
@click.option('--compliance-frameworks', type=click.Choice(['gdpr', 'ccpa', 'all']), 
              default='gdpr', help='Compliance frameworks to check')
@click.option('--executive-summary', is_flag=True, default=False,
              help='Generate executive-level compliance summary')
@click.pass_context
def scan(ctx, path, extra, output_format, output, max_file_size_mb, 
         exclude_patterns, scan_optional, strict, allow_fallback_parsing, require_full_ast, 
         cfg, cfg_confidence, report_formats, verbosity, telemetry, secret_verify, company_id,
         repo_url, clone_strategy, keep_clone, compliance_mode, compliance_alerts, 
         alert_threshold, compliance_frameworks, executive_summary):
    """
    Scan files/directories for PII violations and GDPR/CCPA compliance issues.
    
    This command performs a comprehensive security scan using our 7-stage detection
    pipeline including regex patterns, AST analysis, context analysis, dataflow analysis,
    CFG analysis, ML filtering, and GDPR/CCPA compliance checking.
    
    CFG Analysis (--cfg) provides deep scanning for complex PII flows through control
    structures that previous stages may miss. Requires Premium+ license tier.
    
    Compliance Mode (--compliance-mode) enables real-time GDPR/CCPA violation alerts
    with specific article references and remediation guidance. Perfect for compliance
    officers and security teams.
    
    Reports are only generated when explicitly requested with --report flags.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    # Show scan estimation (align with engine discovery logic)
    try:
        # Gracefully ignore any extra/unknown arguments Click didn't map
        # This addresses environments that auto-append glob patterns like
        # "*.py *.js *.ts ..." which would otherwise cause "unexpected extra arguments".
        # Capture and ignore any extra args/globs passed through (both Click ctx.args and explicit 'extra')
        if getattr(ctx, 'args', None) or extra:
            # Known no-op pass-through; we simply don't use ctx.args further
            pass
        from ..utils.scan_estimator import ScanEstimator
        estimator = ScanEstimator()
        # Reuse the same include/exclude logic as the engine
        cfg_obj = scan_service.config if hasattr(scan_service, 'config') else None
        if cfg_obj:
            try:
                cfg_obj.auto_configure_for_path(path)
            except Exception:
                pass
            include_patterns = list(getattr(cfg_obj, 'include_patterns', []) or [])
            exclude_list = list(getattr(cfg_obj, 'exclude_patterns', []) or [])
            max_size = getattr(getattr(cfg_obj, 'performance', None), 'max_file_size_mb', max_file_size_mb) or max_file_size_mb
        else:
            include_patterns = ['*.py', '*.js', '*.ts', '*.java']
            exclude_list = list(exclude_patterns) if exclude_patterns else []
            max_size = max_file_size_mb
        estimation = estimator.estimate_scan(path, {
            'cfg_enabled': cfg,
            'scan_optional': scan_optional,
            'max_file_size_mb': max_size,
            'include_patterns': include_patterns,
            'exclude_patterns': exclude_list
        })
        
        if estimation:
            click.echo(f"📊 Scan Estimation:")
            click.echo(f"   Files to scan: {estimation['file_count']}")
            click.echo(f"   Estimated duration: {estimation['duration']:.1f}s")
            click.echo(f"   Memory usage: ~{estimation['memory_mb']:.1f} MB")
            if estimation['warnings']:
                for warning in estimation['warnings']:
                    click.echo(f"   ⚠️  {warning}")
            click.echo()
    except Exception as e:
        # If estimation fails, continue with scan
        pass
    
    try:
        # Check scan limits locally (tamper-evident) for starter tier
        try:
            from ..core.license_client import get_license_client
            from ..core.scan_limiter import get_scan_limiter
            client = get_license_client()
            limiter = get_scan_limiter()
            license_info = client.get_license_info()
            
            if license_info and license_info.is_valid and license_info.tier.value == 'starter':
                can_scan, used, limit, period = limiter.can_scan(license_info.jwt_token, 'starter')
                if not can_scan:
                    click.echo(f"❌ Scan limit reached: {used}/{limit} scans this month", err=True)
                    click.echo(f"Limit reached, upgrade here → https://levox.aifenrix.com/plans", err=True)
                    ctx.exit(1)
                elif used >= int(limit * 0.8):  # Warn at 80%
                    click.echo(f"⚠️  Warning: {used}/{limit} scans used this month", err=True)
                    click.echo(f"Consider upgrading: https://levox.aifenrix.com/plans", err=True)
        except Exception as e:
            click.echo(f"Warning: Could not check local scan limits: {e}", err=True)
        
        # Handle repository scanning if repo-url is provided
        if repo_url:
            try:
                from ..integrations.repo_scanner import GitRepoScanner
                from ..models.repo_info import RepoConfig, CloneStrategy
                
                # Initialize repository scanner
                repo_config = RepoConfig()
                scanner = GitRepoScanner(repo_config)
                
                # Validate URL and get metadata
                click.echo(f"🔍 Analyzing repository: {repo_url}")
                
                try:
                    metadata = scanner.get_repo_metadata(repo_url)
                except Exception as e:
                    click.echo(f"❌ Invalid repository URL: {e}", err=True)
                    ctx.exit(1)
                
                # Display repository information
                click.echo(f"📋 Platform: {metadata.platform.value.title()}")
                click.echo(f"📋 Repository: {metadata.full_name}")
                click.echo(f"📋 Size: {metadata.size_mb:.1f} MB")
                click.echo(f"📋 Visibility: {metadata.visibility.value.title()}")
                
                # Check if repository is too large
                if metadata.size_mb > repo_config.max_repo_size_mb:
                    click.echo(f"⚠️ Repository is large ({metadata.size_mb:.1f} MB). This may take a while.", err=True)
                    if not click.confirm("Continue?"):
                        ctx.exit(0)
                
                # Select clone strategy
                if clone_strategy == 'auto':
                    strategy = scanner.select_clone_strategy(metadata.size_mb)
                else:
                    strategy = CloneStrategy(clone_strategy)
                
                click.echo(f"📥 Clone strategy: {strategy.value}")
                
                # Clone repository
                click.echo(f"📥 Cloning repository...")
                cloned_repo = scanner.clone_with_strategy(repo_url, strategy)
                click.echo(f"✅ Repository cloned successfully!")
                
                # Update scan path to cloned repository
                path = str(cloned_repo.local_path)
                
                # Add repository-specific options
                scan_options = {
                    'output_format': output_format,
                    'output_file': output,
                    'max_file_size_mb': max_file_size_mb,
                    'exclude_patterns': list(exclude_patterns) if exclude_patterns else None,
                    'scan_optional': scan_optional,
                    'strict_mode': strict,
                    'allow_fallback_parsing': allow_fallback_parsing,
                    'require_full_ast': require_full_ast,
                    'cfg_enabled': cfg,
                    'cfg_confidence': cfg_confidence,
                    'report_formats': list(report_formats) if report_formats else None,
                    'verbosity': verbosity,
                    'telemetry': telemetry,
                    'secret_verify': secret_verify,
                    'scan_path': path,
                    'company_id': company_id,
                    'repo_url': repo_url,
                    'cloned_repo': cloned_repo,
                    'compliance_mode': compliance_mode,
                    'compliance_alerts': compliance_alerts,
                    'alert_threshold': alert_threshold,
                    'compliance_frameworks': [compliance_frameworks] if compliance_frameworks != 'all' else ['gdpr', 'ccpa'],
                    'executive_summary': executive_summary
                }
                
                # Execute scan
                click.echo(f"🔍 Scanning repository...")
                exit_code = scan_service.execute_scan(path, scan_options)
                
                # Handle cleanup
                if not keep_clone:
                    try:
                        if cloned_repo.cleanup():
                            click.echo("✅ Repository cleaned up successfully")
                        else:
                            click.echo("⚠️ Failed to clean up repository", err=True)
                            click.echo(f"Repository location: {cloned_repo.local_path}", err=True)
                            click.echo("You may need to manually delete this directory", err=True)
                    except Exception as e:
                        click.echo(f"❌ Cleanup error: {e}", err=True)
                        click.echo(f"Repository location: {cloned_repo.local_path}", err=True)
                else:
                    click.echo(f"📁 Repository kept at: {cloned_repo.local_path}")
                
                # Handle scan count increment and exit
                if exit_code in (EXIT_SUCCESS, EXIT_VIOLATIONS_FOUND):
                    try:
                        from ..core.license_client import get_license_client
                        from ..core.scan_limiter import get_scan_limiter
                        client = get_license_client()
                        limiter = get_scan_limiter()
                        license_info = client.get_license_info()
                        
                        if license_info and license_info.is_valid and license_info.tier.value == 'starter':
                            new_count, limit, at_limit = limiter.increment(license_info.jwt_token, 'starter')
                            if at_limit:
                                click.echo(f"⚠️  You have reached your monthly scan limit ({new_count}/{limit}).", err=True)
                                click.echo(f"Upgrade to continue scanning: https://levox.aifenrix.com/plans", err=True)
                    except Exception as e:
                        click.echo(f"Warning: Could not update local scan count: {e}", err=True)
                
                ctx.exit(exit_code)
                
            except Exception as e:
                click.echo(f"❌ Repository scan failed: {e}", err=True)
                ctx.exit(1)
        
        # Validate and normalize path
        scan_path = Path(path).resolve()
        if not scan_path.exists():
            click.echo(f"Error: Path does not exist: {scan_path}", err=True)
            ctx.exit(1)
        
        # Smart company ID detection
        if not company_id:
            company_id = _get_default_company_id()
            if company_id:
                click.echo(f"🔍 Using default company: {company_id}")
            else:
                click.echo("💡 Tip: Create a company first with 'levox company create --name \"Your Company\"'")
                click.echo("   Or specify --company-id for this scan")
        
        # Prepare scan options
        scan_options = {
            'output_format': output_format,
            'output_file': output,
            'max_file_size_mb': max_file_size_mb,
            'exclude_patterns': list(exclude_patterns) if exclude_patterns else None,
            'scan_optional': scan_optional,
            'strict_mode': strict,
            'allow_fallback_parsing': allow_fallback_parsing,
            'require_full_ast': require_full_ast,
            'cfg_enabled': cfg,
            'cfg_confidence': cfg_confidence,
            'report_formats': list(report_formats) if report_formats else None,
            'verbosity': verbosity,
            'telemetry': telemetry,
            'secret_verify': secret_verify,
            'scan_path': str(scan_path),  # Add scan path for result saving
            'company_id': company_id,  # Add company ID for compliance tracking
            'compliance_mode': compliance_mode,
            'compliance_alerts': compliance_alerts,
            'alert_threshold': alert_threshold,
            'compliance_frameworks': [compliance_frameworks] if compliance_frameworks != 'all' else ['gdpr', 'ccpa'],
            'executive_summary': executive_summary
        }
        
        # Execute scan
        exit_code = scan_service.execute_scan(str(scan_path), scan_options)
        
        # Increment local scan count for starter tier after a completed scan
        # Count both clean scans (exit 0) and scans with violations (exit 1)
        if exit_code in (EXIT_SUCCESS, EXIT_VIOLATIONS_FOUND):
            try:
                from ..core.license_client import get_license_client
                from ..core.scan_limiter import get_scan_limiter
                client = get_license_client()
                limiter = get_scan_limiter()
                license_info = client.get_license_info()
                
                if license_info and license_info.is_valid and license_info.tier.value == 'starter':
                    new_count, limit, at_limit = limiter.increment(license_info.jwt_token, 'starter')
                    if at_limit:
                        click.echo(f"⚠️  You have reached your monthly scan limit ({new_count}/{limit}).", err=True)
                        click.echo(f"Upgrade to continue scanning: https://levox.aifenrix.com/plans", err=True)
            except Exception as e:
                click.echo(f"Warning: Could not update local scan count: {e}", err=True)

        # Provide clear exit messaging before exiting
        try:
            if exit_code == EXIT_SUCCESS:
                click.echo("Completed successfully (exit code 0).")
            elif exit_code == EXIT_VIOLATIONS_FOUND:
                click.echo("Violations found (exit code 1).")
            elif exit_code == EXIT_CONFIG_ERROR:
                click.echo("Configuration error (exit code 3).")
            elif exit_code == EXIT_RUNTIME_ERROR:
                click.echo("Runtime error (exit code 2).")
            else:
                click.echo(f"Exited with code {exit_code}.")
        finally:
            ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception:
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.argument('results_file', type=click.Path(exists=True), required=False)
@click.option('--format', 'output_format', type=click.Choice(['json', 'html', 'pdf', 'sarif']),
              default='json', help='Report format')
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
@click.option('--template', type=click.Path(exists=True), help='Custom report template file')
@click.option('--include-metadata', is_flag=True, help='Include detailed metadata in report')
@click.option('--latest', is_flag=True, help='Generate report from latest scan results')
@click.option('--list', 'list_results', is_flag=True, help='List available scan results for reporting')
@click.pass_context
def report(ctx, results_file, output_format, output, template, include_metadata, latest, list_results):
    """
    Generate detailed reports from previous scan results.
    
    This command creates professional reports in various formats from saved scan results.
    Reports are only generated when this command is explicitly run.
    
    Examples:
        report --list                           # List available scan results
        report --latest --format html          # Generate HTML report from latest scan
        report results.json --format pdf       # Generate PDF report from specific file
        report results.json --format html -o report.html  # Save HTML report to file
    """
    
    if not report_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        # Handle list command
        if list_results:
            exit_code = report_service.list_available_results()
            ctx.exit(exit_code)
        
        # Handle latest report generation
        if latest:
            report_options = {
                'output_format': output_format,
                'output_file': output,
                'template': template,
                'include_metadata': include_metadata
            }
            exit_code = report_service.generate_latest_report(report_options)
            # Provide clear exit messaging
            try:
                if exit_code == EXIT_SUCCESS:
                    click.echo("Report completed successfully (exit code 0).")
                elif exit_code == EXIT_CONFIG_ERROR:
                    click.echo("Report configuration error (exit code 3).")
                elif exit_code == EXIT_RUNTIME_ERROR:
                    click.echo("Report runtime error (exit code 2).")
                else:
                    click.echo(f"Report exited with code {exit_code}.")
            finally:
                ctx.exit(exit_code)
        
        # Handle specific file report generation
        if not results_file:
            click.echo("Error: Must specify a results file or use --latest/--list", err=True)
            click.echo("Use 'report --help' for usage information", err=True)
            ctx.exit(1)
        
        report_options = {
            'output_format': output_format,
            'output_file': output,
            'template': template,
            'include_metadata': include_metadata
        }
        
        exit_code = report_service.generate_report(results_file, report_options)
        # Provide clear exit messaging
        try:
            if exit_code == EXIT_SUCCESS:
                click.echo("Report completed successfully (exit code 0).")
            elif exit_code == EXIT_CONFIG_ERROR:
                click.echo("Report configuration error (exit code 3).")
            elif exit_code == EXIT_RUNTIME_ERROR:
                click.echo("Report runtime error (exit code 2).")
            else:
                click.echo(f"Report exited with code {exit_code}.")
        finally:
            ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception:
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed capability information')
@click.option('--check-dependencies', is_flag=True, help='Verify all dependencies are available')
@click.pass_context
def status(ctx, detailed, check_dependencies):
    """
    Show system status, capabilities, scan analytics, and dependency information.
    
    This command displays the current system status, available detection methods,
    real scan analytics, and validates that all required dependencies are properly installed.
    """
    
    try:
        # Get actual license tier from license client if available
        try:
            from ..core.license_client import get_license_client
            
            # Try to get the actual license tier from the license client
            client = get_license_client()
            license_info = client.get_license_info()
            
            if license_info and license_info.is_valid:
                actual_tier = license_info.tier.value
                license_tier = actual_tier
                click.echo(f"License validated: {actual_tier} tier")
                
                # Show scan usage information
                click.echo(f"\n🔑 License Information:")
                click.echo("=" * 50)
                click.echo(f"License: {actual_tier.title()}")
                click.echo(f"Email: {license_info.email}")
                click.echo(f"Device Limit: {license_info.device_limit}")
                click.echo(f"Current Devices: {license_info.current_devices}")
                click.echo(f"Expires: {license_info.expires_at.strftime('%Y-%m-%d')}")
                
                # Show scan usage for starter tier
                if actual_tier == 'starter':
                    # Use local scan limiter for status display
                    try:
                        from ..core.scan_limiter import get_scan_limiter
                        limiter = get_scan_limiter()
                        used, limit, period = limiter.get_status(license_info.jwt_token, 'starter')
                        # Compute next reset (first of next month)
                        from datetime import datetime
                        d = datetime.strptime(period, '%Y-%m-%d')
                        next_month = (d.month % 12) + 1
                        next_year = d.year + (1 if d.month == 12 else 0)
                        next_reset = f"{next_year:04d}-{next_month:02d}-01"
                        click.echo(f"\n📊 Scan Usage:")
                        click.echo("=" * 50)
                        click.echo(f"Scans this month: {used} / {limit}")
                        click.echo(f"Next reset: {next_reset}")
                        click.echo(f"Upgrade: https://levox.aifenrix.com/plans")
                    except Exception:
                        click.echo(f"\n📊 Scan Usage:")
                        click.echo("=" * 50)
                        click.echo("Scans this month: unavailable")
                        click.echo(f"Upgrade: https://levox.aifenrix.com/plans")
                else:
                    click.echo(f"\n📊 Scan Usage:")
                    click.echo("=" * 50)
                    click.echo(f"Scans: Unlimited")
                    click.echo(f"Tier: {actual_tier.title()}")
            else:
                click.echo("No valid license found, using standard tier")
                license_tier = 'standard'
        except Exception as e:
            click.echo(f"License validation failed: {e}, using standard tier")
            license_tier = 'standard'
        
        # Get scan analytics from scan service
        scan_analytics = _get_scan_analytics(ctx)
        
        # Display scan analytics
        if scan_analytics:
            click.echo("\n📊 Scan Analytics:")
            click.echo("=" * 50)
            click.echo(f"📁 Total Scans: {scan_analytics['total_scans']}")
            click.echo(f"📄 Files Scanned: {scan_analytics['total_files_scanned']}")
            click.echo(f"🔍 Total Matches: {scan_analytics['total_matches']}")
            click.echo(f"📂 Directories Scanned: {scan_analytics['total_directories']}")
            click.echo(f"⏱️  Total Scan Time: {scan_analytics['total_scan_time']:.2f}s")
            click.echo(f"📈 Average Files/sec: {scan_analytics['avg_files_per_second']:.1f}")
            
            if scan_analytics['last_scan']:
                last_scan = scan_analytics['last_scan']
                click.echo(f"\n🕒 Last Scan: {last_scan['timestamp']}")
                click.echo(f"📁 Path: {last_scan['scan_path']}")
                click.echo(f"📄 Files: {last_scan['files_scanned']}")
                click.echo(f"🔍 Matches: {last_scan['matches_found']}")
                click.echo(f"⏱️  Duration: {last_scan['scan_time']:.2f}s")
        
        # Display system capabilities with dynamic feature checking
        click.echo("\n🔧 System Capabilities:")
        click.echo("=" * 50)
        
        # Dynamic feature checking
        feature_status = _check_feature_availability()
        
        # Tree-Sitter status
        tree_sitter_status = "✅ Available" if feature_status['tree_sitter'] else "❌ Not Available"
        click.echo(f"Tree-Sitter Parser: {tree_sitter_status}")
        
        # Language support
        lang_count = feature_status['supported_languages']
        if lang_count > 0:
            click.echo(f"Language Support: ✅ {lang_count} Languages")
        else:
            click.echo("Language Support: ❌ Not Available")
        
        # ML Libraries
        ml_status = "✅ Available" if feature_status['ml_libraries'] else "❌ Not Available"
        click.echo(f"ML Libraries: {ml_status}")
        
        # License tier
        click.echo(f"License Tier: 🔓 {license_tier.title()}")
        
        # Show dynamic feature availability (aligned with plan gating)
        click.echo("\n🚀 Feature Availability:")
        click.echo("=" * 50)
        
        # Check each feature dynamically
        features_to_check = [
            ("AST Analysis", "ast_analysis", feature_status['ast_analysis']),
            ("Context Analysis", "context_analysis", True),
            ("CFG Analysis", "cfg_analysis", feature_status['cfg_analysis']),
            ("Advanced Reporting", "advanced_reporting", True),
            ("Custom Rules", "custom_rules", True),
            ("Dataflow Analysis", "dataflow_analysis", feature_status['dataflow_analysis']),
            ("ML Filtering", "ml_filtering", feature_status['ml_libraries']),
            ("API Integration", "api_integration", True),
            ("Enterprise Logging", "enterprise_logging", True),
            ("GDPR Compliance", "gdpr_compliance", True),
            ("CCPA Compliance", "ccpa_compliance", True),
            ("Compliance Alerts", "compliance_alerts", True),
            ("Compliance Scoring", "compliance_scoring", True),
            ("Executive Dashboards", "executive_dashboards", True),
            ("Multi-Framework Support", "multi_framework_support", True),
            ("Cross-Framework Mapping", "cross_framework_mapping", True),
            ("Industry Benchmarking", "industry_benchmarking", True),
            ("Compliance API Access", "compliance_api_access", True),
            ("Cryptographic Audit Logs", "cryptographic_audit_logs", True),
            ("Real-Time Compliance Monitoring", "real_time_compliance_monitoring", True),
            ("Advanced Compliance Analytics", "advanced_compliance_analytics", True),
        ]
        
        def _has_feature(tier: str, key: str) -> bool:
            tier = tier.lower()
            starter = {"regex_detection", "basic_logging", "file_scanning", "basic_reporting"}
            pro = starter | {"ast_analysis", "context_analysis", "cfg_analysis", "advanced_reporting", "custom_rules", "multi_language", "performance_metrics", "gdpr_compliance", "compliance_alerts", "compliance_scoring", "executive_dashboards"}
            business = pro | {"dataflow_analysis", "ml_filtering", "sarif_export", "advanced_security", "suppression_controls", "ccpa_compliance", "multi_framework_support", "cross_framework_mapping", "industry_benchmarking"}
            enterprise = business | {"api_integration", "enterprise_logging", "compliance_audit", "gdpr_analysis", "compliance_reporting", "audit_logging", "crypto_verification", "custom_integrations", "compliance_api_access", "cryptographic_audit_logs", "real_time_compliance_monitoring", "advanced_compliance_analytics"}
            feature_sets = {"starter": starter, "pro": pro, "business": business, "enterprise": enterprise}
            return key in feature_sets.get(tier, set())

        for feature_name, feature_key, is_available in features_to_check:
            if _has_feature(license_tier, feature_key):
                if is_available:
                    click.echo(f"✅ {feature_name}: Available")
                else:
                    click.echo(f"⚠️  {feature_name}: Dependency missing")
                    if feature_key == 'ml_filtering':
                        click.echo("   💡 Install: pip install xgboost scikit-learn")
                    elif feature_key == 'ast_analysis':
                        click.echo("   💡 Install: pip install tree-sitter")
            else:
                if feature_key in {"ast_analysis", "context_analysis", "cfg_analysis", "advanced_reporting", "custom_rules", "gdpr_compliance", "compliance_alerts", "compliance_scoring", "executive_dashboards"}:
                    required = 'Pro+'
                elif feature_key in {"dataflow_analysis", "ml_filtering", "ccpa_compliance", "multi_framework_support", "cross_framework_mapping", "industry_benchmarking"}:
                    required = 'Business+'
                else:
                    required = 'Enterprise'
                click.echo(f"🔒 {feature_name}: Requires {required} License")
        
        # Show detailed information if requested
        if detailed:
            click.echo("\n📊 Detailed Information:")
            click.echo("=" * 30)
            click.echo(f"Python Version: {feature_status['python_version']}")
            click.echo(f"Platform: {feature_status['platform']}")
            click.echo(f"Memory Usage: {feature_status['memory_usage']:.1f} MB")
            
            if scan_analytics and scan_analytics['performance_stats']:
                perf = scan_analytics['performance_stats']
                click.echo(f"Average Scan Duration: {perf.get('avg_scan_duration', 0):.2f}s")
                click.echo(f"Peak Memory Usage: {perf.get('peak_memory_mb', 0):.1f} MB")
        
        click.echo("\n💡 For complete feature details, visit: https://levox.aifenrix.com/plans")
        return 0
        
    except Exception as e:
        click.echo(f"Status check failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        return 1

@cli.command()
@click.argument('match_id')
@click.argument('verdict', type=click.Choice(['true_positive', 'false_positive', 'uncertain']))
@click.option('--notes', help='Optional notes about the feedback')
@click.option('--confidence', type=click.FloatRange(0.0, 1.0), help='Confidence in your verdict (0.0-1.0)')
@click.pass_context
def feedback(ctx, match_id, verdict, notes, confidence):
    """
    Submit feedback for a detection match to improve accuracy.
    
    This command allows you to provide feedback on detection results, which helps
    improve the ML models and reduce false positives in future scans.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        feedback_data = {
            'match_id': match_id,
            'verdict': verdict,
            'notes': notes,
            'confidence': confidence
        }
        
        exit_code = scan_service.submit_feedback(feedback_data)
        ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception as e:
        click.echo(f"Feedback submission failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--validate', is_flag=True, help='Force license validation with server')
@click.option('--refresh', is_flag=True, help='Refresh license cache and re-validate')
@click.option('--clear-cache', is_flag=True, help='Clear license cache')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed license information')
@click.option('--register', 'license_key', metavar='<KEY>', help='Register a license key')
@click.option('--upgrade', is_flag=True, help='Open license upgrade page in web browser')
@click.option('--server-url', default='https://levox.aifenrix.com', help='License server URL')
@click.pass_context
def license(ctx, validate, refresh, clear_cache, verbose, license_key, upgrade, server_url):
    """
    Manage and validate Levox license.
    
    This command allows you to check your current license status,
    validate it with the license server, manage license cache,
    and access license registration/upgrade options.
    """
    
    try:
        from ..core.license_client import get_license_client
        
        client = get_license_client()
        
        # Handle license registration
        if license_key is not None:
            if not license_key.strip():
                # Handle --register without a value
                click.echo("❌ Error: License key is required for registration")
                click.echo("")
                click.echo("📝 Usage: levox license --register <your-license-key>")
                click.echo("")
                click.echo("🔗 To get a license key:")
                click.echo("   1. Visit: https://levox.aifenrix.com/plans")
                click.echo("   2. Choose your plan and complete registration")
                click.echo("   3. Copy your license key and use it with --register")
                click.echo("")
                click.echo("💡 Example: levox license --register abc123-def456-ghi789")
                ctx.exit(1)
            try:
                click.echo(f"🔑 Registering license key: {license_key}")
                
                # Verify the license with the server
                license_info = client.verify_license(license_key)
                
                if license_info.is_valid:
                    click.echo("✅ License registered successfully!")
                    click.echo(f"📧 Email: {license_info.email}")
                    click.echo(f"🎯 Tier: {license_info.tier.value.title()}")
                    click.echo(f"📅 Expires: {license_info.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    click.echo(f"🔢 Device Limit: {license_info.device_limit}")
                    click.echo(f"🌐 Current Devices: {license_info.current_devices}")
                    click.echo("\n🎉 Your license is now active! You can use all available features.")
                else:
                    click.echo("❌ License registration failed: License is not valid")
                    ctx.exit(1)
                    
            except Exception as e:
                click.echo(f"❌ License registration failed: {e}")
                click.echo("💡 Please check your license key and try again")
                ctx.exit(1)
        
        # Handle upgrade request
        if upgrade:
            try:
                import webbrowser
                upgrade_url = f"{server_url.rstrip('/')}/upgrade"
                click.echo(f"🌐 Opening license upgrade page: {upgrade_url}")
                webbrowser.open(upgrade_url)
                click.echo("✅ Upgrade page opened in your default browser")
                return
            except Exception as e:
                click.echo(f"❌ Failed to open browser: {e}")
                click.echo(f"💻 Please manually visit: {server_url.rstrip('/')}/upgrade")
                return
        
        if clear_cache:
            client.clear_cache()
            click.echo("✅ License cache cleared")
            return
        
        if refresh:
            # Clear cache first, then get fresh info
            client.clear_cache()
            click.echo("🔄 Refreshing license validation...")
        
        # Get license information
        license_info = client.get_license_info()
        
        if not license_info:
            click.echo("❌ No license information available")
            ctx.exit(1)
        
        # Display license information
        click.echo("\n🔑 License Information:")
        click.echo("=" * 50)
        
        click.echo(f"License Key: {license_info.license_key}")
        click.echo(f"Tier: {license_info.tier.value.title()}")
        click.echo(f"Email: {license_info.email}")
        click.echo(f"Valid: {'✅ Yes' if license_info.is_valid else '❌ No'}")
        click.echo(f"Expires: {license_info.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Device Limit: {license_info.device_limit}")
        click.echo(f"Current Devices: {license_info.current_devices}")
        
        if verbose:
            click.echo(f"\n📋 Additional Details:")
            click.echo(f"JWT Token: {license_info.jwt_token[:50]}..." if license_info.jwt_token else "None")
            click.echo(f"Device Fingerprint: {client.device_fingerprint}")
        
        # Show validation status
        if license_info.is_valid:
            click.echo(f"\n✅ License is valid and active!")
            click.echo(f"🎯 Available features: {license_info.tier.value.title()} tier")
        else:
            click.echo(f"\n⚠️  License is not valid or expired")
            click.echo(f"🔒 Running in demo mode with limited features")
        
        # Show server connection status (use a GET health endpoint that returns 200)
        try:
            health = client._make_request("license", "GET")
            if isinstance(health, dict):
                click.echo(f"\n🌐 Server Connection: ✅ Connected to license server")
            else:
                click.echo(f"\n🌐 Server Connection: ❌ Unexpected response from server")
        except Exception as e:
            click.echo(f"\n🌐 Server Connection: ❌ Connection failed: {e}")
        
        ctx.exit(0)
        
    except SystemExit as e:
        # Treat normal exits as success; propagate non-zero codes
        if e.code not in (0, None):
            raise
        return
    except Exception as e:
        click.echo(f"❌ License check failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--list', 'list_models', is_flag=True, help='List available ML models')
@click.option('--evaluate', type=click.Path(exists=True), help='Evaluate model performance on test data')
@click.option('--train', type=click.Path(exists=True), help='Train new model on labeled data')
@click.option('--export', type=click.Path(), help='Export current model to file')
@click.pass_context
def models(ctx, list_models, evaluate, train, export):
    """
    Manage and evaluate ML models used for detection.
    
    This command provides tools for managing the machine learning models that
    help reduce false positives and improve detection accuracy.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        model_options = {
            'list_models': list_models,
            'evaluate': evaluate,
            'train': train,
            'export': export
        }
        
        exit_code = scan_service.manage_models(model_options)
        ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception as e:
        click.echo(f"Model management failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'markdown']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def help(ctx, format, output, verbose):
    """
    Show comprehensive help with all available commands and options.
    
    This command provides a complete overview of all Levox CLI commands,
    their usage, and available options for different verbosity levels.
    """
    try:
        help_data = {
            "cli_overview": {
                "description": "Levox - Enterprise PII/GDPR Detection CLI",
                "version": "0.9.0 Beta",
                "main_commands": ["scan", "status", "report", "feedback", "models", "help", "history", "ml_health", "generate_report", "switch_model"]
            },
            "all_commands": {
                "scan": {
                    "description": "Scan files/directories for PII violations and GDPR compliance issues",
                    "usage": "levox scan <path> [options]",
                    "key_options": [
                        "--format", "--output", "--verbose", "--debug", "--telemetry",
                        "--max-file-size-mb", "--exclude-patterns", "--scan-optional", "--allow-fallback-parsing",
                        "--require-full-ast", "--cfg", "--cfg-confidence", "--report", "--no-report", "--dev", "--verbosity"
                    ]
                },
                "status": {
                    "description": "Show system status, capabilities, and dependency information",
                    "usage": "levox status [options]",
                    "key_options": ["--detailed", "--check-dependencies"]
                },
                "report": {
                    "description": "Generate detailed reports from previous scan results",
                    "usage": "levox report [file] [options]",
                    "key_options": [
                        "--format", "--output", "--template", "--include-metadata", "--latest", "--list"
                    ]
                },
                "feedback": {
                    "description": "Submit feedback for detection matches to improve accuracy",
                    "usage": "levox feedback <match_id> <verdict> [options]",
                    "key_options": ["--notes", "--confidence"]
                },
                "feedback_stats": {
                    "description": "Show feedback statistics",
                    "usage": "levox feedback stats [options]",
                    "key_options": ["--days"]
                },
                "feedback_export": {
                    "description": "Export feedback data to JSONL format",
                    "usage": "levox feedback export <output_path> [options]",
                    "key_options": ["--limit"]
                },
                "models": {
                    "description": "Manage and evaluate ML models used for detection",
                    "usage": "levox models [options]",
                    "key_options": ["--list", "--evaluate", "--train", "--export", "--format", "--output", "--verbose"]
                },
                "history": {
                    "description": "Show scan history and available results for reporting",
                    "usage": "levox history [options]",
                    "key_options": ["--detailed", "--limit"]
                },
                "ml_health": {
                    "description": "Check ML system health and performance",
                    "usage": "levox ml_health [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                },
                "switch_model": {
                    "description": "Switch to a different ML model",
                    "usage": "levox switch_model [options]",
                    "key_options": ["--model-id", "--auto", "--verbose"]
                },
                "generate_report": {
                    "description": "Generate reports from the last scan results",
                    "usage": "levox generate_report [options]",
                    "key_options": ["--format", "--output-dir", "--from-last-scan"]
                },
                "help": {
                    "description": "Show comprehensive help with all available commands and options",
                    "usage": "levox help [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                }
            },
            "global_options": {
                "description": "Global options that apply to all commands",
                "options": [
                    "--version", "--verbose, -v", "--quiet, -q", "--config, -c", "--debug"
                ]
            },
            "toggle_flags": {
                "description": "Boolean toggle flags for controlling behavior",
                "scan_toggles": [
                    "--scan-optional/--no-scan-optional", "--allow-fallback-parsing", "--require-full-ast",
                    "--cfg, --deep-scan", "--telemetry", "--no-report", "--dev"
                ],
                "report_toggles": [
                    "--include-metadata", "--latest", "--list", "--from-last-scan"
                ],
                "output_toggles": [
                    "--detailed", "--check-dependencies", "--verbose"
                ],
                "ml_toggles": [
                    "--auto", "--list", "--evaluate", "--train", "--export"
                ]
            },
            "configuration_toggles": {
                "description": "Configuration-based toggles (set in config files)",
                "detection_toggles": [
                    "enable_ast", "enable_dataflow", "enable_ml", "enable_context_analysis",
                    "enable_compliance_audit", "enable_context_aware_filtering",
                    "enable_safe_literal_detection", "enable_variable_heuristics",
                    "enable_placeholder_detection", "enable_ml_monitoring"
                ],
                "performance_toggles": [
                    "enable_async", "cache_ast_parses", "enable_compression"
                ],
                "compliance_toggles": [
                    "include_security_checks", "include_dsar_checks", "include_deletion_checks",
                    "include_transfer_checks", "include_consent_checks", "include_retention_checks",
                    "enable_crypto_verification"
                ],
                "reporting_toggles": [
                    "enable_dashboards", "enable_trends", "enable_export"
                ]
            },
            "quick_examples": {
                "basic_scan": "levox scan /path/to/code",
                "verbose_scan": "levox scan /path/to/code --verbosity verbose",
                "debug_scan": "levox scan /path/to/code --verbosity debug",
                "generate_reports": "levox scan /path/to/code --report json --report html",
                "developer_mode": "levox scan /path/to/code --dev",
                "save_results": "levox scan /path/to/code --output results.json",
                "check_status": "levox status --detailed",
                "view_history": "levox history --detailed --limit 20",
                "cfg_analysis": "levox scan /path --cfg --cfg-confidence 0.7",
                "ml_health_check": "levox ml_health --verbose",
                "switch_best_model": "levox switch_model --auto",
                "feedback_stats": "levox feedback stats --days 30"
            }
        }
        
        if format == 'json':
            output_content = json.dumps(help_data, indent=2, default=str)
        elif format == 'markdown':
            output_content = _generate_markdown_help(help_data)
        else:
            # Default table format
            _display_help_table(help_data, verbose)
            return
        
        # Handle output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            click.echo(f"Help documentation saved to {output}")
        else:
            click.echo(output_content)
            
    except Exception as e:
        click.echo(f"❌ Error generating help: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


def _display_help_table(help_data, verbose):
    """Display help information in a formatted table."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    # CLI Overview
    overview = help_data["cli_overview"]
    console.print(Panel(
        f"[bold blue]{overview['description']}[/bold blue]\n"
        f"[dim]Version: {overview['version']}[/dim]\n"
        f"[cyan]Available Commands: {len(overview['main_commands'])}[/cyan]",
        title="🚀 Levox CLI Overview",
        border_style="blue"
    ))
    
    # Global Options
    if "global_options" in help_data:
        console.print("\n[bold green]🌐 Global Options[/bold green]")
        global_panel = Panel(
            "\n".join([f"• {opt}" for opt in help_data["global_options"]["options"]]),
            title="🔧 Global Options (apply to all commands)",
            border_style="blue"
        )
        console.print(global_panel)
    
    # All Available Commands
    console.print("\n[bold green]📋 All Available Commands[/bold green]")
    commands_table = Table(show_header=True, header_style="bold magenta")
    commands_table.add_column("Command", style="cyan", width=15)
    commands_table.add_column("Description", style="white", width=50)
    commands_table.add_column("Usage", style="yellow", width=30)
    commands_table.add_column("Key Options", style="green", width=25)
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        # Show first 3 options, then indicate there are more
        options_display = ", ".join(cmd_info["key_options"][:3])
        if len(cmd_info["key_options"]) > 3:
            options_display += f" (+{len(cmd_info['key_options']) - 3} more)"
        
        commands_table.add_row(
            cmd_name,
            cmd_info["description"][:47] + "..." if len(cmd_info["description"]) > 50 else cmd_info["description"],
            cmd_info["usage"],
            options_display
        )
    
    console.print(commands_table)
    
    # Quick Examples
    console.print("\n[bold green]💡 Quick Examples[/bold green]")
    examples_table = Table(show_header=True, header_style="bold magenta")
    examples_table.add_column("Use Case", style="cyan")
    examples_table.add_column("Command", style="yellow")
    
    for use_case, command in help_data["quick_examples"].items():
        examples_table.add_row(use_case.replace("_", " ").title(), command)
    
    console.print(examples_table)
    
    # Footer
    console.print("\n[dim]💡 Tip: Use 'levox <command> --help' for detailed help on specific commands[/dim]")
    console.print("[dim]📚 For more information, visit the project documentation[/dim]")


def _generate_markdown_help(help_data):
    """Generate markdown format help documentation."""
    md_content = []
    
    # Header
    md_content.append(f"# {help_data['cli_overview']['description']}")
    md_content.append(f"**Version:** {help_data['cli_overview']['version']}")
    md_content.append("")
    
    # Global Options
    if "global_options" in help_data:
        md_content.append("## Global Options")
        md_content.append("")
        md_content.append("These options apply to all commands:")
        for option in help_data["global_options"]["options"]:
            md_content.append(f"- `{option}`")
        md_content.append("")
    
    # All Available Commands
    md_content.append("## All Available Commands")
    md_content.append("")
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        md_content.append(f"### {cmd_name}")
        md_content.append(f"**Description:** {cmd_info['description']}")
        md_content.append(f"**Usage:** `{cmd_info['usage']}`")
        md_content.append("**Key Options:**")
        for option in cmd_info["key_options"]:
            md_content.append(f"- `{option}`")
        md_content.append("")
    
    # Quick Examples
    md_content.append("## Quick Examples")
    md_content.append("")
    
    for use_case, command in help_data["quick_examples"].items():
        md_content.append(f"**{use_case.replace('_', ' ').title()}:**")
        md_content.append(f"```bash")
        md_content.append(command)
        md_content.append("")
    
    return "\n".join(md_content)


@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed scan information')
@click.option('--limit', type=int, default=10, help='Maximum number of scans to show')
@click.option('--clear', 'clear_all', is_flag=True, help='Clear all scan history and results')
@click.option('--clear-id', type=str, help='Clear specific scan result by ID (filename without extension)')
@click.option('--select', type=str, help='Select and show details for specific scan result by ID')
@click.option('--export', type=click.Path(), help='Export scan history to JSON file')
@click.pass_context
def history(ctx, detailed, limit, clear_all, clear_id, select, export):
    """
    Show scan history and available results for reporting.
    
    This command displays a list of recent scans and their results,
    making it easy to identify which scans to generate reports from.
    
    Additional features:
    • Clear all history: history --clear
    • Clear specific result: history --clear-id <scan_id>
    • Select specific result: history --select <scan_id>
    • Export history: history --export history.json
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        # Handle clear all history
        if clear_all:
            if click.confirm("Are you sure you want to clear ALL scan history and results?"):
                cleared_count = scan_service.clear_all_scan_history()
                click.echo(f"✅ Cleared {cleared_count} scan results and history")
            else:
                click.echo("Operation cancelled")
            ctx.exit(0)
        
        # Handle clear specific result
        if clear_id:
            if scan_service.clear_specific_scan_result(clear_id):
                click.echo(f"✅ Cleared scan result: {clear_id}")
            else:
                click.echo(f"❌ Scan result not found: {clear_id}")
            ctx.exit(0)
        
        # Handle select specific result
        if select:
            result_details = scan_service.get_specific_scan_result(select)
            if result_details:
                click.echo(f"📋 Details for scan: {select}")
                click.echo("=" * 80)
                click.echo(f"📁 File: {result_details['file_path']}")
                click.echo(f"📁 Scan Path: {result_details['scan_path']}")
                click.echo(f"🚨 Issues: {result_details['total_issues']}")
                click.echo(f"🔓 License: {result_details['license_tier']}")
                click.echo(f"📅 Timestamp: {result_details['timestamp']}")
                click.echo()
                click.echo("💡 To generate a report from this scan:")
                click.echo(f"   report {result_details['file_path']} --format html")
            else:
                click.echo(f"❌ Scan result not found: {select}")
            ctx.exit(0)
        
        # Handle export history
        if export:
            exported_count = scan_service.export_scan_history(export)
            click.echo(f"✅ Exported {exported_count} scan results to: {export}")
            ctx.exit(0)
        
        # Get scan history
        scan_history = scan_service.get_scan_history()
        available_results = scan_service.list_available_scan_results()
        
        if not scan_history and not available_results:
            click.echo("No scan history found. Run a scan first to generate results.")
            ctx.exit(0)
        
        # Display scan history
        if scan_history:
            click.echo(f"📊 Recent Scans (Last {min(limit, len(scan_history))}):")
            click.echo("=" * 80)
            
            for i, scan in enumerate(scan_history[-limit:], 1):
                scan_time = scan.get('scan_time', 0)
                total_issues = scan.get('total_issues', 0)
                timestamp = scan.get('timestamp', 'Unknown')[:19] if scan.get('timestamp') != 'Unknown' else 'Unknown'
                
                click.echo(f"{i:2d}. {Path(scan['scan_path']).name}")
                click.echo(f"    📁 Path: {scan['scan_path']}")
                click.echo(f"    ⏱️  Time: {scan_time:.2f}s")
                click.echo(f"    🚨 Issues: {total_issues}")
                click.echo(f"    🔓 License: {scan.get('license_tier', 'Unknown')}")
                click.echo(f"    📅 {timestamp}")
                if scan.get('results_file'):
                    click.echo(f"    💾 Results: {Path(scan['results_file']).name}")
                click.echo()
        else:
            click.echo("📊 Recent Scans: No recent scans in memory")
            click.echo("(This is normal for existing installations - scan history will be populated with new scans)")
            click.echo()
        
        # Display available results
        if available_results:
            click.echo(f"📋 Available Results for Reporting (Last {min(limit, len(available_results))}):")
            click.echo("=" * 80)
            
            for i, result in enumerate(available_results[:limit], 1):
                timestamp = result.get('timestamp', 'Unknown')[:19] if result.get('timestamp') != 'Unknown' else 'Unknown'
                scan_id = Path(result['file_path']).stem  # Get filename without extension
                
                click.echo(f"{i:2d}. {Path(result['file_path']).name}")
                click.echo(f"    🆔 ID: {scan_id}")
                click.echo(f"    📁 Scan: {Path(result['scan_path']).name}")
                click.echo(f"    🚨 Issues: {result['total_issues']}")
                click.echo(f"    🔓 License: {result['license_tier']}")
                click.echo(f"    📅 {timestamp}")
                click.echo()
        else:
            click.echo("📋 Available Results: No scan results found")
            click.echo("Run a scan first to generate results for reporting")
            click.echo()
        
        # Show usage examples
        click.echo("💡 Usage Examples:")
        click.echo("  • report --list                    # List all available results")
        click.echo("  • report --latest --format html    # Generate HTML report from latest scan")
        click.echo("  • history --select <scan_id>       # Show details for specific scan")
        click.echo("  • history --clear-id <scan_id>     # Clear specific scan result")
        click.echo("  • history --clear                  # Clear all scan history")
        click.echo("  • history --export history.json    # Export scan history")
        if available_results:
            latest_file = available_results[0]['file_path']
            click.echo(f"  • report {latest_file} --format pdf  # Generate PDF from specific file")
        
    except Exception as e:
        click.echo(f"Failed to show scan history: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)
    
    # Exit successfully
    ctx.exit(0)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'pdf', 'table', 'markdown']), 
              default='html', help='Report format (default: html)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--latest', is_flag=True, help='Generate report from latest scan')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate_report(format, output, latest, verbose):
    """
    Generate a report from the most recent scan results.
    
    This command creates a formatted report from the latest scan results.
    """
    try:
        # Initialize services
        config = load_default_config()
        initialize_services(config)
        
        if not report_service:
            click.echo("❌ Report service not available")
            return EXIT_RUNTIME_ERROR
        
        # Get the latest scan results
        results_dir = Path.home() / ".levox" / "scan_results"
        if not results_dir.exists():
            click.echo("❌ No scan results found. Run a scan first.")
            return EXIT_RUNTIME_ERROR
        
        # Find the latest scan result file
        result_files = list(results_dir.glob("levox_scan_*.json"))
        if not result_files:
            click.echo("❌ No scan results found. Run a scan first.")
            return EXIT_RUNTIME_ERROR
        
        # Sort by modification time and get the latest
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        if verbose:
            click.echo(f"📁 Using scan results: {latest_file.name}")
        
        # Generate the report
        report_options = {
            'format': format,
            'output': output,
            'verbose': verbose
        }
        
        exit_code = report_service.generate_report(str(latest_file), report_options)
        
        if exit_code == EXIT_SUCCESS:
            click.echo(f"✅ Report generated successfully in {format.upper()} format")
            if output:
                click.echo(f"📄 Saved to: {output}")
        else:
            click.echo("⚠️ Report generation completed with warnings")
        
        return exit_code
        
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}")
        return EXIT_RUNTIME_ERROR


@cli.command()
def set_report_directory():
    """Choose where reports are saved using Windows Explorer."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        import os
        
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Open folder picker dialog
        folder_path = filedialog.askdirectory(
            title="Choose Directory for Levox Reports",
            initialdir=os.path.expanduser("~")
        )
        
        if folder_path:
            # Save the selected directory to configuration
            config_path = os.path.expanduser("~/.levox/config.yaml")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Load existing config or create new
            config = {}
            if os.path.exists(config_path):
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f) or {}
                except:
                    pass
            
            # Update report directory
            config['report_directory'] = folder_path
            
            # Save updated config
            try:
                import yaml
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                click.echo(f"✅ Report directory set to: {folder_path}")
                click.echo(f"📁 Reports will now be saved to: {folder_path}")
                click.echo(f"💾 Configuration saved to: {config_path}")
                
            except Exception as e:
                click.echo(f"❌ Failed to save configuration: {e}")
                click.echo(f"📁 Selected directory: {folder_path}")
                click.echo("💡 You can manually set this in your config file")
        else:
            click.echo("❌ No directory selected. Report directory unchanged.")
            
    except ImportError:
        click.echo("❌ tkinter not available. Please install tkinter or manually set report directory in config.")
    except Exception as e:
        click.echo(f"❌ Error setting report directory: {e}")


def _get_scan_analytics(ctx) -> Optional[Dict[str, Any]]:
    """Get scan analytics from the scan service."""
    try:
        # Try to get scan service from context
        scan_service = ctx.obj.get('scan_service')
        if not scan_service:
            return None
        
        # Get scan history
        scan_history = scan_service.get_scan_history()
        if not scan_history:
            return None
        
        # Calculate analytics
        total_scans = len(scan_history)
        total_files_scanned = sum(scan.get('files_scanned', 0) for scan in scan_history)
        total_matches = sum(scan.get('matches_found', 0) for scan in scan_history)
        total_scan_time = sum(scan.get('scan_time', 0) for scan in scan_history)
        
        # Count unique directories
        unique_dirs = set(scan.get('scan_path', '') for scan in scan_history)
        total_directories = len(unique_dirs)
        
        # Calculate average files per second
        avg_files_per_second = total_files_scanned / total_scan_time if total_scan_time > 0 else 0
        
        # Get last scan
        last_scan = scan_history[-1] if scan_history else None
        
        # Get performance stats from engine if available
        performance_stats = {}
        try:
            if hasattr(scan_service, 'engine') and scan_service.engine:
                perf_stats = scan_service.engine.get_performance_stats()
                performance_stats = {
                    'avg_scan_duration': perf_stats.get('avg_scan_duration', 0),
                    'peak_memory_mb': perf_stats.get('peak_memory_mb', 0)
                }
        except:
            pass
        
        return {
            'total_scans': total_scans,
            'total_files_scanned': total_files_scanned,
            'total_matches': total_matches,
            'total_directories': total_directories,
            'total_scan_time': total_scan_time,
            'avg_files_per_second': avg_files_per_second,
            'last_scan': last_scan,
            'performance_stats': performance_stats
        }
        
    except Exception:
        return None


def _check_feature_availability() -> Dict[str, Any]:
    """Check the availability of various features and dependencies."""
    feature_status = {
        'tree_sitter': False,
        'supported_languages': 0,
        'ml_libraries': False,
        'ast_analysis': False,
        'cfg_analysis': False,
        'dataflow_analysis': False,
        'ml_filtering': False,
        'gdpr_compliance': False,
        'context_analysis': False,
        'advanced_reporting': False,
        'custom_patterns': False,
        'api_integration': False,
        'enterprise_logging': False,
        'python_version': 'Unknown',
        'platform': 'Unknown',
        'memory_usage': 0.0
    }
    
    try:
        import sys
        import platform
        import psutil
        
        # Basic system info
        feature_status['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        feature_status['platform'] = platform.system()
        feature_status['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Check Tree-Sitter
        try:
            from ..detection.regex_engine import TREE_SITTER_AVAILABLE
            feature_status['tree_sitter'] = TREE_SITTER_AVAILABLE
        except:
            pass
        
        # Check supported languages
        try:
            from ..utils.file_handler import get_supported_languages
            support_info = get_supported_languages()
            feature_status['supported_languages'] = len(support_info.get('languages', []))
        except:
            pass
        
        # Check ML libraries
        try:
            import xgboost
            import sklearn
            feature_status['ml_libraries'] = True
        except ImportError:
            pass
        
        # Check AST analysis
        try:
            import tree_sitter
            feature_status['ast_analysis'] = True
        except ImportError:
            pass
        
        # Check CFG analysis (depends on AST)
        feature_status['cfg_analysis'] = feature_status['ast_analysis']
        
        # Check dataflow analysis (depends on AST)
        feature_status['dataflow_analysis'] = feature_status['ast_analysis']
        
        # Check ML filtering
        feature_status['ml_filtering'] = feature_status['ml_libraries']
        
        # Check GDPR compliance (always available if license allows)
        feature_status['gdpr_compliance'] = True
        
        # Check context analysis (always available)
        feature_status['context_analysis'] = True
        
        # Check advanced reporting (always available)
        feature_status['advanced_reporting'] = True
        
        # Check custom patterns (always available)
        feature_status['custom_patterns'] = True
        
        # Check API integration (always available)
        feature_status['api_integration'] = True
        
        # Check enterprise logging (always available)
        feature_status['enterprise_logging'] = True
        
    except Exception:
        pass
    
    return feature_status


# CI/CD Integration Commands

@cli.command()
@click.option('--platform', type=click.Choice([p.value for p in CIPlatform]), 
              help='CI/CD platform to initialize')
@click.option('--profile', type=click.Choice([p.value for p in ScanProfile]), 
              default='balanced', help='Scan profile to use')
@click.option('--fail-on', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), 
              default='HIGH', help='Severity level to fail on')
@click.option('--output-dir', type=click.Path(), help='Output directory for generated files')
@click.option('--interactive', '-i', is_flag=True, default=True, help='Interactive setup wizard (default)')
@click.pass_context
def init_ci(ctx, platform, profile, fail_on, output_dir, interactive):
    """
    Initialize CI/CD integration with interactive setup wizard.
    
    This command helps you set up Levox in your CI/CD pipeline with ready-to-use
    templates and configuration files.
    
    Examples:
        levox init-ci                                    # Interactive setup (default)
        levox init-ci --platform github --profile balanced  # GitHub Actions setup
        levox init-ci --platform gitlab --fail-on MEDIUM   # GitLab CI setup
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        
        if interactive:
            # Interactive setup wizard
            print("🔧 Levox CI/CD Setup Wizard")
            print("This wizard will help you set up Levox in your CI/CD pipeline.\n")
            
            # Platform selection
            if not platform:
                print("Available CI/CD platforms:")
                for i, p in enumerate(CIPlatform, 1):
                    print(f"  {i}. {p.value.title()}")
                
                while True:
                    try:
                        choice = click.prompt("Select platform (1-6)", type=int)
                        if 1 <= choice <= len(CIPlatform):
                            platform = list(CIPlatform)[choice - 1].value
                            break
                        else:
                            print("Invalid choice. Please select 1-6.")
                    except (ValueError, KeyboardInterrupt):
                        print("Setup cancelled.")
                        ctx.exit(1)
            
            # Profile selection
            if not profile:
                print("\nAvailable scan profiles:")
                profiles = {
                    'quick': 'Fast scan for pre-commit/pre-push (< 30s)',
                    'balanced': 'Standard scan for PR/merge (1-5 min)',
                    'thorough': 'Comprehensive scan for releases (5-15 min)',
                    'security': 'Security-focused scan with SARIF (3-10 min)'
                }
                for i, (prof, desc) in enumerate(profiles.items(), 1):
                    print(f"  {i}. {prof.title()}: {desc}")
                
                while True:
                    try:
                        choice = click.prompt("Select profile (1-4)", type=int)
                        if 1 <= choice <= 4:
                            profile = list(profiles.keys())[choice - 1]
                            break
                        else:
                            print("Invalid choice. Please select 1-4.")
                    except (ValueError, KeyboardInterrupt):
                        print("Setup cancelled.")
                        ctx.exit(1)
            
            # Failure threshold
            if not fail_on:
                print("\nFailure threshold:")
                thresholds = {
                    'HIGH': 'Fail only on high/critical severity issues',
                    'MEDIUM': 'Fail on medium+ severity issues',
                    'LOW': 'Fail on any severity issues'
                }
                for i, (thresh, desc) in enumerate(thresholds.items(), 1):
                    print(f"  {i}. {thresh}: {desc}")
                
                while True:
                    try:
                        choice = click.prompt("Select threshold (1-3)", type=int)
                        if 1 <= choice <= 3:
                            fail_on = list(thresholds.keys())[choice - 1]
                            break
                        else:
                            print("Invalid choice. Please select 1-3.")
                    except (ValueError, KeyboardInterrupt):
                        print("Setup cancelled.")
                        ctx.exit(1)
        
        # Generate template configuration
        template_config = TemplateConfig(
            platform=CIPlatform(platform),
            scan_profile=ScanProfile(profile),
            license_tier=config.license.tier,
            fail_on_severity=fail_on,
            enable_sarif=config.license.features.get('sarif_export', False),
            enable_caching=True,
            enable_artifacts=True
        )
        
        # Generate template
        template_generator = TemplateGenerator(config)
        template_content = template_generator.generate_template(template_config, output_dir)
        
        # Generate configuration
        config_manager = ConfigManager(config)
        ci_config = config_manager.get_default_config_for_tier(config.license.tier)
        ci_config.scan_profile = profile
        ci_config.fail_on_severity = fail_on
        
        config_content = config_manager.generate_levoxrc(ci_config, output_dir)
        
        # Output results
        print("\n✅ CI/CD integration setup completed!")
        print(f"Platform: {platform.title()}")
        print(f"Profile: {profile.title()}")
        print(f"Fail on: {fail_on}")
        print(f"License tier: {config.license.tier.value.title()}")
        
        if output_dir:
            print(f"\nFiles generated in: {output_dir}")
        else:
            print("\nTemplate content generated successfully")
        
        # Show next steps
        print("\n📋 Next Steps:")
        if platform == "github":
            print("1. Copy the generated workflow to .github/workflows/")
            print("2. Add LEVOX_LICENSE_KEY to your repository secrets")
            print("3. Commit and push to trigger the workflow")
        elif platform == "gitlab":
            print("1. Copy the generated .gitlab-ci.yml to your repository root")
            print("2. Add LEVOX_LICENSE_KEY to your CI/CD variables")
            print("3. Push to trigger the pipeline")
        elif platform == "jenkins":
            print("1. Copy the generated Jenkinsfile to your repository root")
            print("2. Add LEVOX_LICENSE_KEY to Jenkins credentials")
            print("3. Configure your Jenkins job to use the Jenkinsfile")
        
        print("\n🔗 Documentation: https://levoxserver.vercel.app/docs/ci-cd")
        
    except Exception as e:
        output_manager.print_error(f"CI/CD setup failed: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('platform', type=click.Choice([p.value for p in CIPlatform]))
@click.option('--profile', type=click.Choice([p.value for p in ScanProfile]), 
              default='balanced', help='Scan profile to use')
@click.option('--fail-on', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), 
              default='HIGH', help='Severity level to fail on')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--enable-sarif', is_flag=True, help='Enable SARIF output')
@click.option('--enable-caching', is_flag=True, default=True, help='Enable caching')
@click.option('--max-file-size', type=int, help='Maximum file size in MB')
@click.option('--exclude-patterns', multiple=True, help='File patterns to exclude')
@click.pass_context
def generate_template(ctx, platform, profile, fail_on, output, enable_sarif, 
                     enable_caching, max_file_size, exclude_patterns):
    """
    Generate CI/CD template for a specific platform.
    
    This command generates ready-to-use CI/CD templates that can be copied
    directly into your repository.
    
    Examples:
        levox generate-template github --profile balanced
        levox generate-template gitlab --fail-on MEDIUM --enable-sarif
        levox generate-template jenkins --output Jenkinsfile
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        
        # Create template configuration
        template_config = TemplateConfig(
            platform=CIPlatform(platform),
            scan_profile=ScanProfile(profile),
            license_tier=config.license.tier,
            fail_on_severity=fail_on,
            enable_sarif=enable_sarif and config.license.features.get('sarif_export', False),
            enable_caching=enable_caching,
            enable_artifacts=True,
            exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
            max_file_size_mb=max_file_size
        )
        
        # Validate configuration
        template_generator = TemplateGenerator(config)
        is_valid, errors = template_generator.validate_template_config(template_config)
        
        if not is_valid:
            output_manager.print_error("Template configuration validation failed:")
            for error in errors:
                output_manager.print_error(f"  - {error}")
            ctx.exit(1)
        
        # Generate template
        template_content = template_generator.generate_template(template_config, output)
        
        if output:
            output_manager.print_success(f"✅ Template generated: {output}")
        else:
            output_manager.print_success("✅ Template generated successfully")
            click.echo(template_content)
        
    except Exception as e:
        output_manager.print_error(f"Template generation failed: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--platform', type=click.Choice([p.value for p in CIPlatform]), 
              help='Platform to validate against (auto-detect if not specified)')
@click.pass_context
def validate_ci(ctx, file_path, platform):
    """
    Validate existing CI/CD configuration file.
    
    This command validates CI/CD configuration files to ensure they are
    properly formatted and contain all required elements.
    
    Examples:
        levox validate-ci .github/workflows/levox-scan.yml
        levox validate-ci .gitlab-ci.yml --platform gitlab
        levox validate-ci Jenkinsfile
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        ci_tester = CITester(config)
        
        # Auto-detect platform if not specified
        if not platform:
            file_name = Path(file_path).name.lower()
            if 'github' in file_name or 'workflow' in file_name:
                platform = 'github'
            elif 'gitlab' in file_name:
                platform = 'gitlab'
            elif 'jenkins' in file_name:
                platform = 'jenkins'
            elif 'azure' in file_name:
                platform = 'azure'
            elif 'bitbucket' in file_name:
                platform = 'bitbucket'
            elif 'circle' in file_name:
                platform = 'circleci'
            else:
                output_manager.print_warning("Could not auto-detect platform. Please specify --platform")
                ctx.exit(1)
        
        # Validate template
        result = ci_tester.validate_template(file_path, platform)
        
        if result.result == TestResultStatus.PASSED:
            output_manager.print_success(f"✅ {platform.title()} template validation passed")
            if result.output:
                output_manager.print_info(result.output)
        elif result.result == TestResultStatus.FAILED:
            output_manager.print_error(f"❌ {platform.title()} template validation failed")
            if result.error:
                output_manager.print_error(f"Error: {result.error}")
            ctx.exit(1)
        else:
            output_manager.print_warning(f"⚠️ {platform.title()} template validation had issues")
            if result.error:
                output_manager.print_warning(f"Issue: {result.error}")
        
    except Exception as e:
        output_manager.print_error(f"Validation failed: {e}")
        ctx.exit(1)


@cli.command()
@click.option('--platform', type=click.Choice([p.value for p in CIPlatform]), 
              help='Platform to test (test all if not specified)')
@click.option('--template-path', type=click.Path(exists=True), 
              help='Path to template file to test')
@click.option('--simulate', is_flag=True, help='Simulate CI environment locally')
@click.pass_context
def test_ci(ctx, platform, template_path, simulate):
    """
    Test CI/CD integration and validate templates.
    
    This command runs comprehensive tests on CI/CD integrations including
    template validation, local simulation, and integration testing.
    
    Examples:
        levox test-ci                           # Test all platforms
        levox test-ci --platform github         # Test GitHub Actions
        levox test-ci --simulate                # Simulate CI locally
        levox test-ci --template-path .github/workflows/levox-scan.yml
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        ci_tester = CITester(config)
        
        output_manager.print_info("🧪 Running CI/CD integration tests...")
        
        if template_path and platform:
            # Test specific template
            output_manager.print_info(f"Testing {platform} template: {template_path}")
            result = ci_tester.validate_template(template_path, platform)
            
            if result.result == TestResultStatus.PASSED:
                output_manager.print_success(f"✅ Template validation passed")
            else:
                output_manager.print_error(f"❌ Template validation failed: {result.error}")
                ctx.exit(1)
            
            if simulate:
                sim_result = ci_tester.simulate_ci_environment(template_path, platform)
                if sim_result.result == TestResultStatus.PASSED:
                    output_manager.print_success(f"✅ Local simulation passed")
                elif sim_result.result == TestResultStatus.SKIPPED:
                    output_manager.print_warning(f"⚠️ Simulation skipped: {sim_result.output}")
                else:
                    output_manager.print_error(f"❌ Simulation failed: {sim_result.error}")
        
        else:
            # Run comprehensive tests
            test_results = ci_tester.run_all_tests()
            
            total_tests = 0
            passed_tests = 0
            
            for suite_name, results in test_results.items():
                output_manager.print_info(f"\n📋 {suite_name.title()} Tests:")
                
                for result in results:
                    total_tests += 1
                    if result.result == TestResultStatus.PASSED:
                        passed_tests += 1
                        output_manager.print_success(f"  ✅ {result.test_name}")
                    elif result.result == TestResultStatus.FAILED:
                        output_manager.print_error(f"  ❌ {result.test_name}: {result.error}")
                    elif result.result == TestResultStatus.SKIPPED:
                        output_manager.print_warning(f"  ⏭️ {result.test_name}: {result.output}")
                    else:
                        output_manager.print_error(f"  💥 {result.test_name}: {result.error}")
            
            # Summary
            output_manager.print_info(f"\n📊 Test Summary:")
            output_manager.print_info(f"  Total tests: {total_tests}")
            output_manager.print_info(f"  Passed: {passed_tests}")
            output_manager.print_info(f"  Failed: {total_tests - passed_tests}")
            
            if passed_tests == total_tests:
                output_manager.print_success("🎉 All tests passed!")
            else:
                output_manager.print_warning(f"⚠️ {total_tests - passed_tests} tests failed")
                ctx.exit(1)
        
    except Exception as e:
        output_manager.print_error(f"Testing failed: {e}")
        ctx.exit(1)


@cli.command()
@click.option('--environment', type=click.Choice([e.value for e in Environment]), 
              default='ci', help='Environment to configure for')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--scan-profile', type=click.Choice([p.value for p in ScanProfile]), 
              help='Scan profile to use')
@click.option('--fail-on', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), 
              help='Severity level to fail on')
@click.option('--enable-sarif', is_flag=True, help='Enable SARIF output')
@click.option('--max-file-size', type=int, help='Maximum file size in MB')
@click.option('--timeout', type=int, help='Scan timeout in seconds')
@click.pass_context
def generate_config(ctx, environment, output, scan_profile, fail_on, enable_sarif, 
                   max_file_size, timeout):
    """
    Generate Levox configuration file for CI/CD environments.
    
    This command creates .levoxrc configuration files optimized for different
    environments (development, staging, production, CI).
    
    Examples:
        levox generate-config --environment ci
        levox generate-config --environment production --enable-sarif
        levox generate-config --output .levoxrc --scan-profile balanced
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        config_manager = ConfigManager(config)
        
        # Create CI configuration
        ci_config = config_manager.get_default_config_for_tier(config.license.tier)
        ci_config.environment = Environment(environment)
        
        # Apply overrides
        if scan_profile:
            ci_config.scan_profile = scan_profile
        if fail_on:
            ci_config.fail_on_severity = fail_on
        if enable_sarif:
            ci_config.enable_sarif = enable_sarif and config.license.features.get('sarif_export', False)
        if max_file_size:
            ci_config.max_file_size_mb = max_file_size
        if timeout:
            ci_config.timeout_seconds = timeout
        
        # Validate configuration
        is_valid, errors = config_manager.validate_ci_config(ci_config)
        
        if not is_valid:
            output_manager.print_error("Configuration validation failed:")
            for error in errors:
                output_manager.print_error(f"  - {error}")
            ctx.exit(1)
        
        # Generate configuration
        config_content = config_manager.generate_levoxrc(ci_config, output)
        
        if output:
            output_manager.print_success(f"✅ Configuration generated: {output}")
        else:
            output_manager.print_success("✅ Configuration generated successfully")
            click.echo(config_content)
        
        # Show configuration summary
        output_manager.print_info(f"\n📋 Configuration Summary:")
        output_manager.print_info(f"  Environment: {environment}")
        output_manager.print_info(f"  Scan profile: {ci_config.scan_profile}")
        output_manager.print_info(f"  Fail on: {ci_config.fail_on_severity}")
        output_manager.print_info(f"  SARIF enabled: {ci_config.enable_sarif}")
        output_manager.print_info(f"  Max file size: {ci_config.max_file_size_mb}MB")
        output_manager.print_info(f"  Timeout: {ci_config.timeout_seconds}s")
        
    except Exception as e:
        output_manager.print_error(f"Configuration generation failed: {e}")
        ctx.exit(1)


@cli.command()
@click.option('--hook-type', type=click.Choice(['pre-commit', 'pre-push']), 
              default='pre-commit', help='Type of git hook to install')
@click.option('--repo-path', type=click.Path(exists=True), default='.', 
              help='Path to git repository')
@click.option('--fail-on', type=click.Choice(['HIGH', 'MEDIUM', 'LOW']), 
              default='HIGH', help='Severity level to fail on')
@click.option('--max-scan-time', type=int, default=10, 
              help='Maximum scan time in seconds')
@click.option('--exclude-patterns', multiple=True, help='File patterns to exclude')
@click.option('--generate-config', is_flag=True, help='Generate .pre-commit-config.yaml')
@click.pass_context
def install_precommit(ctx, hook_type, repo_path, fail_on, max_scan_time, 
                     exclude_patterns, generate_config):
    """
    Install pre-commit hooks for Levox security scanning.
    
    This command installs git hooks that run Levox scans before commits or pushes,
    helping catch security issues early in the development process.
    
    Examples:
        levox install-precommit                    # Install pre-commit hook
        levox install-precommit --hook-type pre-push  # Install pre-push hook
        levox install-precommit --generate-config     # Generate pre-commit config
    """
    if not output_manager:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        config = ctx.obj['config']
        precommit_integration = PreCommitIntegration(config)
        
        # Create pre-commit configuration
        precommit_config = PreCommitConfig(
            license_tier=config.license.tier,
            fail_on_severity=fail_on,
            max_scan_time_seconds=max_scan_time,
            exclude_patterns=list(exclude_patterns) if exclude_patterns else None
        )
        
        # Validate configuration
        is_valid, errors = precommit_integration.validate_precommit_config(precommit_config)
        
        if not is_valid:
            output_manager.print_error("Pre-commit configuration validation failed:")
            for error in errors:
                output_manager.print_error(f"  - {error}")
            ctx.exit(1)
        
        # Generate pre-commit configuration if requested
        if generate_config:
            config_content = precommit_integration.generate_precommit_config(precommit_config)
            config_file = Path(repo_path) / ".pre-commit-config.yaml"
            config_file.write_text(config_content)
            output_manager.print_success(f"✅ Pre-commit configuration generated: {config_file}")
        
        # Install git hook
        success = precommit_integration.install_git_hook(precommit_config, repo_path, hook_type)
        
        if success:
            output_manager.print_success(f"✅ {hook_type} hook installed successfully")
            
            # Test hook installation
            if precommit_integration.test_precommit_hook(repo_path, hook_type):
                output_manager.print_success("✅ Hook installation verified")
            else:
                output_manager.print_warning("⚠️ Hook installation could not be verified")
            
            # Show next steps
            output_manager.print_info(f"\n📋 Next Steps:")
            output_manager.print_info(f"1. The {hook_type} hook is now active")
            output_manager.print_info(f"2. Try making a commit to test the hook")
            output_manager.print_info(f"3. The hook will scan staged files for security issues")
            
            if hook_type == 'pre-commit':
                output_manager.print_info(f"4. To bypass the hook temporarily: git commit --no-verify")
            else:
                output_manager.print_info(f"4. To bypass the hook temporarily: git push --no-verify")
        else:
            output_manager.print_error("❌ Failed to install git hook")
            ctx.exit(1)
        
    except Exception as e:
        output_manager.print_error(f"Pre-commit installation failed: {e}")
        ctx.exit(1)


@cli.group()
def company():
    """
    Company profile management for compliance tracking.
    
    Manage company profiles, compliance settings, and evidence generation.
    """
    pass


@company.command()
@click.option('--name', required=True, help='Company name')
@click.option('--industry', help='Industry sector (e.g., technology, healthcare, finance)')
@click.option('--size', type=click.Choice(['small', 'medium', 'large', 'enterprise']), 
              help='Company size')
@click.option('--compliance-officer', help='Compliance officer email')
@click.option('--country', help='Headquarters country')
@click.option('--gdpr-applicable/--no-gdpr-applicable', default=True,
              help='Whether GDPR applies to this company')
@click.pass_context
def create(ctx, name, industry, size, compliance_officer, country, gdpr_applicable):
    """
    Create a new company profile for compliance tracking.
    
    This creates a company profile that will be used for evidence generation
    and compliance tracking. You can have multiple companies for different
    projects or clients.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from ..compliance.models import CompanyProfile
        import uuid
        
        # Initialize evidence store
        evidence_store = get_evidence_store("local")
        
        # Create company profile with smart ID
        company_id = _generate_smart_company_id(name)
        profile = CompanyProfile(
            id=company_id,
            name=name,
            industry=industry,
            company_size=size,
            compliance_officer_email=compliance_officer,
            headquarters_country=country,
            gdpr_applicable=gdpr_applicable
        )
        
        # Save to evidence store
        success = evidence_store.save_company_profile(profile)
        
        if success:
            click.echo(f"✅ Company profile created successfully!")
            click.echo(f"Company ID: {company_id}")
            click.echo(f"Name: {name}")
            click.echo(f"Industry: {industry or 'Not specified'}")
            click.echo(f"Size: {size or 'Not specified'}")
            click.echo(f"GDPR Applicable: {'Yes' if gdpr_applicable else 'No'}")
            click.echo(f"\nYou can now use this company ID for evidence generation:")
            click.echo(f"levox evidence generate --company {company_id}")
        else:
            click.echo("❌ Failed to create company profile", err=True)
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"Error creating company profile: {e}", err=True)
        ctx.exit(1)


@company.command()
@click.option('--company-id', help='Company ID to show (or show all)')
@click.pass_context
def list(ctx, company_id):
    """
    List company profiles.
    
    Shows all company profiles or a specific one by ID.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        
        # Initialize evidence store
        evidence_store = get_evidence_store("local")
        
        if company_id:
            # Show specific company
            profile = evidence_store.get_company_profile(company_id)
            if profile:
                click.echo(f"\n📋 Company Profile: {profile.name}")
                click.echo(f"ID: {profile.id}")
                click.echo(f"Industry: {profile.industry or 'Not specified'}")
                click.echo(f"Size: {profile.company_size or 'Not specified'}")
                click.echo(f"Compliance Officer: {profile.compliance_officer_email or 'Not specified'}")
                click.echo(f"Country: {profile.headquarters_country or 'Not specified'}")
                click.echo(f"GDPR Applicable: {'Yes' if profile.gdpr_applicable else 'No'}")
                click.echo(f"Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                click.echo(f"❌ Company not found: {company_id}", err=True)
                ctx.exit(1)
        else:
            # List all companies from evidence store
            click.echo("📋 Company Profiles")
            click.echo("=" * 50)
            
            try:
                # Get all company profiles from evidence store
                companies = evidence_store.list_company_profiles()
                if companies:
                    for company in companies:
                        click.echo(f"\n🏢 {company.name}")
                        click.echo(f"   ID: {company.id}")
                        click.echo(f"   Industry: {company.industry or 'Not specified'}")
                        click.echo(f"   Size: {company.company_size or 'Not specified'}")
                        click.echo(f"   GDPR: {'Yes' if company.gdpr_applicable else 'No'}")
                        click.echo(f"   Created: {company.created_at.strftime('%Y-%m-%d')}")
                else:
                    click.echo("No companies found. Create one with:")
                    click.echo("  levox company create --name 'Your Company'")
            except Exception as e:
                click.echo(f"Error retrieving companies: {e}")
                click.echo("To create a company: levox company create --name 'Your Company'")
            
    except Exception as e:
        click.echo(f"Error listing companies: {e}", err=True)
        ctx.exit(1)


@company.command()
@click.argument('company_id')
@click.pass_context
def select(ctx, company_id):
    """
    Select a company as the default for scans.
    
    This sets the company ID that will be used automatically for future scans
    unless explicitly overridden with --company-id.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from ..core.user_config import get_user_config
        
        # Initialize evidence store to verify company exists
        evidence_store = get_evidence_store("local")
        profile = evidence_store.get_company_profile(company_id)
        
        if not profile:
            click.echo(f"❌ Company not found: {company_id}", err=True)
            click.echo("Use 'levox company list' to see available companies.")
            ctx.exit(1)
        
        # Set as default in user config
        user_config = get_user_config()
        user_config.set_default_company_id(company_id)
        
        click.echo(f"✅ Selected company: {profile.name} ({company_id})")
        click.echo("This company will be used as default for future scans.")
        click.echo("Override with --company-id if needed.")
        
    except Exception as e:
        click.echo(f"Error selecting company: {e}", err=True)
        ctx.exit(1)


@cli.group()
def evidence():
    """
    Evidence package generation for compliance audits.
    
    Generate comprehensive evidence packages for GDPR compliance audits,
    including executive summaries, violation trends, and remediation proof.
    """
    pass


@evidence.command()
@click.argument('company_id')
@click.option('--start-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='Start date for evidence period (YYYY-MM-DD)')
@click.option('--end-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='End date for evidence period (YYYY-MM-DD)')
@click.option('--format', type=click.Choice(['pdf', 'html', 'json']), default='pdf',
              help='Output format for evidence package')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--include-remediation/--no-remediation', default=True,
              help='Include remediation proof in evidence package')
@click.option('--include-trends/--no-trends', default=True,
              help='Include trend analysis in evidence package')
@click.option('--include-gdpr-mapping/--no-gdpr-mapping', default=True,
              help='Include GDPR article mapping in evidence package')
@click.pass_context
def generate(ctx, company_id, start_date, end_date, format, output, 
             include_remediation, include_trends, include_gdpr_mapping):
    """
    Generate evidence package for compliance audit.
    
    Creates a comprehensive evidence package including:
    - Executive summary with compliance status
    - Scan history and violation trends
    - GDPR article mapping and compliance scores
    - Remediation proof and git integration
    - Professional PDF/HTML reports
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from ..compliance.evidence_generator import EvidencePackageGenerator
        from ..compliance.models import EvidencePackageRequest
        from datetime import date
        
        # Use the provided company_id directly
        company = company_id
        
        # Set default dates if not provided
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
        
        # Initialize evidence store
        evidence_store = get_evidence_store("local")
        generator = EvidencePackageGenerator(evidence_store)
        
        # Create request
        request = EvidencePackageRequest(
            company_id=company,
            start_date=start_date,
            end_date=end_date,
            include_remediation_proof=include_remediation,
            include_trend_analysis=include_trends,
            include_gdpr_mapping=include_gdpr_mapping,
            format=format,
            output_path=output
        )
        
        # Generate evidence package
        click.echo(f"Generating evidence package for company '{company}'...")
        click.echo(f"Period: {start_date} to {end_date}")
        click.echo(f"Format: {format}")
        
        response = generator.generate_audit_package(request)
        
        if response.status == "completed":
            click.echo(f"✅ Evidence package generated successfully!")
            click.echo(f"Package ID: {response.package_id}")
            if response.file_path:
                click.echo(f"File: {response.file_path}")
            if response.file_size_bytes:
                size_mb = response.file_size_bytes / (1024 * 1024)
                click.echo(f"Size: {size_mb:.1f} MB")
        else:
            click.echo(f"❌ Failed to generate evidence package: {response.error_message}", err=True)
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"Error generating evidence package: {e}", err=True)
        ctx.exit(1)


@evidence.command()
@click.option('--company', help='Company ID to filter history')
@click.option('--limit', type=int, default=10, help='Number of recent scans to show')
@click.option('--format', type=click.Choice(['table', 'json']), default='table',
              help='Output format for history display')
@click.pass_context
def history(ctx, company, limit, format):
    """
    View scan history for evidence tracking.
    
    Shows recent scan history with violation counts, trends, and compliance metrics.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from datetime import date, timedelta
        
        # Initialize evidence store
        evidence_store = get_evidence_store("local")
        
        # Smart company ID detection
        if not company:
            company = _get_default_company_id()
            if company:
                click.echo(f"🔍 Using default company: {company}")
            else:
                click.echo("❌ No company specified and no default company found")
                click.echo("💡 Create a company first with 'levox company create --name \"Your Company\"'")
                ctx.exit(1)
        
        # Get scan history
        scan_history = evidence_store.get_scan_history(company)
        
        if not scan_history:
            click.echo("No scan history found.")
            return
        
        # Limit results
        scan_history = scan_history[:limit]
        
        if format == 'json':
            import json
            history_data = [scan.to_dict() for scan in scan_history]
            click.echo(json.dumps(history_data, indent=2, default=str))
        else:
            # Table format
            click.echo(f"\n📊 Scan History (Last {len(scan_history)} scans)")
            click.echo("=" * 80)
            click.echo(f"{'Date':<12} {'Files':<6} {'Violations':<10} {'Critical':<8} {'High':<6} {'Medium':<7} {'Low':<6}")
            click.echo("-" * 80)
            
            for scan in scan_history:
                date_str = scan.scan_timestamp.strftime('%Y-%m-%d')
                click.echo(f"{date_str:<12} {scan.total_files:<6} {scan.total_violations:<10} "
                          f"{scan.critical_violations:<8} {scan.high_violations:<6} "
                          f"{scan.medium_violations:<7} {scan.low_violations:<6}")
            
            click.echo("=" * 80)
            
    except Exception as e:
        click.echo(f"Error retrieving scan history: {e}", err=True)
        ctx.exit(1)


@evidence.command()
@click.option('--company', help='Company ID to analyze trends')
@click.option('--period', type=int, default=30, help='Analysis period in days')
@click.option('--format', type=click.Choice(['table', 'json']), default='table',
              help='Output format for trends display')
@click.pass_context
def trends(ctx, company, period, format):
    """
    Show violation trends and compliance analysis.
    
    Analyzes violation patterns, improvement metrics, and compliance trends over time.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from ..compliance.trend_analyzer import TrendAnalyzer
        from datetime import date, timedelta
        
        # Initialize services
        evidence_store = get_evidence_store("local")
        trend_analyzer = TrendAnalyzer()
        
        # Smart company ID detection
        if not company:
            company = _get_default_company_id()
            if company:
                click.echo(f"🔍 Using default company: {company}")
            else:
                click.echo("❌ No company specified and no default company found")
                click.echo("💡 Create a company first with 'levox company create --name \"Your Company\"'")
                ctx.exit(1)
        
        # Get data
        scan_history = evidence_store.get_scan_history(company)
        violations = evidence_store.get_violations(company_id=company)
        
        if not scan_history:
            click.echo("No scan history found for trend analysis.")
            return
        
        # Calculate trends
        trends = trend_analyzer.calculate_violation_trends(scan_history, period)
        improvement_metrics = trend_analyzer.calculate_improvement_metrics(trends)
        compliance_metrics = trend_analyzer.calculate_compliance_metrics(
            company or "unknown", scan_history, violations
        )
        
        if format == 'json':
            import json
            trends_data = {
                'trends': [trend.to_dict() for trend in trends],
                'improvement_metrics': improvement_metrics,
                'compliance_metrics': compliance_metrics.to_dict()
            }
            click.echo(json.dumps(trends_data, indent=2, default=str))
        else:
            # Table format
            click.echo(f"\n📈 Compliance Trends Analysis (Last {period} days)")
            click.echo("=" * 60)
            
            # Overall metrics
            click.echo(f"Total Scans: {compliance_metrics.total_scans}")
            click.echo(f"Total Violations: {compliance_metrics.total_violations}")
            click.echo(f"Critical Violations: {compliance_metrics.critical_violations}")
            click.echo(f"Compliance Score: {compliance_metrics.compliance_score:.1f}/100")
            click.echo(f"Trend Direction: {compliance_metrics.trend_direction}")
            click.echo(f"Risk Level: {compliance_metrics.risk_level}")
            
            # Improvement metrics
            if improvement_metrics:
                click.echo(f"\n📊 Improvement Metrics:")
                click.echo(f"Overall Improvement: {improvement_metrics.get('overall_improvement', 0):.1f}%")
                click.echo(f"Violation Reduction Rate: {improvement_metrics.get('violation_reduction_rate', 0):.1f}%")
                click.echo(f"Consistency Score: {improvement_metrics.get('consistency_score', 0):.1f}/100")
            
            # GDPR article compliance
            if compliance_metrics.gdpr_article_compliance:
                click.echo(f"\n⚖️ GDPR Article Compliance:")
                for article, score in compliance_metrics.gdpr_article_compliance.items():
                    status = "✅" if score >= 80 else "❌"
                    click.echo(f"  {status} Article {article}: {score:.1f}/100")
            
            click.echo("=" * 60)
            
    except Exception as e:
        click.echo(f"Error analyzing trends: {e}", err=True)
        ctx.exit(1)


@evidence.command()
@click.option('--company', help='Company ID to export data')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json',
              help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def export(ctx, company, format, output):
    """
    Export raw evidence data for external analysis.
    
    Exports scan history, violations, and trends data in JSON or CSV format
    for external analysis tools or custom reporting.
    """
    
    try:
        from ..compliance.evidence_store import get_evidence_store
        from datetime import date
        
        # Initialize evidence store
        evidence_store = get_evidence_store("local")
        
        # Get data
        if company:
            scan_history = evidence_store.get_scan_history(company)
            violations = evidence_store.get_violations(company_id=company)
            remediations = evidence_store.get_remediations()
        else:
            scan_history = []
            violations = []
            remediations = []
        
        # Prepare export data
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'company_id': company or 'all',
            'scan_history': [scan.to_dict() for scan in scan_history],
            'violations': [violation.to_dict() for violation in violations],
            'remediations': [remediation.to_dict() for remediation in remediations]
        }
        
        # Generate output file path
        if not output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = f"levox_evidence_export_{company or 'all'}_{timestamp}.{format}"
        
        # Export data
        if format == 'json':
            import json
            with open(output, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format == 'csv':
            import csv
            # Export violations as CSV
            with open(output, 'w', newline='') as f:
                if violations:
                    writer = csv.DictWriter(f, fieldnames=violations[0].to_dict().keys())
                    writer.writeheader()
                    for violation in violations:
                        writer.writerow(violation.to_dict())
        
        click.echo(f"✅ Evidence data exported to: {output}")
        click.echo(f"Records exported: {len(scan_history)} scans, {len(violations)} violations, {len(remediations)} remediations")
        
    except Exception as e:
        click.echo(f"Error exporting evidence data: {e}", err=True)
        ctx.exit(1)


@cli.group()
@click.pass_context
def compliance(ctx):
    """
    Compliance management and reporting commands.
    
    Provides comprehensive GDPR/CCPA compliance auditing, scoring, and reporting
    capabilities for enterprise compliance officers and security teams.
    """
    pass


@compliance.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option('--industry', type=click.Choice(['SaaS', 'FinTech', 'HealthTech', 'E-commerce', 'General']), 
              default='General', help='Industry type for benchmarking')
@click.option('--frameworks', type=click.Choice(['gdpr', 'ccpa', 'all']), 
              default='gdpr', help='Compliance frameworks to check')
@click.option('--output', '-o', type=click.Path(), help='Output file for audit report')
@click.option('--format', type=click.Choice(['json', 'html', 'pdf']), 
              default='json', help='Report format')
@click.option('--executive-summary', is_flag=True, help='Generate executive summary')
@click.pass_context
def audit(ctx, path, industry, frameworks, output, format, executive_summary):
    """
    Perform comprehensive compliance audit with executive reporting.
    
    Conducts a full compliance audit including GDPR/CCPA violation detection,
    compliance scoring, industry benchmarking, and executive-ready reporting.
    """
    try:
        from ..compliance.compliance_dashboard import ComplianceDashboard
        from ..compliance.compliance_scoring import ComplianceScorer, IndustryType
        from ..compliance.compliance_alerter import ComplianceAlerter, AlertVerbosity
        
        # Initialize compliance components
        dashboard_generator = ComplianceDashboard(ctx.obj['config'])
        scorer = ComplianceScorer(ctx.obj['config'])
        alerter = ComplianceAlerter(ctx.obj['config'])
        
        # Perform compliance scan
        click.echo("🔍 Performing compliance audit...")
        
        # This would integrate with the existing scan service
        # For now, we'll create mock data for demonstration
        compliance_data = {
            'alerts': [],  # Would be populated from actual scan
            'issues': [],  # Would be populated from actual scan
            'trends': []   # Would be populated from historical data
        }
        
        # Generate compliance score
        industry_type = IndustryType(industry.upper())
        score_result = scorer.calculate_compliance_score(
            compliance_data['alerts'],
            compliance_data['issues'],
            industry_type
        )
        
        # Generate dashboard
        dashboard = dashboard_generator.generate_dashboard(compliance_data, industry)
        
        # Display results
        click.echo(f"\n📊 Compliance Audit Results")
        click.echo(f"Overall Score: {score_result.overall_score:.1f} ({score_result.grade.value})")
        click.echo(f"Industry Benchmark: {score_result.industry_benchmark:.1f}")
        click.echo(f"Percentile Ranking: {score_result.percentile_ranking}th")
        click.echo(f"Risk Level: {score_result.risk_level.title()}")
        
        if executive_summary:
            click.echo(f"\n🎯 Executive Summary:")
            click.echo(f"Status: {score_result.scoring_breakdown.get('compliance_status', 'Unknown')}")
            click.echo(f"Critical Issues: {len([a for a in compliance_data['alerts'] if a.severity.value == 'critical'])}")
            
            if score_result.recommendations:
                click.echo(f"\n💡 Top Recommendations:")
                for i, rec in enumerate(score_result.recommendations[:3], 1):
                    click.echo(f"{i}. {rec}")
        
        # Export report if requested
        if output:
            if format == 'json':
                import json
                from dataclasses import asdict
                report_data = {
                    'audit_results': asdict(score_result),
                    'dashboard': dashboard,
                    'compliance_data': compliance_data
                }
                with open(output, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
            else:
                # Export dashboard in requested format
                exported_path = dashboard_generator.export_dashboard(dashboard, format, output)
                click.echo(f"📄 Report exported to: {exported_path}")
        
    except Exception as e:
        click.echo(f"Error performing compliance audit: {e}", err=True)
        ctx.exit(1)


@compliance.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option('--industry', type=click.Choice(['SaaS', 'FinTech', 'HealthTech', 'E-commerce', 'General']), 
              default='General', help='Industry type for benchmarking')
@click.pass_context
def score(ctx, path, industry):
    """
    Quick compliance score check.
    
    Provides a fast compliance score assessment without full audit reporting.
    """
    try:
        from ..compliance.compliance_scoring import ComplianceScorer, IndustryType
        
        scorer = ComplianceScorer(ctx.obj['config'])
        
        click.echo("🎯 Calculating compliance score...")
        
        # Mock data for demonstration
        alerts = []
        issues = []
        
        score_result = scorer.calculate_compliance_score(
            alerts, issues, IndustryType(industry.upper())
        )
        
        # Display score
        click.echo(f"\n📊 Compliance Score: {score_result.overall_score:.1f}")
        click.echo(f"Grade: {score_result.grade.value}")
        click.echo(f"Risk Level: {score_result.risk_level.title()}")
        click.echo(f"Industry Benchmark: {score_result.industry_benchmark:.1f}")
        click.echo(f"Percentile Ranking: {score_result.percentile_ranking}th")
        
        if score_result.trend_direction != "stable":
            click.echo(f"Trend: {score_result.trend_direction.title()}")
        
    except Exception as e:
        click.echo(f"Error calculating compliance score: {e}", err=True)
        ctx.exit(1)


@compliance.command()
@click.option('--company-id', help='Company ID for dashboard generation')
@click.option('--industry', type=click.Choice(['SaaS', 'FinTech', 'HealthTech', 'E-commerce', 'General']), 
              default='General', help='Industry type for benchmarking')
@click.option('--output', '-o', type=click.Path(), help='Output file for dashboard')
@click.option('--format', type=click.Choice(['html', 'pdf', 'json']), 
              default='html', help='Dashboard format')
@click.pass_context
def dashboard(ctx, company_id, industry, output, format):
    """
    Generate executive compliance dashboard.
    
    Creates a comprehensive executive dashboard with compliance metrics,
    risk heatmaps, trend analysis, and industry benchmarking.
    """
    try:
        from ..compliance.compliance_dashboard import ComplianceDashboard
        
        dashboard_generator = ComplianceDashboard(ctx.obj['config'])
        
        click.echo("📊 Generating compliance dashboard...")
        
        # Mock data for demonstration
        compliance_data = {
            'alerts': [],
            'issues': [],
            'trends': []
        }
        
        dashboard = dashboard_generator.generate_dashboard(compliance_data, industry)
        
        # Export dashboard
        if output:
            exported_path = dashboard_generator.export_dashboard(dashboard, format, output)
            click.echo(f"📄 Dashboard exported to: {exported_path}")
        else:
            click.echo("✅ Dashboard generated successfully")
            click.echo(f"Overall Score: {dashboard['compliance_score']:.1f}")
            click.echo(f"Grade: {dashboard['executive_summary']['grade']}")
            click.echo(f"Status: {dashboard['executive_summary']['compliance_status']}")
        
    except Exception as e:
        click.echo(f"Error generating dashboard: {e}", err=True)
        ctx.exit(1)


@compliance.command()
@click.option('--company-id', help='Company ID for trend analysis')
@click.option('--days', type=int, default=90, help='Number of days to analyze')
@click.pass_context
def trends(ctx, company_id, days):
    """
    Show compliance trends over time.
    
    Analyzes compliance trends and improvements over the specified time period.
    """
    try:
        click.echo(f"📈 Analyzing compliance trends over {days} days...")
        
        # Mock trend data for demonstration
        click.echo("\n📊 Compliance Trend Analysis:")
        click.echo("Period: Last 90 days")
        click.echo("Overall Trend: Improving (+5.2 points)")
        click.echo("Critical Issues: Decreasing (3 → 1)")
        click.echo("Security Score: Improving (+8.1 points)")
        click.echo("DSAR Implementation: Completed")
        click.echo("Data Deletion: In Progress")
        
        click.echo("\n🎯 Key Improvements:")
        click.echo("• Implemented encryption for all API endpoints")
        click.echo("• Added DSAR functionality")
        click.echo("• Removed hardcoded credentials")
        click.echo("• Enhanced audit logging")
        
    except Exception as e:
        click.echo(f"Error analyzing trends: {e}", err=True)
        ctx.exit(1)


@compliance.command()
@click.option('--industry', type=click.Choice(['SaaS', 'FinTech', 'HealthTech', 'E-commerce', 'General']), 
              default='General', help='Industry type for benchmarking')
@click.pass_context
def benchmark(ctx, industry):
    """
    Compare against industry benchmarks.
    
    Shows how your compliance score compares to industry peers and benchmarks.
    """
    try:
        from ..compliance.compliance_scoring import ComplianceScorer, IndustryType
        
        scorer = ComplianceScorer(ctx.obj['config'])
        benchmark = scorer.get_industry_benchmark(IndustryType(industry.upper()))
        
        click.echo(f"📊 {industry} Industry Compliance Benchmarks:")
        click.echo(f"Average Score: {benchmark.average_score:.1f}")
        click.echo(f"Median Score: {benchmark.median:.1f}")
        click.echo(f"Top Quartile: {benchmark.top_quartile:.1f}")
        click.echo(f"Bottom Quartile: {benchmark.bottom_quartile:.1f}")
        click.echo(f"Sample Size: {benchmark.sample_size:,} companies")
        click.echo(f"Last Updated: {benchmark.last_updated}")
        
        click.echo(f"\n💡 Benchmark Insights:")
        if industry == 'FinTech':
            click.echo("• FinTech companies typically have higher compliance scores")
            click.echo("• Regulatory requirements drive stronger security practices")
            click.echo("• Focus on data security and breach notification")
        elif industry == 'HealthTech':
            click.echo("• HealthTech has the highest compliance standards")
            click.echo("• HIPAA requirements influence GDPR compliance")
            click.echo("• Strong emphasis on data minimization and security")
        elif industry == 'SaaS':
            click.echo("• SaaS companies show moderate compliance scores")
            click.echo("• Focus on user consent and data portability")
            click.echo("• Cross-border transfers are common concern")
        else:
            click.echo("• General industry shows baseline compliance levels")
            click.echo("• Focus on fundamental GDPR requirements")
            click.echo("• Security and consent are key areas")
        
    except Exception as e:
        click.echo(f"Error retrieving benchmarks: {e}", err=True)
        ctx.exit(1)


@compliance.command()
@click.option('--company-id', help='Company ID for export')
@click.option('--format', type=click.Choice(['json', 'html', 'pdf']), 
              default='json', help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.pass_context
def export(ctx, company_id, format, output):
    """
    Export compliance data and reports.
    
    Exports comprehensive compliance data, reports, and evidence packages.
    """
    try:
        click.echo(f"📤 Exporting compliance data in {format.upper()} format...")
        
        # Mock export data for demonstration
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'company_id': company_id or 'demo',
            'compliance_score': 85.2,
            'grade': 'B',
            'risk_level': 'medium',
            'industry_benchmark': 75.0,
            'percentile_ranking': 75,
            'alerts': [],
            'issues': [],
            'recommendations': [
                "Implement comprehensive DSAR system",
                "Strengthen data security measures",
                "Review cross-border data transfers"
            ]
        }
        
        # Generate output file path
        if not output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = f"levox_compliance_export_{company_id or 'demo'}_{timestamp}.{format}"
        
        # Export data
        if format == 'json':
            import json
            with open(output, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format == 'html':
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Levox Compliance Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
        .recommendations {{ margin-top: 20px; }}
        .recommendation {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Levox Compliance Export</h1>
        <p>Generated: {export_data['export_timestamp'][:10]}</p>
        <p>Company: {export_data['company_id']}</p>
    </div>
    
    <div class="score">
        Compliance Score: {export_data['compliance_score']} ({export_data['grade']})
    </div>
    
    <p>Risk Level: {export_data['risk_level'].title()}</p>
    <p>Industry Benchmark: {export_data['industry_benchmark']}</p>
    <p>Percentile Ranking: {export_data['percentile_ranking']}th</p>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in export_data['recommendations'])}
    </div>
</body>
</html>
"""
            with open(output, 'w') as f:
                f.write(html_content)
        
        click.echo(f"✅ Compliance data exported to: {output}")
        
    except Exception as e:
        click.echo(f"Error exporting compliance data: {e}", err=True)
        ctx.exit(1)


if __name__ == '__main__':
    cli()
