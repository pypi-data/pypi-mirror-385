import winreg
import argparse
import os
import re
from dataclasses import dataclass

import rich
from rich import print
from rich.table import Table

from searcher import searcher

com_entries = []

@dataclass
class ComDictEntry:
    registry_path: str
    values: dict[str, any]

@dataclass
class ComEntry:
    registry_path: str
    class_name: str
    assembly: str
    codebase: str
    runtime_version: str
    threading_model: str

def format_com_entry(entry: ComDictEntry) -> ComEntry:
    return ComEntry(
        class_name= entry.values['Class'] if 'Class' in entry.values else "null",
        assembly= entry.values['Assembly'] if 'Assembly' in entry.values else "null",
        codebase= entry.values['CodeBase'] if 'CodeBase' in entry.values else "null",
        runtime_version=entry.values['RuntimeVersion'] if 'RuntimeVersion' in entry.values else "null",
        threading_model=entry.values['ThreadingModel'] if 'ThreadingModel' in entry.values else "null",
        registry_path=entry.registry_path,
    )

def is_end_node(key_path) -> bool:
    #print(f"Checking {key_path}...")
    arr = key_path.split('\\')
    last = arr[-1]
    #print(f"Last = {last}")
    pattern = r'^\d+\.\d+\.\d+\.\d+$'
    return last == "InprocServer32"

def read_registry_recursive(key_path, base_hive=winreg.HKEY_LOCAL_MACHINE, log: bool = False):
    """Legge ricorsivamente tutti i dati e le sottochiavi dal percorso del registro specificato."""

    try:
        with winreg.OpenKey(base_hive, key_path) as key:
            values = {}
            subkeys = []

            # Legge i valori della chiave corrente
            i = 0
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    values[value_name] = value_data
                    i += 1
                except OSError:
                    break

            # Elenca le sottochiavi
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkeys.append(subkey_name)
                    i += 1
                except OSError:
                    break

            # Stampa i valori della chiave corrente
            if values:
                print(f"[green]Valori trovati in {key_path}:[/green]") if log else None
                for name, data in values.items():
                    print(f"  {name}: {data}") if log else None

            com_entries.append(ComDictEntry(
                registry_path=key_path,
                values=values,
            ))

            # Ricorsivamente legge le sottochiavi
            for subkey in subkeys:
                subkey_path = os.path.normpath(f"{key_path}\\{subkey}")
                if is_end_node(subkey_path):
                    #print(f"\n[yellow]Esplorando sottochiave: {subkey_path}[/yellow]")
                    read_registry_recursive(subkey_path, base_hive)

    except FileNotFoundError:
        pass
        print(f"[red]Chiave non trovata: {key_path}[/red]") if log else None
    except PermissionError:
        print(f"[red]Permessi insufficienti per accedere a: {key_path}[/red]")
    except Exception as e:
        print(f"[red]Errore durante l'accesso a {key_path}: {e}[/red]")

def find_guids_in_cs_files(directory):
    guid_pattern = re.compile(r'Guid\(\s*"([A-Fa-f0-9-]+)"\s*\)')
    guids = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = guid_pattern.findall(content)
                        if matches:
                            for i in matches:
                                print(f"Found [orange]GUID[/orange] in file [magenta]{file_path}[/magenta]: {i}")
                            guids.extend(matches)
                except Exception as e:
                    pass

    return guids

def find_guid_in_list_file(file_path):
    righe = []
    try:
        with open(file_path, 'r') as file:
            for linea in file:
                # Rimuove gli spazi o i caratteri di nuova linea alla fine della riga
                righe.append(linea.strip())
        return righe
    except FileNotFoundError:
        print(f"Il file {file_path} non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

def export_guids_to_file(guids):
    try:
        with open("guids.txt", 'w', encoding='utf-8') as file:
            for riga in guids:
                file.write(riga + '\n')  # Scrivi ogni elemento su una nuova riga
        print(f"File scritto correttamente in guids.txt")
    except Exception as e:
        print(f"Si è verificato un errore: {e}")

def print_com_entries(array: list[ComEntry]):
    table = Table(title="COM Entries")

    # Aggiungi intestazioni
    table.add_column("Registry Path", style="cyan", overflow="fold")
    table.add_column("Class Name", style="green")
    table.add_column("Assembly", style="yellow", overflow="fold")
    table.add_column("Codebase", style="magenta", overflow="fold")

    # Aggiungi i dati
    for entry in array:
        table.add_row(
            entry.registry_path,
            entry.class_name,
            entry.assembly,
            entry.codebase,
        )

    rich.print(table)

def print_relevant_info_com_entries(array: list[ComEntry]):
    for entry in array:
        str = f"[green]{entry.class_name}[/green] -> [magenta]{entry.codebase}[/magenta]"
        rich.print(str)

def main():
    parser = argparse.ArgumentParser(description="Trova GUID nei file .cs e verifica le chiavi di registro.")
    parser.add_argument("--path", type=str, help="Percorso iniziale della directory da scansionare")
    parser.add_argument("--list", type=str, help="Percorso del file contenente la lista degli GUID.")
    parser.add_argument("--search-from-list", type=str, help="Percorso del file contenente la lista delle chiavi.")
    parser.add_argument("--export", action='store_true' , help="Export to current directory all GIUD found in a .txt file.")
    parser.add_argument("--verbose", action='store_true' , help="Log all entries found and not found.")
    args = parser.parse_args()

    if args.search_from_list:
        searcher(args.search_from_list)
        return

    if args.path:
        guids_found_all = find_guids_in_cs_files(args.path)
        seen = set()
        guids_found = [x for x in guids_found_all if not (x in seen or seen.add(x))]
        if args.export:
            export_guids_to_file(guids_found)
    elif args.list:
        guids_found_all = find_guid_in_list_file(args.list)
        seen = set()
        guids_found = [x for x in guids_found_all if not (x in seen or seen.add(x))]

    base_paths = [
        r"SOFTWARE\Classes\CLSID",
        r"SOFTWARE\WOW6432Node\Classes\CLSID",
    ]

    list = []

    for clsid in guids_found:
        for base_path in base_paths:
            key_path = os.path.normpath(f"{base_path}\\{{{clsid}}}")
            list.append(key_path)
            print(f"Registry path loaded: [green]{key_path}[/green]")

    for item in list:
        #print(f"\n\nChecking path [blue]{item}[/blue]")
        read_registry_recursive(item, winreg.HKEY_LOCAL_MACHINE, args.verbose)

    rich.print("\n\n\n")
    formatted_entries = []
    for i in com_entries:
        if i.registry_path.endswith('InprocServer32'):
            formatted_com_entry = format_com_entry(i)
            formatted_entries.append(formatted_com_entry)

    print_com_entries(formatted_entries)

    print_relevant_info_com_entries(formatted_entries)


if __name__ == "__main__":
    main()
