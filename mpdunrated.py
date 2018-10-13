import fnmatch
import os
from mpd import MPDConfig

# removes duplicates in same playlist, removes nonexistant files, asks user about dups in different playlists

if __name__ == '__main__':
    # read config
    mpd = MPDConfig().parse()

    # read playlists
    playlists = {}
    music_dir = mpd.data['music_directory']

    for root, _, filenames in os.walk(os.path.expanduser(mpd.data['playlist_directory'])):
        for filename in fnmatch.filter(filenames, '*.m3u'):
            name = os.path.splitext(filename)[0]
            playlist = []

            with open(os.path.join(root, filename), 'r') as f:
                for line in f:
                    line=line.strip()
                    if line != '':
                        if os.path.isfile(os.path.join(music_dir,line)): # only if actual file exists
                            if line not in playlist: # not duplicate
                                playlist.append(line)

            playlists[name] = playlist

    # read songs
    flat_playlist = [x for l in playlists.values() for x in l]
    for root, _, filenames in os.walk(os.path.expanduser(music_dir)):
        for filename in fnmatch.filter(filenames, '*.mp3'):
            fullpath = os.path.join(root, filename)
            song = os.path.relpath(fullpath, music_dir)

            if song not in flat_playlist:
                playlist = playlists.get('unrated',[])
                playlist.append(song)
                playlists['unrated'] = playlist

    # check duplicates
    # flip dictionary (item --> playlists)
    flipped = {}
    for name, playlist in playlists.items():
        for item in playlist:
            if item not in flipped:
                flipped[item] = [name]
            else:
                flipped[item].append(name)

    for k,v in flipped.items():
        if len(v)>1:
            print(k)

    # write playlists
    for k,v in playlists.items():
        with open(os.path.join(os.path.expanduser(mpd.data['playlist_directory']),str(k)+'.m3u'),'w') as f:
            for song in v:
                f.write(song+'\n')