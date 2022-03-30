
from configparser import ConfigParser
import os
from shutil import copy

ini = ConfigParser()
gui_folder = os.path.dirname(os.path.abspath(__file__))
ini.read(os.path.join(gui_folder, 'config.ini'))


def get_whitelist() -> list:
    """
    Load a list of words. If an error matches a word in this list it will be
    marked as whitelisted, which can then be ignored if the user activate the
    corresponding option
    :return:
    """
    fn = ini.get('paths', 'whitelist')
    if "\\" not in fn or "/" not in fn:  # file in the same directory pylanggui
        fn = os.path.join(gui_folder, fn)
    with open(fn) as fh:
        return [word.lower() for word in fh.read().split('\n') if word]


def save_whitelist(words: list, outfile: str, overwrite: bool = True):
    """
    Saves `words` to `outfile`
    :param words: list of words whitelisted
    :param outfile: target storage file
    :param overwrite: if `outfile`, if exists, will be overwritten
    :return:
    """
    mode = "w" if overwrite else "a"
    if "\\" not in outfile or "/" not in outfile:
        fn = os.path.join(gui_folder, outfile)
    copy(outfile, "bk-" + outfile + '.bak')
    with open(outfile, mode=mode) as fh:
        fh.write('\n'.join(word.lower().strip() for word in words))
