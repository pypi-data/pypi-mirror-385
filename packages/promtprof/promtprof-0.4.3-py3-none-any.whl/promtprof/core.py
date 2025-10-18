from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math
import re

try:
    import tiktoken # type: ignore (VS-Code error)
except Exception:
    tiktoken = None

from .models import PricingTable, Pricing
from .fx import FxRates

@dataclass(frozen=True)
class Profile:
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    currency: str = "USD"
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

def _fallback_tokenize(text: str) -> int:
    if not text:
        return 0
    tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return max(1, len(tokens))

def _tiktoken_len(text: str, model: Optional[str]) -> Optional[int]:
    if tiktoken is None:
        return None
    try:
        if model:
            enc = tiktoken.encoding_for_model(model)
        else:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            return None

def count_tokens(text: str, model: Optional[str] = None) -> int:
    n = _tiktoken_len(text, model)
    if n is not None:
        return n
    approx = max(1, math.ceil(len(text) / 4))
    regex_est = _fallback_tokenize(text)
    return max(1, math.floor((approx + regex_est) / 2))

def _cost(tokens: int, per_million: float) -> float:
    return round((tokens / 1_000_000) * per_million, 6)

def estimate(
    prompt: str,
    *,
    model: str,
    pricing: Optional[PricingTable] = None,
    expected_output_tokens: Optional[int] = None,
    output_text: Optional[str] = None,
    currency: Optional[str] = None,
    fx: Optional[FxRates] = None,
) -> Profile:
    """
    Berechnet Token & Kosten für Eingabe und (optional) Ausgabe.
    Falls 'currency' gesetzt ist, werden die USD-Kosten zusätzlich in die Zielwährung konvertiert.
    """
    pricing = pricing or _try_yaml_or_default()

    p = pricing.get(model)
    if p is None:
        raise ValueError(
            f"Unbekanntes Modell '{model}'. Stelle sicher, dass es in der Pricing-YAML definiert ist "
            f"oder nutze PricingTable.override(...)."
        )

    in_tokens = count_tokens(prompt, model=model)
    out_tokens = count_tokens(output_text, model=model) if output_text is not None else (expected_output_tokens or 0)

    in_cost_usd = _cost(in_tokens, p.prompt_per_million)
    out_cost_usd = _cost(out_tokens, p.completion_per_million)
    total_usd = round(in_cost_usd + out_cost_usd, 6)

    cur = "USD"
    in_cost = in_cost_usd
    out_cost = out_cost_usd
    total_cost = total_usd

    if currency and currency.upper() != "USD":
        fx = fx or _try_fx_or_none()
        if fx is None:
            raise FileNotFoundError("FX-Umrechnung gewünscht, aber keine FX-YAML gefunden. Setze ENV PROMTPROF_FX oder übergib fx=FxRates.from_yaml(...).")
        
        rate = fx.rate_to(currency)
        cur = currency.upper()
        in_cost = round(in_cost_usd * rate, 6)
        out_cost = round(out_cost_usd * rate, 6)
        total_cost = round(total_usd * rate, 6)

    return Profile(
        model=model,
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        total_tokens=in_tokens + out_tokens,
        input_cost_usd=in_cost_usd,
        output_cost_usd=out_cost_usd,
        total_cost_usd=total_usd,
        currency=cur,
        input_cost=in_cost,
        output_cost=out_cost,
        total_cost=total_cost,
    )

def _try_yaml_or_default() -> PricingTable:
    try:
        return PricingTable.from_yaml()
    except Exception:
        return PricingTable.default()

def _try_fx_or_none() -> Optional[FxRates]:
    try:
        return FxRates.from_yaml()
    except Exception:
        return None
