#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.02'
__author__ = 'Julien G. (@bfishadow) and Sean F. (@fqx)'

'''
This script will download all artcles from a specific Sina Blog.
Based on these HTML files, you might generate an ebook by importing into Calibre.
Or simply save them anywhere as archives.
'''

import sys
import urllib2
import os


# noinspection PyPep8Naming
def getBetween(str, str1, str2):
    strOutput = str[str.find(str1) + len(str1):str.find(str2)]
    return strOutput


strUsage = "Usage: SBB.py <Sina blog URL> [asc]\n\nExample:\nSBB.py http://blog.sina.com.cn/gongmin desc\nSBB.py http://blog.sina.com.cn/u/1239657051\n"

# Step 0: get target blog homepage URL
try:
    strUserInput = sys.argv[1]
except:
    print strUsage
    sys.exit(0)

try:
    strUserOrder = sys.argv[2]
except:
    strUserOrder = ""

# The URL *must* start with http://blog.sina.com.cn/, otherwise the universe will be destroied XD
if strUserInput.find("http://blog.sina.com.cn/") == -1 or len(strUserInput) <= 24:
    print strUsage
    sys.exit(0)

# Get UID for the blog, UID is critical.
objResponse = urllib2.urlopen(strUserInput)
strResponse = objResponse.read()
objResponse.close()

strUID = getBetween(getBetween(strResponse, "format=html5;", "format=wml;"), "/blog/u/", '">')

if len(strUID) > 10:
    print strUsage
    sys.exit(0)

# Here's the UID. Most of the UID is a string of ten digits.
strTargetUID = strUID


# Step 1: get list for first page and article count
strTargetBlogListURL = "http://blog.sina.com.cn/s/articlelist_" + strTargetUID + "_0_1.html"

objResponse = urllib2.urlopen(strTargetBlogListURL)
strResponse = objResponse.read()
objResponse.close()

strBlogPostList = getBetween(getBetween(strResponse, "$blogArticleSortArticleids", "$blogArticleCategoryids"), " : [",
                             "],")
strBlogPostID = strBlogPostList

strBlogPageCount = getBetween(getBetween(strResponse, "全部博文", "<!--第一列end-->"), "<em>(", ")</em>")
intBlogPostCount = int(strBlogPageCount)  # article count
intPageCount = int(intBlogPostCount / 50) + 1  # page count, default page size is 50

strBlogName = getBetween(getBetween(strResponse, "<title>", "</title>"), "博文_", "_新浪博客")


# Step 2: get list for the rest of pages
for intCurrentPage in range(intPageCount - 1):
    strTargetBlogListURL = "http://blog.sina.com.cn/s/articlelist_" + strTargetUID + "_0_" + str(
        intCurrentPage + 2) + ".html"
    objResponse = urllib2.urlopen(strTargetBlogListURL)
    strResponse = objResponse.read()
    strBlogPostList = getBetween(getBetween(strResponse, "$blogArticleSortArticleids", "$blogArticleCategoryids"),
                                 " : [", "],")
    strBlogPostID = strBlogPostID + "," + strBlogPostList
    objResponse.close()

strBlogPostID = strBlogPostID.replace('"', '')
# strBlogPostID <- this string has all article IDs for current blog


# Step 3: get all articles one by one

arrBlogPost = strBlogPostID.split(',')
if strUserOrder != "desc":
    arrBlogPost.reverse()

intCounter = 0
# strHTML4Index = ""
if not os.path.exists('OEBPS'):
    os.mkdir('OEBPS')

for strCurrentBlogPostID in arrBlogPost:
    intCounter += 1
    strTargetBlogPostURL = "http://blog.sina.com.cn/s/blog_" + strCurrentBlogPostID + ".html"
    objResponse = urllib2.urlopen(strTargetBlogPostURL)
    strPageCode = objResponse.read()
    objResponse.close()

    # Parse blog title
    strBlogPostTitle = getBetween(strPageCode, "<title>", "</title>")
    strBlogPostTitle = strBlogPostTitle.replace("_新浪博客", "")
    strBlogPostTitle = strBlogPostTitle.replace("_" + strBlogName, "")

    # Parse blog post
    strBlogPostBody = getBetween(strPageCode, "<!-- 正文开始 -->", "<!-- 正文结束 -->")
    strBlogPostBody = strBlogPostBody.replace("http://simg.sinajs.cn/blog7style/images/common/sg_trans.gif", "")
    strBlogPostBody = strBlogPostBody.replace('src=""', "")
    strBlogPostBody = strBlogPostBody.replace("real_src =", "src =")

    # Parse blog timestamp
    strBlogPostTime = getBetween(strPageCode, '<span class="time SG_txtc">(', ')</span><div class="turnBoxzz">')

    # Write into local file
    strLocalFilename = "/OEBPS/Post_" + str(intCounter).zfill(5) + "_" + strCurrentBlogPostID + ".html"
    objLocalFile = os.getcwd() + strLocalFilename
    strHTML4Post = ('<!DOCTYPE html\n'
                    'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
                    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
                    '<html xmlns="http://www.w3.org/1999/xhtml" lang="zh" xml:lang="zh">\n'
                    '    <head>\n'
                    '    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                    '    <title>'
                    ) + strBlogPostTitle + '</title><style type="text/css">body{font-family: arial, sans-serif;}</style></head><body><h2>' + strBlogPostTitle + (
                       '</h2><p>By: <em>') + strBlogName + '</em> 原文发布于：<em>' + strBlogPostTime + '</em></p>' + strBlogPostBody + '</body></html>'
    objFileArticle = open(objLocalFile, "w")
    objFileArticle.write(strHTML4Post)
    objFileArticle.close()

    # strHTML4Index = strHTML4Index + '<li><a href="' + strLocalFilename + '">' + strBlogPostTitle + '</a></li>\n'

    print intCounter, "/", intBlogPostCount

# strCurrentTimestamp = str(strftime("%Y-%m-%d %H:%M:%S"))
# strHTML4Index = "<html>\n<head>\n<meta http-equiv=""Content-Type"" content=""text/html; charset=utf-8"" />\n<title>" + strBlogName + "博客文章汇总</title>\n</head>\n<body>\n<h2>新浪博客：" + strBlogName + "</h2>\n<p>共" + str(
#     intBlogPostCount) + "篇文章，最后更新：<em>" + strCurrentTimestamp + "</em></p>\n<ol>\n" + strHTML4Index + "\n</ol>\n</body>\n</html>"
# objFileIndex = open("index.html", "w")
# objFileIndex.write(strHTML4Index);
# objFileIndex.close()

# Generate OPF file
import mimetypes
import glob
import os
import os.path

# Initialize the mimetypes database
mimetypes.init()
# Create the package.opf file
package = open('OEBPS/package.opf', 'w')

# The glob below should encompass everything under
# OEBPS but I'm not certain how it'll work
package_content = glob.glob('OEBPS/*.html')
# package_content += glob.glob('OEBPS/*/*')
# package_content += glob.glob('OEBPS/*/*/*')

template_top1 = '''<package xmlns="http://www.idpf.org/2007/opf"
  unique-identifier="book-id"
  version="3.0" xml:lang="zh">
  <metadata >
  '''
# <!-- TITLE -->
template_title = '<dc:title>' + strBlogName + '</dc:title>'
template_top2 = '''    <!-- AUTHOR, PUBLISHER AND PUBLICATION DATES-->
    <dc:creator></dc:creator>
    <dc:publisher></dc:publisher>
     <dc:date></dc:date>
     <meta property="dcterms:modified"></meta>
     <!-- MISC INFORMATION -->
      <dc:language>zh</dc:language>
      <dc:identifier id="book-id"></dc:identifier>
      <meta name="cover" content="img-cov" />
  <manifest>
  '''
template_transition = '''</manifest>
  <spine toc="ncx">'''

template_bottom = '''</spine>
</package>'''

manifest = ""
spine = ""

# Write each HTML file to the ebook, collect information for the index
for i, item in enumerate(package_content):
    basename = os.path.basename(item)
    mime = mimetypes.guess_type(item, strict=True)
    manifest += '\t<item id="file_%s" href="%s" media-type="%s"/>\n' % (i + 1, basename, mime[0])
    spine += '\n\t<itemref idref="file_%s" />' % (i + 1)

# I don't remember my python all that well to remember
# how to print the interpolated content.
# This should do for now.
package.write(template_top1)
package.write(template_title)
package.write(template_top2)
package.write(manifest)
package.write(template_transition)
package.write(spine)
package.write(template_bottom)
package.close()
