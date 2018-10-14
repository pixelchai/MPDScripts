import fnmatch
import os
from mpd import MPDConfig

# copies a proportional subset of chosen playlists

if __name__=='__main__':
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
                    line = line.strip()
                    if line != '':
                        playlist.append(line)

            playlists[name] = playlist

    print(playlists)
