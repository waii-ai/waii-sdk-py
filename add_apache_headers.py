import os

HEADER = '''"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
'''

EXCLUDED_DIRS = {"__pycache__", "build", "dist", ".git", "venv", ".venv", "docs"}
SCRIPT_NAME = os.path.basename(__file__)

def should_skip(path):
    return any(part in EXCLUDED_DIRS for part in path.split(os.sep))

def has_header(content):
    return "Licensed under the Apache License" in content

def add_header(file_path):
    if os.path.basename(file_path) == SCRIPT_NAME:
        return
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if not has_header(content):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(HEADER + "\n" + content)
        print(f"Added header to: {file_path}")

def walk(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                add_header(path)

walk(".")

