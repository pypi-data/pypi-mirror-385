
import winreg
import sys
import os

import rich


def read_strings_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

# Stampa i valori di una chiave
def print_key_values(key, key_path):
    try:
        i = 0
        while True:
            name, value, _ = winreg.EnumValue(key, i)
            print(f"    {name} = {value}")
            i += 1
    except OSError:
        pass

# Ricorsivamente esplora una chiave e i suoi figli
def search_and_print_recursive(root, path):
    try:
        key = winreg.OpenKey(root, path)
    except FileNotFoundError:
        return

    rich.print(f"\n[green][KEY] {path}[/green]")
    print_key_values(key, path)

    try:
        i = 0
        while True:
            subkey_name = winreg.EnumKey(key, i)
            search_and_print_recursive(root, os.path.join(path, subkey_name))
            i += 1
    except OSError:
        pass
    finally:
        winreg.CloseKey(key)

# Cerca in tutto il registro partendo da radici note
def search_registry_for_string(search_string):
    roots = {
        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
        'HKEY_USERS': winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
    }

    for root_name, root_const in roots.items():
        try:
            def recursive_search(root, path=""):
                try:
                    key = winreg.OpenKey(root, path)
                except OSError:
                    return

                if search_string.lower() in path.lower():
                    search_and_print_recursive(root, path)

                try:
                    i = 0
                    while True:
                        subkey_name = winreg.EnumKey(key, i)
                        recursive_search(root, os.path.join(path, subkey_name))
                        i += 1
                except OSError:
                    pass
                finally:
                    winreg.CloseKey(key)

            recursive_search(root_const)
        except Exception as e:
            print(f"Errore nel cercare in {root_name}: {e}")

def searcher(file_path: str):

    stringhe = read_strings_from_file(file_path)

    for s in stringhe:
        rich.print(f"\n[cyan]=== CERCA: '{s}' ===[/cyan]")
        search_registry_for_string(s)