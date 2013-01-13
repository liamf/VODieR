#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
    modified: jpearce
"""

import sys
import os
import urllib
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib2
import re
import pickle
from Channels import Channels
import MenuConstants

__settings__ = xbmcaddon.Addon(id='plugin.video.vodie')
getLS = __settings__.getLocalizedString

class updateArgs:

    def __init__(self, *args, **kwargs):
        self.mode = None
        for key, value in kwargs.iteritems():
            if value == 'None':
                kwargs[key] = None
            else:
                kwargs[key] = urllib.unquote_plus(kwargs[key])
        self.__dict__.update(kwargs)


class UI:

    def __init__(self):
        self.main = Main(checkMode = False)
    
    def endofdirectory(self, sortingMethods = [xbmcplugin.SORT_METHOD_NONE]):
        #Sort methods are required in library mode. ie.
        #    xbmcplugin.SORT_METHOD_DATE
        #    xbmcplugin.SORT_METHOD_TITLE
        for sortingMethod in sortingMethods:
            xbmcplugin.addSortMethod(int(sys.argv[1]), sortingMethod)
        
        #let xbmc know the script is done adding items to the list.
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]))

    def addItem(self, info, isFolder=True, addToFavorites=True):
        #Defaults in dict. Use 'None' instead of None so it is compatible for quote_plus in parseArgs
        info.setdefault('url', 'None')
        info.setdefault('Thumb', 'None')
        info.setdefault('Icon', info['Thumb'])
        
        #create params for xbmcplugin module
        u = sys.argv[0]+\
            '?url='    +urllib.quote_plus(info['url'])    +\
            '&mode='   +urllib.quote_plus(info['mode'])   +\
            '&name='   +urllib.quote_plus(info['Title'])  +\
            '&icon='   +urllib.quote_plus(info['Thumb'])  +\
            '&channel='+urllib.quote_plus(info['Channel'])

        #create the listitem for this item
        li=xbmcgui.ListItem(label          = info['Title'],
                            iconImage      = info['Icon'],
                            thumbnailImage = info['Thumb'])
        
        li.setInfo(type       = 'video',
                   infoLabels = info)

        if 'Fanart_Image' in info.keys():
            li.setProperty('Fanart_Image', info['Fanart_Image'])
        #else:
        #    li.setProperty('Fanart_Image', info['Thumb'])
        
        #If it is a Folder, we add the context menu to add to favorite shows
        if isFolder:
            if addToFavorites:
                contexturl = 'plugin://plugin.video.vodie/?'+\
                             'mode=addfavorite'+\
                             '&url='     +urllib.quote_plus(info['url'])+\
                             '&name='    +urllib.quote_plus(info['Title'])+\
                             '&icon='    +urllib.quote_plus(info['Thumb'])+\
                             '&channel=' +urllib.quote_plus(info['Channel'])
                runScript = "XBMC.RunPlugin(%s)" % contexturl
                li.addContextMenuItems([('Add to Favorite Program Series', runScript)], True)
            else:
                contexturl = 'plugin://plugin.video.vodie/?'+\
                    'mode=delfavorite'+\
                    '&url='+urllib.quote_plus(info['url'])+\
                    '&name='+urllib.quote_plus(info['Title'])+\
                    '&icon='+urllib.quote_plus(info['Thumb'])+\
                    '&channel='+urllib.quote_plus(info['Channel'])
                runScript = "XBMC.RunPlugin(%s)" % contexturl
                li.addContextMenuItems([('Remove from Favorite Program Series', runScript)], True)
                
        #add item to list
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=li, isFolder=isFolder)

    def playVideo(self, channel, details):

        # Access the video playlist
        objPL=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        objPL.clear()
        
        # For each video detail in the array, we create a listitem and add it to the playlist
        for video in details:
            liz=xbmcgui.ListItem(video['Title'],
                                iconImage = self.main.args.icon,
                                thumbnailImage = self.main.args.icon)
            liz.setInfo( type = "Video", infoLabels=video)

            # Now that we're actually playing the video, ask the scraper to give us the video url
            url=Channels().referenceURL(channel, video['url']);
            objPL.add(url, liz)

        # Play the Playlist        
        xbmc.Player( xbmc.PLAYER_CORE_DVDPLAYER ).play(objPL)

    def playRadio(self, name, url):
        # Access the music playlist
        objPL=xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        objPL.clear()
        
        liz=xbmcgui.ListItem(name,
                            iconImage = self.main.args.icon,
                            thumbnailImage = self.main.args.icon)
        objPL.add(url, liz)

        # Play the Playlist        
        xbmc.Player( xbmc.PLAYER_CORE_AUTO ).play(objPL)
    
    def createMenu(self, items, isFolder = True):
        for item in items:
            if not item is None:
                self.addItem(item, isFolder)

        if isFolder:
            self.endofdirectory()
        else:
            self.endofdirectory([xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_NONE])

class Main:

    def __init__(self, checkMode = True):
        self.parseArgs()
        self.getSettings()
        
        # Initialize convenience constants

        self.ADDON_ID = os.path.basename(os.getcwd())
        self.ADDON = xbmcaddon.Addon(id = self.ADDON_ID)
        self.ADDON_DATA_PATH = xbmc.translatePath(self.ADDON.getAddonInfo("Profile"))
        self.FAVORITES_PATH = os.path.join(self.ADDON_DATA_PATH, 'favorites.pickle')
        self.RECENT_PATH = os.path.join(self.ADDON_DATA_PATH, 'recent.pickle')

        # Create addon data path
        if(not os.path.isdir(os.path.dirname(self.ADDON_DATA_PATH))):
            os.makedirs(os.path.dirname(self.ADDON_DATA_PATH))

        if checkMode:
            self.checkMode()

    def addFavorite(self, slug):
        if os.path.exists(self.FAVORITES_PATH):
            favorites = pickle.load(open(self.FAVORITES_PATH, 'rb'))
        else:
            favorites = list()
    
        if not favorites.count(slug):
            favorites.append(slug)
        pickle.dump(favorites, open(self.FAVORITES_PATH, 'wb'))
    
        xbmcgui.Dialog().ok('Favorite program series', 'Program series added')
    
    def delFavorite(self, slug):
        if os.path.exists(self.FAVORITES_PATH):
            favorites = pickle.load(open(self.FAVORITES_PATH, 'rb'))
            favorites.remove(slug)
            pickle.dump(favorites, open(self.FAVORITES_PATH, 'wb'))
    
        xbmcgui.Dialog().ok('Favorite program series', 'Program series removed')
    
    def updateRecentlyWatched(self, slug):
        if os.path.exists(self.RECENT_PATH):
            recent = pickle.load(open(self.RECENT_PATH, 'rb'))
        else:
            recent = list()
    
        if recent.count(slug):
            recent.remove(slug)
        recent.insert(0, slug)
    
        recent = recent[0:10] # Limit to ten items
        pickle.dump(recent, open(self.RECENT_PATH, 'wb'))

    def parseArgs(self):
        # call updateArgs() with our formatted argv to create the self.args object
        if (sys.argv[2]):
            exec "self.args = updateArgs(%s')" % (sys.argv[2][1:].replace('&', "',").replace('=', "='"))
        else:
            # updateArgs will turn the 'None' into None.
            # Don't simply define it as None because unquote_plus in updateArgs will throw an exception.
            # This is a pretty ugly solution, but fuck it :(
            self.args = updateArgs(mode = 'None', url = 'None', name = 'None')

    def getSettings(self):
        self.settings = dict()
        # Boolean allowing to enable or disable showing of the ads.        
        self.settings['include_ads'] = __settings__.getSetting('ads')

    def checkMode(self):
        mode = self.args.mode
        if mode is None:
            UI().createMenu(Channels().getChannels())

        elif mode == MenuConstants.MODE_PLAYVIDEO:
            video = Channels().getVideoDetails(self.args.channel, self.args.url, (self.settings['include_ads'] == 'true'))
            UI().playVideo(self.args.channel, video)
            
        elif mode == MenuConstants.MODE_PLAYRADIO:
            UI().playRadio(self.args.name, self.args.url)

        elif mode == MenuConstants.MODE_MAINMENU:
            menus, isFolder = Channels().getMainMenu(self.args.channel)
            UI().createMenu(menus, isFolder)

        elif mode == MenuConstants.MODE_CREATEMENU:
            UI().createMenu(Channels().getMenu(self.args.channel, self.args.url, self.args.name))
            
        elif mode == MenuConstants.MODE_GETEPISODES:
            if not self.args.name.find(' on %s' % (self.args.channel)) > -1:
                self.updateRecentlyWatched({'icon':self.args.icon, 'name':self.args.name, 'url':self.args.url, 'channel':self.args.channel})
            UI().createMenu(Channels().getEpisodes(self.args.channel, self.args.url), False)
        elif mode == 'addfavorite':
            self.addFavorite({'name':self.args.name, 'url':self.args.url, 'channel':self.args.channel, 'icon': self.args.icon})
            
        elif mode == 'delfavorite':
            self.delFavorite({'name':self.args.name.replace(' on ' + self.args.channel, ''), 'url':self.args.url, 'channel':self.args.channel, 'icon': self.args.icon})
            
        elif mode == 'favorites':
            favorites = list()
            if os.path.exists(self.FAVORITES_PATH):
                favorites = pickle.load(open(self.FAVORITES_PATH, 'rb'))
                for favorite in favorites:
                    UI().addItem({'Thumb':favorite['icon'], 'Channel':favorite['channel'], 'Title':urllib.unquote_plus(favorite['name']) + ' on ' + favorite['channel'], 'mode':'GETEPISODES', 'Plot':'', 'url':favorite['url']}, True, False)
                UI().endofdirectory()

        elif mode == 'recentlyWatched':
            recent = list()
            if os.path.exists(self.RECENT_PATH):
                recents = pickle.load(open(self.RECENT_PATH, 'rb'))
                for show in recents:
                    UI().addItem({'Thumb':show['icon'], 'Channel':show['channel'], 'Title':urllib.unquote_plus(show['name']) + ' on ' + show['channel'], 'mode':'GETEPISODES', 'Plot':'', 'url':show['url']}, True, True)
                UI().endofdirectory()
