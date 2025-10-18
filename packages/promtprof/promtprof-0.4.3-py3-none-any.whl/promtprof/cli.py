from __future__ import annotations
import argparse, sys, json, os
from .colors import bcolors
from pathlib import Path
from .core import estimate
from .models import PricingTable
from .fx import FxRates

def main():
    ap = argparse.ArgumentParser(description="promtprof – Prompt-Profiler & Token-Kostenrechner")
    ap.add_argument("--model", required=True, help="Modellname (aus der Pricing-YAML)")
    ap.add_argument("--pricing", help="Pfad zu Pricing-YAML (Alternativ: ENV PROMTPROF_PRICING)")
    ap.add_argument("--fx", help="Pfad zu FX-YAML (Alternativ: ENV PROMTPROF_FX)")
    ap.add_argument("--file", help="Pfad zu einer Textdatei (optional)")
    ap.add_argument("--expected-output-tokens", type=int, default=0, help="Erwartete Antwortlänge in Tokens (optional)")
    ap.add_argument("--output-file", help="Antwortdatei für realen Output (optional)")
    ap.add_argument("--json", action="store_true", help="JSON-Ausgabe statt Text (optional)")
    ap.add_argument("--to-currency", help="Zielwährung (z. B. EUR, GBP). Wenn gesetzt, werden Kosten umgerechnet. (optional)")
    args = ap.parse_args()

    if args.file:
        p = Path(args.file)
        try:
            prompt = p.read_text(encoding="utf-8")
        except FileNotFoundError:
            ap.error(f"{bcolors.FAIL}Datei nicht gefunden: {p}{bcolors.ENDC}")
        except PermissionError:
            ap.error(f"{bcolors.FAIL}Kein Zugriff auf Datei: {p}{bcolors.ENDC}")
    else:
        prompt = sys.stdin.read()

    output_text = None
    if args.output_file:
        p = Path(args.output_file)
        try:
            output_text = p.read_text(encoding="utf-8")
        except FileNotFoundError:
            ap.error(f"{bcolors.FAIL}Datei nicht gefunden: {p}{bcolors.ENDC}")

    pricing = None
    if args.pricing:
        pricing_path = args.pricing
    else:
        env_path = os.environ.get("PROMTPROF_PRICING")
        if env_path:
            pricing_path = env_path

    try:
        pricing = PricingTable.from_yaml(pricing_path)
    except FileNotFoundError:
        ap.error(f"{bcolors.FAIL}Datei nicht gefunden: {pricing_path}{bcolors.ENDC}")

    fx_rates = None
    target_currency = (args.to_currency or "USD").upper()
    if target_currency != "USD":
        fx_path = args.fx or os.environ.get("PROMTPROF_FX")
        if not fx_path:
            ap.error(f"{bcolors.FAIL}--to-currency gesetzt ({target_currency}), aber keine FX-YAML via --fx oder ENV PROMTPROF_FX angegeben.{bcolors.ENDC}")
        try:
            fx_rates = FxRates.from_yaml(fx_path)
        except FileNotFoundError:
            ap.error(f"{bcolors.FAIL}FX-YAML nicht gefunden: {fx_path}{bcolors.ENDC}")
        except ValueError as e:
            ap.error(f"{bcolors.FAIL}Ungültige FX-YAML ({fx_path}): {e}{bcolors.ENDC}")

    prof = estimate(
        prompt,
        model=args.model,
        pricing=pricing,
        expected_output_tokens=args.expected_output_tokens or None,
        output_text=output_text,
        currency=args.to_currency,
        fx=fx_rates,
    )

    if args.json:
        print(json.dumps(prof.__dict__, ensure_ascii=False, indent=2))
    else:
        print(f"")
        print(f"{bcolors.HEADER}Model: {prof.model}{bcolors.ENDC}")
        print(f"Input tokens: {prof.input_tokens:>3}")
        print(f"Output tokens: {prof.output_tokens:>2}")
        print(f"Total tokens: {prof.total_tokens:>3}")
        print(f"")
        print(f"Input cost (USD): ${prof.input_cost_usd:.8f}")
        print(f"Output cost (USD): ${prof.output_cost_usd:.8f}")
        print(f"Total cost (USD): ${prof.total_cost_usd:.8f}")
        if args.to_currency:
            print(f"Currency: {prof.currency}")
            print(f"Input cost ({prof.currency}): {prof.input_cost:.8f}")
            print(f"Output cost ({prof.currency}): {prof.output_cost:.8f}")
            print(f"Total cost ({prof.currency}): {prof.total_cost:.8f}")
        print(f"")

if __name__ == "__main__":
    main()
