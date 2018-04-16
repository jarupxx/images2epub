# images2epub.py

Converts a directory of images into a modern EPUB3 ebook. Use a tool to extract CBZ/CBR/CBT files and then run this program to generate a nice fixed-layout EPUB ebook of it. You can optionally set the reading direction to right-to-left (e.g. for manga).


## Usage

Install dependencies with `pip install imagesize lxml`

```
usage: images2epub.py [-h] [-t TITLE] [-a AUTHOR] [-i STORYID] [-d DIRECTION]
                      [-s SUBJECT] [-l LEVEL]
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
```

## Example

`./images2epub.py -t "Sailor Moon #1" -a "Naoko Takeuchi" -s "Magical Girl" -s "Manga" -d rtl images/ sailormoon1.epub`
