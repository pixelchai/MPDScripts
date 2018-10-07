import os
import re

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

    def parse_values(self,text:str):
        data={}
        value_rgx = re.compile(r'(\w+)\s+("|)([^"]*)("|)',flags=re.MULTILINE)
        for line in text.splitlines():
            match = value_rgx.search(line)
            if match is not None:
                data[match.group(1)]=match.group(3)
        return data

m = MPDConfig()
m.parse()
print(m)