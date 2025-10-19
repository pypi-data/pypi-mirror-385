from __future__ import annotations

from datetime import datetime
from pathlib import Path

def create_license(
    root: str | Path,
    license_type: str = "MIT",
    owner_name: str = "Tamer",
    force: bool = False,
) -> Path:
    """
    Create a LICENSE file in the specified root directory.

    Args:
        root (str | Path): Target directory where the LICENSE file will be created.
        license_type (str): License type to apply. Only "MIT" is supported. Defaults to "MIT".
        owner_name (str): Name of the license holder. Defaults to "Tamer".
        force (bool): If True, overwrite existing LICENSE file. Defaults to False.

    Returns:
        Path: Path to the created or existing LICENSE file.

    Raises:
        ValueError: If an unsupported license_type is provided.
    """
    year = datetime.now().year
    target = Path(root) / "LICENSE"

    if license_type != "MIT":
        raise ValueError(f"Unsupported license type: {license_type}")

    if target.exists() and not force:
        print("LICENSE already exists (use --force to overwrite).")
        return target

    mit_text = f"""MIT License

Copyright (c) {year} {owner_name}

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

    target.write_text(mit_text, encoding="utf-8")
    print(f"LICENSE file created for {owner_name} ({license_type}).")
    return target