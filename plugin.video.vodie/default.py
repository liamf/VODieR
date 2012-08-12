#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
    liam.friel@gmail.com
"""
import sys

# Set to "True" to enable source-level Eclipse debugging

REMOTE_DBG = False 

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

#plugin constants
__plugin__  = "VODie"
__author__  = "kitesurfing@kitesurfing.ie, liam.friel@gmail.com, jpearce"
__url__     = "http://code.google.com/p/xbmc-vodie/"
__svn_url__ = "http://xbmc-vodie.googlecode.com/svn/trunk/"
__version__ = "1.1.3k"

print "[PLUGIN] '%s: version %s' initialized!" % (__plugin__, __version__)

if __name__ == "__main__":
    import resources.lib.VODie as VODie
    VODie.Main()

sys.modules.clear()
