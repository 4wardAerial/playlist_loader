import os

from time import sleep
from pathlib import Path
from pytubefix import Playlist

from manager import download_playlist, sync_playlist

TEMP_PATH = '/temp'  # Path to temp folder 
USB_PATH = '/run/user/1000/gvfs/mtp:host=motorola_moto_g56_5G_ZF5257PRVK/SD_MUSIC/Music'  # Path to USB
PLAYLISTS_URLS : list[str] = [
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P8E7ajBeqDttWEvhMW4beFv',  # The Best of Youtube
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P9RSuR4PkTcIfslMiXBAYhj',  # Oops! All instrumental
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P_OhqOuK7JSN_uN0U_O8Rj1',  # Hidden Indie Gems
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P-DFD5aufaItfrnpXCgqDBS',  # Songs to Hear With Your Ears
]


def create_dir():
    try:
        os.mkdir(OUTPUT_PATH)
        print(f"Directory '{OUTPUT_PATH}' created successfully.")
    except FileExistsError:
        print(f"Directory '{OUTPUT_PATH}' already exists.")
    except PermissionError:
        print(f"[ERROR] Permission denied: Unable to create '{OUTPUT_PATH}'")
    except FileNotFoundError:
        raise FileNotFoundError
 

if __name__ == '__main__':
    print('\nYouTube playlist downloader -------------------------made by 4wardAerial')

    if 'gvfs' in USB_PATH or 'mtp:host' in USB_PATH:
        IS_MTP = True
        print("-> [Detectado: CELULAR (MTP)] Usando modo de transferência temporária.")
        quit()
    else:
        IS_MTP = False
        print("-> [Detectado: ARMAZENAMENTO DIRETO (USB/PenDrive)] Salvando arquivos diretamente.")
        quit()

    print('\n[0] Just download   [1] Download and sync')
    mode : int = int(input('> '))

    try:
        for PLAYLIST_URL in PLAYLISTS_URLS:
            p = Playlist(PLAYLIST_URL)
            dir = p.title
            OUTPUT_PATH : str = f'{USB_PATH}/{dir}'

            print("\n------------------------------------------------------------------------")
            print(f'Downloading playlist: {p.title}\n')

            create_dir()

            urls_txt = Path(f'{OUTPUT_PATH}/urls.txt')
            urls_dict : dict = {}

            if not os.path.exists(urls_txt):
                print(f"File '{urls_txt}' created successfully.")
                open(urls_txt, 'w').close()
            else:
                print(f"File '{urls_txt}' already exists.")
                with open(urls_txt, 'r+', encoding='utf-8') as urltxt:
                    lines = urltxt.readlines()
                    for line in lines:
                        url, title = line.split(sep=',', maxsplit=1)
                        urls_dict[url] = [title, 0]  # converts the lines to a 'url : (title, counter)' dictionary
            
            logs_txt = Path(f'{OUTPUT_PATH}/logs.txt')
            logs_dict : dict = {}
            open(logs_txt, 'w', encoding='utf-8').close()
            print(f"File '{logs_txt}' created successfully.\n")
            
            download_playlist(p, urls_dict, logs_dict, urls_txt, logs_txt, OUTPUT_PATH)
            with open(logs_txt, 'r', encoding='utf-8') as logtxt:
                lines = logtxt.readlines()
            print(f'\nDownloaded Playlist {p.title} with {len(lines)}/{p.length} skips.')
            print("------------------------------------------------------------------------")
            sleep(1)

            if mode == 1:
                deleted : int = sync_playlist(urls_dict, logs_dict, urls_txt, logs_txt, OUTPUT_PATH)
                print(f'\nSynced Playlist {p.title} with {deleted} deletions')
                print("------------------------------------------------------------------------")
                sleep(1)

            print(f'Playlist {p.title} fully updated!')
            print("------------------------------------------------------------------------")
            sleep(1)
            
        print('\nAll playlists updated successfully.\n')
    except KeyboardInterrupt as e:
        print('\nProgram forcefully ended.')
    except FileNotFoundError as e:
        print(f'\n[ERROR] USB not found. Error: {e}\n')