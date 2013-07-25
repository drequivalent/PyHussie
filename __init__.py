#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  Homestuck Russian Translation Project
#  <xmpp:homestuck@conference.jabber.ru>
#  dr.Equivalent the Incredible <doctor@equivalent.me>

import urllib
import os.path
import os
import fnmatch

def get_hussies_page(pagenum):
    """Gets a specified page from mspaintadventures.com by specified pagenumber and normalizes Andrew Hussie's EOLs. Returns a string with clean page text, that can be fed to parse_page()"""
    hussieresponse = urllib.urlopen("http://www.mspaintadventures.com/6/" + pagenum + ".txt")
    readhussie = hussieresponse.read()
    return "\n".join(readhussie.splitlines())

def parse_page(text):
    """Parses the page, no matter Andrew Hussie's or Translated. Returns a list, containing the following:
    0. The Caption
    1. Some weird hash
    2. The time this page is created
    3. Links to the visual/interactive content
    4. The text content
    5. The link (links) to the next page (pages)
    It takes a string with page's text as an argument."""
    reslist = text.split("\n###\n")
    dirty = reslist[5]
    reslist[5] = dirty.strip("\nX")
    return reslist

def locate_trans_page(pagenumber, root = os.curdir):
    """Locates an absolute path to the specified page. Takes the full page number, returns the path as a string."""
    pattern = pagenumber + ".txt"    
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            return os.path.join(path, filename)

def get_trans_page_from_path(path):
    """Gets the Translated page from path specified in the argument. Returns a string with the page text, that can be fed to parse_page()."""
    trans_page = open(path)
    return trans_page.read()
        

def get_trans_page(pagenum):
    """Gets the Translated page by specified pagenumber. Returns a string with page text, that can be fed to parse_page()"""
    return get_trans_page_from_path(locate_trans_page(pagenum))

def get_parsed_hussies_page(pagenum):
    """Gets a specified page from mspaintadventures.com by specified pagenumber, normalizes Andrew Hussie's EOLs and feeds it to the parse_page(). Returns a list. For description of the contained data, see parse_page()."""
    return parse_page(get_hussies_page(pagenum))

def get_parsed_trans_page(pagenum):
    """Gets the Translated page from path specified in the argument and feeds it to the parse_page(). Returns a list. For description of the contained data, see parse_page()."""
    return parse_page(get_trans_page(pagenum))

def assemble_page(parsedlist, markx = True, onlyfilenames = True):
    """Assembles the page from the list given as the argument. Returns a string with page text. Optionally, it can be told not to append the Newline and X symbol. This option is reserved for future use. It also reduces the links in Hussie's page to filenames by default."""
    if markx == True:
        if parsedlist[5] != "":
            parsedlist[5] = parsedlist[5] + "\nX"
        else:
            parsedlist[5] = parsedlist[5] + "X"
    if onlyfilenames == True:
        links = parsedlist[3].split("\n")
        newlinks = []        
        for element in links:
            if element[:2] == "F|":
                element = element[2:] + ".swf"
            newlinks.append(element.split('/')[-1])
        parsedlist[3] = "\n".join(newlinks)
    return "\n###\n".join(parsedlist)

###############################################################
#DANGER ZONE: this thing writes to real files. Handle with care
###############################################################

def write_page(pagenumber, page):
    """Writes the assembled page into the Translated page's file. Takes a page number and a string with page's text. Returns nothing, but writes into file."""
    trans_page = open(locate_trans_page(pagenumber), "w")
    trans_page.write(page)
    trans_page.close()