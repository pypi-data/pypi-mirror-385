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

import re
from string import Template as t
from bs4 import BeautifulSoup
import typing

from brackettree import Node, CurlyNode, QuoteNode


NEWCOMMAND_TPL = t("\\newcommand{\\$name}[$num]{$definition}\n")
MACROS_FILE = "/tmp/mkbc/macros.tex"


def write_macros(f: typing.IO, soup: BeautifulSoup):
    r"""
    Currently not working.
    >>> import sys, httplib2, bs4
    >>> url = "https://www.aldebaran.cz/bulletin/2022_09_pri.php"
    >>> response, content = httplib2.Http("/tmp/mkbc").request(url)
    >>> soup = bs4.BeautifulSoup(content, 'lxml')
    >>> write_macros(sys.stdout, soup)
    \newcommand{\dd}[0]{{\rm d}}
    \newcommand{\CC}[0]{{\mathbb C}}
    \newcommand{\RR}[0]{{\mathbb R}}
    \newcommand{\ZZ}[0]{{\mathbb Z}}
    \newcommand{\OO}[0]{{\mathbb O}}
    \newcommand{\O}[0]{{\mathcal O}}
    \newcommand{\HHH}[0]{{\mathbb H}}
    \newcommand{\NN}[0]{{\mathbb N}}
    \newcommand{\NNN}[0]{{\mathcal N}}
    \newcommand{\FF}[0]{{\mathcal F}}
    \newcommand{\HH}[0]{{\mathcal H}}
    \newcommand{\LL}[0]{{\mathcal L}}
    \newcommand{\meV}[0]{{\,\,{\rm meV}}}
    \newcommand{\eV}[0]{{\,\,{\rm eV}}}
    \newcommand{\keV}[0]{{\,\,{\rm keV}}}
    \newcommand{\MeV}[0]{{\,\,{\rm MeV}}}
    \newcommand{\GeV}[0]{{\,\,{\rm GeV}}}
    \newcommand{\TeV}[0]{{\,\,{\rm TeV}}}
    \newcommand{\diag}[0]{{\rm diag}}
    \newcommand{\pfrac}[2]{\frac{\partial #1}{\partial #2}}
    \newcommand{\ddfrac}[2]{\frac{{\rm d} #1}{{\rm d} #2}}
    \newcommand{\bold}[1]{{\bf #1}}
    \newcommand{\zav}[1]{\left({#1}\right)}
    \newcommand{\zzav}[1]{\left[{#1}\right]}
    \newcommand{\eq}[1]{\begin{align} #1 \end{align}}
    \newcommand{\abs}[1]{\left|{#1}\right|}
    \newcommand{\braket}[2]{\langle{#1}|{#2}\rangle}
    \newcommand{\bra}[1]{\langle{#1}|}
    \newcommand{\ket}[1]{{|{#1}\rangle}}
    \newcommand{\iddots}[0]{{\kern3mu\raise1mu{.}\kern3mu\raise6mu{.}\kern3mu\raise12mu{.}}}
    """
    # matjax_cfg = soup.find("script", {"type": "text/x-mathjax-config"})
    m = '\n'.join(i.text for i in soup.findAll(
        "script", {"type": "text/x-mathjax-config"}))

    def gen_defs(macros):
        it = iter(macros.items)
        for i in it:
            match = re.search(r'(\w+):', i)
            name = match.group(1) if match else ""
            try:
                square = next(it)
            except StopIteration:
                return

            # print("name: " + name)
            definition = square.find(QuoteNode > ".*").replace(r'\\', '\\')
            # print("definition: " + str(definition))
            match = re.search(
                r'\d', square.items[1]) if len(square) > 1 else None
            num = match.group() if match else "0"
            # print("num: " + num)
            yield NEWCOMMAND_TPL.substitute(**locals())

    cfg = '{' + ''.join(re.findall(r'MathJax.Hub.Config\({(.*?)}\);',
                                   m, re.DOTALL)) + '}'

    n = Node(cfg)
    macros = n.find(".*TeX.*" + CurlyNode > ".*Macros.*" + CurlyNode)

    if macros:
        f.writelines(gen_defs(macros))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
