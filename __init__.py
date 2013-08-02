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
        raise IOError("MS Paint Adventures website appears not to have this page.")
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
    for path, dirs, files in os.walk(os.path.abspath(os.path.expanduser(root))):
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
#LITTLE TWEAKS ZONE: small utilities that are nice to have
###############################################################

def list_all_pages(root = os.curdir):
    """Returns the list of all pages present in the repository, plus their acts"""
    pages = []
    pattern = "[0-9][0-9][0-9][0-9][0-9][0-9].txt" #Fsck it. Just fsck it.
    for path, dirs, files in os.walk(os.path.abspath(os.path.expanduser(root))):
        for filename in fnmatch.filter(files, pattern):
            pages.append([filename.strip(".txt"), path_to_act(path, root)])
    return sorted(pages)

def get_latest_pagenumber(root = os.curdir):
    """Gets the latest pagenumber and act in the repository. Convinitent for updating."""
    return list_all_pages(root)[-1]

def special_link_to_ordinary(link):
    """Converts a special link for animated/interactive content (like the ones starting with F| for .swf files) to an ordinary link pointing to an actual file. A small utility that is nice to have"""
    if link[:2] == "F|":
        link = link[2:] + "/" + link[2:].split("/")[-1] + ".swf" # Ugh, this thing is ugly as fsck. But I guess, it works. I was too lazy for urlsplit, may be later.
    return link

def act_to_rel_path(act):
    """Converts the name of act given as an argument to path relative to repository root. For example 'Act6 Act6' will result in 'Act6/Act6'"""
    return os.sep.join(act.split(" "))

def act_to_abs_path(act, root = os.curdir):
    """Converts the name of act given as an argument to an absolute path of the directory in the filesystem."""
    return os.sep.join([os.path.expanduser(root), act_to_rel_path(act)])

def act_to_img_path(act, root = os.curdir, imgdirname = "img"):
    """Converts the name of act given as an argument to an absolute path to the visual/interactive content of the act."""
    return os.sep.join([act_to_abs_path(act, root), imgdirname])

def check_act(act, root = os.curdir, imgdirname = "img"):
    """Checks if the specified act (and corresponding images directory) exists in the repository. Returns True if it does.""" 
    if os.path.exists(act_to_abs_path(act, root)):
        if os.path.exists(act_to_img_path(act, root, imgdirname)):
            return True
        else:
            return False
    else:
        return False

def path_to_act(path, root = os.curdir):
    act = " ".join(path.strip(os.path.abspath(os.path.expanduser(root))).split("/"))
    return act

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
        for path, dirs, files in os.walk(os.path.abspath(os.path.expanduser(root))):
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
    """Gets the visual content for Translated page by specified pagenumber. Returns list of file objets with images open."""
    return get_trans_images_from_paths(locate_trans_images(pagenumber, root))

###############################################################
#DANGER ZONE: this thing writes to real files. Handle with care
###############################################################

def write_image(image, act, root = os.curdir, imgdirname = "img"):
    """Writes the image given in the first argument into the specified act. Returns nothing, but writes into files."""
    filename = image.geturl().split("/")[-1]
    abspath = os.sep.join([act_to_img_path(act, root, imgdirname), filename])
    imgfile = open(abspath, "w")
    imgfile.write(image.read())
    imgfile.close

def create_image(image, act, root = os.curdir, imgdirname = "img"):
    """Creates the images from the given list in the specified act."""
    filename = image.geturl().split("/")[-1]
    if not check_act(act, root):
        create_act(act, root)
    abspath = os.sep.join([act_to_img_path(act, root, imgdirname), filename])
    imgfile = open(abspath, "w+")
    imgfile.write(image.read())
    imgfile.close

def write_page(pagenumber, page, root = os.curdir):
    """Writes the assembled page into the Translated page's file. Takes a page number and a string with page's text. Returns nothing, but writes into file. Also may write to specified repository."""
    pagepath = locate_trans_page(pagenumber, root)
    trans_page = open(pagepath, "w")
    trans_page.write(page)
    trans_page.close()

def create_page(pagenumber, act, page, root = os.curdir):
    """Creates a new page that has a specified pagenumber in the specified act. Recieves an assembeled page as a first argument. Returns nothing, but writes into file. Also may write to specified repository."""
    pagepath = os.sep.join([act_to_abs_path(act, root), pagenumber + ".txt"])
    if not check_act(act):
        create_act(act, root)
    new_page = open(pagepath, "w+")
    new_page.write(page)
    new_page.close()

def create_act(act, root = os.curdir, imgdirname = "img"):
    """Creates the sprcified act in the repository. Takes a string with an act name (like Act6 Act6). Returns nothing, but creates a directory."""
    abspath = act_to_abs_path(act, root)
    absimgpath = act_to_img_path(act, root, imgdirname)
    if not os.path.exists(abspath):
        os.makedirs(abspath)
    if not os.path.exists(absimgpath):
        os.makedirs(absimgpath)

def move_page(pagenumber, act, root = os.curdir, imgdirname = "img"):
    """Moves specified page into specified act. Takes a pagenumber and the name of the act. Creates an act if it's not present."""
    if not check_act(act):
        create_act(act, root)
    pagepath = locate_trans_page(pagenumber, root)
    imgpaths = locate_trans_images(pagenumber, root)
    newactpath = act_to_abs_path(act, root)
    newpagepath = os.sep.join([newactpath, pagenumber + ".txt"])
    for imgpath in imgpaths:
        newimgpath = (os.sep.join([newactpath, imgdirname, imgpath.split(os.sep)[-1]]))
        os.rename(imgpath, newimgpath)
    os.rename(pagepath, newpagepath)

def drop_act(act, root = os.curdir, imgdirname = "img"):
    """Deletes the act from repository, but only if it is empty."""
    os.rmdir(act_to_img_path(act, root, imgdirname))
    os.rmdir(act_to_abs_path(act, root))
