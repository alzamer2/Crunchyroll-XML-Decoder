﻿"""
Crunchyroll Export Script DX - Last Updated 2014/07/16
Removes need for rtmpExplorer
ORIGINAL SOURCE:
  http://www.darkztar.com/forum/showthread.php?219034-Ripping-videos-amp-subtitles-from-Crunchyroll-%28noob-friendly%29
"""

# -*- coding: utf-8 -*-
# import lxml
import os
import re
import shutil
import subprocess
import sys
import HTMLParser

import altfuncs
from bs4 import BeautifulSoup
from crunchyDec import CrunchyDec
from unidecode import unidecode
# I hate unicode, bring on python 3.3

# ----------

print '''
--------------------------
---- Start New Export ----
--------------------------

CrunchyRoll Downloader Toolkit DX v0.98

Crunchyroll hasn't changed anything.

If you don't have a premium account, go and sign up for one now. It's well worthit, and supports the animators.

----------
'''

# ----------

print 'Booting up...'
lang = altfuncs.config()
# http://www.crunchyroll.com/miss-monochrome-the-animation/episode-2-645085
# http://www.crunchyroll.com/naruto-shippuden/episode-136-the-light-dark-of-the-mangekyo-sharingan-535200
# page_url = 'http://www.crunchyroll.com/media-535200'

try:
    page_url = sys.argv[1]
except IndexError:
    page_url = raw_input('Please enter Crunchyroll video URL:\n')

try:
    seasonnum, epnum = sys.argv[2:4]
except ValueError:
    try:
        epnum = str(int(sys.argv[2]))
        seasonnum = ''
    except IndexError:
        # sys.exit('No season or episode numbers.')
        seasonnum, epnum = '', ''
        pass

# ----------

try:
    int(page_url)
    page_url = 'http://www.crunchyroll.com/media-' + page_url
except ValueError:
    if not page_url.startswith('http://') and not page_url.startswith('https://'):
        page_url = 'http://' + page_url
    try:
        int(page_url[-6:])
    except ValueError:
        if 'proxy' in sys.argv and bool(seasonnum):
            page_url = altfuncs.vidurl(page_url, seasonnum, epnum)
        elif bool(epnum):
            page_url = altfuncs.vidurl(page_url, 1, epnum)
        else:
            page_url = altfuncs.vidurl(page_url, False, False)

subprocess.call('title ' + page_url.replace('http://www.crunchyroll.com/', ''), shell=True)

# ----------

player_revision = altfuncs.playerrev(page_url)
html = altfuncs.gethtml(page_url)

h = HTMLParser.HTMLParser()
title = re.findall('<title>(.+?)</title>', html).pop().replace('Crunchyroll - Watch ', '')
title = h.unescape(unidecode(title)).replace('/', ' - ').replace(':', '-').replace('?', '.').replace('"', '\'').strip()
subprocess.call('title ' + title.replace('&', '^&'), shell=True)

# ----------

media_id = page_url[-6:]
xmlconfig = BeautifulSoup(altfuncs.getxml('RpcApiVideoPlayer_GetStandardConfig', media_id), 'xml')
if '<code>4</code>' in xmlconfig:
    print 'Video not available in your region.'
    sys.exit()
vid_id = xmlconfig.find('media_id').string

# ----------

try:
    host = xmlconfig.find('host').string
except AttributeError:
    print 'Downloading 2 minute preview.'
    media_id = xmlconfig.find('media_id').string
    xmlconfig = BeautifulSoup(altfuncs.getxml('RpcApiVideoEncode_GetStreamInfo', media_id), 'xml')
    host = xmlconfig.find('host').string

if re.search('fplive\.net', host):
    url1 = re.findall('.+/c[0-9]+', host).pop()
    url2 = re.findall('c[0-9]+\?.+', host).pop()
else:
    url1 = re.findall('.+/ondemand/', host).pop()
    url2 = re.findall('ondemand/.+', host).pop()
filen = xmlconfig.find('file').string

# ----------

print 'Downloading video...'
cmd = '.\\video-engine\\rtmpdump -r "' + url1 + '" -a "' \
      + url2 + '" -f "WIN 11,8,800,50" -m 15 -W "http://static.ak.crunchyroll.com/flash/' \
      + player_revision + '/ChromelessPlayerApp.swf" -p "' + page_url + '" -y "' + filen + '" -o "' + title + '.flv"'
error = subprocess.call(cmd)

num = 1
while error != 0 and num < 4:
    if error == 1:
        print '\nVideo failed to download, trying again. (' + str(num) + '/3)'
        error = subprocess.call(cmd)
        num += 1
    if error == 2:
        print '\nVideo download is incomplete, resuming. (' + str(num) + '/3)'
        error = subprocess.call(cmd + ' -e')
        num += 1

if error != 0:
    print '\nVideo failed to download. Writing error...'
    if os.path.exists('error.log'):
        log = open('error.log', 'a')
    else:
        log = open('error.log', 'w')
    log.write(page_url + '\n')
    log.close()
    os.remove('.\\' + title + '.flv"')
    sys.exit()

# ----------

xmllist = unidecode(altfuncs.getxml('RpcApiSubtitle_GetListing', media_id)).replace('><', '>\n<')

if '<media_id>None</media_id>' in xmllist:
    print 'The video has hardcoded subtitles.'
    hardcoded = True
    sub_id = False
else:
    try:
        sub_id = re.findall("id=([0-9]+)' title='.+" + lang.replace('(', '\(').replace(')', '\)') + "'", xmllist).pop()
        hardcoded = False
    except IndexError:
        try:
            sub_id = re.findall("id=([0-9]+)' title='.+English", xmllist).pop()  # default back to English
            print 'Language not found, reverting to English'
            hardcoded = False
        except IndexError:
            print 'The video\'s subtitles cannot be found, or are region-locked.'
            hardcoded = True
            sub_id = False

if not hardcoded:
    xmlsub = altfuncs.getxml('RpcApiSubtitle_GetXml', sub_id)
    formattedSubs = CrunchyDec().returnsubs(xmlsub)
    try:
        subfile = open(title + '.ass', 'wb')
    except IOError:
        title = title.split(' - ', 1)[0]  # episode name too long, splitting after episode number
        subfile = open(title + '.ass', 'wb')
    subfile.write(formattedSubs.encode('utf-8-sig'))
    subfile.close()
    shutil.move(title + '.ass', '.\export\\')
shutil.move(title + '.flv', '.\export\\')

print 'Starting mkv merge'
if hardcoded:
    subprocess.call('"video-engine\mkvmerge.exe" -o ".\export\\' + title + '.mkv" -a 1 ".\export\\' + title + '.flv"')
else:
    subprocess.call('"video-engine\mkvmerge.exe" -o ".\export\\'
                    + title + '.mkv" -a 1 ".\export\\' + title + '.flv" ".\export\\' + title + '.ass"')
print 'Merge process complete'
print
print '----------'
print

print 'Starting Final Cleanup'
for i in ['.flv', '.ass']:
    os.remove('.\export\\' + title + i)
print 'Cleanup Complete'