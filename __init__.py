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
import StringIO

###############################################################
#PAGES ZONE: handling pages, the essential part of repository
###############################################################

def get_hussies_page(pagenum):
    """Gets a specified page from mspaintadventures.com by specified pagenumber and normalizes Andrew Hussie's EOLs. Returns a string with clean page text, that can be fed to parse_page()"""
    hussieresponse = urllib.urlopen("http://www.mspaintadventures.com/6/" + pagenum + ".txt")
    readhussie = hussieresponse.read()
    if readhussie.find("404 Not Found") == -1:
        return "\n".join(readhussie.splitlines())
    else:
        raise IOError("MS Paint Adventures webdite appears not to have this page.")
        return

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
        

def get_trans_page(pagenum, root = os.curdir):
    """Gets the Translated page by specified pagenumber. Returns a string with page text, that can be fed to parse_page()"""
    return get_trans_page_from_path(locate_trans_page(pagenum, root))

def get_parsed_hussies_page(pagenum):
    """Gets a specified page from mspaintadventures.com by specified pagenumber, normalizes Andrew Hussie's EOLs and feeds it to the parse_page(). Returns a list. For description of the contained data, see parse_page()."""
    return parse_page(get_hussies_page(pagenum))

def get_parsed_trans_page(pagenum, root = os.curdir):
    """Gets the Translated page from path specified in the argument and feeds it to the parse_page(). Returns a list. For description of the contained data, see parse_page()."""
    return parse_page(get_trans_page(pagenum, root))

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
            element = special_link_to_ordinary(element)
            newlinks.append(element.split('/')[-1])
        parsedlist[3] = "\n".join(newlinks)
    return "\n###\n".join(parsedlist)

###############################################################
#LITTLE TWEAKS ZONE: small things that are nice to have
###############################################################

def special_link_to_ordinary(link):
    """Converts a special link for animated/interactive content (like the ones starting with F| for .swf files) to an ordinary link pointing to an actual file. A small utility that is nice to have"""
    if link[:2] == "F|":
        link = link[2:] + "/" + link[2:].split("/")[-1] + ".swf" # Ugh, this thing is ugly as fsck. But I guess, it works. I was too lazy for urlsplit, may be later.
    return link

def act_to_rel_path(act):
    """Converts the name of act given as an argument to path relative to repository root. For example 'Act6 Act6' will result in 'Act6/Act6'"""
    actlist = act.split(" ")
    return os.sep.join(actlist)
###############################################################
#IMAGES ZONE: handling images
###############################################################
def get_hussies_images(pagenumber):
    """Gets visual content for specified page from mspaintadventures.com by specified pagenumber. Returns list of file-like objects, that can be read."""
    linksstring = get_parsed_hussies_page(pagenumber)[3]
    links = linksstring.split("\n")
    hussiesimages = []
    for link in links:
        hussiesimage = urllib.urlopen(special_link_to_ordinary(link))
        hussiesimages.append(hussiesimage)
    return hussiesimages

def locate_trans_images(pagenumber, root = os.curdir):
    """Locates absolute paths to visual content for specified page. Takes full page number, returns list of paths."""
    filenamesstring = get_parsed_trans_page(pagenumber, root)[3]
    filenames = filenamesstring.split("\n")
    paths = []
    for pattern in filenames:
        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                paths.append(os.path.join(path, filename))
    return paths

def get_trans_images_from_paths(paths):
    """Gets the visual content for Translated page from list of paths specified in the argument. Returns list file objets with images open."""
    transimages = []    
    for path in paths:
        transimage = open(path)
        transimages.append(transimage)
    return transimages

def get_trans_images(pagenumber, root = os.curdir):
    """Gets the visual content for Translated page by specified pagenumber. Returns list file objets with images open."""
    return get_trans_images_from_paths(locate_trans_images(pagenumber, root))

###############################################################
#DANGER ZONE: this thing writes to real files. Handle with care
###############################################################

def write_page(pagenumber, page, root = os.curdir):
    """Writes the assembled page into the Translated page's file. Takes a page number and a string with page's text. Returns nothing, but writes into file. Also may write to specified repository."""
    pagepath = locate_trans_page(pagenumber, root)
    trans_page = open(pagepath, "w")
    trans_page.write(page)
    trans_page.close()

def create_page(pagenumber, act, page, root = os.curdir):
    """Creates a new page that has a specified pagenumber in the specified act. Recieves an assembeled page as a first argument. Returns nothing, but writes into file. Also may write to specified repository."""
    pagepath = os.sep.join([os.path.expanduser(root), act_to_rel_path(act), pagenumber + ".txt"])
    pagedir = os.path.split(pagepath)[0]
    if not os.path.exists(pagedir):
        os.makedirs(pagedir)
    new_page = open(pagepath, "w+")
    new_page.write(page)
    new_page.close()