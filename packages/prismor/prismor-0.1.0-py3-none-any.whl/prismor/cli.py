"""Command-line interface for Prismor security scanning tool."""

import sys
import json
import click
from typing import Optional
from .api import PrismorClient, PrismorAPIError


def print_success(message: str):
    """Print success message in green."""
    click.secho(f"✓ {message}", fg="green")


def print_error(message: str):
    """Print error message in red."""
    click.secho(f"✗ {message}", fg="red", err=True)


def print_info(message: str):
    """Print info message in blue."""
    click.secho(f"ℹ {message}", fg="blue")


def print_warning(message: str):
    """Print warning message in yellow."""
    click.secho(f"⚠ {message}", fg="yellow")


def format_scan_results(results: dict, scan_type: str):
    """Format and display scan results."""
    click.echo("\n" + "=" * 60)
    click.secho(f"  Scan Results - {scan_type}", fg="cyan", bold=True)
    click.echo("=" * 60 + "\n")
    
    # Display repository information
    if "repository" in results:
        click.secho("Repository:", fg="yellow", bold=True)
        click.echo(f"  {results['repository']}\n")
    
    # Display scan status
    if "status" in results:
        status_color = "green" if results["status"] == "success" else "red"
        click.secho(f"Status: ", fg="yellow", bold=True, nl=False)
        click.secho(results["status"], fg=status_color)
        click.echo()
    
    # Display scan results based on type
    if "scan_results" in results:
        scan_data = results["scan_results"]
        
        # Vulnerability scan results
        if "vulnerabilities" in scan_data or "Results" in scan_data:
            click.secho("Vulnerabilities Found:", fg="yellow", bold=True)
            vuln_data = scan_data.get("vulnerabilities", scan_data.get("Results", []))
            if isinstance(vuln_data, list):
                click.echo(f"  Total: {len(vuln_data)}")
            else:
                click.echo(f"  Data available in detailed output")
            click.echo()
        
        # Secret scan results
        if "secrets" in scan_data or "findings_summary" in scan_data:
            click.secho("Secrets Detected:", fg="yellow", bold=True)
            secrets = scan_data.get("secrets", scan_data.get("findings_summary", {}))
            if isinstance(secrets, dict):
                for key, value in secrets.items():
                    click.echo(f"  {key}: {value}")
            else:
                click.echo(f"  {len(secrets) if isinstance(secrets, list) else 'Data available'}")
            click.echo()
        
        # SBOM results
        if "sbom" in scan_data or "artifacts" in scan_data:
            click.secho("SBOM Generated:", fg="yellow", bold=True)
            sbom_data = scan_data.get("sbom", scan_data.get("artifacts", []))
            if isinstance(sbom_data, list):
                click.echo(f"  Total artifacts: {len(sbom_data)}")
            else:
                click.echo(f"  SBOM data available")
            click.echo()
    
    # Display result URLs if available
    if "public_url" in results:
        click.secho("Results URL:", fg="yellow", bold=True)
        click.echo(f"  {results['public_url']}\n")
    
    if "presigned_url" in results:
        click.secho("Download URL:", fg="yellow", bold=True)
        click.echo(f"  {results['presigned_url']}\n")
    
    click.echo("=" * 60 + "\n")


@click.group(invoke_without_command=True)
@click.option(
    "--scan",
    type=str,
    help="Repository to scan (username/repo or full GitHub URL)"
)
@click.option("--vex", is_flag=True, help="Perform vulnerability scanning")
@click.option("--sbom", is_flag=True, help="Generate Software Bill of Materials")
@click.option("--detect-secret", is_flag=True, help="Detect secrets in repository")
@click.option("--fullscan", is_flag=True, help="Perform all scan types")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
@click.version_option(version="0.1.0", prog_name="prismor")
@click.pass_context
def cli(ctx, scan: Optional[str], vex: bool, sbom: bool, detect_secret: bool, 
        fullscan: bool, output_json: bool):
    """Prismor CLI - Security scanning tool for GitHub repositories.
    
    Examples:
        prismor --scan username/repo --vex
        prismor --scan username/repo --fullscan
        prismor --scan https://github.com/username/repo --detect-secret
    """
    # If no command and no scan option, show help
    if ctx.invoked_subcommand is None and not scan:
        click.echo(ctx.get_help())
        return
    
    # If scan option is provided, perform the scan
    if scan:
        # Check if at least one scan type is selected
        if not any([vex, sbom, detect_secret, fullscan]):
            print_error("Please specify at least one scan type: --vex, --sbom, --detect-secret, or --fullscan")
            sys.exit(1)
        
        try:
            # Initialize API client
            print_info(f"Initializing Prismor scan for: {scan}")
            client = PrismorClient()
            
            # Determine scan type for display
            scan_types = []
            if fullscan:
                scan_types.append("Full Scan (VEX + SBOM + Secret Detection)")
            else:
                if vex:
                    scan_types.append("VEX")
                if sbom:
                    scan_types.append("SBOM")
                if detect_secret:
                    scan_types.append("Secret Detection")
            
            print_info(f"Scan type: {', '.join(scan_types)}")
            print_info("Starting scan... (this may take a few minutes)")
            
            # Perform scan
            results = client.scan(
                repo=scan,
                vex=vex,
                sbom=sbom,
                detect_secret=detect_secret,
                fullscan=fullscan
            )
            
            # Output results
            if output_json:
                click.echo(json.dumps(results, indent=2))
            else:
                print_success("Scan completed successfully!")
                format_scan_results(results, ', '.join(scan_types))
            
        except PrismorAPIError as e:
            print_error(str(e))
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            sys.exit(1)


@cli.command()
def version():
    """Display the version of Prismor CLI."""
    click.echo("Prismor CLI v0.1.0")


@cli.command()
def config():
    """Display current configuration."""
    import os
    
    click.echo("\n" + "=" * 60)
    click.secho("  Prismor CLI Configuration", fg="cyan", bold=True)
    click.echo("=" * 60 + "\n")
    
    # Check API key
    api_key = os.environ.get("PRISMOR_API_KEY")
    if api_key:
        # Show only first and last 4 characters
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print_success(f"PRISMOR_API_KEY: {masked_key}")
    else:
        print_error("PRISMOR_API_KEY: Not set")
        click.echo("\nTo set your API key, run:")
        click.echo("  export PRISMOR_API_KEY=your_api_key")
    
    click.echo("\nAPI Endpoint: https://api.prismor.dev")
    click.echo("=" * 60 + "\n")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

