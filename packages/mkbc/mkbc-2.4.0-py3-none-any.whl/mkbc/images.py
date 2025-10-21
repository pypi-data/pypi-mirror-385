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

import os
import sys
import httplib2
from urllib.parse import urljoin
import tempfile
import cairosvg
from PIL import Image
from io import BytesIO
from base64 import b64decode
import re
from pathlib import Path

CACHE_DIR = "images"
USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'QtWebEngine/5.15.4 Chrome/87.0.4280.144 Safari/537.36')


class ImageCache(dict):
    """(url, src): path.
    """
    def __init__(self, http: httplib2.Http = None, tmp: str = "/tmp"):
        if http is None:
            # self.http = httplib2.Http(tmp)
            self.http = httplib2.Http(
                CACHE_DIR, disable_ssl_certificate_validation=True)
        else:
            self.http = http

        self.tmp = tmp

    def __missing__(self, key: tuple[str, str]) -> str:
        url, src = key

        if src.startswith("data:image"):
            match = re.search(r"data:image/(.*?);base64,(.*)", src)
            if not match:
                print(src)
                return ""
            suff, data = match.groups()
            fd, name = tempfile.mkstemp(suffix='.' + suff, dir=self.tmp)
            try:
                decoded = b64decode(data)
            except Exception:
                print(data)
                return ""
            with open(name, 'wb') as f:
                f.write(decoded)

        else:
            try:
                response, content = self.http.request(urljoin(*key), headers={
                    "Referer": url,
                    'user-agent': USER_AGENT,
                })
            except Exception as ex:
                print(ex)
                return ""

            basename = os.path.basename(src)
            base, ext = os.path.splitext(basename)
            # fd, name = tempfile.mkstemp(suffix=base + ".png", dir=self.tmp)
            fd, name = tempfile.mkstemp(suffix=".png", dir=self.tmp)

            if ext in {".svg", ".svgz"}:
                cairosvg.svg2png(bytestring=content, write_to=name)
            else:
                try:
                    img = Image.open(BytesIO(content))
                    img = img.convert('RGBA')
                    img.save(name)
                except Exception:
                    print("img content err: {}".format(key))
                    return src

        self[key] = name
        return os.path.relpath(name, '.')


sys.modules[__name__] = ImageCache(tmp=CACHE_DIR)
