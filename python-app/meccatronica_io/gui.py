from __future__ import annotations

import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from meccatronica_io import db
from meccatronica_io.exporters import EXPORT_PROFILES, export_signals
from meccatronica_io.importers import read_tabular
from meccatronica_io.mapping import INTERNAL_FIELDS, REQUIRED_FIELDS, map_rows


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Meccatronica IO Suite (MVP)")
        self.geometry("980x640")
        self.minsize(900, 600)

        self.db_path = tk.StringVar(value=str(pathlib.Path("meccatronica.sqlite").resolve()))
        self.import_path = tk.StringVar(value="")
        self.out_dir = tk.StringVar(value=str(pathlib.Path("_export").resolve()))
        self.profile = tk.StringVar(value="csv_generico")

        self.headers: list[str] = []
        self.rows: list[dict[str, str]] = []
        self.colmap_vars: dict[str, tk.StringVar] = {f: tk.StringVar(value="") for f in INTERNAL_FIELDS}

        self._build()

    def _build(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.LabelFrame(root, text="Progetto / DB")
        top.pack(fill="x")
        ttk.Label(top, text="SQLite").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Entry(top, textvariable=self.db_path).grid(row=0, column=1, sticky="ew", padx=8, pady=8)
        ttk.Button(top, text="Scegli...", command=self._choose_db).grid(row=0, column=2, padx=8, pady=8)
        top.columnconfigure(1, weight=1)

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, pady=(12, 0))

        tab_import = ttk.Frame(nb, padding=12)
        tab_export = ttk.Frame(nb, padding=12)
        tab_data = ttk.Frame(nb, padding=12)
        nb.add(tab_import, text="Import")
        nb.add(tab_data, text="Dati")
        nb.add(tab_export, text="Export")

        # Import tab
        ttk.Label(tab_import, text="File CSV/XLSX").grid(row=0, column=0, sticky="w")
        ttk.Entry(tab_import, textvariable=self.import_path).grid(row=1, column=0, sticky="ew", pady=(4, 10))
        ttk.Button(tab_import, text="Scegli file...", command=self._choose_import).grid(row=1, column=1, padx=(8, 0))
        tab_import.columnconfigure(0, weight=1)

        map_frame = ttk.LabelFrame(tab_import, text="Mappatura colonne -> campi interni")
        map_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        tab_import.rowconfigure(2, weight=1)
        map_frame.columnconfigure(1, weight=1)

        ttk.Label(map_frame, text="Campo").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(map_frame, text="Colonna sorgente").grid(row=0, column=1, sticky="w", padx=8, pady=6)

        self._map_widgets: dict[str, ttk.Combobox] = {}
        for i, field in enumerate(INTERNAL_FIELDS, start=1):
            ttk.Label(map_frame, text=field + (" *" if field in REQUIRED_FIELDS else "")).grid(
                row=i, column=0, sticky="w", padx=8, pady=4
            )
            cb = ttk.Combobox(map_frame, textvariable=self.colmap_vars[field], values=[], state="readonly")
            cb.grid(row=i, column=1, sticky="ew", padx=8, pady=4)
            self._map_widgets[field] = cb

        btns = ttk.Frame(tab_import)
        btns.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(btns, text="Carica anteprima", command=self._load_preview).pack(side="left")
        ttk.Button(btns, text="Importa nel DB (sovrascrive)", command=self._import_db).pack(side="left", padx=8)

        self.import_log = tk.Text(tab_import, height=8, wrap="word")
        self.import_log.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        tab_import.rowconfigure(4, weight=1)
        self.import_log.configure(state="disabled")

        # Data tab
        self.data_label = ttk.Label(tab_data, text="Nessun dato caricato.")
        self.data_label.pack(anchor="w")
        ttk.Button(tab_data, text="Aggiorna", command=self._refresh_data).pack(anchor="w", pady=(8, 0))
        self.data_text = tk.Text(tab_data, height=24, wrap="none")
        self.data_text.pack(fill="both", expand=True, pady=(10, 0))
        self.data_text.configure(state="disabled")

        # Export tab
        ttk.Label(tab_export, text="Profilo").grid(row=0, column=0, sticky="w")
        ttk.Combobox(tab_export, textvariable=self.profile, values=EXPORT_PROFILES, state="readonly").grid(
            row=1, column=0, sticky="ew", pady=(4, 10)
        )
        ttk.Label(tab_export, text="Cartella output").grid(row=2, column=0, sticky="w")
        ttk.Entry(tab_export, textvariable=self.out_dir).grid(row=3, column=0, sticky="ew", pady=(4, 10))
        ttk.Button(tab_export, text="Scegli...", command=self._choose_out).grid(row=3, column=1, padx=(8, 0))
        ttk.Button(tab_export, text="Esporta", command=self._export).grid(row=4, column=0, sticky="w")
        tab_export.columnconfigure(0, weight=1)

        self.export_log = tk.Text(tab_export, height=14, wrap="word")
        self.export_log.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        tab_export.rowconfigure(5, weight=1)
        self.export_log.configure(state="disabled")

    def _choose_db(self) -> None:
        p = filedialog.asksaveasfilename(
            title="Scegli DB SQLite",
            defaultextension=".sqlite",
            filetypes=[("SQLite", "*.sqlite;*.db"), ("Tutti i file", "*.*")],
            initialfile="meccatronica.sqlite",
        )
        if p:
            self.db_path.set(p)

    def _choose_import(self) -> None:
        p = filedialog.askopenfilename(
            title="Scegli file segnali",
            filetypes=[("CSV/XLSX", "*.csv;*.xlsx;*.txt"), ("Tutti i file", "*.*")],
        )
        if p:
            self.import_path.set(p)

    def _choose_out(self) -> None:
        p = filedialog.askdirectory(title="Scegli cartella export")
        if p:
            self.out_dir.set(p)

    def _set_log(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.configure(state="disabled")

    def _load_preview(self) -> None:
        path = self.import_path.get().strip()
        if not path:
            messagebox.showerror("Errore", "Scegli un file CSV/XLSX.")
            return
        try:
            headers, rows = read_tabular(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Errore lettura", str(exc))
            return

        self.headers = headers
        self.rows = rows
        for cb in self._map_widgets.values():
            cb.configure(values=[""] + headers)

        # euristica: prova ad auto-mappare per nomi comuni
        hints = {
            "tag": ["tag", "nome", "name", "signal", "segnale"],
            "descrizione": ["descrizione", "description", "commento", "comment"],
            "tipo": ["tipo", "type", "io", "i/o"],
            "indirizzo": ["indirizzo", "address", "addr"],
            "dispositivo": ["dispositivo", "device"],
            "modulo": ["modulo", "module"],
            "morsetto": ["morsetto", "terminal"],
            "unita": ["unita", "unit"],
            "note": ["note", "notes"],
        }
        lower = {h.lower(): h for h in headers}
        for field, keys in hints.items():
            if self.colmap_vars[field].get():
                continue
            for k in keys:
                if k in lower:
                    self.colmap_vars[field].set(lower[k])
                    break

        preview_lines = [f"Colonne: {len(headers)} | Righe: {len(rows)}", ""]
        preview_lines.append("Prime 5 righe (raw):")
        for r in rows[:5]:
            preview_lines.append(str(r))
        self._set_log(self.import_log, "\n".join(preview_lines))

    def _import_db(self) -> None:
        if not self.rows or not self.headers:
            self._load_preview()
            if not self.rows:
                return
        colmap = {f: self.colmap_vars[f].get().strip() for f in INTERNAL_FIELDS}
        try:
            signals = map_rows(self.rows, colmap)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Errore mappatura", str(exc))
            return
        if not signals:
            messagebox.showerror("Errore", "Nessun segnale valido dopo la mappatura.")
            return

        con = db.connect(self.db_path.get().strip())
        db.clear_signals(con)
        n = db.insert_signals(con, signals)
        self._set_log(self.import_log, f"OK importati nel DB: {n}\nDB: {self.db_path.get()}")
        self._refresh_data()

    def _refresh_data(self) -> None:
        con = db.connect(self.db_path.get().strip())
        n = db.count_signals(con)
        self.data_label.configure(text=f"Segnali nel DB: {n} | {self.db_path.get()}")
        sigs = db.list_signals(con)[:200]
        lines = []
        for s in sigs:
            lines.append(f"{s.tag} | {s.tipo} | {s.indirizzo} | {s.descrizione}")
        if n > 200:
            lines.append(f"... (mostrati 200/{n})")
        self._set_log(self.data_text, "\n".join(lines) if lines else "Nessun dato.")

    def _export(self) -> None:
        con = db.connect(self.db_path.get().strip())
        signals = db.list_signals(con)
        if not signals:
            messagebox.showerror("Errore", "DB vuoto. Importa prima.")
            return
        try:
            out = export_signals(signals, self.out_dir.get().strip(), self.profile.get().strip())
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Errore export", str(exc))
            return
        self._set_log(self.export_log, f"OK export:\n- {out}\n\nProfilo: {self.profile.get()}")
        messagebox.showinfo("Export completato", f"Creato:\n{out}")


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

