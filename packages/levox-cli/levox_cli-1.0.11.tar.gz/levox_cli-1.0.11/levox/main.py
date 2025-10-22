#!/usr/bin/env python3
"""
Levox - AI-powered PII/GDPR Detection CLI
Main entry point for the PyPI package

This replicates the behavior of the standalone main.py file
"""

import sys
import os
import warnings
from pathlib import Path

def main():
    """Main entry point for Levox CLI application."""
    try:
        # Suppress tree_sitter deprecation warnings globally
        warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter") 
        
        # Import the CLI system
        from .cli.commands import cli
        
        # If arguments are provided, dispatch directly to CLI (non-interactive)
        if len(sys.argv) > 1:
            try:
                cli.main(args=sys.argv[1:], standalone_mode=False)
            except SystemExit as e:
                # Click may call sys.exit; respect exit code
                sys.exit(e.code)
            except Exception as e:
                # SECURITY: Don't expose sensitive error details in production
                if os.getenv('LEVOX_DEBUG', '').lower() in ('1', 'true', 'yes'):
                    print(f"Fatal error: {e}", file=sys.stderr)
                else:
                    print("Fatal error: An unexpected error occurred. Enable debug mode for details.", file=sys.stderr)
                sys.exit(2)
            return

        # Interactive mode - import and run interactive CLI
        from .cli.interactive import InteractiveCLI
        
        interactive_cli = InteractiveCLI()
        interactive_cli.run()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        # SECURITY: Don't expose sensitive error details in production
        if os.getenv('LEVOX_DEBUG', '').lower() in ('1', 'true', 'yes'):
            print(f"Fatal error: {e}", file=sys.stderr)
        else:
            print("Fatal error: An unexpected error occurred. Enable debug mode for details.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
