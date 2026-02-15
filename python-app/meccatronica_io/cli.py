from __future__ import annotations

import argparse
import pathlib
import sys

from meccatronica_io import db
from meccatronica_io.exporters import EXPORT_PROFILES, export_signals
from meccatronica_io.importers import read_tabular
from meccatronica_io.mapping import INTERNAL_FIELDS, map_rows


def main() -> int:
    parser = argparse.ArgumentParser(prog="meccatronica-io", description="IO Suite: import CSV/XLSX e export profili.")
    parser.add_argument("--db", default="meccatronica.sqlite", help="Percorso DB SQLite")

    sub = parser.add_subparsers(dest="cmd", required=True)

    imp = sub.add_parser("import", help="Importa segnali da CSV/XLSX nel DB")
    imp.add_argument("--file", required=True, help="Percorso CSV/XLSX")
    imp.add_argument("--clear", action="store_true", help="Svuota tabella signals prima di importare")
    # mappatura semplice via argomenti: --map tag=COL --map tipo=COL ...
    imp.add_argument("--map", action="append", default=[], help="Mappatura: campo=colonna (es. tag=TAG)")

    exp = sub.add_parser("export", help="Esporta segnali dal DB")
    exp.add_argument("--profile", required=True, choices=EXPORT_PROFILES, help="Profilo export")
    exp.add_argument("--out-dir", default="_export", help="Cartella output")

    args = parser.parse_args()
    con = db.connect(args.db)

    if args.cmd == "import":
        headers, rows = read_tabular(args.file)
        colmap = {k: "" for k in INTERNAL_FIELDS}
        for m in args.map:
            if "=" not in m:
                continue
            k, v = m.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k in colmap and v in headers:
                colmap[k] = v
        if args.clear:
            db.clear_signals(con)
        signals = map_rows(rows, colmap)
        n = db.insert_signals(con, signals)
        print(f"OK importati: {n}")
        return 0

    if args.cmd == "export":
        signals = db.list_signals(con)
        if not signals:
            print("Nessun segnale nel DB. Importa prima.")
            return 1
        p = export_signals(signals, args.out_dir, args.profile)
        print(f"OK export: {p}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

