# PromtProf

[![PyPI](https://img.shields.io/pypi/v/promtprof.svg)](https://pypi.org/project/promtprof/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aiact-checker.svg)](https://pypi.org/project/promtprof/)

Ein **leichter Token-Kostenrechner & Prompt-Profiler** – mit:
- **YAML-basierter Preistabelle** (`PROMTPROF_PRICING` oder `--pricing`)
- **Währungsumrechnung (FX)** per YAML (`PROMTPROF_FX` oder `--fx` + `--to-currency`)
- Tokenzählung via `tiktoken` (optional) und Fallback
- CLI & Python-API

## Installation

```bash
pip install -e .
```

## Pricing-YAML

```yaml
# pricing.yaml
models:
  gpt-5-mini:
    prompt_per_million: 0.25
    completion_per_million: 2.00
  sonnet-3-7:
    prompt_per_million: 3.00
    completion_per_million: 15.00
  gemini-flash:
    prompt_per_million: 0.10
    completion_per_million: 0.40
  llama-4:
    prompt_per_million: 0.15
    completion_per_million: 0.60
  my-internal-model:
    prompt_per_million: 0.07
    completion_per_million: 0.11
```

Setze den Pfad per ENV oder Flag:
```bash
export PROMTPROF_PRICING=/pricing.yaml
```

## FX-YAML (Währungsumrechnung)

```yaml
# fx.yaml
base: USD
rates:
  EUR: 0.92
  GBP: 0.78
  JPY: 145.0
```

ENV setzen oder Flag verwenden:
```bash
export PROMTPROF_FX=/fx.yaml
```

## CLI

```bash
# Ohne Umrechnung (USD)
promtprof --model my-internal-model --pricing /path/pricing.yaml --file prompt.txt

# Mit Umrechnung in EUR
promtprof --model my-internal-model --pricing /path/pricing.yaml --fx /path/fx.yaml --to-currency EUR --file prompt.txt
```

## Python-API

```python
from promtprof import estimate, PricingTable, FxRates

pt = PricingTable.from_yaml("/path/pricing.yaml")
fx = FxRates.from_yaml("/path/fx.yaml")
prof = estimate("Hallo", model="my-internal-model", pricing=pt, expected_output_tokens=5, currency="EUR", fx=fx)
print(prof.total_cost_usd, prof.total_cost, prof.currency)
```

MIT
