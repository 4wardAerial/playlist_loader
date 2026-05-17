import os

from time import sleep
from pathlib import Path
from pytubefix import Playlist
from shutil import copyfile, rmtree

from manager import download_playlist, sync_playlist

TEMP_PATH = '/home/aerial/Coding/Python/playlist_loader/temp'  # Path to temp folder 
DEVICE_PATH = '/run/user/1000/gvfs/mtp:host=motorola_moto_g56_5G_ZF5257PRVK/SD_MUSIC/Music'  # Path to Device
PLAYLISTS_URLS : list[str] = [
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P8E7ajBeqDttWEvhMW4beFv',  # The Best of Youtube
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P9RSuR4PkTcIfslMiXBAYhj',  # Oops! All instrumental
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P_OhqOuK7JSN_uN0U_O8Rj1',  # Hidden Indie Gems
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P-DFD5aufaItfrnpXCgqDBS',  # Songs to Hear With Your Ears
]


def create_dir(output_path : Path):
    try:
        os.mkdir(output_path)
        print(f"Directory '{output_path}' created successfully.")
    except FileExistsError:
        print(f"Directory '{output_path}' already exists.")
    except PermissionError:
        print(f"[ERROR] Permission denied: Unable to create '{output_path}'")
    except FileNotFoundError:
        raise FileNotFoundError
 

if __name__ == '__main__':
    print('\nYouTube playlist downloader -------------------------made by 4wardAerial')
    
    # Checks if device exists, if it is a Mobile (needs temp files) or an USB 
    if not Path(DEVICE_PATH).exists():
        print("\nNo device was found.")
        exit(1)
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
                create_dir(TEMP_PATH)
                LOCAL_OUTPUT_PATH : str = f'{TEMP_PATH}/{dir}'
                create_dir(LOCAL_OUTPUT_PATH)  # Creates directory locally with the playlist's name
            else:
                # If device is an USB, it does not need to create temp files, so the the local output
                # can be set as the actual output to be redundant
                LOCAL_OUTPUT_PATH = DEVICE_OUTPUT_PATH

            device_urls_txt = Path(f'{DEVICE_OUTPUT_PATH}/urls.txt')
            local_urls_txt = Path(f'{LOCAL_OUTPUT_PATH}/urls.txt')
            urls_dict : dict = {}

            if os.path.exists(device_urls_txt):
                if IS_MOBILE:
                    print(f"File '{device_urls_txt}' found on Mobile, copied to local.")
                    copyfile(device_urls_txt, local_urls_txt)

                # Reminder taht local_urls_txt is the same as device_urls_txt if device is an USB
                with open(local_urls_txt, 'r+', encoding='utf-8') as urltxt:
                    lines = urltxt.readlines()
                    for line in lines:
                        url, title = line.split(sep=',', maxsplit=1)
                        urls_dict[url] = [title, 0]  # converts the lines to a 'url : (title, counter)' dictionary
            else:
                print(f"File '{device_urls_txt}' not found, creating one locally.")
                open(local_urls_txt, 'w').close()

            device_logs_txt = Path(f'{DEVICE_OUTPUT_PATH}/logs.txt')
            local_logs_txt = Path(f'{LOCAL_OUTPUT_PATH}/logs.txt')
            logs_dict : dict = {}
            open(local_logs_txt, 'w', encoding='utf-8').close()
            print(f"File '{local_logs_txt}' created successfully.\n")
            
            download_playlist(p, 
                              urls_dict, 
                              logs_dict, 
                              local_urls_txt, 
                              local_logs_txt, 
                              LOCAL_OUTPUT_PATH,
                              DEVICE_OUTPUT_PATH,
                              IS_MOBILE)

            with open(local_logs_txt, 'r', encoding='utf-8') as logtxt:
                lines = logtxt.readlines()
            print(f'\nDownloaded Playlist {p.title} with {len(lines)}/{p.length} skips.')
            print("------------------------------------------------------------------------")
            sleep(1)

            if mode == 1:
                deleted : int = sync_playlist(urls_dict, 
                                              logs_dict, 
                                              local_urls_txt, 
                                              local_logs_txt, 
                                              DEVICE_OUTPUT_PATH)
                
                print(f'\nSynced Playlist {p.title} with {deleted} deletions')
                print("------------------------------------------------------------------------")
                sleep(1)

            # Copies files that are on temp folder back to Mobile device
            if IS_MOBILE:
                print('\nUploading .txt files to Mobile.')
                copyfile(local_urls_txt, device_urls_txt)
                copyfile(local_logs_txt, device_logs_txt)

            print(f'Playlist {p.title} fully updated!')
            print("------------------------------------------------------------------------")
            sleep(1)

        # Clears temp folder at the end
        if IS_MOBILE and Path(TEMP_PATH).exists():
            rmtree(Path(TEMP_PATH))
            
        print('\nAll playlists updated successfully.\n')
    except KeyboardInterrupt as e:
        print('\nProgram forcefully ended.')
    # except Exception as e:
    #     print(f'\n[ERROR] {e}\n')