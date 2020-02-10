FROM python:3

RUN apt-get update && \
  apt-get -y install libxml2-dev libxslt-dev python-dev && \
  pip install lxml imagesize

WORKDIR /opt/

COPY . /opt

CMD ./images2epub.py -t "Sailor Moon #1" -a "Naoko Takeuchi" -s "Magical Girl" -s "Manga" -d rtl images/ sailormoon1.epub