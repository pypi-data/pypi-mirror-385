from __future__ import annotations
from pathlib import Path
from datetime import datetime


def create_license(
    root,
    license_type: str = "MIT",
    owner_name: str = "Tamer",
    force: bool = False,
):
    """
    Create a LICENSE file in `root`.
    - Supports only MIT for now.
    - Uses current year.
    - If file exists and force=False, do nothing.
    - If file exists and force=True, overwrite (no emoji, ASCII-only prints).
    """
    year = datetime.now().year
    target = Path(root) / "LICENSE"

    # Only MIT is supported by this minimal implementation
    if license_type != "MIT":
        raise ValueError(f"Unsupported license type: {license_type}")

    # Respect existing file unless forced
    if target.exists() and not force:
        print("LICENSE already exists (use --force to overwrite).")
        return target

    mit_text = f"""MIT License

Copyright (c) {year} {owner_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
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
