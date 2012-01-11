#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""
import sys

#plugin constants
__plugin__  = "VODie"
__author__  = "kitesurfing@kitesurfing.ie"
__url__     = "http://code.google.com/p/xbmc-vodie/"
__svn_url__ = "http://xbmc-vodie.googlecode.com/svn/trunk/"
__version__ = "1.1.3b"

print "[PLUGIN] '%s: version %s' initialized!" % (__plugin__, __version__)

if __name__ == "__main__":
    import resources.lib.VODie as VODie
    VODie.Main()

sys.modules.clear()
