#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
import MenuConstants

# Channel Constants
CHANNEL = 'Irish Radios'
LOGOICON = 'http://www.rte.ie/radio/images/logo.gif'

RADIOS = [
          {'id': 'rte_radio_1',
           'name': 'RTE Radio 1',
           'logo': 'http://www.rte.ie/radio/images/logo_radio1.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/radio1.asx'},
          {'id': 'rte_radio_1_extra',
           'name': 'RTE Radio 1 Extra',
           'logo': 'http://www.rte.ie/radio/images/logo_extra.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/radio1extra.asx'},
          {'id': 'rte_2fm',
           'name': 'RTE 2FM',
           'logo': 'http://www.rte.ie/radio/images/logo_2fm.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/2fm.asx'},
          {'id': 'rte_radio_1',
           'name': 'RTE Lyric FM',
           'logo': 'http://www.rte.ie/radio/images/logo_lyric.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/lyric.asx'},
          {'id': 'rte_radio_rnag',
           'name': 'RTE Radio na Gaeltachta',
           'logo': 'http://www.rte.ie/radio/images/logo_rnag.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/rnag.asx'},
          {'id': 'rte_2xm',
           'name': 'RTE 2XM',
           'logo': 'http://www.rte.ie/radio/images/logo_2xm.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/0304.asx'},
          {'id': 'rte_choice',
           'name': 'RTE Choice',
           'logo': 'http://www.rte.ie/radio/images/logo_choice.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/0910.asx'},
          {'id': 'rte_junior',
           'name': 'RTE Junior',
           'logo': 'http://www.rte.ie/radio/images/logo_junior.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/0708.asx'},
          {'id': 'rte_gold',
           'name': 'RTE Gold',
           'logo': 'http://www.rte.ie/radio/images/logo_gold.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/0102.asx'},
          {'id': 'rte_pulse',
           'name': 'RTE Pulse',
           'logo': 'http://www.rte.ie/radio/images/logo_pulse.gif',
           'stream': 'http://dynamic.rte.ie/av/live/radio/1112.asx'},
          {'id': 'q102',
           'name': "Dublin's Q102",
           'logo': 'http://www.q102.ie/Images/Listen/Q102_logo_listenlive.jpg',
           'stream': 'http://q102-128.media.vistatec.ie/listen.pls'},
          {'id': 'fm104',
           'name': "FM104 Dublin's Hit Music Station",
           'logo': 'http://www.fm104.ie/Images/Layout/fm104_logo.png',
           'stream': 'http://fm104-128.media.vistatec.ie/listen.pls'},
          {'id': 'spin1038',
           'name': "Spin 103.8",
           'logo': 'http://spin1038.com/wp-content/themes/spin1038/assets/img/logos/spin.png',
           'url': 'http://media.spin1038.com/get_settings.php',
           'stream': 'http://208.72.155.250:8413/listen.pls'},
          {'id': '98fm',
           'name': "Dublin's 98FM",
           'logo': 'http://98fm.s3.amazonaws.com/wp-content/themes/98fm/assets/img/logos/98fm_logo.png',
           'url': 'http://media.98fm.com/get_settings.php',
           'stream': 'http://208.72.155.250:8000/listen.pls'},
          {'id': 'newstalk',
           'name': "Newstalk Live From Ireland",
           'logo': 'http://www.newstalk.ie/wp-content/themes/newstalk/assets/img/logo.gif',
           'url': 'http://media.newstalk.ie/get_settings.php',
           'stream': 'http://208.72.155.18:8080/listen.pls'},
     ]


class RTERadio:

    def getChannelDetail(self):
        return {'Channel'  : CHANNEL,
                'Thumb'    : LOGOICON,
                'Title'    : CHANNEL,
                'mode'     : MenuConstants.MODE_MAINMENU,
                'Plot'     : CHANNEL
                }

    def getMainMenu(self):
        for radio in RADIOS:
            yield {'Channel' : CHANNEL,
                   'Thumb'   : radio['logo'],
                   'url'     : radio['stream'],
                   'Title'   : radio['name'],
                   'mode'    : MenuConstants.MODE_PLAYRADIO}
