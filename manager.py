import os
import re

from pathlib import Path
from pytubefix import Playlist, YouTube
from pytubefix.exceptions import VideoUnavailable, AgeRestrictedError, BotDetection
from shutil import copyfile

from errors import FFMPEGError

   
def add_to_log(reason : str, log : str, logs_dict : dict, logs_txt : Path):
    if log not in logs_dict:
        with open(logs_txt, 'a', encoding="utf-8") as logtxt:
            logtxt.write(f'{log},{reason}\n')  # updates file



def m4a_to_mp3(m4a_path : str, mp3_path : str):
    # Adjusted command to ensure compatibility
    command = f'ffmpeg -y -nostats -i "{m4a_path}" -fflags +genpts -vn -ar 44100 -ac 2 -ab 192k -f mp3 -hide_banner -loglevel quiet "{mp3_path}"'
    result = os.system(command)

    if os.path.exists(m4a_path):  # deletes the m4a file regardless
        try:
            os.remove(m4a_path)
        except Exception as e:
            print(f'[ERROR] Error while deleting {m4a_path}: {e}')

    if result != 0:
        raise FFMPEGError()
    

def download_playlist(p : Playlist, urls_dict : dict, logs_dict : dict, urls_txt : Path, logs_txt : Path, LOCAL_OUTPUT_PATH : Path, DEVICE_OUTPUT_PATH : Path, IS_MOBILE : bool):
    for counter, url in enumerate(p.video_urls, start=1):
        try:
            if counter == 1: print('\nDownloading audio from:')  # prints just before the first download
            if url in urls_dict:
                urls_dict[url][1] = 1  # updates counter to show the song is still on the playlist 
                continue  # ignores videos that are already on the playlist

            yt = YouTube(url)
            print(f'({counter}/{p.length}) {yt.title}')
            
            ys = yt.streams.filter(only_audio=True, file_extension='mp4').first()

            title = re.sub(r'[\W_]+', '_', yt.title).strip('_')
            m4a_title = f'{title}.m4a'
            mp3_title = f'{title}.mp3'
            ys.download(output_path=LOCAL_OUTPUT_PATH, filename=m4a_title)
            m4a_to_mp3(f'{LOCAL_OUTPUT_PATH}/{m4a_title}', f'{LOCAL_OUTPUT_PATH}/{mp3_title}')

            if IS_MOBILE:
                copyfile(Path(f'{LOCAL_OUTPUT_PATH}/{mp3_title}'), Path(f'{DEVICE_OUTPUT_PATH}/{mp3_title}'))

            with open(urls_txt, 'a', encoding="utf-8") as urltxt:
                urltxt.write(f'{url},{title}\n')  # updates file
            
        except FFMPEGError:
            print(f'Video "{url}" caused an ffmpeg error, skipping.')
            add_to_log('ffmpeg', title, logs_dict, logs_txt)
        except (BotDetection, KeyError):
            print(f'Video "{url}" flags as bot, skipping.')
            add_to_log('bot_detection', url, logs_dict, logs_txt)
        except AgeRestrictedError:
            print(f'Video "{url}" is age restricted, skipping.')
            add_to_log('age_restriction', url, logs_dict, logs_txt)
        except VideoUnavailable:
            print(f'Video "{url}" is unavailable, skipping.')
            add_to_log('unavailable', url, logs_dict, logs_txt)
        except Exception as e:
            print(f'Video "{url}" caused unkown exception "{e}", skipping.')
            add_to_log('unknown', url, logs_dict, logs_txt)


def sync_playlist(urls_dict : dict, logs_dict : dict, urls_txt : Path, logs_txt : Path, DEVICE_OUTPUT_PATH : Path) -> int:
    # Creates list of videos that were deleted on youtube, but not in the USB
    to_remove = [url for url, data in urls_dict.items() if data[1] == 0]
    if not to_remove:
        print('Device is already synced.')
        return 0

    print(f'{len(to_remove)} file(s) will be removed during syncing. Proceed? [Y/n]')
    confirmation = input("> ")

    # Confirmation just to prevent it from deleting everything
    if confirmation != 'Y':
        return 0

    print('\nDeleting:')
    for counter, url_key in enumerate(to_remove, start=1):
        title = urls_dict[url_key][0].rstrip()
        mp3_title = f'{title}.mp3'
        mp3_path = f'{DEVICE_OUTPUT_PATH}/{mp3_title}'

        if os.path.exists(mp3_path):
            try:
                print(f'({counter}/{len(to_remove)}) {title}')
                os.remove(mp3_path)
                add_to_log('deletion', title, logs_dict, logs_txt)
            except Exception as e:
                print(f'Error while deleting {mp3_path}: {e}')

        del urls_dict[url_key]  # removes from the dict

    with open(urls_txt, 'w', encoding='utf-8') as urltxt:
        for url, data in urls_dict.items():
            urltxt.write(f'{url},{data[0]}')  # updates file
    return counter