import os
import datetime
import subprocess
from pathlib import Path

REVIEW_DIR = Path("review_reports")
FLAGGED_DIR = Path("flagged_code")
REVIEW_DIR.mkdir(exist_ok=True)
FLAGGED_DIR.mkdir(exist_ok=True)

def run_lint_check(filepath):
    """Run flake8 lint check and return the list of issues."""
    result = subprocess.run(
        ["flake8", filepath],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().splitlines()

def run_pylint(filepath):
    """Optional: Run pylint for deeper code analysis."""
    result = subprocess.run(
        ["pylint", filepath, "--disable=R,C", "--score=n"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().splitlines()

def review_files():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = REVIEW_DIR / f"{timestamp}_review.md"

    total_files = 0
    flagged_files = 0
    total_issues = 0

    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"# 🔍 Code Review Report – {timestamp}\n\n")

        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".py") and not root.startswith("./agents"):
                    total_files += 1
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath)

                    issues = run_lint_check(filepath)
                    pylint_issues = run_pylint(filepath)
                    all_issues = issues + pylint_issues

                    if all_issues:
                        flagged_files += 1
                        total_issues += len(all_issues)

                        log.write(f"## 📄 {relpath}\n\n")
                        log.write("### Flake8 + Pylint Warnings:\n")
                        log.write("```text\n")
                        for issue in all_issues:
                            log.write(issue + "\n")
                        log.write("```\n\n")

                        # Save the flagged copy
                        flagged_path = FLAGGED_DIR / f"{file.replace('.py', '')}_flagged.py"
                        with open(filepath, "r", encoding="utf-8") as src, open(flagged_path, "w", encoding="utf-8") as dst:
                            dst.write(src.read())

        log.write(f"---\n\n")
        log.write(f"✅ **Review Summary:**\n")
        log.write(f"- Total Python files checked: `{total_files}`\n")
        log.write(f"- Files with issues: `{flagged_files}`\n")
        log.write(f"- Total issues found: `{total_issues}`\n")

    print(f"✅ Detailed review completed. Report saved to {log_file}")

if __name__ == "__main__":
    review_files()
