
---

#### <font color='#FFF'>radiobutton</font> ####
# <font color='#00B'>class RadioButton(parent, text='', fontname=None)</font> #

Inherits from [ToggleButton](cls_ToggleButton.md).

Inherits from ToggleButton. If pressed upon, sets the state of all sibling RadioButton instances to False, and its own state to True.

When this happens, all instances will fire eventStateChanged (after the states are set). So it's only necessary to bind to one of them  to detect the selection of  another item.






---

