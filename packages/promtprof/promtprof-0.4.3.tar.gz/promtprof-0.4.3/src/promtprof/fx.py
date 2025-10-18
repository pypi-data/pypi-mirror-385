from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from .colors import bcolors
import yaml # type: ignore (VS-Code error)
import os

@dataclass(frozen=True)
class FxRates:
    base: str
    rates: Dict[str, float]

    @staticmethod
    def from_yaml(path: Optional[str] = None) -> "FxRates":
        if path is None:
            path = os.environ.get("PROMTPROF_FX") or os.environ.get("TOK_PROF_FX")
            if not path:
                raise FileNotFoundError("Kein Pfad zu FX-YAML angegeben und ENV PROMTPROF_FX/TOK_PROF_FX ist nicht gesetzt.")
            
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        base = str(data.get("base", "USD")).upper()
        rates = data.get("rates", {})
        if not isinstance(rates, dict) or not rates:
            raise ValueError(f"{bcolors.FAIL}Ungültige oder leere FX-YAML: Schlüssel 'rates' fehlt oder ist leer.{bcolors.ENDC}")
        
        norm = {str(k).upper(): float(v) for k, v in rates.items()}
        return FxRates(base=base, rates=norm)

    def rate_to(self, target: str) -> float:
        t = target.upper()
        if t == self.base.upper():
            return 1.0
        if t not in self.rates:
            raise KeyError(f"Kein FX-Kurs für Zielwährung '{t}' vorhanden.")
        return float(self.rates[t])
