from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    tag: str
    descrizione: str
    tipo: str  # DI, DO, AI, AO, SAFETY, ecc.
    indirizzo: str  # es. I0.0, %I0.0, IW64, ecc.
    dispositivo: str = ""
    modulo: str = ""
    morsetto: str = ""
    unita: str = ""
    note: str = ""

