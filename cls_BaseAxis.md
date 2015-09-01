
---

#### <font color='#FFF'>baseaxis</font> ####
# <font color='#00B'>class BaseAxis(parent)</font> #

Inherits from [Wobject](cls_Wobject.md).

This is the (abstract) base class for all axis classes, such as the CartesianAxis and PolarAxis.

An Axis object represents the lines, ticks and grid that make up an axis. Not to be confused with an Axes, which represents a scene and is a Wibject.





**The BaseAxis class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#axisColor.md'>axisColor</a><br /><a href='#gridLineStyle.md'>gridLineStyle</a><br /><a href='#showBox.md'>showBox</a><br /><a href='#showGrid.md'>showGrid</a><br /><a href='#showGridX.md'>showGridX</a><br /><a href='#showGridY.md'>showGridY</a><br /></td>
<td valign='top'>
<a href='#showGridZ.md'>showGridZ</a><br /><a href='#showMinorGrid.md'>showMinorGrid</a><br /><a href='#showMinorGridX.md'>showMinorGridX</a><br /><a href='#showMinorGridY.md'>showMinorGridY</a><br /><a href='#showMinorGridZ.md'>showMinorGridZ</a><br /><a href='#tickFontSize.md'>tickFontSize</a><br /></td>
<td valign='top'>
<a href='#xLabel.md'>xLabel</a><br /><a href='#xTicks.md'>xTicks</a><br /><a href='#yLabel.md'>yLabel</a><br /><a href='#yTicks.md'>yTicks</a><br /><a href='#zLabel.md'>zLabel</a><br /><a href='#zTicks.md'>zTicks</a><br /></td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>axisColor</font> ####
### <font color='#070'>BaseAxis.axisColor</font> ###

> Get/Set the color of the box, ticklines and tick marks.

#### <font color='#FFF'>gridLineStyle</font> ####
### <font color='#070'>BaseAxis.gridLineStyle</font> ###

> Get/Set the style of the gridlines as a single char similar to the lineStyle (ls) property of the line wobject (or in plot).

#### <font color='#FFF'>showBox</font> ####
### <font color='#070'>BaseAxis.showBox</font> ###

> Get/Set whether to show the box of the axis.

#### <font color='#FFF'>showGrid</font> ####
### <font color='#070'>BaseAxis.showGrid</font> ###

> Show/hide the grid for the x,y and z dimension.

#### <font color='#FFF'>showGridX</font> ####
### <font color='#070'>BaseAxis.showGridX</font> ###

> Get/Set whether to show a grid for the x dimension.

#### <font color='#FFF'>showGridY</font> ####
### <font color='#070'>BaseAxis.showGridY</font> ###

> Get/Set whether to show a grid for the y dimension.

#### <font color='#FFF'>showGridZ</font> ####
### <font color='#070'>BaseAxis.showGridZ</font> ###

> Get/Set whether to show a grid for the z dimension.

#### <font color='#FFF'>showMinorGrid</font> ####
### <font color='#070'>BaseAxis.showMinorGrid</font> ###

> Show/hide the minor grid for the x, y and z dimension.

#### <font color='#FFF'>showMinorGridX</font> ####
### <font color='#070'>BaseAxis.showMinorGridX</font> ###

> Get/Set whether to show a minor grid for the x dimension.

#### <font color='#FFF'>showMinorGridY</font> ####
### <font color='#070'>BaseAxis.showMinorGridY</font> ###

> Get/Set whether to show a minor grid for the y dimension.

#### <font color='#FFF'>showMinorGridZ</font> ####
### <font color='#070'>BaseAxis.showMinorGridZ</font> ###

> Get/Set whether to show a minor grid for the z dimension.

#### <font color='#FFF'>tickFontSize</font> ####
### <font color='#070'>BaseAxis.tickFontSize</font> ###

> Get/Set the font size of the tick marks.

#### <font color='#FFF'>xLabel</font> ####
### <font color='#070'>BaseAxis.xLabel</font> ###

> Get/Set the label for the x dimension.


#### <font color='#FFF'>xTicks</font> ####
### <font color='#070'>BaseAxis.xTicks</font> ###

> Get/Set the ticks for the x dimension.

> The value can be:
    * None: the ticks are determined automatically.
    * A tuple/list/numpy\_array with float or string values: Floats  specify at which location tickmarks should be drawn. Strings are drawn at integer positions corresponding to the index in the given list.
    * A dict with numbers or strings as values. The values are drawn at the positions specified by the keys (which should be numbers).


#### <font color='#FFF'>yLabel</font> ####
### <font color='#070'>BaseAxis.yLabel</font> ###

> Get/Set the label for the y dimension.


#### <font color='#FFF'>yTicks</font> ####
### <font color='#070'>BaseAxis.yTicks</font> ###

> Get/Set the ticks for the y dimension.

> The value can be:
    * None: the ticks are determined automatically.
    * A tuple/list/numpy\_array with float or string values: Floats  specify at which location tickmarks should be drawn. Strings are drawn at integer positions corresponding to the index in the given list.
    * A dict with numbers or strings as values. The values are drawn at the positions specified by the keys (which should be numbers).


#### <font color='#FFF'>zLabel</font> ####
### <font color='#070'>BaseAxis.zLabel</font> ###

> Get/Set the label for the z dimension.


#### <font color='#FFF'>zTicks</font> ####
### <font color='#070'>BaseAxis.zTicks</font> ###

> Get/Set the ticks for the z dimension.

> The value can be:
    * None: the ticks are determined automatically.
    * A tuple/list/numpy\_array with float or string values: Floats  specify at which location tickmarks should be drawn. Strings are drawn at integer positions corresponding to the index in the given list.
    * A dict with numbers or strings as values. The values are drawn at the positions specified by the keys (which should be numbers).



---

