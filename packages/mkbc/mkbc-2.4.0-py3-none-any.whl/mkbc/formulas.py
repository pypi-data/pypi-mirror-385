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
import subprocess
import tempfile

CACHE_DIR = "/tmp/mkbc/formulas"
# TEXFILE = os.path.join(os.path.dirname(__file__), "main.tex")
TEXFILE = "/usr/share/mkbc/latex/main.tex"
FORMULAFILE = "/tmp/mkbc/formula.tex"
DVIFILE = "/tmp/mkbc/main.dvi"


class FormulaCache(dict):
    def __init__(self, cache: str = "/tmp"):
        os.makedirs(cache, exist_ok=True)
        self.cache = cache

    def __missing__(self, formula: str) -> str:
        suff = ".png"
        fd, png = tempfile.mkstemp(suffix=suff, dir=self.cache)

        with open(FORMULAFILE, mode="w") as f:
            f.write(formula)

        try:
            os.remove(DVIFILE)
        except FileNotFoundError:
            pass

        subprocess.call([
            "latex", "-interaction=nonstopmode", "-output-directory=/tmp/mkbc",
            TEXFILE], stdout=subprocess.DEVNULL)

        if not os.path.exists(DVIFILE):
            print("Could not typeset formula: " + formula)
            return None

        subprocess.check_call([
            "dvipng", "-Ttight", "-D300", "-bgTransparent", "-o" + png,
            DVIFILE], stdout=subprocess.DEVNULL)

        self[formula] = png
        return png


sys.modules[__name__] = FormulaCache(cache=CACHE_DIR)
