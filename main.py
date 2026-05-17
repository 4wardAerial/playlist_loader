import os

from time import sleep
from pathlib import Path
from pytubefix import Playlist

from manager import download_playlist, sync_playlist

TEMP_PATH = '/temp'  # Path to temp folder 
DEVICE_PATH = '/run/user/1000/gvfs/mtp:host=motorola_moto_g56_5G_ZF5257PRVK/SD_MUSIC/Music'  # Path to Device
PLAYLISTS_URLS : list[str] = [
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P8E7ajBeqDttWEvhMW4beFv',  # The Best of Youtube
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P9RSuR4PkTcIfslMiXBAYhj',  # Oops! All instrumental
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P_OhqOuK7JSN_uN0U_O8Rj1',  # Hidden Indie Gems
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P-DFD5aufaItfrnpXCgqDBS',  # Songs to Hear With Your Ears
]


def create_dir(DEVICE_OUTPUT_PATH : Path):
    try:
        os.mkdir(DEVICE_OUTPUT_PATH)
        print(f"Directory '{DEVICE_OUTPUT_PATH}' created successfully.")
    except FileExistsError:
        print(f"Directory '{DEVICE_OUTPUT_PATH}' already exists.")
    except PermissionError:
        print(f"[ERROR] Permission denied: Unable to create '{DEVICE_OUTPUT_PATH}'")
    except FileNotFoundError:
        raise FileNotFoundError
 

if __name__ == '__main__':
    print('\nYouTube playlist downloader -------------------------made by 4wardAerial')
    # Checks if device is a Mobile (needs temp files) or an USB 
    if 'gvfs' in DEVICE_PATH or 'mtp:host' in DEVICE_PATH:
        IS_MOBILE : bool = True
        print("\nSearching for MOBILE device.")
    else:
        IS_MOBILE : bool = False
        print("\nSearching for USB device.")

    print('\n[0] Just download   [1] Download and sync')
    mode : int = int(input('> '))

    try:
        for PLAYLIST_URL in PLAYLISTS_URLS:
            p = Playlist(PLAYLIST_URL)
            dir = p.title
            DEVICE_OUTPUT_PATH : str = f'{DEVICE_PATH}/{dir}'

            print("\n------------------------------------------------------------------------")
            print(f'Downloading playlist: {p.title}\n')

            create_dir(DEVICE_OUTPUT_PATH)  # Creates directory in the device with the playlist's name
            if IS_MOBILE:
                LOCAL_OUTPUT_PATH : str = f'{TEMP_PATH}/{dir}'
                create_dir(LOCAL_OUTPUT_PATH)  # Creates directory locally with the playlist's name

            urls_txt = Path(f'{DEVICE_OUTPUT_PATH}/urls.txt')
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
            
            logs_txt = Path(f'{DEVICE_OUTPUT_PATH}/logs.txt')
            logs_dict : dict = {}
            open(logs_txt, 'w', encoding='utf-8').close()
            print(f"File '{logs_txt}' created successfully.\n")
            
            download_playlist(p, urls_dict, logs_dict, urls_txt, logs_txt, DEVICE_OUTPUT_PATH)
            with open(logs_txt, 'r', encoding='utf-8') as logtxt:
                lines = logtxt.readlines()
            print(f'\nDownloaded Playlist {p.title} with {len(lines)}/{p.length} skips.')
            print("------------------------------------------------------------------------")
            sleep(1)

            if mode == 1:
                deleted : int = sync_playlist(urls_dict, logs_dict, urls_txt, logs_txt, DEVICE_OUTPUT_PATH)
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