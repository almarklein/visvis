Visvis supports rendering of text. It has a [Label](cls_Label.md) class and a [Text](cls_Text.md) class, which are a wibject and a wobject respectively. Both are able to produce a single line of text oriented at a certain angle.

See the [text example](example_text.md).

### Character support ###

Characters are available for the following unicode sets:

  * u0020 - u003f  numbers
  * u0040 - u00bf  alphabet
  * u00c0 - u037f  latin
  * u0380 - u03ff  greek
  * u2000 - u23ff  symbols


### Formatting ###
Text can be formatted using the following constructs (which can be mixed):

  * `hello^2 or hello^{there}`, makes one or more charactes superscript.
  * `hello_2 or hello_{there}`, makes one or more charactes subscript.
  * `hell\io or hell\i{ohoo}`, makes one or more charactes italic.
  * `hell\bo or hell\b{ohoo}`, makes one or more charactes bold.
  * `hello\_there`,  a backslash escapes, thus keeping the `_^` or `\` after it.


### Mathematical symbols ###

There are several escape sequences for (mathematical) characters
that can be inserted using the backslash (for example `\infty`).
People familiar with Latex know what they do:

<table width='100%'>
<tr><td>Re         </td><td>Im          </td><td>null         </td><td>infty<br>
</td><td></td><td></td></tr>
<tr><td>int        </td><td>iint        </td><td>iiint        </td><td>forall<br>
</td><td></td><td></td></tr>
<tr><td>leq        </td><td>geq         </td><td>approx       </td><td>approxeq<br>
</td><td>ne        </td><td>in</td></tr>
<tr><td>leftarrow  </td><td>uparrow     </td><td>rightarrow  </td><td>downarrow<br>
</td><td></td><td></td></tr>
<tr><td>Leftarrow  </td><td>Uparrow     </td><td>Rightarrow  </td><td>Downarrow<br>
</td><td></td><td></td></tr>
<tr><td>leftceil    </td><td>rightceil   </td><td>leftfloor   </td><td>rightfloor<br>
</td><td></td><td></td></tr>
<tr><td>times       </td><td>cdot        </td><td>pm<br>
</td><td></td><td></td><td></td></tr>
<tr><td>oplus       </td><td>ominus      </td><td>otimes      </td><td>oslash<br>
</td><td></td><td></td></tr>
</table>

Note: In case one needs a character that is not in this list,
one can always look up its unicode value and use that instead.

### Greek ###

Letters from the greek alfabet can be inserted in the same
way (By starting the name with an uppercase letter, the
corresponding upper case greek letter is inserted):

<table width='100%'>
<tr><td>alpha       </td><td>beta        </td><td>gamma       </td><td>delta</td></tr>
<tr><td>epsilon     </td><td>zeta        </td><td>eta         </td><td>theta</td></tr>
<tr><td>iota        </td><td>kappa       </td><td>lambda      </td><td>mu</td></tr>
<tr><td>nu          </td><td>xi          </td><td>omicron     </td><td>pi</td></tr>
<tr><td>rho         </td><td>varsigma    </td><td>sigma       </td><td>tau</td></tr>
<tr><td>upsilon     </td><td>phi         </td><td>chi         </td><td>psi</td></tr>
<tr><td>omega</td></tr>
</table>