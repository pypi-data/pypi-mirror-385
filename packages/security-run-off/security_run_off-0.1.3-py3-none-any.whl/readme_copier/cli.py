"""Command-line interface for readme-copier."""
import click
import sys
from pathlib import Path
from .copier import ReadmeCopier
from . import __readme__, __version__, __readme_full__

# Configure UTF-8 output for Windows
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')


@click.command()
@click.argument('source', type=click.Path(exists=True), required=False)
@click.argument('target', type=click.Path(), required=False)
@click.option('--overwrite', '-o', is_flag=True, help='Overwrite existing file in target directory')
@click.option('--rename', '-r', type=str, help='Rename the file in the target directory')
@click.option('--info', '-i', is_flag=True, help='Show information about source and target paths')
@click.option('--show-readme', is_flag=True, help='Display the embedded README documentation')
@click.option('--show-cheatsheet', is_flag=True, help='Display the full Python cheatsheet')
@click.version_option(version=__version__, prog_name='readme-copier')
def main(source, target, overwrite, rename, info, show_readme, show_cheatsheet):
    """
    Copy README files to project folders.
    
    SOURCE: Path to the source README file (optional with --show-readme or --show-cheatsheet)
    TARGET: Path to the target directory (optional with --show-readme or --show-cheatsheet)
    
    Examples:
    
        readme-copy README.md ./my-project
        
        readme-copy README.md ./my-project --overwrite
        
        readme-copy README.md ./my-project --rename PROJECT_README.md
        
        readme-copy --show-readme       # Display package documentation
        
        readme-copy --show-cheatsheet   # Display Python cheatsheet
    """
    if show_readme:
        click.echo(__readme__)
        return
    
    if show_cheatsheet:
        click.echo(__readme_full__)
        return
    
    # Validate that source and target are provided for copy operations
    if not source or not target:
        raise click.UsageError("SOURCE and TARGET are required unless using --show-readme or --show-cheatsheet")
    
    copier = ReadmeCopier(source, target)
    
    if info:
        info_dict = copier.get_info()
        click.echo("\n=== Path Information ===")
        click.echo(f"Source Path: {info_dict['source_path']}")
        click.echo(f"Source Exists: {info_dict['source_exists']}")
        if 'source_size' in info_dict:
            click.echo(f"Source Size: {info_dict['source_size']} bytes")
        click.echo(f"Target Path: {info_dict['target_path']}")
        click.echo(f"Target Exists: {info_dict['target_exists']}")
        click.echo()
    
    success = copier.copy(overwrite=overwrite, rename=rename)
    
    if success:
        click.secho("✓ README copied successfully!", fg='green')
    else:
        click.secho("✗ Failed to copy README", fg='red')
        raise click.Abort()


if __name__ == '__main__':
    main()
