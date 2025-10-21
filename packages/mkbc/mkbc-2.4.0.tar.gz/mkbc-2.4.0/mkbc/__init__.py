# Copyright (C) 2016  Pachol, Vojtěch <pacholick@gmail.com>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

"""Make ebook Collection."""
# TODO:
# ~/.webs.json

# dependencies:
# texlive-latex-base, dvipng,
# python3-httplib2, python3-bs4, python3-cairosvg, python3-pil, python3-ebooklib,
# python3-langdetect, python3-qrcode

import os
import sys
import subprocess
import re
import json
import httplib2
from urllib.parse import urlparse
import bs4
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import html
from functools import reduce
import argparse
from ebooklib import epub
from langdetect import detect
from PIL import Image
import io
from pathlib import Path
from base64 import urlsafe_b64encode
import qrcode
from concurrent.futures import ThreadPoolExecutor

from mkbc import images, formulas


WEBS_FILE = os.path.expanduser("~/.webs.json")
if not os.path.isfile(WEBS_FILE):
    with open(WEBS_FILE, 'w') as f:
        f.write(r"{}")
CACHE_DIR = "/tmp/mkbc"
USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'QtWebEngine/5.15.4 Chrome/87.0.4280.144 Safari/537.36')

with open(WEBS_FILE, "r", encoding="utf-8") as f:
    webs = json.load(f)


@dataclass
class Article:
    title: str
    content: str
    media: list = field(default_factory=list)


def _find_content(soup: BeautifulSoup):
    soup.find('article')
    soup.find('div', {'class': 'article'})
    soup.find('h1').parent
    soup.find('h2').parent
    soup.find('h3').parent
    soup.find('font')


def _create_id(x):
    return urlsafe_b64encode(id(x).to_bytes(6, byteorder='big')).decode()


def get_article(url: str, imgs: bool = False, maths: bool = True) -> Article:
    context_element = get_context_element(url)

    h = httplib2.Http(CACHE_DIR, disable_ssl_certificate_validation=True)
    try:
        response, content = h.request(url, headers={'user-agent': USER_AGENT})
    except Exception:
        print(url)
        raise
    soup = BeautifulSoup(content, 'lxml')

    try:
        title = soup.find("title").contents[0]
    except AttributeError:
        print(f"{url} has no title")
        title = "article"

    snip = soup.find(*context_element)
    if snip is None:
        print(context_element)
        raise RuntimeError(url)

    for iframe in snip.find_all('iframe'):
        video_qr(iframe)
    for video in snip.find_all('video'):
        video_qr(video)

    imglist = []
    if imgs:
        for img in snip.find_all("img"):
            img['src'] = images[url, img.get('src', '')]
            imglist.append(img)

    content = str(snip)
    if maths:
        content = html.unescape(content)
        content = replace_maths(content)

    return Article(title, content, imglist)


EQUATION_REGEXES = [re.compile(p) for p in (
    r"(\\begin{equation}.*?\\end{equation})",
    r"(\\begin{equation\*}.*?\\end{equation\*})",
    r"(\\begin{align}.*?\\end{align})",
    r"(\\begin{align\*}.*?\\end{align\*})",
    r"(\\begin{alignat}.*?\\end{alignat})",
    r"(\\begin{alignat\*}.*?\\end{alignat\*})",
    r"(\\begin{gather}.*?\\end{gather})",
    r"(\\begin{gather\*}.*?\\end{gather\*})",
    # r"\$$(.*?)\$$",
)]
INPLACE_REGEXES = [re.compile(p) for p in (
    r"\\\((.*?)\\\)",
    # r"\$(.*?)\$",
    # r"\eq{<br />(.*?)}<br />",
    r"\\\[(.*?)\\\]",
)]

def video_qr(tag: bs4.element.Tag):
    tag_src = tag.get('src')
    if not tag_src:
        tag.decompose()
        return
    qrimg = qrcode.make(tag_src)
    qrimg_path = Path('images') / (_create_id(tag_src) + '.png')
    qrimg.save(qrimg_path)
    tag.name = 'img'
    tag.attrs = {'src': str(qrimg_path), 'alt': 'QR code'}

def replace_maths(text: str) -> str:
    def eq_frepl(matchobj):
        return r"""<img src={} />""".format(formulas[matchobj.group(1)])

    def in_frepl(matchobj):
        return r"""<img src={} />""".format(formulas[
            '$' + matchobj.group(1) + '$'])

    text = re.sub(r"\n\r?", " ", text)
    text = reduce(lambda s, x: re.sub(x, eq_frepl, s), EQUATION_REGEXES, text)
    text = reduce(lambda s, x: re.sub(x, in_frepl, s), INPLACE_REGEXES, text)
    return text


def make_epub(articles: list[Article], name: str = "", titles: bool = True) -> str:
    book = epub.EpubBook()
    book.set_identifier(_create_id(book))
    book.set_title(name)
    book.set_language(detect(articles[0].content))
    book.spine.append('nav')

    for a in articles:
        href = _create_id(a.title) + '.xhtml'
        item = epub.EpubHtml(title=a.title, content=a.content, file_name=href)
        book.add_item(item)

        for img in a.media:
            src = Path(img['src'])
            try:
                pil_image = Image.open(src)
            except Exception as ex:
                print(ex)
                continue
            b = io.BytesIO()
            pil_image.save(b, 'png')
            b_image = b.getvalue()
            image_item = epub.EpubItem(
                uid=src.stem,
                file_name=img['src'],
                media_type='image/png',
                content=b_image
            )
            book.add_item(image_item)

        book.spine.append(item)
        book.toc.append(epub.Link(href, a.title, href))

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    filename = name + '.epub'
    epub.write_epub(filename, book)
    return filename


def get_context_element(url: str) -> tuple[str, dict[str, str]]:
    try:
        context_element = webs[urlparse(url).hostname]
    except KeyError:
        print('URL "%s" not listed in %s file. Using <body> element.' % (
            urlparse(url).hostname, WEBS_FILE))
        context_element = "body", {"": ""}
    return context_element


def main():
    parser = argparse.ArgumentParser(
        prog='mkbc',
        description="Make Kindle Collection.")

    parser.add_argument("name",
                        default="Spam",
                        help="""title of the collection""")

    # parser.add_argument("--images",
    #                     action="store_true", dest="images", default=True,
    #                     help="""include images (default)""")
    parser.add_argument("--noimages",
                        action="store_false", dest="images",
                        help="""do not include images""")

    parser.add_argument("--formulas",
                        action="store_true", dest="formulas", default=False,
                        help="""include formulas""")
    # parser.add_argument("--noformulas",
    #                     action="store_false", dest="formulas",
    #                     help="""do not include formulas (default)""")

    parser.add_argument("--sort",
                        action="store_true",
                        help="""sort articles by title""")

    parser.add_argument("--notitles",
                        action="store_false", dest="titles",
                        help="""show title above each article""")

    args = parser.parse_args()

    urls = sys.stdin.read().splitlines()

    with ThreadPoolExecutor() as executor:
        articles = list(executor.map(
            lambda url: get_article(url, imgs=args.images, maths=args.formulas),
            urls
        ))
    if args.sort:
        articles.sort(key=lambda a: a.title)

    filename = make_epub(articles, name=args.name, titles=args.titles)
    subprocess.run(['kepubify', '--inplace', filename])
    kepub = filename.replace('.epub', '.kepub.epub')
    os.remove(filename)
    os.chmod(kepub, 0o644)
    print(kepub)


def test():
    urls = open('/tmp/aldebaran_2022-1').readlines()
    articles = [get_article(url, imgs=True, maths=False)
                for url in urls]
    filename = make_epub(articles, name='/tmp/aldebaran_2022-1', titles=True)
    subprocess.run(['kepubify', '--inplace', filename])
    kepub = filename.replace('.epub', '.kepub.epub')
    os.chmod(kepub, 0o644)
    print(kepub)


if __name__ == "__main__":
    # sys.exit(main())

    articles = [
        get_article('https://kosmonautix.cz/2025/08/29/pokec-s-kosmonautixem-srpen-2025/',
                    imgs=False, maths=False),
        get_article('https://kosmonautix.cz/2025/08/31/kosmotydenik-676-25-8-31-8/',
                    imgs=False, maths=False),
    ]
    make_epub(articles, name='no-video', titles=True)
