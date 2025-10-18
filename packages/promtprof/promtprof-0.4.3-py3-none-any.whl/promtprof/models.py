from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import yaml # type: ignore (VS-Code error)
import os

@dataclass(frozen=True)
class Pricing:
    name: str
    prompt_per_million: float
    completion_per_million: float

    def to_dict(self):
        return asdict(self)

class PricingTable:
    """
    Preistabelle mit Support für YAML-Dateien.
    YAML-Schema:
    ---
    models:
      <model-name>:
        prompt_per_million: <float>
        completion_per_million: <float>
    """

    def __init__(self, table: Optional[Dict[str, Pricing]] = None):
        self._table: Dict[str, Pricing] = table or {}

    @staticmethod
    def default() -> "PricingTable":
        return PricingTable({})

    @staticmethod
    def from_yaml(path: Optional[str] = None) -> "PricingTable":
        if path is None:
            path = os.environ.get("PROMTPROF_PRICING") or os.environ.get("TOK_PROF_PRICING")
            if not path:
                raise FileNotFoundError("Kein Pfad zur Pricing-YAML angegeben und ENV PROMTPROF_PRICING/TOK_PROF_PRICING ist nicht gesetzt.")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        models = data.get("models", {})

        if not isinstance(models, dict) or not models:
            raise ValueError("Ungültige oder leere Pricing-YAML: Schlüssel 'models' fehlt oder ist leer.")
        
        table: Dict[str, Pricing] = {}
        for name, cfg in models.items():
            ppm = float(cfg["prompt_per_million"])
            cpm = float(cfg["completion_per_million"])
            table[name] = Pricing(name, prompt_per_million=ppm, completion_per_million=cpm)
            
        return PricingTable(table)

    def get(self, name: str) -> Optional[Pricing]:
        return self._table.get(name)

    def override(self, name: str, *, prompt_per_million: float, completion_per_million: float) -> None:
        self._table[name] = Pricing(name, prompt_per_million, completion_per_million)

    def to_dict(self) -> Dict[str, dict]:
        return {k: v.to_dict() for k, v in self._table.items()}
