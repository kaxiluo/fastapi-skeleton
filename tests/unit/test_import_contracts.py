import subprocess


def test_lint_imports_clean():
    result = subprocess.run(["uv", "run", "lint-imports"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
