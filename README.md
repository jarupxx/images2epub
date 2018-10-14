# images2epub.py

Converts a directory of images into a modern EPUB3 ebook. Use a tool to extract CBZ/CBR/CBT files and then run this program to generate a nice fixed-layout EPUB ebook of it. You can optionally set the reading direction to right-to-left (e.g. for manga). For Kobo ereaders, use the file extension .kepub.epub to get the modern reader and correct reading direction.


## Usage

Install dependencies with `pip install imagesize lxml`

```
usage: images2epub.py [-h] [-t TITLE] [-a AUTHOR] [-i STORYID] [-d DIRECTION]
                      [-s SUBJECT] [-l LEVEL] [--pagelist PAGELIST]
                      [--toclist TOCLIST]
                      directory output

positional arguments:
  directory             Path to directory with images
  output                Output EPUB filename

optional arguments:
  -h, --help            show this help message and exit
  -t TITLE, --title TITLE
                        Title of the story
  -a AUTHOR, --author AUTHOR
                        Author of the story
  -i STORYID, --storyid STORYID
                        Story id (default: random)
  -d DIRECTION, --direction DIRECTION
                        Reading direction (ltr or rtl, default: ltr)
  -s SUBJECT, --subject SUBJECT
                        Subject of the story. Can be used multiple times.
  -l LEVEL, --level LEVEL
                        Compression level [0-9] (default: 9)
  --pagelist PAGELIST   Text file with list of images
  --toclist TOCLIST     Text file with table of contents
```

## Example

`./images2epub.py -t "Sailor Moon #1" -a "Naoko Takeuchi" -s "Magical Girl" -s "Manga" -d rtl images/ sailormoon1.epub`


## Advanced usage

You can specify a pagelist. Newlines are ignored:

```
cover.jpg

prologue.jpg

chapter-01-cover.jpg
chapter_01_page_01.jpg
chapter_01_page_02.jpg

chapter_02_intro.jpg
chapter_02_page_01.jpg
...
```

You can specify a table of contents (EPUB metadata). Newlines are ignored:

```
Cover
cover.jpg

Prologue
prologue.jpg

Chapter One
chapter-01-cover.jpg
...
```
