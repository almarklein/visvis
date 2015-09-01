
---

#### <font color='#FFF'>light</font> ####
# <font color='#00B'>class Light(axes, index)</font> #

Inherits from [object](cls_object.md).

A Light object represents a light source in the scene. It  determines how lit objects (such as Mesh objects) are visualized.

Each axes has 8 light sources, of which the 0th is turned on by default. De 0th light source provides the ambient light in the scene (the ambient component is 0 by default for the other light sources). Obtain the lights using the axes.light0 and axes.lights properties.

The 0th light source is a directional camera light by default; it shines in the direction in which you look. The other lights are  oriented at the origin by default.





**The Light class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#ambient.md'>ambient</a><br /><a href='#color.md'>color</a><br /><a href='#diffuse.md'>diffuse</a><br /><a href='#isCamLight.md'>isCamLight</a><br /></td>
<td valign='top'>
<a href='#isDirectional.md'>isDirectional</a><br /><a href='#isOn.md'>isOn</a><br /><a href='#position.md'>position</a><br /><a href='#specular.md'>specular</a><br /></td>
<td valign='top'>
</td>
</tr></table>

**The Light class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Off.md'>Off</a><br /><a href='#On.md'>On</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>ambient</font> ####
### <font color='#070'>Light.ambient</font> ###

> Get/Set the ambient color of the light. This is the color that is everywhere, coming from all directions, independent of  the light position.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of the reference color.


#### <font color='#FFF'>color</font> ####
### <font color='#070'>Light.color</font> ###

> Get/Set the reference color of the light. If the ambient, diffuse or specular properties specify a scalar, that scalar represents the fraction of **this** color.


#### <font color='#FFF'>diffuse</font> ####
### <font color='#070'>Light.diffuse</font> ###

> Get/Set the diffuse color of the light. This component is the light that comes from one direction, so it's brighter if it comes squarely down on a surface than if it barely glances off the  surface. It depends on the light position how a material is lit.


#### <font color='#FFF'>isCamLight</font> ####
### <font color='#070'>Light.isCamLight</font> ###

> Get/Set whether the light is a camera light. A camera light moves along with the camera, like the lamp on a miner's hat.


#### <font color='#FFF'>isDirectional</font> ####
### <font color='#070'>Light.isDirectional</font> ###

> Get/Set whether the light is a directional light. A directional light has no real position (it can be thought of as infinitely far away), but shines in a particular direction. The sun is a good example of a directional light.


#### <font color='#FFF'>isOn</font> ####
### <font color='#070'>Light.isOn</font> ###

> Get whether the light is on.


#### <font color='#FFF'>position</font> ####
### <font color='#070'>Light.position</font> ###

> Get/Set the position of the light. Can be represented as a 3 or 4 element tuple. If the fourth element is a 1, the light has a position, if it is a 0, it represents a direction (i.o.w. the light is a directional light, like the sun).


#### <font color='#FFF'>specular</font> ####
### <font color='#070'>Light.specular</font> ###

> Get/Set the specular color of the light. This component represents the light that comes from the light source and bounces off a surface in a particular direction. This is what makes  materials appear shiny.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of the reference color.




---


## Methods ##

#### <font color='#FFF'>!Off</font> ####
### <font color='#066'>Light.Off()</font> ###

> Turn the light off.


#### <font color='#FFF'>!On</font> ####
### <font color='#066'>Light.On(on=True)</font> ###

> Turn the light on.



---

