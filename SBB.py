#!/usr/bin/env python
# -*- coding: utf-8 -*-


__version__ = '0.03'
__author__ = 'Julien G. (@bfishadow) and Sean F. (@fqx)'

'''
This script will download all artcles from a specific Sina Blog.
Based on these HTML files, you might generate an ebook by importing into Calibre.
Or simply save them anywhere as archives.
'''

import sys
import urllib2
import mimetypes
import os
import os.path
from time import strftime

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
strTOC = ""
strHTML4Index = ""
if not os.path.exists('OEBPS'):
    os.mkdir('OEBPS')




# Initialize the mimetypes database
mimetypes.init()

manifest = ""
spine = ""

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
    strLocalFilename = "Post_" + str(intCounter) + "_" + strCurrentBlogPostID + ".html"
    objLocalFile = os.getcwd() + "/OEBPS/" + strLocalFilename
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
    mime = mimetypes.guess_type(objLocalFile, strict=True)
    manifest += '\t<item id = "file_%s" href="%s" media-type="%s"/>\n' % (intCounter, strLocalFilename, mime[0])
    spine += '\n\t<itemref idref="file_%s" />' % (intCounter)

    strTOC += '''<navPoint class="chapter " id="{0:s}" playorder="{1:s}">
<navLabel>
<text>{2:s}</text>
</navLabel>
<content src="{3:s}"/>
</navPoint>'''.format(str(intCounter), str(intCounter + 1), strBlogPostTitle, strLocalFilename)
    strHTML4Index = strHTML4Index + '<li><a href="' + strLocalFilename + '">' + strBlogPostTitle + '</a></li>\n'

    print intCounter, "/", intBlogPostCount

strCurrentTimestamp = str(strftime("%Y-%m-%d %H:%M:%S"))
strHTML4Index = ('<!DOCTYPE html\n'
                 'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
                 '<html xmlns="http://www.w3.org/1999/xhtml" lang="zh" xml:lang="zh">\n'
                 '    <head>\n'
                 '    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                 '    <title>'
                 ) + strBlogName + "博客文章汇总</title>\n</head>\n<body>\n<h2>新浪博客：" + strBlogName + "</h2>\n<p>共" + str(
    intBlogPostCount) + "篇文章，最后更新：<em>" + strCurrentTimestamp + "</em></p>\n<ol>\n" + strHTML4Index + "\n</ol>\n</body>\n</html>"
objFileIndex = open("OEBPS/index.html", "w")
objFileIndex.write(strHTML4Index)
objFileIndex.close()

# build opf
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
<guide>
<reference type="toc" title="Table of Contents" href="index.html"></reference>
</guide>
</package>'''
# Create the package.opf file
package = open('OEBPS/package.opf', 'w')

package.write(template_top1)
package.write(template_title)
package.write(template_top2)
package.write(manifest)
package.write('''<item id="toc" media-type="application/x-dtbncx+xml" href="toc.ncx"/>
<item id="index" media-type="text/html" href="index.html"/>''')
package.write(template_transition)
package.write(spine)
package.write('''<itemref idref="toc"/>
<itemref idref="index"/>''')
package.write(template_bottom)
package.close()

# build TOC
strTOC = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<!--
For a detailed description of NCX usage please refer to:
http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.4.1
-->

<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="zh-CN">
<head>
<meta name="dtb:uid" content=""/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<navMap>
<navPoint class="toc" id="toc" playOrder="1">
<navLabel>
<text>Table of Contents</text>
</navLabel>
<content src="index.html"/>
</navPoint>''' + strTOC + '''</navmap>
</ncx>'''
objTOC = open("OEBPS/toc.ncx", "w")
objTOC.write(strTOC)
objTOC.close()
