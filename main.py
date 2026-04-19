import os
import re

from time import sleep
from pathlib import Path

from pytubefix import Playlist, YouTube
from pytubefix.exceptions import VideoUnavailable, AgeRestrictedError, BotDetection

class FFMPEGError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"


USB_PATH = '/media/aerial/MUSIC'
PLAYLISTS_URLS : list[str] = [
    #'https://www.youtube.com/playlist?list=PLKhMBl2bi_P8E7ajBeqDttWEvhMW4beFv',  # The Best of Youtube
    'https://www.youtube.com/playlist?list=PLKhMBl2bi_P-DFD5aufaItfrnpXCgqDBS',  # Anything Goes
]


def create_dir():
    try:
        os.mkdir(OUTPUT_PATH)
        print(f"Directory '{OUTPUT_PATH}' created successfully.")
    except FileExistsError:
        print(f"Directory '{OUTPUT_PATH}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{OUTPUT_PATH}'")
    except FileNotFoundError:
        raise FileNotFoundError


def download_playlist(urls_dict : dict, errors_dict : dict):
    counter : int = 0
    for url in p.video_urls:
        try:
            yt = YouTube(url)

            if url not in urls_dict:  # ignores videos that are already on the playlist

                print(f'({counter}/{p.length}) Downloading audio from: {yt.title}')
                ys = yt.streams.get_audio_only()
                title = re.sub(r'[^\w\-_\. /]', '_', yt.title)  # replaces invalid chars from titles
                m4a_title = f'{title}.m4a'
                mp3_title = f'{title}.mp3'
                ys.download(output_path=OUTPUT_PATH, filename=m4a_title)
                m4a_to_mp3(f'{OUTPUT_PATH}/{m4a_title}', f'{OUTPUT_PATH}/{mp3_title}')

                with open(urls_txt, 'a', encoding="utf-8") as urltxt:
                    urltxt.write(f'{url},{yt.title}\n')  # updates file
        except FFMPEGError:
            print(f'Video "{title}" caused an ffmpeg error, skipping.')
        except AgeRestrictedError:
            print(f'Video "{title}" is age restricted, skipping.')
        except BotDetection:
            print(f'Video "{title}" flags as bot, skipping.')
        except VideoUnavailable:
            print(f'Video "{title}" is unavailable, skipping.')
            
        counter += 1


def m4a_to_mp3(m4a_path, mp3_path):
    # Adjusted command to ensure compatibility
    command = f'ffmpeg -nostats -i "{m4a_path}" -vn -ar 44100 -ac 2 -ab 192k -f mp3 -hide_banner -loglevel quiet "{mp3_path}"'
    result = os.system(command)

    if os.path.exists(m4a_path):    # deletes the m4a file regardless
        os.remove(m4a_path)

    if result != 0: # 
        raise FFMPEGError()


if __name__ == '__main__':
    print('\nYouTube playlist downloader -------------------------made by 4wardAerial')

    try:
        for PLAYLIST_URL in PLAYLISTS_URLS:
            p = Playlist(PLAYLIST_URL)
            dir = p.title
            OUTPUT_PATH : str = f'{USB_PATH}/{dir}'

            print(f'\nDownloading playlist: {p.title}\n')

            create_dir()

            urls_txt = Path(f'{OUTPUT_PATH}/urls.txt')
            urls_dict : dict = {}

            if not os.path.exists(urls_txt):
                print(f"File '{urls_txt}' created successfully.\n")
                open(urls_txt, 'w').close()
            else:
                print(f"File '{urls_txt}' already exists.\n")
                with open(urls_txt, 'r+', encoding='utf-8') as urltxt:
                    lines = urltxt.readlines()
                    for line in lines:
                        url, title = line.split(sep=',', maxsplit=1)
                        urls_dict[url] = title  # converts the lines to a 'url : title' dictionary
            
            errors_txt = Path(f'{OUTPUT_PATH}/errors.txt')
            errors_dict : dict = {}

            if not os.path.exists(errors_txt):
                print(f"File '{errors_txt}' created successfully.\n")
                open(errors_txt, 'w').close()
            else:
                print(f"File '{errors_txt}' already exists.\n")
                with open(errors_txt, 'r+', encoding='utf-8') as errortxt:
                    lines = errortxt.readlines()
                    for line in lines:
                        error, title = line.split(sep=',', maxsplit=1)
                        errors_dict[error] = title
        
            download_playlist(urls_dict, errors_dict)
            print("------------------------------------------------------------------------")
            sleep(1)
            print(f'\nPlaylist {p.title} fully updated!')
            sleep(1)
            
        print('\nAll playlists updated successfully.\n')
    except KeyboardInterrupt as e:
        print('\nProgram forcefully ended.')
    except FileNotFoundError as e:
        print('\nUSB not found. Error: {e}\n')
