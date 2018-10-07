import os


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
