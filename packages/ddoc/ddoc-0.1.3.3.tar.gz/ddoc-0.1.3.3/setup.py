# ddoc/setup.py
import json
import os
from setuptools import setup, find_packages

# 🔹 `config.json` 경로를 설정하고 읽기
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print('-'*55)
print('BASE_DIR = ', BASE_DIR)
print('-'*55)
CONFIG_FILE = os.path.join(BASE_DIR, "ddoc/config/config.json")
print('-'*55)
print('CONFIG_FILE = ', CONFIG_FILE)
print('-'*55)

with open(CONFIG_FILE, "r") as f:
    config_info = json.load(f)

setup(
    name="ddoc",
    description="ddoc: Data doctor for data drift",
    version=config_info["version"],  # 🔹 버전 정보 설정
    packages=find_packages(include=["ddoc", "ddoc.*"]),
    package_data={"ddoc": ["fonts/NanumGothicCoding-Bold.ttf",
                         "fonts/NanumGothicCoding-Regular.ttf", 
                         "config/config.json", ]}, 
    license="Apache2.0",
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests",
        "pandas",
        "numpy",
        "scikit-learn",
        "pyyaml",
        "fpdf",
        "weasyprint",
        "pluggy>=1.5.0",
        "typer>=0.12",
        "rich>=13.7",
        "pydantic>=2.7",
        "typer",
    ],
    entry_points={
        "console_scripts": [
            "ddoc = ddoc.cli.main:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

