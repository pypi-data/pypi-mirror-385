from __future__ import annotations
from pathlib import Path
from datetime import datetime

# Supported licenses
SUPPORTED_LICENSES = {"MIT"}

# Full MIT license text with placeholders for year and owner
MIT_TEXT = """MIT License

Copyright (c) {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def _write_text_ascii_safe(path: Path, text: str) -> None:
    """Write the given text to a file using UTF-8 encoding.

    Args:
        path (Path): The file path where the text will be written.
        text (str): The content to write into the file.
    """
    path.write_text(text, encoding="utf-8")

def create_license(
    root: Path,
    license_type: str = "MIT",
    owner_name: str = "Tamer",
    force: bool = False,
) -> Path:
    """Create a LICENSE file in the specified directory.

    Args:
        root (Path): The root directory where the LICENSE file will be created.
        license_type (str, optional): The type of license. Defaults to "MIT".
        owner_name (str, optional): The owner's name to include in the license. Defaults to "Tamer".
        force (bool, optional): Whether to overwrite an existing LICENSE file. Defaults to False.

    Returns:
        Path: The path to the created or existing LICENSE file.

    Raises:
        ValueError: If the license_type is unsupported.
    """
    root = Path(root)
    license_path = root / "LICENSE"

    if license_type not in SUPPORTED_LICENSES:
        raise ValueError(f"Unsupported license type: {license_type}")

    if license_path.exists() and not force:
        print("LICENSE already exists (use --force to overwrite).")
        return license_path

    if license_path.exists() and force:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = license_path.with_name(f"LICENSE.{ts}.bak")
        try:
            license_path.replace(backup)
        except Exception:
            pass

    year = datetime.now().year
    if license_type == "MIT":
        text = MIT_TEXT.format(year=year, owner=owner_name)
    else:
        text = f"{license_type} License\n\n(c) {year} {owner_name}\n"

    _write_text_ascii_safe(license_path, text)

    print(f"LICENSE file created for {owner_name} ({license_type}).")
    return license_path