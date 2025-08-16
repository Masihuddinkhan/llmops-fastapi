import shutil
import zipfile
from pathlib import Path

def clear_dir(path: str):
    """
    Delete the folder if it exists, then recreate it empty.
    """
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

def _is_within_directory(directory: Path, target: Path) -> bool:
    """
    Ensure 'target' path is inside 'directory' to prevent Zip Slip attacks.
    """
    try:
        directory = directory.resolve()
        target = target.resolve()
        return str(target).startswith(str(directory))
    except Exception:
        return False

def extract_zip(zip_path: str, target_dir: str) -> str:
    """
    Securely extract a ZIP file to target_dir.
    - Protects against Zip Slip (no absolute path or ../).
    - Preserves original folder structure.
    Returns path to extracted root.
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)

            if member_path.is_absolute():
                print(f"[WARNING] Skipping absolute path: {member_path}")
                continue

            final_path = target / member_path

            if not _is_within_directory(target, final_path):
                print(f"[WARNING] Skipping suspicious path: {member_path}")
                continue

            if member.is_dir():
                final_path.mkdir(parents=True, exist_ok=True)
            else:
                final_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member, "r") as src, open(final_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    print(f"[INFO] Extracted {zip_path} -> {target_dir}")
    return str(target)

def flatten_if_wrapper(path: Path) -> Path:
    """
    If path has only one subfolder and no files, return that folder.
    """
    items = list(path.iterdir())
    if len(items) == 1 and items[0].is_dir():
        return items[0]
    return path