import os

USB_PATH = '/media/aerial/MUSIC'
OUTPUT_PATH : str = f'{USB_PATH}/Anything Goes'

try:
    os.mkdir(OUTPUT_PATH)
    print(f"Directory '{OUTPUT_PATH}' created successfully.")
except FileExistsError:
    print(f"Directory '{OUTPUT_PATH}' already exists.")
except PermissionError:
    print(f"Permission denied: Unable to create '{OUTPUT_PATH}'")
except FileNotFoundError:
    raise FileNotFoundError