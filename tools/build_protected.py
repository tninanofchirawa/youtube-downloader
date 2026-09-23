"""Developer Tools: Encrypt and Protect Core Engine for Public Release."""

import base64
import os
from pathlib import Path
import zlib

KEY = 0x5A


def encrypt_source(raw_code: str, key: int = KEY) -> str:
  compressed = zlib.compress(raw_code.encode("utf-8"), 9)
  encrypted = bytes([b ^ key for b in compressed])
  encoded = base64.b85encode(encrypted).decode("ascii")
  template = f"""# -*- coding: utf-8 -*-
# Protected Encrypted Binary Module (Zero-Trust Security Core)
import base64, zlib
_K = {hex(key)}
_E = b\"{encoded}\"
_D = bytes([b ^ _K for b in base64.b85decode(_E)])
exec(zlib.decompress(_D).decode('utf-8'), globals())
"""
  return template


def build_release():
  """Compiles and encrypts developer source into public protected release."""
  root_dir = Path(__file__).resolve().parent.parent
  src_file = root_dir / "tools" / "security_source.py"
  target_file = root_dir / "app" / "core" / "security.py"

  if not src_file.exists():
    print("Error: tools/security_source.py not found!")
    return

  with open(src_file, "r", encoding="utf-8") as f:
    clean_code = f.read()

  encrypted_code = encrypt_source(clean_code)

  with open(target_file, "w", encoding="utf-8") as f:
    f.write(encrypted_code)

    print("[OK] Successfully built and encrypted app/core/security.py for public release!")


if __name__ == "__main__":
  build_release()
