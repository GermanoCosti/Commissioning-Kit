# Commissioning Kit

Suite Windows (Python) per chi fa meccatronica/automazione: import lista segnali (CSV/XLSX), normalizza i dati e genera export in diversi formati (TIA/Beckhoff/Rockwell/CoDeSys + CSV generico).

Stato: MVP in sviluppo (export "bozza" per i formati vendor, con profili modificabili).

## Avvio rapido (sviluppo)
```powershell
cd python-app
python -m pip install -e .
meccatronica-io-gui
```

## Note importanti
- Gli export vendor (TIA/Beckhoff/Rockwell/CoDeSys) sono **template bozza**: spesso vanno adattati alla versione/software e al formato di import del cliente.
- L'export CSV generico e' sempre disponibile.
