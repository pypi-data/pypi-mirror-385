# pyresolve/cli.py

import typer
from typing_extensions import Annotated
from pyresolve.resolver import solve_dependencies
import os

# We no longer need the app = typer.Typer() line here

def read_target_packages(file_path: str) -> list[str]:
    """Reads a list of packages from a target file."""
    if not os.path.exists(file_path):
        print(f"❌ Error: Target file not found at '{file_path}'")
        raise typer.Exit(code=1)
    
    with open(file_path, "r") as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return packages

def create_app(
    target_file: Annotated[str, typer.Option(help="The path to the target file to resolve.")] = "target.txt",
    output_file: Annotated[str, typer.Option("--output", "-o", help="The name of the output file.")] = "requirements.txt"
):
    """
    Solves dependencies from a target file and creates a requirements file.
    """
    print(f"🔎 Reading target packages from '{target_file}'...")
    target_packages = read_target_packages(target_file)
    
    if not target_packages:
        print(f"⚠️ Target file '{target_file}' is empty. Nothing to do.")
        raise typer.Exit()

    print(f"🔎 Resolving dependencies for: {', '.join(target_packages)}")
    resolved_packages = solve_dependencies(target_packages)
    
    if not resolved_packages:
        print("❌ Could not resolve dependencies.")
        raise typer.Exit(code=1)
        
    with open(output_file, "w") as f:
        for pkg in resolved_packages:
            f.write(f"{pkg}\n")
            
    print(f"✅ Successfully created '{output_file}' with {len(resolved_packages)} packages.")