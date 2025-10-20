import os
import webbrowser
from pathlib import Path
import shutil
import codestack
import importlib.resources as pkg_resources
import codestack  # user must have codestack installed

def create_env(output_path=".env"):
    """
    Copy .env.example from the installed codestack package
    to the user-specified location.
    """
    try:
        # Locate .env.example inside the installed package
        src_path = pkg_resources.files(codestack) / ".env.example"
    except Exception:
        raise FileNotFoundError("Could not locate .env.example in the codestack package.")

    # Copy to output path
    shutil.copy(src_path, output_path)
    print(f" Created environment file at '{output_path}'")


def preview_project(output_dir:str):
    """
    Preview the contents and structure of a generated project 
    in the specified output directory.

    This function scans the project folder, identifies known 
    entry points (e.g., main scripts, index.html), and prints 
    a hierarchical view of the files. If no recognized entry 
    point is found, it lists all files and folders.

    Parameters

    output_dir : str
        The directory path of the generated project to preview.

    Return

    None
        Prints a summary of the project structure and main entry points.

    Notes
    - Designed to work with projects of any language or framework.
    - Helps developers quickly understand the generated project 
      without opening files manually.
    """
    output_dir = Path(output_dir)
    
    if not output_dir.exists():
        print(f" Folder '{output_dir}' does not exist.")
        return
    
    print(f" Previewing app in '{output_dir}'\n")

    #  Search recursively for index.html
    index_file = None
    for path in output_dir.rglob("index.html"):
        index_file = path
        break

    if index_file:
        print(f" Web app detected! Opening {index_file} in browser...")
        webbrowser.open(index_file.resolve().as_uri())
        return
    
    #  Check for README
    readme_file = None
    for f in output_dir.rglob("README.*"):
        readme_file = f
        break
    if readme_file:
        print(f" Found README: {readme_file.name}")
        try:
            with open(readme_file, "r", encoding="utf-8") as file:
                for line in file.readlines()[:20]:
                    print(line.rstrip())
        except:
            pass
        print("...")  # indicate truncated preview

    #  Detect Python CLI / backend apps
    python_entry = None
    for f in ["main.py", "app.py", "server.py"]:
        candidates = list(output_dir.rglob(f))
        if candidates:
            python_entry = candidates[0]
            break
    if python_entry:
        print(f" Python entry detected: {python_entry.name}")
        print(f"Run: python {python_entry.resolve()}")
        return

    #  Detect Node.js / frontend projects
    package_json = None
    for f in output_dir.rglob("package.json"):
        package_json = f
        break
    if package_json:
        print(" Node.js project detected!")
        print("Run:")
        print(f"  cd {package_json.parent.resolve()}")
        print("  npm install")
        print("  npm start")
        return

    # 5️ Fallback: list folder contents
    print("📂 No known entry point detected. Listing folder contents:")
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            path = Path(root) / f
            print("-", path.relative_to(output_dir))

