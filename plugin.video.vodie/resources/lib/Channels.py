#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib, urllib2

import RTEScrapper
from RTEScrapper import RTE
import RTERadioScrapper
from RTERadioScrapper import RTERadio
import TV3Scrapper
from TV3Scrapper import TV3
import TG4Scrapper
from TG4Scrapper import TG4
import MagnetWebTvScrapper
from MagnetWebTvScrapper import Magnet
import AnlarScrapper
from AnlarScrapper import Anlar
import ShoutcastRadioScrapper
from ShoutcastRadioScrapper import ShoutcastRadio

import MenuConstants

class Channels:

    def getChannels(self):
        return [RTE().getChannelDetail(),
                TV3().getChannelDetail(),
                TG4().getChannelDetail(),
                Anlar().getChannelDetail(),
                Magnet().getChannelDetail(),
                RTERadio().getChannelDetail(),
                ShoutcastRadio().getChannelDetail(),
                {'Channel': 'All', 'Thumb':'../icon.png', 'Title':'Recently watched', 'mode':'recentlyWatched', 'Plot':''},\
                {'Channel': 'All', 'Thumb':'../icon.png', 'Title':'Favorites', 'mode':'favorites', 'Plot':''}]

    def grabDetails(self, url, img, title = None):
        if channel == RTEScrapper.CHANNEL:
            return RTE().grabDetails(url, img, title)
        elif mode == TG4Scrapper.CHANNEL:
            return TG4().grabDetails(url, img, title)
        elif mode == TV3Scrapper.CHANNEL:
            return TV3().grabDetails(url, img, title)
        
    def getVideoDetails(self, channel, url, skipAds):
        if channel == RTEScrapper.CHANNEL:
            return RTE().getVideoDetails(url, skipAds)
        elif channel == TG4Scrapper.CHANNEL:
            return TG4().getVideoDetails(url)
        elif channel == TV3Scrapper.CHANNEL:
            return TV3().getVideoDetails(url)
        elif channel == MagnetWebTvScrapper.CHANNEL:
            return Magnet().getVideoDetails(url)
        elif channel == AnlarScrapper.CHANNEL:
            return Anlar().getVideoDetails(url)

    def getMainMenu(self, channel):
        if channel == RTEScrapper.CHANNEL:
            return RTE().getMainMenu(), True
        elif channel == RTERadioScrapper.CHANNEL:
            return RTERadio().getMainMenu(), True
        elif channel == TG4Scrapper.CHANNEL:
            return TG4().getMainMenu(), True
        elif channel == TV3Scrapper.CHANNEL:
            return TV3().getMainMenu(), True
        elif channel == MagnetWebTvScrapper.CHANNEL:
            return Magnet().getMainMenu(), True
        elif channel == ShoutcastRadioScrapper.CHANNEL:
            return ShoutcastRadio().getMainMenu(), True
            
    def getEpisodes(self, channel, showID):
        if channel == RTEScrapper.CHANNEL:
            return RTE().getEpisodes(showID)
        elif channel == TG4Scrapper.CHANNEL:
            return TG4().getEpisodes(showID)
        elif channel == TV3Scrapper.CHANNEL:
            return TV3().getEpisodes(showID)
        elif channel == MagnetWebTvScrapper.CHANNEL:
            return Magnet().getEpisodes(showID)

    def getMenu(self, channel, menutype, name = None):
        if channel == RTEScrapper.CHANNEL:
            if menutype == MenuConstants.MODE_CATEGORY:
                return RTE().SearchByCategory(name)
            elif menutype == MenuConstants.MODE_ATOZ:
                return RTE().SearchAtoZ(name)
            else:
                return RTE().getMenuItems(menutype)
        elif channel == TG4Scrapper.CHANNEL:
            return TG4().getMenuItems(menutype)
        elif channel == ShoutcastRadioScrapper.CHANNEL:
            return ShoutcastRadio().getMenuItems(menutype)
                
if __name__ == '__main__':
    print 'hello'