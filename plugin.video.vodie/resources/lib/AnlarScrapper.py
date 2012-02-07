#!/usr/bin/python

"""
    VODie
    
    Updated AnLar scraper, handles several channels
    
    liam.friel@gmail.com
    
"""

import re
import sys
import BeautifulSoup
import urllib, urllib2
import MenuConstants
from datetime import date

# Channel Constants
CHANNEL = 'An Lar'
MAINURL = 'http://anlar.tv/'
ANLARLOGO = 'http://anlar.tv/images/stories/logo1.png'

class Anlar:
    def __init__(self):
        print "Initialising An Lar"

    def getChannelDetail(self):

        return {'Channel'  : CHANNEL,
                'Thumb'    : ANLARLOGO,
                'Title'    : 'An Lar',
                'mode'     : MenuConstants.MODE_MAINMENU,
                'Plot'     : 'An Lar'
                }

    def getMainMenu(self):

        # Load and read the URL. Not amenable to parsing entirely with regex, too crapiful

        page = urllib2.urlopen(MAINURL)
        soup = BeautifulSoup.BeautifulSoup(page)
        page.close()
        
        divs = soup.findAll("div", {"class" : "fusion-submenu-wrapper level2"})
        
        # Channels are in divs[1]
        # We can use a REGEX now to parse out the interesting bits

        # This page is not so amenable to being parsed 
        REGEXP = 'href="(.*)".*\s+<span>.*\s+([^\t]*)\s*.*\s+</span>'
        allmatches = re.findall(REGEXP, str(divs[1]), re.MULTILINE) 
        for match in allmatches:
            print match[0]
            print match[1]
            yield {'Channel' : CHANNEL,
                   'Thumb'   : ANLARLOGO,
                   'url'     : match[0],
                   'Title'   : match[1],
                   'mode'    : MenuConstants.MODE_PLAYVIDEO}
                
    def getVideoDetails(self, url):
        
        # Load and read the URL
        f    = urllib2.urlopen(url)
        text = f.read()
        f.close()

        # It's just easier to do this in a few separate REGEX expressions. Easier to understand
        REGEXPPLAYPATH = 'clip:{\s+url:"(.*)"'
        for mymatch in re.findall(REGEXPPLAYPATH, text):
            playPath = str(mymatch)
            
        REGEXPSWF = "rtmp:{\s+url: '(.*)'"
        for mymatch in re.findall(REGEXPSWF, text):
            swf = str(mymatch)
        
        REGEXPRTMP = "netConnectionUrl: '(.*)/live'"    
        for mymatch in re.findall(REGEXPRTMP, text):
            rtmpServer = str(mymatch)
        
        rtmpURL = '%s app=live swfUrl=%s playpath=%s' %(rtmpServer, swf, playPath)
        
        yield {'Channel'     : CHANNEL,
               'Title'       : CHANNEL,
               'Director'    : CHANNEL,
               'Genre'       : CHANNEL,
               'Plot'        : CHANNEL,
               'PlotOutline' : CHANNEL,
               'id'          : rtmpURL,
               'url'         : rtmpURL
               }
                
if __name__ == '__main__':

#    TV3().generateShowsAndSave()
#    exit(1)

    channels = Anlar().getMainMenu()
    
    for channel in channels:
        for detail in Anlar().getVideoDetails(channel['url']):
            print detail
