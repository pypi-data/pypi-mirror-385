# Skylos 🔍

![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![100% Local](https://img.shields.io/badge/privacy-100%25%20local-brightgreen)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/skylos)
![PyPI version](https://img.shields.io/pypi/v/skylos)
![VS Code Marketplace](https://img.shields.io/visual-studio-marketplace/v/oha.skylos-vscode-extension)
![Security Policy](https://img.shields.io/badge/security-policy-brightgreen)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

<div align="center">
   <img src="assets/SKYLOS.png" alt="Skylos Logo" width="200">
</div>

> A static analysis tool for Python codebases written in Python that detects unreachable functions and unused imports, aka dead code. Faster and better results than many alternatives like Flake8 and Pylint, and finding more dead code than Vulture in our tests with comparable speed.

<div align="center">
   <img src="assets/FE_SS.png" alt="FE" width="800">
</div>


## Table of Contents

- [Features](#features)
- [Benchmark](#benchmark-you-can-find-this-benchmark-test-in-test-folder)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Web Interface](#web-interface)
- [Design](#design)
- [Test File Detection](#test-file-detection)
- [Vibe Coding](#vibe-coding)
- [Ignoring Pragmas](#ignoring-pragmas)
- [Including & Excluding Files](#including--excluding-files)
- [CLI Options](#cli-options)
- [Example Output](#example-output)
- [Interactive Mode](#interactive-mode)
- [Development](#development)
- [CI/CD (Pre-commit & GitHub Actions)](#cicd-pre-commit--github-actions)
- [VS Code extension](#vsc-extension)
- [FAQ](#faq)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

## Features

* **CST-safe removals:** Uses LibCST to remove selected imports or functions (handles multiline imports, aliases, decorators, async etc..)
* **Framework-Aware Detection**: Attempt at handling Flask, Django, FastAPI routes and decorators  
* **Test File Exclusion**: Auto excludes test files (you can include it back if you want)
* **Interactive Cleanup**: Select specific items to remove from CLI
* **Unused Functions & Methods**: Finds functions and methods that not called
* **Unused Classes**: Detects classes that are not instantiated or inherited
* **Unused Imports**: Identifies imports that are not used
* **Folder Management**: Inclusion/exclusion of directories 
* **Ignore Pragmas**: Skip lines tagged with `# pragma: no skylos`, `# pragma: no cover`, or `# noqa`
* **NEW** **Secrets Scanning (PoC, opt-in)**: Detects API keys & secrets (GitHub, GitLab, Slack, Stripe, AWS, Google, SendGrid, Twilio, private key blocks)
* **NEW** **Dangerous Patterns**: Flags risky code such as `eval/exec`, `os.system`, `subprocess(shell=True)`, `pickle.load/loads`, `yaml.load` without SafeLoader, hashlib.md5/sha1. Refer to `DANGEROUS_CODE.md` for the whole list. This includes SQL injection, path traversal and any other security flaws that may arise from the practise of vibe-coding. 

## Benchmark (You can find this benchmark test in `test` folder)

The benchmark checks how well static analysis tools spot dead code in Python. Things such as unused functions, classes, imports, variables, that kinda stuff. To read more refer down below.

**The methodology and process for benchmarking can be found in `BENCHMARK.md`** 

| Tool | Time (s) | Items | TP | FP | FN | Precision | Recall | F1 Score |
|------|----------|-------|----|----|----|-----------|---------|---------| 
| **Skylos (Local Dev)** | **0.013** | **34** | **22** | **12** | **7** | **0.6471** | **0.7586** | **0.6984** |
| Vulture (0%) | 0.054 | 32 | 11 | 20 | 18 | 0.3548 | 0.3793 | 0.3667 |
| Vulture (60%) | 0.044 | 32 | 11 | 20 | 18 | 0.3548 | 0.3793 | 0.3667 |
| Flake8 | 0.371 | 16 | 5 | 7 | 24 | 0.4167 | 0.1724 | 0.2439 |
| Pylint | 0.705 | 11 | 0 | 8 | 29 | 0.0000 | 0.0000 | 0.0000 |
| Ruff | 0.140 | 16 | 5 | 7 | 24 | 0.4167 | 0.1724 | 0.2439 |

To run the benchmark:
`python compare_tools.py /path/to/sample_repo`

**Note: More can be found in `BENCHMARK.md`**

## Installation

### Basic Installation

```bash
pip install skylos
```

### From Source

```bash
git clone https://github.com/duriantaco/skylos.git
cd skylos

pip install .
```

## Quick Start

```bash
skylos /path/to/your/project

skylos /path/to/your/project --secrets  ## include api key scan
skylos /path/to/your/project --danger   ## include safety scan for dangerous code

# To launch the front end
skylos run

# Interactive mode - select items to remove
skylos --interactive /path/to/your/project 

# Comment out items
skylos . --interactive --comment-out

# Dry run - see what would be removed
skylos --interactive --dry-run /path/to/your/project 

# Load the results in json format
skylos --json /path/to/your/project 

# Load the results in table format
skylos --table /path/to/your/project 

# With confidence
skylos path/to/your/file --confidence 20 ## or whatever value u wanna set
```

## Web Interface

Skylos includes a modern web dashboard for interactive analysis:

```bash
skylos run

# Opens browser at http://localhost:5090
```

## Design

### Summary 

Framework endpoints are often invoked externally (eg, via HTTP, signals), so we use framework aware signals + confidence scores to try avoid false positives while still catching dead codes

Name resolution handles aliases and modules, but when things get ambiguous, we rather miss some dead code than accidentally mark live code as dead lmao

Tests are excluded by default because their call patterns are noisy. You can opt in when you really need to audit it

### Understanding Confidence Levels

Skylos uses a confidence-based system to try to handle Python's dynamic nature and web frameworks.

### How Confidence Works

- **Confidence 100**: 100% unused (default imports, obvious dead functions)
- **Confidence 60**: Default value - conservative detection 
- **Confidence 40**: Framework helpers, functions in web app files
- **Confidence 20**: Framework routes, decorated functions
- **Confidence 0**: Show everything

### Framework Detection

When Skylos detects web framework imports (Flask, Django, FastAPI), it applies different confidence levels:

```bash
# only obvious dead codes
skylos app.py --confidence 60  # THIS IS THE DEFAULT

# include unused helpers in framework files  
skylos app.py --confidence 30

# include potentially unused routes
skylos app.py --confidence 20

# everything.. shows how all potential dead code
skylos app.py --confidence 0
```

## Test File Detection

Skylos automatically excludes test files from analysis because test code patterns often appear as "dead code" but are actually called by test frameworks. Should you need to include them in your test, just refer to the [Folder Management](#folder-management)  

### What Gets Detected as Test Files

**File paths containing:**
- `/test/` or `/tests/` directories
- Files ending with `_test.py`

**Test imports:**
- `pytest`, `unittest`, `nose`, `mock`, `responses`

**Test decorators:**  
- `@pytest.fixture`, `@pytest.mark.*`
- `@patch`, `@mock.*`

### Test File Behavior

When Skylos detects a test file, it by default, will apply a confidence penalty of 100, which will essentially filter out all dead code detection

```bash
# This will show 0 dead code because its treated as test file
/project/tests/test_user.py
/project/test/helper.py  
/project/utils_test.py

# The files will be analyzed normally. Note that it doesn't end with _test.py
/project/user.py
/project/test_data.py 
```

## Vibe-Coding

We are aware that vibe coding has created a lot of vulnerabilities. To an AI, it's job is to spit out a list of tokens with the highest probability, whether it's right or not. This may introduce vulnerabilities in their applications. We have expanded Skylos to catch the most important problems first. 

- SQL injection (cursor)
- SQL injection (raw-API)
- Command injection
- SSRF
- Path traversal
- eval/exec
- pickle.load/loads
- yaml.load w/o SafeLoader
- weak hashes MD5/SHA1
- subprocess(..., shell=True)
- requests(..., verify=False)

### Quick Start

```bash
skylos /path/to/your/project --danger
```

### Examples that will be flagged

```
# SQLi (cursor)
cur.execute(f"SELECT * FROM users WHERE name='{name}'")

# SQLi (raw-api)
pd.read_sql("SELECT * FROM users WHERE name='" + q + "'", conn)

# Command injection
os.system("zip -r out.zip " + folder)

# SSRF
requests.get(request.args["url"], timeout=3)

# Path traversal
with open(request.args.get("p"), "r") as f: ...
```

This list will be expanded in the near future. For more information, refer to `DANGEROUS_CODE.md` 

## Ignoring Pragmas

1. To ignore any warning, indicate `# pragma: no skylos` **ON THE SAME LINE** as the function/class you want to ignore

Example

```python
    def with_logging(self, enabled: bool = True) -> "WebPath":     # pragma: no skylos
        new_path = WebPath(self._url)
        return new_path
```

2. To suppress a **secret** on a line, add: `# skylos: ignore[SKY-S101]`
 
Example
 ```python

API_KEY = "ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # skylos: ignore[SKY-S101]
```

## Including & Excluding Files

### Default Exclusions
By default, Skylos excludes common folders: `__pycache__`, `.git`, `.pytest_cache`, `.mypy_cache`, `.tox`, `htmlcov`, `.coverage`, `build`, `dist`, `*.egg-info`, `venv`, `.venv`

### Folder Options
```bash
skylos --list-default-excludes

# Exclude single folder (The example here will be venv)
skylos /path/to/your/project --exclude-folder venv 

# Exclude multiple folders
skylos /path/to/your/project --exclude-folder venv --exclude-folder build

# Force include normally excluded folders
skylos /path/to/your/project --include-folder venv 

# Scan everything (no exclusions)
skylos path/to/your/project --no-default-excludes 
```

## CLI Options
```
Usage: skylos [OPTIONS] PATH

Arguments:
  PATH  Path to the Python project to analyze

Options:
  -h, --help                   Show this help message and exit
  --json                       Output raw JSON instead of formatted text  
  --table                      Output results in table format via the CLI
  -o, --output FILE            Write output to file instead of stdout
  -v, --verbose                Enable verbose output
  --version                    Checks version
  -i, --interactive            Interactively select items to remove
  --dry-run                    Show what would be removed without modifying files
  --exclude-folder FOLDER      Exclude a folder from analysis (can be used multiple times)
  --include-folder FOLDER      Force include a folder that would otherwise be excluded
  --no-default-excludes        Don't exclude default folders (__pycache__, .git, venv, etc.)
  --list-default-excludes      List the default excluded folders and
  -c, --confidence LEVEL       Confidence threshold (0-100). Lower values will show more items.
  -- secrets                   Scan for api keys/secrets
  -- danger                    Scan for dangerous code
```

## Interactive Mode

The interactive mode lets you select specific functions and imports to remove:

1. **Select items**: Use arrow keys and `spacebar` to select/unselect
2. **Confirm changes**: Review selected items before applying
3. **Auto-cleanup**: Files are automatically updated

## CI/CD (Pre-commit & GitHub Actions)

Pick **one** (or use **both**) 

1. GitHub Actions: runs Skylos on pushes/PRs in CI.
   - No local install needed

2. Pre-commit (local + CI): runs Skylos before commits/PRs.
   - You must install pre-commit locally once. Skylos gets installed automatically by the hook.

### Option A — Github Actions

1. Create .github/workflows/skylos.yml **(COPY THE ENTIRE SKYLOS.YAML FROM BELOW)**:

```yaml
name: Skylos Deadcode Scan

on:
  pull_request:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    env:
      SKYLOS_STRICT: ${{ vars.SKYLOS_STRICT || 'false' }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Skylos
        run: pip install skylos

      - name: Run Skylos
        env:
          REPORT: skylos_${{ github.run_number }}_${{ github.sha }}.json
        run: |
          echo "REPORT=$REPORT" >> "$GITHUB_OUTPUT"
          skylos . --json > "$REPORT"
        id: scan

      - name: Fail if there are findings
        continue-on-error: ${{ env.SKYLOS_STRICT != 'true' }}
        env:
          REPORT: ${{ steps.scan.outputs.REPORT }}
        run: |
            python - << 'PY'
            import json, sys, os
            report = os.environ["REPORT"]
            data = json.load(open(report, "r", encoding="utf-8"))
            count = 0
            for value in data.values():
                if isinstance(value, list):
                    count += len(value)
            print(f"Findings: {count}")
            if count > 0:
              print(f"::warning title=Skylos findings::{count} potential issues found. See {report}")
            sys.exit(1 if count > 0 else 0)
            PY

      - name: Upload report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ${{ steps.scan.outputs.REPORT }}
          path: ${{ steps.scan.outputs.REPORT }}

      - name: Summarize in job log
        if: always()
        run: |
          echo "Skylos report: ${{ steps.scan.outputs.REPORT }}" >> $GITHUB_STEP_SUMMARY
```

**To make the job fail on findings (strict mode)**:

1. Go to GitHub -> Settings -> Secrets and variables -> Actions -> Variables

2. Add variable SKYLOS_STRICT with value true

### Option B — Pre-commit (local + CI)

. Create or edit `.pre-commit-config.yaml` at the repo root:

**A: Skylos hook repo**
```yaml
## .pre-commit-config.yaml
repos:
  - repo: https://github.com/duriantaco/skylos
    rev: v2.4.0
    hooks:
      - id: skylos-scan
        name: skylos report
        entry: python -m skylos.cli
        language: python
        types_or: [python]
        pass_filenames: false
        require_serial: true
        args: [".", "--output", "report.json", "--confidence", "70", "--danger"]

  - repo: local
    hooks:
      - id: skylos-fail-on-findings
        name: skylos
        env:
          SKYLOS_SOFT: "1"
        language: python
        language_version: python3
        pass_filenames: false
        require_serial: true
        entry: >
          python -c "import os, json, sys, pathlib;
          p=pathlib.Path('report.json');

          if not p.exists(): 
            sys.exit(0);

          data=json.loads(p.read_text(encoding='utf-8'));

          count = 0
          for v in data.values():
            if isinstance(v, list):
              count += len(v)

          print(f'[skylos] findings: {count}');
          sys.exit(0 if os.getenv('SKYLOS_SOFT') or count==0 else 1)"
```
**B: self-contained local hook**

```yaml
repos:
  - repo: local
    hooks:
      - id: skylos-scan
        name: skylos report
        language: python
        entry: python -m skylos.cli
        pass_filenames: false
        require_serial: true
        additional_dependencies: [skylos==2.4.0]
        args: [".", "--output", "report.json", "--confidence", "70"]

      - id: skylos-fail-on-findings
        name: skylos (soft)
        language: python
        language_version: python3
        pass_filenames: false
        require_serial: true
        entry: >
          python -c "import os, json, sys, pathlib;
          p=pathlib.Path('report.json');

          if not p.exists(): 
            sys.exit(0);

          data=json.loads(p.read_text(encoding='utf-8'));

          count = 0
          for v in data.values():
            if isinstance(v, list):
              count += len(v)

          print(f'[skylos] findings: {count}');
          sys.exit(0 if os.getenv('SKYLOS_SOFT') or count==0 else 1)"
```

**Install requirements:**

You must install pre-commit locally once:
```bash
pip install pre-commit
pre-commit install
```

2. pre-commit run --all-files


3. Run the same hooks in CI (GitHub Actions): create .github/workflows/pre-commit.yml:

```yaml
name: pre-commit
on: [push, pull_request]
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - uses: pre-commit/action@v3.0.1
        with: { extra_args: --all-files }
```

**Pre commit behavior:** the second hook is soft by default (SKYLOS_SOFT=1). This means that it prints findings and passes. You can remove the env/logic if you want pre-commit to block commits on finding

## VS Code extension

Skylos has a VS Code extension that runs on save like a linter. Runs automatically on save of Python files. You will ll see squiggles + a popup like "Skylos found N items." For more information, refer to the VSC `README.md` inside the marketplace.

### Install

From VS Code Marketplace: "Skylos" (publisher: oha)

Version: `0.1.0`

## Development

### Prerequisites

- `Python ≥3.9`
- `pytest`
- `inquirer`

### Setup

```bash
git clone https://github.com/duriantaco/skylos.git
cd skylos

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Running Tests

```bash
python -m pytest tests/
```

## FAQ 

**Q: Why doesn't Skylos find 100% of dead code?**
A: Python's dynamic features (getattr, globals, etc.) can't be perfectly analyzed statically. No tool can achieve 100% accuracy. If they say they can, they're lying.

**Q: Why are the results different on my codebase?**
A: These benchmarks use specific test cases. Your code patterns (frameworks, legacy code, etc.) will give different results.

**Q: Are these benchmarks realistic?**
A: They test common scenarios but can't cover every edge case. Use them as a guide, not gospel.

**Q: Should I automatically delete everything flagged as unused?**
A: No. Always review results manually, especially for framework code, APIs, and test utilities.

**Q: Why did Ruff underperform?**
A: Like all other tools, Ruff is focused on detecting specific, surface-level issues. Tools like Vulture and Skylos are built SPECIFICALLY for dead code detection. It is NOT a specialized dead code detector. If your goal is dead code, then ruff is the wrong tool. It is a good tool but it's like using a wrench to hammer a nail. Good tool, wrong purpose. 

**Q: Why doesn't Skylos detect my unused Flask routes?**
A: Web framework routes are given low confidence (20) because they might be called by external HTTP requests. Use `--confidence 20` to see them. We acknowledge there are current limitations to this approach so use it sparingly.

**Q: What confidence level should I use?**
A: Start with 60 (default) for safe cleanup. Use 30 for framework applications. Use 20 for more comprehensive auditing.

**Q: What does `--danger` check**?
A: It flags common security problems. Refer to `DANGEROUS_CODE.md` for the full details

## Limitations

- **Dynamic code**: `getattr()`, `globals()`, runtime imports are hard to detect
- **Frameworks**: Django models, Flask, FastAPI routes may appear unused but aren't
- **Test data**: Limited scenarios, your mileage may vary
- **False positives**: Always manually review before deleting code
- **Secrets PoC**: May emit both a provider hit and a generic high-entropy hit for the same token. All tokens are detected only in py files (`.py`, `.pyi`, `.pyw`).

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```
   Error: Permission denied when removing function
   ```
   Check file permissions before running in interactive mode.

2. **Missing Dependencies**
   ```
   Interactive mode requires 'inquirer' package
   ```
   Install with: `pip install skylos[interactive]`

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap
- [x] Expand our test cases
- [ ] Configuration file support 
- [x] Git hooks integration
- [x] CI/CD integration examples
- [ ] Further optimization
- [ ] Add new rules
- [ ] Expanding on the `dangerous.py` list
- [ ] Porting to uv

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Author**: oha
- **Email**: aaronoh2015@gmail.com
- **GitHub**: [@duriantaco](https://github.com/duriantaco)