import fnmatch
import math
import os
import random
import shutil

from mpd import MPDConfig
from consolemenu import SelectionMenu
from natsort import natsorted
# todo rem dependencies

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

    # selecting the playlists
    playlist_names = natsorted(playlists.keys())
    selected = []

    while True:
        sel = SelectionMenu.get_selection(playlist_names,"Select a playlist:")

        if sel>len(playlist_names)-1:
            break

        selected.append(playlist_names[sel])

    print('Selected: '+', '.join(selected))
    sample_limit = int(input("Enter sample total size limit: "))

    # subset composition calculation
    a_total = 0.0
    for sel in selected:
        a_total += len(playlists[sel])

    s_nums = []
    for sel in selected:
        s_nums.append(math.floor((len(playlists[sel])/a_total)*sample_limit))

    # subset generation
    subset = {}
    i=0
    for sel in selected:
        songs = []
        rem_songs = playlists[sel]
        for j in range(s_nums[i]):
            songs.append(rem_songs.pop(random.randint(0,len(rem_songs)-1)))

        subset[sel]=songs
        i+=1

    # write subset
    root='subset'
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)

    for name, playlist in subset.items():
        path = os.path.join(root,name)
        os.makedirs(path)

        for entry in playlist:
            shutil.copy2(os.path.join(music_dir,entry),path)