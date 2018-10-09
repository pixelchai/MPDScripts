import fnmatch
import os
from pprint import pprint

import click
import mutagen.id3
from mpd import MPDConfig
import hyou

@click.command()
@click.option('-k','--keyfile',envvar='KEYFILE',prompt=True)
def backup(keyfile, sheet_id='11ZzdMLfILRPZW0NDDXSlwHlyVp13PvAeRTZnoVEWpqU'):
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

    # spreadsheet updating
    sh = hyou.login(keyfile)[sheet_id]

    # worksheet for each playlist
    for pname,playlist in playlists.items():
        # create if not exist
        try:
            sh.add_worksheet(pname,"1024","3")
        except:
            pass

        worksheet = sh[pname]

        # for i in range(len(playlist[0])):
        #     col = [list(reversed(data))[i] for data in playlist]
        #     # worksheet.insert_row(col)
        #     # pprint([x for x in col])
        i=0
        for data in playlist:
            j=0
            for cell in data:
                worksheet[i][j]=cell
                j+=1
            i+=1
        worksheet.commit()


if __name__ == '__main__':
    backup()