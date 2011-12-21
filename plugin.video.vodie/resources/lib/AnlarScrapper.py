#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib, urllib2
import MenuConstants
from datetime import date

# Channel Constants
CHANNEL = 'An Lar'
ANLARLOGO = 'http://anlar.tv/images/stories/logo1.png'

class Anlar:
    def __init__(self):
        print "Initialising An Lar"

    def getChannelDetail(self):
        return {'Channel'  : CHANNEL,
                'Thumb'    : ANLARLOGO,
                'Title'    : 'An Lar',
                'mode'     : MenuConstants.MODE_PLAYVIDEO,
                'Plot'     : 'An Lar'
                }

    def getVideoDetails(self, url):
        
        rtmpServer = "rtmp://parrot.tekbits.net:443/live"
        file = "Stream1"
        
        url = '%s playpath=%s live=true' % (rtmpServer, file)
        
        yield {'Channel'     : CHANNEL,
               'Title'       : CHANNEL,
               'Director'    : CHANNEL,
               'Genre'       : CHANNEL,
               'Plot'        : CHANNEL,
               'PlotOutline' : CHANNEL,
               'id'          : url,
               'url'         : url
               }