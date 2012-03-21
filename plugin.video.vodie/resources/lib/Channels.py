#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
    modified: jpearce
"""

import re
import sys
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib, urllib2

import RTEScraper
from RTEScraper import RTE
import RTERadioScraper
from RTERadioScraper import RTERadio
import TV3Scraper
from TV3Scraper import TV3
import TG4Scraper
from TG4Scraper import TG4
import AerTVScraper
from AerTVScraper import AerTV
import AnlarScraper
from AnlarScraper import Anlar
import ShoutcastRadioScraper
from ShoutcastRadioScraper import ShoutcastRadio

import MenuConstants

class Channels:

    def getChannels(self):
        return [RTE().getChannelDetail(),
                TV3().getChannelDetail(),
                TG4().getChannelDetail(),
                Anlar().getChannelDetail(),
                AerTV().getChannelDetail(),
                RTERadio().getChannelDetail(),
                ShoutcastRadio().getChannelDetail(),
                {'Channel': 'All', 'Thumb':'../icon.png', 'Title':'Recently watched', 'mode':'recentlyWatched', 'Plot':''},\
                {'Channel': 'All', 'Thumb':'../icon.png', 'Title':'Favorites', 'mode':'favorites', 'Plot':''}]

    def grabDetails(self, url, img, title = None):
        if channel == RTEScraper.CHANNEL:
            return RTE().grabDetails(url, img, title)
        elif mode == TG4Scraper.CHANNEL:
            return TG4().grabDetails(url, img, title)
        elif mode == TV3Scraper.CHANNEL:
            return TV3().grabDetails(url, img, title)
        
    def getVideoDetails(self, channel, url, skipAds):
        if channel == RTEScraper.CHANNEL:
            return RTE().getVideoDetails(url, skipAds)
        elif channel == TG4Scraper.CHANNEL:
            return TG4().getVideoDetails(url)
        elif channel == TV3Scraper.CHANNEL:
            return TV3().getVideoDetails(url)
        elif channel == AerTVScraper.CHANNEL:
            return AerTV().getVideoDetails(url)
        elif channel == AnlarScraper.CHANNEL:
            return Anlar().getVideoDetails(url)

    def getMainMenu(self, channel):
        if channel == RTEScraper.CHANNEL:
            return RTE().getMainMenu(), True
        elif channel == RTERadioScraper.CHANNEL:
            return RTERadio().getMainMenu(), True
        elif channel == TG4Scraper.CHANNEL:
            return TG4().getMainMenu(), True
        elif channel == TV3Scraper.CHANNEL:
            return TV3().getMainMenu(), True
        elif channel == AerTVScraper.CHANNEL:
            return AerTV().getMainMenu(), True
        elif channel == ShoutcastRadioScraper.CHANNEL:
            return ShoutcastRadio().getMainMenu(), True
        elif channel == AnlarScraper.CHANNEL:
            return Anlar().getMainMenu(), True
            
    def getEpisodes(self, channel, showID):
        if channel == RTEScraper.CHANNEL:
            return RTE().getEpisodes(showID)
        elif channel == TG4Scraper.CHANNEL:
            return TG4().getEpisodes(showID)
        elif channel == TV3Scraper.CHANNEL:
            return TV3().getEpisodes(showID)
        elif channel == MagnetWebTvScraper.CHANNEL:
            return AerTV().getEpisodes(showID)

# This is to allow an indirection on the url.  Right now, hacked - TODO: Make properly OO by adding this as a required method of each scraper
# For the moment, we'll just call referenceURL on the TV3 scraper, otherwise return the passed url
    def referenceURL(self, channel, url):
        if channel == RTEScraper.CHANNEL:
            return url
        elif channel == TG4Scraper.CHANNEL:
            return url
        elif channel == TV3Scraper.CHANNEL:
            return TV3().referenceURL(url)
        elif channel == MagnetWebTvScraper.CHANNEL:
            return url

    def getMenu(self, channel, menutype, name = None):
        if channel == RTEScraper.CHANNEL:
            if menutype == MenuConstants.MODE_CATEGORY:
                return RTE().SearchByCategory(name)
            elif menutype == MenuConstants.MODE_ATOZ:
                return RTE().SearchAtoZ(name)
            else:
                return RTE().getMenuItems(menutype)
        elif channel == TG4Scraper.CHANNEL:
            return TG4().getMenuItems(menutype)
        elif channel == ShoutcastRadioScraper.CHANNEL:
            return ShoutcastRadio().getMenuItems(menutype)
                
if __name__ == '__main__':
    print 'hello'
