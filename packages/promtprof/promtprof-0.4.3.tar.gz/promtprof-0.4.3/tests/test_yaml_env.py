import os, json, subprocess, shutil

def test_env_pricing_and_fx(tmp_path, monkeypatch):
    pr = tmp_path / "pricing.yaml"
    pr.write_text("models:\n  m:\n    prompt_per_million: 1\n    completion_per_million: 2\n", encoding="utf-8")

    fx = tmp_path / "fx.yaml"
    fx.write_text("base: USD\nrates:\n  EUR: 2.0\n", encoding="utf-8")

    monkeypatch.setenv("PROMTPROF_PRICING", str(pr))
    monkeypatch.setenv("PROMTPROF_FX", str(fx))

    p = subprocess.run(
        [shutil.which("python"), "-m", "promtprof.cli", "--model", "m", "--to-currency", "EUR", "--json"],
        input="Hi", text=True, capture_output=True, check=True
    )

    data = json.loads(p.stdout)
    assert data["currency"] == "EUR"
    assert abs(data["total_cost"] - 2 * data["total_cost_usd"]) < 1e-6
