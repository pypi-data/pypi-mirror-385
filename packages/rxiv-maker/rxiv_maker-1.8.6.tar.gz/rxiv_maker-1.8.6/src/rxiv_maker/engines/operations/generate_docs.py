"""Documentation generation script using lazydocs.

This script generates comprehensive markdown documentation for the rxiv-maker
Python modules that can be viewed directly on GitHub without requiring GitHub Pages.
It provides detailed information about classes, methods, functions, and their
signatures.
"""

import os
import shutil
import subprocess
from pathlib import Path


def generate_module_docs(docs_dir, module_path, project_root):
    """Generate documentation for a specific module using lazydocs."""
    try:
        # Find lazydocs executable
        lazydocs_cmd = shutil.which("lazydocs")
        if not lazydocs_cmd:
            print("⚠️ lazydocs not found in PATH (this is expected in CI/development environments)")
            return None  # Indicate that tool is not available, but it's not an error

        # Set up environment with proper Python path for import resolution
        env = os.environ.copy()
        src_path = str(project_root / "src")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path

        # Generate documentation for the specific module
        cmd = [
            lazydocs_cmd,
            str(module_path),
            "--output-path",
            str(docs_dir),
            "--no-watermark",
            "--remove-package-prefix",
            "--src-base-url",
            "https://github.com/henriqueslab/rxiv-maker/blob/main",
        ]

        print(f"Running: {' '.join(cmd)}")
        print(f"PYTHONPATH: {env.get('PYTHONPATH', 'Not set')}")
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )  # nosec B603
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating documentation for {module_path}: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"❌ lazydocs command not found: {e}")
        return False


def generate_enhanced_index(docs_dir, successful_modules):
    """Generate an enhanced index.md file with better organization.

    Args:
        docs_dir: Path to the docs directory
        successful_modules: List of successfully generated module paths
    """
    index_path = docs_dir / "index.md"
    readme_path = docs_dir / "README.md"

    # Create categories for modules
    categories: dict[str, list[str]] = {
        "commands": [],
        "processors": [],
        "converters": [],
        "scripts": [],
        "debug": [],
        "core": [],  # For modules at the root level
    }

    # Categorize the modules
    for module_path in successful_modules:
        parts = str(module_path).split("/")
        if len(parts) > 1 and parts[0] in categories:
            categories[parts[0]].append(module_path)
        else:
            categories["core"].append(module_path)

    # Generate the index.md file
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# API Documentation\n\n")
        f.write("Welcome to the API documentation for rxiv-maker.\n\n")

        # Generate sections for each category
        for category, modules in categories.items():
            if modules:
                f.write(f"## {category.capitalize()} Modules\n\n")
                for module in sorted(modules):
                    module_name = str(module).replace("/", ".")
                    file_name = str(module).replace("/", "_") + ".md"
                    f.write(f"- [{module_name}]({file_name})\n")
                f.write("\n")

    # Copy the same content to README.md for GitHub browsing
    if index_path.exists():
        shutil.copy(index_path, readme_path)

    return index_path


def generate_api_docs(project_root: Path | None = None) -> bool:
    """Generate API documentation using lazydocs with enhancements.

    Args:
        project_root: Root directory of the project. If None, attempts to find it.

    Returns:
        True if documentation generation was successful, False otherwise.
    """
    # Get the project root directory (script is in src/rxiv_maker/engines/operations/)
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent.parent.parent

    src_dir = project_root / "src" / "rxiv_maker"
    docs_dir = project_root / "src" / "docs" / "api"

    # Ensure docs directory exists
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing generated docs (except .gitkeep)
    for item in docs_dir.iterdir():
        if item.name != ".gitkeep":
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    print("🚀 Generating API documentation with lazydocs...")

    # Change to project root for proper module discovery
    os.chdir(project_root)

    # Find all Python files to document
    python_files = []

    # Collect all Python modules excluding __pycache__ and test files
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file) and not py_file.name.startswith("test_"):
            python_files.append(py_file)

    successful_files = []
    failed_files = []
    lazydocs_available = None

    print(f"Found {len(python_files)} Python files to document:")
    for py_file in python_files:
        rel_path = py_file.relative_to(src_dir)
        print(f"  - {rel_path}")

    # Generate documentation for key modules with better handling
    print("\n📦 Generating docs for key Python modules...")

    # Find lazydocs executable
    lazydocs_cmd = shutil.which("lazydocs")
    if not lazydocs_cmd:
        print("⚠️ lazydocs not found in PATH (this is expected in CI/development environments)")
        lazydocs_available = False
    else:
        lazydocs_available = True

        # Set up environment with proper Python path for import resolution
        env = os.environ.copy()
        src_path = str(project_root / "src")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path

        # Filter to key modules that are likely to work (avoid complex imports)
        simple_files = []
        for py_file in python_files:
            rel_path = py_file.relative_to(src_dir)
            path_str = str(rel_path)

            # Only include files that are likely to work with lazydocs
            if (
                path_str.endswith("__version__.py")
                or path_str.endswith("__init__.py")
                or "logging" in path_str
                or "utils" in path_str
                or "error" in path_str
                or path_str.endswith("validate.py")
            ):
                simple_files.append(py_file)

        print(f"Found {len(simple_files)} key modules to document")

        # Generate documentation for each simple file
        for py_file in simple_files:
            rel_path = py_file.relative_to(src_dir)
            print(f"\n📦 Generating docs for {rel_path}...")

            try:
                # Generate documentation using relative path from src_dir
                cmd = [
                    lazydocs_cmd,
                    f"rxiv_maker/{rel_path}",
                    "--output-path",
                    str(docs_dir),
                    "--no-watermark",
                    "--remove-package-prefix",
                    "--src-base-url",
                    "https://github.com/henriqueslab/rxiv-maker/blob/main/src",
                ]

                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                    cwd=src_path,  # Run from src directory
                )  # nosec B603

                successful_files.append(rel_path)
                print(f"✅ {rel_path} documented successfully")

            except subprocess.CalledProcessError:
                failed_files.append(rel_path)
                print(f"❌ Failed to document {rel_path}")
                # Don't print detailed errors to keep output clean

    print(f"\n📁 Documentation saved to: {docs_dir}")

    # List generated files
    print("\n📄 Generated files:")
    md_files = list(docs_dir.rglob("*.md"))
    if md_files:
        for file in sorted(md_files):
            if file.name != "README.md":
                rel_path = file.relative_to(docs_dir)
                print(f"  - {rel_path}")
    else:
        print("  No markdown files generated")

    # Generate enhanced index.md
    print("\n🔍 Generating enhanced documentation index...")
    index_path = generate_enhanced_index(docs_dir, successful_files)
    print(f"✅ Enhanced index created at {index_path}")

    # Summary
    print("\n📊 Summary:")
    print(f"  ✅ Successful: {len(successful_files)} files")
    print(f"  ❌ Failed: {len(failed_files)} files")

    # Handle case where lazydocs is not available
    if lazydocs_available is False:
        print("⚠️ Documentation generation skipped (lazydocs not available)")
        print("   This is normal for development/CI environments")
        return True  # Don't fail the pre-commit hook for missing optional tool
    elif successful_files:
        print("✅ Documentation generated successfully!")
        print(f"\n📚 To view the documentation, browse to: {docs_dir}")
        print("   You can also open the index.md file in a Markdown viewer.")
        return True
    else:
        print("❌ No documentation could be generated")
        return False


def main() -> int:
    """Main entry point for the generate docs command.

    Returns:
        0 for success, 1 for failure
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate API documentation")
    parser.add_argument(
        "--project-root",
        help="Path to project root directory (default: auto-detect)",
        type=Path,
    )

    args = parser.parse_args()

    try:
        # Use provided project root or auto-detect
        project_root = args.project_root
        if project_root is None:
            # Auto-detect based on current script location
            current_file = Path(__file__).resolve()
            # Navigate up from src/rxiv_maker/engines/operations/generate_docs.py to project root
            project_root = current_file.parent.parent.parent.parent.parent

        if not project_root.exists():
            print(f"❌ Project root not found: {project_root}")
            return 1

        # Generate documentation
        success = generate_api_docs(project_root)
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
