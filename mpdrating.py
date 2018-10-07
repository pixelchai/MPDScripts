import fnmatch
import glob
import os
import re
import mutagen.id3

class MPDConfig:
    def __init__(self,path=None):
        """
        :raises IOError: if mpd config file cannot be found
        """
        if path is None:
            path = os.path.expanduser('~/.mpd/mpd.conf')
        if not os.path.isfile(path):
            raise IOError
        self.path = path
        self.data = {}

    def parse(self):
        with open(self.path, 'r') as f:
            raw = f.read()

        raw = re.sub(r'#.*','',raw,flags=re.MULTILINE) # remove comments

        block_rgx = re.compile(r'(\w+)\s*{([^}]*)}')
        for section in block_rgx.finditer(raw):
            self.data[section.group(1)]=self.parse_values(section.group(2))

        raw = block_rgx.sub('',raw) # remove sections
        self.data.update(self.parse_values(raw))
        return self

    def parse_values(self,text:str):
        data={}
        value_rgx = re.compile(r'(\w+)\s+("|)([^"]*)("|)',flags=re.MULTILINE)
        for line in text.splitlines():
            match = value_rgx.search(line)
            if match is not None:
                data[match.group(1)]=match.group(3)
        return data

if __name__ == '__main__':
    music_dir = MPDConfig().parse().data['music_directory']

    categories = ["BEST+", "Best", "Good",  "Ok+",   "Ok",  "Out",  "Bad","Unrated"]
    bins =       [    248,    219,    191,    157,    123,     59,      1,        0]

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
    print(playlists)