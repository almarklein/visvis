# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" Subpackage visvis.text

For rendering text in visvis.

Defines a wibject and a wobject: Label and Text,
which are both able to produce a single line of text
oriented at a certain angle.

Visvis used the FreeType library to render text, enabling good-looking text
(with proper kerning and anti-aliasing) at any size. If FreeType is not
available, visvis falls back on system that uses pre-rendered fonts.
FreeType is available:

  * On Linux: by default
  * On Windows: needs to be installed (there is an installer on the visvis website)
  * On Mac: probably needs to be installed (also fc-match if you want to
    make use of other fonts then the default.


Formatting
----------

Text can be formatted using the following constructs (which can be mixed):
  * hello^2 or hello^{there}, makes one or more charactes superscript.
  * hello_2 or hello_{there}, makes one or more charactes subscript.
  * hell\io or hell\i{ohoo}, makes one or more charactes italic.
  * hell\bo or hell\b{ohoo}, makes one or more charactes bold.
  * hello\_there,  a backslash escapes, thus keeping the _^ or \ after it.


Special characters
------------------

Characters are available for the following unicode sets:
  * u0020 - u003f  numbers
  * u0040 - u00bf  alphabet
  * u00c0 - u037f  latin
  * u0380 - u03ff  greek
  * u2000 - u23ff  symbols

There are several escape sequences for (mathematical) characters
that can be inserted using the backslash (for example '\infty').
People familiar with Latex know what they do:
  * Re          Im          null        infty
  * int         iint        iiint       forall
  * leq         geq         approx      approxeq        ne          in
  * leftarrow   uparrow     rightarrow  downarrow
  * Leftarrow   Uparrow     Rightarrow  Downarrow
  * leftceil    rightceil   leftfloor   rightfloor
  * times       cdot        pm
  * oplus       ominus      otimes      oslash

Letters from the greek alfabet can be inserted in the same
way (By starting the name with an uppercase letter, the
corresponding upper case greek letter is inserted):
  * alpha       beta        gamma       delta
  * epsilon     zeta        eta         theta
  * iota        kappa       lambda      mu
  * nu          xi          omicron     pi
  * rho         varsigma    sigma       tau
  * upsilon     phi         chi         psi
  * omega

Note: In case one needs a character that is not in this list,
one can always look up its unicode value and use that instead.

"""

from visvis.text.text_base import AtlasTexture, FontManager, BaseText
from visvis.text.text_base import Text, Label

from visvis.text.text_prerendered import PrerenderedFontManager

# Try importing the freetype font manager
# Note that FreeType must be installed. On Linux this would usually be
# the case, otherwise you can install it via the package manager.
# For Windows users there is a simple installer on the Visvis website.
# For Mac I'm not sure yet.
try:
    from visvis.text.text_freetype import FreeTypeFontManager
except RuntimeError:
    FreeTypeFontManager = None

if FreeTypeFontManager is not None:
    FontManager = FreeTypeFontManager
else:
    FontManager = PrerenderedFontManager
