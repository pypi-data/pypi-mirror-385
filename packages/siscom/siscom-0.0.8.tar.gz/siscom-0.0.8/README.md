
# SISCOM

This is windows cli utility to print COM registrations inside your Windows Registry.

You can import the CLSID/GGUID list from: 
- Your source code (it will scan every .h/.cpp/.c/.cs file in the given directory)
- a .txt file (one item per line)

## Features
- Scan source code files for CLSID/GUID definitions
- Read CLSID/GUIDs from a text file
- Query Windows Registry for COM registration details
- Output results in a structured format
- Save results to a file

## Installation


## Usage
   ```bash
   $ siscom.exe --help
usage: siscom.exe [-h] [--path PATH] [--list LIST] [--search-from-list SEARCH_FROM_LIST] [--export] [--verbose]

Trova GUID nei file .cs e verifica le chiavi di registro.

options:
  -h, --help            show this help message and exit
  --path PATH           Percorso iniziale della directory da scansionare
  --list LIST           Percorso del file contenente la lista degli GUID.
  --search-from-list SEARCH_FROM_LIST
                        Percorso del file contenente la lista delle chiavi.
  --export              Export to current directory all GIUD found in a .txt file.
  --verbose             Log all entries found and not found.
   ```

