from __future__ import annotations

import csv
import pathlib

from meccatronica_io.schema import Signal


EXPORT_PROFILES = [
    "csv_generico",
    "tia_csv_bozza",
    "beckhoff_csv_bozza",
    "rockwell_csv_bozza",
    "codesys_csv_bozza",
]


def export_signals(signals: list[Signal], out_dir: str, profile: str) -> pathlib.Path:
    out = pathlib.Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if profile == "csv_generico":
        return _export_csv_generico(signals, out / "signals.csv")

    if profile == "tia_csv_bozza":
        return _export_tia_bozza(signals, out / "tia_tags.csv")

    if profile == "beckhoff_csv_bozza":
        return _export_beckhoff_bozza(signals, out / "beckhoff_tags.csv")

    if profile == "rockwell_csv_bozza":
        return _export_rockwell_bozza(signals, out / "rockwell_tags.csv")

    if profile == "codesys_csv_bozza":
        return _export_codesys_bozza(signals, out / "codesys_tags.csv")

    raise ValueError(f"Profilo export non supportato: {profile}")


def _export_csv_generico(signals: list[Signal], path: pathlib.Path) -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(
            [
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
        )
        for s in signals:
            w.writerow([s.tag, s.descrizione, s.tipo, s.indirizzo, s.dispositivo, s.modulo, s.morsetto, s.unita, s.note])
    return path


def _export_tia_bozza(signals: list[Signal], path: pathlib.Path) -> pathlib.Path:
    # ATTENZIONE: formato di import TIA varia per versione/progetto. Questa e' una bozza.
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Name", "DataType", "Address", "Comment"])
        for s in signals:
            dtype = _guess_tia_datatype(s.tipo)
            w.writerow([s.tag, dtype, s.indirizzo, s.descrizione])
    return path


def _export_beckhoff_bozza(signals: list[Signal], path: pathlib.Path) -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Name", "Type", "Comment"])
        for s in signals:
            w.writerow([s.tag, _guess_plc_type(s.tipo), s.descrizione])
    return path


def _export_rockwell_bozza(signals: list[Signal], path: pathlib.Path) -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["Tag Name", "Data Type", "Description"])
        for s in signals:
            w.writerow([s.tag, _guess_rockwell_type(s.tipo), s.descrizione])
    return path


def _export_codesys_bozza(signals: list[Signal], path: pathlib.Path) -> pathlib.Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Name", "Type", "Comment"])
        for s in signals:
            w.writerow([s.tag, _guess_plc_type(s.tipo), s.descrizione])
    return path


def _guess_tia_datatype(io_type: str) -> str:
    t = (io_type or "").upper().strip()
    if t in ["DI", "DO", "BOOL"]:
        return "Bool"
    if t in ["AI", "AO", "ANALOG"]:
        return "Real"
    return "Bool"


def _guess_plc_type(io_type: str) -> str:
    t = (io_type or "").upper().strip()
    if t in ["DI", "DO", "BOOL"]:
        return "BOOL"
    if t in ["AI", "AO", "ANALOG"]:
        return "REAL"
    return "BOOL"


def _guess_rockwell_type(io_type: str) -> str:
    t = (io_type or "").upper().strip()
    if t in ["DI", "DO", "BOOL"]:
        return "BOOL"
    if t in ["AI", "AO", "ANALOG"]:
        return "REAL"
    return "BOOL"

