import fnmatch
import os
import mutagen.id3
from mpd import MPDConfig

exit()

if __name__ == '__main__':
    mpdconfig = MPDConfig().parse()
    music_dir = mpdconfig.data['music_directory']

    categories = ["0 - BEST+", "1 - Best", "2 - Good",  "3 - Ok+",   "4 - Ok",  "5 - Out",  "6 - Bad","7 - Unrated"]
    bins =       [        248,        219,        191,        157,        123,         59,          1,            0]
    # write_bins compatible with MusicBee (and therefore) WMP, FooBar, etc:
    write_bins = [        255,        245,        196,        186,        128,         64,          1,            0]

    playlists = {} # name: paths

    # make playlists from mp3s
    for root, _, filenames in os.walk(os.path.expanduser(music_dir)):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            fullpath = os.path.join(root, filename)
            song = os.path.relpath(fullpath,music_dir)

            audio = mutagen.id3.ID3(fullpath)
            popms = audio.getall('POPM')
            if len(popms)>0:
                rating = popms[0].rating
                for i in range(len(categories)):
                    if rating>=bins[i]:
                        playlist = playlists.get(categories[i],[])
                        playlist.append(song)
                        playlists[categories[i]] = playlist
                        break
            else:
                playlist = playlists.get(categories[-1], [])
                playlist.append(song)
                playlists[categories[-1]] = playlist

    # write playlists to mpd
    for k,v in playlists.items():
        with open(os.path.join(os.path.expanduser(mpdconfig.data['playlist_directory']),str(k)+'.m3u'),'w') as f:
            for song in v:
                f.write(song+'\n')
