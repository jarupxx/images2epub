#!/usr/bin/env python3

import sys
from os import listdir, path
from lxml import etree
from html import escape
from uuid import uuid4
import argparse
import datetime
import zipfile
import imagesize

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--title', help='Title of the story', default="Unknown Title")
parser.add_argument('-a', '--author', help='Author of the story', default="Unknown Author")
parser.add_argument('-i', '--storyid', help='Story id (default: random)', default='urn:uuid:' + str(uuid4()))
parser.add_argument('-d', '--direction', help='Reading direction (ltr or rtl, default: ltr)', default='ltr')
parser.add_argument('-s', '--subject', help='Subject of the story. Can be used multiple times.', action='append', default=[])
parser.add_argument('-l', '--level', help='Compression level [0-9] (default: 9)', default=9, type=int)
parser.add_argument('directory', help='Path to directory with images')
parser.add_argument('output', help='Output EPUB filename')
args = parser.parse_args()

if args.direction != 'rtl':
    args.direction = 'ltr'

UID_FORMAT = '{:03d}'
NAMESPACES = {'OPF': 'http://www.idpf.org/2007/opf',
              'DC': 'http://purl.org/dc/elements/1.1/'}

CONTAINER_PATH = 'META-INF/container.xml'
CONTAINER_XML = '''<?xml version='1.0' encoding='utf-8'?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="OEBPS/content.opf"/>
  </rootfiles>
</container>
'''

IBOOKS_DISPLAY_OPTIONS_PATH = 'META-INF/com.apple.ibooks.display-options.xml'
IBOOKS_DISPLAY_OPTIONS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<display_options>
  <platform name="*">
    <option name="fixed-layout">true</option>
    <option name="open-to-spread">false</option>
  </platform>
</display_options>
'''

IMAGESTYLE_CSS = '''
@page {
  padding: 0;
  margin: 0;
}
html,
body {
  padding: 0;
  margin: 0;
  height: 100%;
}
#image {
  width: 100%;
  height: 100%;
  display: block;
  margin: 0;
  padding: 0;
}
'''

IMAGE_TYPES = {
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png'
}

def image2xhtml(imgfile, width, height, title, epubtype = 'bodymatter', lang = 'en'):
    content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}">
<head>
  <meta name="viewport" content="width={width}, height={height}"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="imagestyle.css"/>
</head>

<body epub:type="{epubtype}">
  <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="image" version="1.1" viewBox="0 0 {width} {height}"><image width="{width}" height="{height}" xlink:href="{filename}"/></svg>
</body>
</html>
'''.format(width=width, height=height,
           filename=escape(imgfile), title=escape(title),
           epubtype=epubtype, lang=lang)
    return content

def createOpf(title, author, bookId, imageFiles):
    package_attributes = {'xmlns': NAMESPACES['OPF'],
                          'unique-identifier': 'bookId',
                          'version': '3.0',
                          'prefix': 'rendition: http://www.idpf.org/vocab/rendition/#',
                          'dir': args.direction}
    nsmap = {'dc': NAMESPACES['DC'], 'opf': NAMESPACES['OPF']}

    root = etree.Element('package', package_attributes)

    # metadata
    metadata = etree.SubElement(root, 'metadata', nsmap=nsmap)
    el = etree.SubElement(metadata, 'meta', {'property': 'dcterms:modified'})
    el.text = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    el = etree.SubElement(metadata, '{' + NAMESPACES['DC'] + '}identifier', {'id': 'bookId'})
    el.text = bookId

    el = etree.SubElement(metadata, '{' + NAMESPACES['DC'] + '}title')
    el.text = title

    el = etree.SubElement(metadata, '{' + NAMESPACES['DC'] + '}creator', {'id': 'creator'})
    el.text = author
    el = etree.SubElement(metadata, 'meta', {'refines': '#creator', 'property': 'role', 'scheme': 'marc:relators'})
    el.text = 'aut'

    el = etree.SubElement(metadata, '{' + NAMESPACES['DC'] + '}language')
    el.text = 'en'

    for subject in args.subject:
        el = etree.SubElement(metadata, '{' + NAMESPACES['DC'] + '}subject')
        el.text = subject

    etree.SubElement(metadata, 'meta', {'name': 'cover', 'content': 'img-' + UID_FORMAT.format(0)})

    el = etree.SubElement(metadata, 'meta', {'property': 'rendition:layout'})
    el.text = 'pre-paginated'
    el = etree.SubElement(metadata, 'meta', {'property': 'rendition:orientation'})
    el.text = 'portrait'
    el = etree.SubElement(metadata, 'meta', {'property': 'rendition:spread'})
    el.text = 'landscape'

    width, height = imagesize.get(path.join(args.directory, imageFiles[0]))
    etree.SubElement(metadata, 'meta', {'name': 'original-resolution', 'content': str(width) + 'x' + str(height)})

    # manifest
    manifest = etree.SubElement(root, 'manifest')

    etree.SubElement(manifest, 'item', {
        'href': 'imagestyle.css',
        'id': 'imagestyle',
        'media-type': 'text/css'
    })

    for i, img in enumerate(imageFiles):
        uid = UID_FORMAT.format(i)

        imgattrs = {
            'href': 'images/page-' + uid + path.splitext(img)[1],
            'id': 'img-' + uid,
            'media-type': IMAGE_TYPES[path.splitext(img)[1][1:]],
        }
        if i == 0:
            imgattrs['properties'] = 'cover-image'
        etree.SubElement(manifest, 'item', imgattrs)

        etree.SubElement(manifest, 'item', {
            'href': 'page-' + uid + '.xhtml',
            'id': 'page-' + uid,
            'media-type': 'application/xhtml+xml',
            'properties': 'svg'
        })

    etree.SubElement(manifest, 'item', {
        'href': 'toc.ncx',
        'id': 'ncxtoc',
        'media-type': 'application/x-dtbncx+xml',
    })
    etree.SubElement(manifest, 'item', {
        'href': 'toc.xhtml',
        'id': 'toc',
        'media-type': 'application/xhtml+xml',
        'properties': 'nav'
    })

    # spine
    spine = etree.SubElement(root, 'spine', {
        'toc': 'ncxtoc',
        'page-progression-direction': args.direction
    })

    for i, img in enumerate(imageFiles):
        uid = UID_FORMAT.format(i)
        props = 'page-spread-left'
        if (i % 2 == 0 and args.direction == 'ltr') or (i % 2 != 0 and args.direction == 'rtl'):
            props = 'page-spread-right'
        etree.SubElement(spine, 'itemref', {
            'idref': 'page-' + uid,
            'properties': props
        })

    tree_str = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    return tree_str

def createNcx(title, author, bookId):
    return '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<ncx:ncx xmlns:ncx="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <ncx:head>
    <ncx:meta name="dtb:uid" content="{bookId}"/>
    <ncx:meta name="dtb:depth" content="1"/>
    <ncx:meta name="dtb:totalPageCount" content="0"/>
    <ncx:meta name="dtb:maxPageNumber" content="0"/>
  </ncx:head>
  <ncx:docTitle>
    <ncx:text>{title}</ncx:text>
  </ncx:docTitle>
  <ncx:docAuthor>
    <ncx:text>{author}</ncx:text>
  </ncx:docAuthor>
  <ncx:navMap>
    <ncx:navPoint id="p1" playOrder="1">
      <ncx:navLabel><ncx:text>{title}</ncx:text></ncx:navLabel>
      <ncx:content src="page-000.xhtml"/>
    </ncx:navPoint>
  </ncx:navMap>
</ncx:ncx>
'''.format(title=escape(title), author=escape(author), bookId=bookId)

def createNav(title, pageCount):
    pages = [None] * pageCount
    for i, page in enumerate(pages):
        uid = UID_FORMAT.format(i)
        pages[i] = '          <li><a href="page-{uid}.xhtml">{pageNumber}</a></li>'.format(uid=uid, pageNumber=i)
    pages.pop(0)

    return '''<?xml version="1.0" encoding="utf-8"?>
<?xml-model href="http://www.idpf.org/epub/30/schema/epub-nav-30.rnc" type="application/relax-ng-compact-syntax"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
  <head>
    <title>{title}</title>
  </head>
  <body>
    <section class="frontmatter" epub:type="frontmatter toc">
      <h1>Table of Contents</h1>
      <nav epub:type="toc" id="toc">
        <ol>
          <li epub:type="chapter"><a href="page-000.xhtml">{title}</a></li>
        </ol>
      </nav>
      <nav epub:type="page-list">
        <ol>
{pages}
        </ol>
      </nav>
    </section>
  </body>
</html>'''.format(pages='\n'.join(pages), title=escape(title))

imageFiles = sorted([f for f in listdir(args.directory) if path.isfile(path.join(args.directory, f))])

imageFiles = list(filter(lambda img: path.splitext(img)[1][1:] in IMAGE_TYPES, imageFiles))

if len(imageFiles) < 1:
    print('Too few images:', len(imageFiles))
    sys.exit(1)

print('Found ' + str(len(imageFiles)) + ' pages.')

prev_compression = zipfile.zlib.Z_DEFAULT_COMPRESSION
zipfile.zlib.Z_DEFAULT_COMPRESSION = args.level

output = zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED)
output.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
output.writestr(CONTAINER_PATH, CONTAINER_XML)
output.writestr(IBOOKS_DISPLAY_OPTIONS_PATH, IBOOKS_DISPLAY_OPTIONS_XML)
output.writestr('OEBPS/content.opf', createOpf(args.title, args.author, args.storyid, imageFiles))
output.writestr('OEBPS/toc.ncx', createNcx(args.title, args.author, args.storyid))
output.writestr('OEBPS/toc.xhtml', createNav(args.title, len(imageFiles)))
output.writestr('OEBPS/imagestyle.css', IMAGESTYLE_CSS)

for i, img in enumerate(imageFiles):
    uid = UID_FORMAT.format(i)
    title = 'Page ' + str(i)
    epubtype = 'bodymatter'
    if i == 0:
        title = 'Cover'
        epubtype = 'cover'
    width, height = imagesize.get(path.join(args.directory, img))
    print(str(round(i/len(imageFiles)*100)) + '%', 'Processing page ' + str(i+1) + ' of ' + str(len(imageFiles)) + ': ' + img, '(' + str(width) + 'x' + str(height) + ')')
    html = image2xhtml('images/page-' + uid + path.splitext(img)[1], width, height, title, epubtype, 'en')
    output.writestr('OEBPS/page-{uid}.xhtml'.format(uid=uid), html)
    output.write(path.join(args.directory, img), 'OEBPS/images/page-' + uid + path.splitext(img)[1])

output.close()
zipfile.zlib.Z_DEFAULT_COMPRESSION = prev_compression

print('Complete! Saved EPUB as ' + args.output)
