import json, subprocess, shutil, os

def test_cli_json_stdin(tmp_path):
    pr = tmp_path / "pricing.yaml"
    pr.write_text("models:\n  m:\n    prompt_per_million: 1\n    completion_per_million: 2\n", encoding="utf-8")
    p = subprocess.run(
        [shutil.which("python"), "-m", "promtprof.cli", "--model", "m", "--pricing", str(pr), "--json"],
        input="Hallo", text=True, capture_output=True, check=True
    )
    data = json.loads(p.stdout)
    assert data["model"] == "m"
    assert "total_cost_usd" in data

def test_cli_fx_needed_but_missing(tmp_path):
    pr = tmp_path / "pricing.yaml"
    pr.write_text("models:\n  m:\n    prompt_per_million: 1\n    completion_per_million: 2\n", encoding="utf-8")
    p = subprocess.run(
        [shutil.which("python"), "-m", "promtprof.cli",
         "--model", "m", "--pricing", str(pr), "--to-currency", "EUR"],
        input="Hi", text=True, capture_output=True
    )
    assert p.returncode != 0
    assert "FX-YAML" in (p.stderr or p.stdout)