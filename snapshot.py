import os
from pathlib import Path

ROOT_DIR = Path("./backend").resolve()
OUTPUT_FILE = "flattened_repo.txt"

# 🔥 Hard ignore directories (path-based, not name-based)
IGNORE_DIR_NAMES = {
    ".git",
    ".next",
    "node_modules",
    "dist",
    "build",
    "out",
    "coverage",
    ".cache",
    ".turbo",
    ".vercel",
    "__pycache__",
    ".idea",
    ".vscode",
}

# ✅ Only include human-written source files
ALLOWED_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx",
    ".css",
    ".md",
    ".txt",
    '.py'
}

# ❌ Explicitly excluded even if extension matches
EXCLUDE_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    OUTPUT_FILE,
}

MAX_FILE_SIZE_KB = 200  # prevent accidental huge files


def is_ignored_path(path: Path) -> bool:
    return any(part in IGNORE_DIR_NAMES for part in path.parts)


def is_allowed_file(path: Path) -> bool:
    if path.name in EXCLUDE_FILES:
        return False
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    if path.stat().st_size > MAX_FILE_SIZE_KB * 1024:
        return False
    return True


def build_tree(root: Path) -> list[str]:
    lines = []

    for path in sorted(root.rglob("*")):
        if is_ignored_path(path):
            continue

        rel = path.relative_to(root)
        depth = len(rel.parts) - 1
        indent = "  " * depth

        if path.is_dir():
            lines.append(f"{indent}📁 {path.name}/")
        elif is_allowed_file(path):
            lines.append(f"{indent}📄 {path.name}")

    return lines


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[Error reading file: {e}]"


def flatten():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("DIRECTORY TREE (SOURCE FILES ONLY)\n")
        out.write("=================================\n\n")

        tree = build_tree(ROOT_DIR)
        out.write("\n".join(tree))

        out.write("\n\n\nFILE CONTENTS\n")
        out.write("=================================\n")

        for path in sorted(ROOT_DIR.rglob("*")):
            if is_ignored_path(path):
                continue
            if not path.is_file():
                continue
            if not is_allowed_file(path):
                continue

            out.write(f"\n\n--- FILE: {path.relative_to(ROOT_DIR)} ---\n\n")
            out.write(read_file(path))


if __name__ == "__main__":
    flatten()
    print(f"✔ Flattened source-only repo into {OUTPUT_FILE}")
