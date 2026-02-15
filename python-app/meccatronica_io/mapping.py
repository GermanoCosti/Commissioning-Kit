from __future__ import annotations

from meccatronica_io.schema import Signal

INTERNAL_FIELDS = [
    "tag",
    "descrizione",
    "tipo",
    "indirizzo",
    "dispositivo",
    "modulo",
    "morsetto",
    "unita",
    "note",
]

REQUIRED_FIELDS = ["tag", "tipo", "indirizzo"]


def map_rows(rows: list[dict[str, str]], colmap: dict[str, str]) -> list[Signal]:
    # colmap: internal_field -> source_column_name
    missing = [f for f in REQUIRED_FIELDS if not colmap.get(f)]
    if missing:
        raise ValueError(f"Mappatura incompleta. Mancano: {', '.join(missing)}")

    signals: list[Signal] = []
    for r in rows:
        def get(internal: str) -> str:
            src = colmap.get(internal, "")
            return (r.get(src, "") if src else "").strip()

        tag = get("tag")
        tipo = get("tipo")
        indirizzo = get("indirizzo")
        if not tag or not tipo or not indirizzo:
            continue
        signals.append(
            Signal(
                tag=tag,
                descrizione=get("descrizione") or "",
                tipo=tipo,
                indirizzo=indirizzo,
                dispositivo=get("dispositivo"),
                modulo=get("modulo"),
                morsetto=get("morsetto"),
                unita=get("unita"),
                note=get("note"),
            )
        )
    return signals

