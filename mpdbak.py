import fnmatch
import os
from pprint import pprint

import click
import mutagen.id3
from gspread.exceptions import APIError

from mpd import MPDConfig
import gspread
from oauth2client.service_account import ServiceAccountCredentials

@click.command()
@click.option('-k','--keyfile',envvar='KEYFILE',prompt=True)
def backup(keyfile, sheet_url=r'https://docs.google.com/spreadsheets/d/'
                              r'11ZzdMLfILRPZW0NDDXSlwHlyVp13PvAeRTZnoVEWpqU/edit?usp=sharing'):
    # read mpd config
    mpd = MPDConfig().parse()

    # read playlists
    playlists={}
    music_dir = mpd.data['music_directory']

    for root, _, filenames in os.walk(os.path.expanduser(mpd.data['playlist_directory'])):
        for filename in fnmatch.filter(filenames, '*.m3u'):
            name = os.path.splitext(filename)[0]
            playlist = []

            with open(os.path.join(root, filename),'r') as f:
                for line in f:
                    if line.strip() != '':
                        data = [line]
                        audio = mutagen.id3.ID3(os.path.join(music_dir,line.strip()))

                        # add audio data (if available)
                        tit2s = audio.getall('TIT2')
                        tpe1s = audio.getall('TPE1')

                        if len(tit2s)>0:
                            data.append('/'.join(tit2s[0].text))
                        else:
                            data.append('')

                        if len(tpe1s)>0:
                            data.append('/'.join(tpe1s[0].text))
                        else:
                            data.append('')

                        playlist.append(data)

            playlists[name] = playlist

    # gspread updating
    client = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_name(keyfile,['https://spreadsheets.google.com/feeds']))
    sh = client.open_by_url(sheet_url)

    # worksheet for each playlist
    for pname,playlist in playlists.items():
        # create if not exist
        try:
            sh.add_worksheet(pname,"1024","3")
            pass
        except APIError:
            pass

        worksheet = sh.worksheet(pname)
        worksheet.clear()

        for i in range(len(playlist[0])):
            col = [list(reversed(data))[i] for data in playlist]
            worksheet.insert_row(col)
            # pprint([x for x in col])


if __name__ == '__main__':
    backup()