"""Cai cac thu vien can thiet cho Solar Forecast vao Python hien tai.

Cach dung trong PowerShell (nen kich hoat .venv truoc):
    python cai_thu_vien.py
    python web/app.py
"""

from __future__ import annotations

import subprocess
import sys


THU_VIEN = [
    "flask>=3.0,<4",
    "numpy>=1.26,<3",
    "pandas>=2.1,<3",
    "scikit-learn>=1.4,<2",
    "joblib>=1.3,<2",
    "pyarrow>=15,<24",
    "matplotlib>=3.8,<4",
    "openpyxl>=3.1,<4",
]


def main() -> None:
    print("Python dang dung:", sys.executable)
    print("Dang nang cap pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    print("\nDang cai thu vien cho Solar Forecast...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *THU_VIEN])

    print("\nDa cai xong.")
    print("Chay web bang lenh:")
    print(f'  "{sys.executable}" web/app.py')
    print("Sau do mo: http://127.0.0.1:6001")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            f"Cai thu vien that bai (ma loi {error.returncode}). "
            "Kiem tra ket noi mang va quyen ghi vao moi truong Python."
        ) from error
