
---


# The classes of Visvis #

Visvis knows two kinds of visualization objects:
wibjects (widget objects) which have a position in screen coordinates,
and wobjects (world objects) which reside in a scene represented by an
Axes object.

Most of the time, the wobjects represent the stuff we want
to visualize, and wibjects help doing that. Both the Wibject and Wobject
class inherit from visvis.BaseObject.
<table width='100%'><tr>
<td valign='top'>
<b>Base classes:</b>
<ul><li><a href='cls_BaseObject.md'>BaseObject</a>
</li><li><a href='cls_Wibject.md'>Wibject</a>
</li><li><a href='cls_Wobject.md'>Wobject</a>
</td>
<td valign='top'>
<b>Wibject classes:</b>
</li><li><a href='cls_Axes.md'>Axes</a>
</li><li><a href='cls_AxesContainer.md'>AxesContainer</a>
</li><li><a href='cls_BaseFigure.md'>BaseFigure</a>
</li><li><a href='cls_BaseMapableEditor.md'>BaseMapableEditor</a>
</li><li><a href='cls_BaseSlider.md'>BaseSlider</a>
</li><li><a href='cls_Box.md'>Box</a>
</li><li><a href='cls_ClimEditor.md'>ClimEditor</a>
</li><li><a href='cls_Colorbar.md'>Colorbar</a>
</li><li><a href='cls_ColormapEditor.md'>ColormapEditor</a>
</li><li><a href='cls_DraggableBox.md'>DraggableBox</a>
</li><li><a href='cls_Label.md'>Label</a>
</li><li><a href='cls_Legend.md'>Legend</a>
</li><li><a href='cls_PushButton.md'>PushButton</a>
</li><li><a href='cls_RadioButton.md'>RadioButton</a>
</li><li><a href='cls_RangeSlider.md'>RangeSlider</a>
</li><li><a href='cls_Slider.md'>Slider</a>
</li><li><a href='cls_Title.md'>Title</a>
</li><li><a href='cls_ToggleButton.md'>ToggleButton</a>
</td>
<td valign='top'>
<b>Wobject classes:</b>
</li><li><a href='cls_BaseAxis.md'>BaseAxis</a>
</li><li><a href='cls_BaseTexture.md'>BaseTexture</a>
</li><li><a href='cls_Line.md'>Line</a>
</li><li><a href='cls_Mesh.md'>Mesh</a>
</li><li><a href='cls_MotionDataContainer.md'>MotionDataContainer</a>
</li><li><a href='cls_MotionTexture2D.md'>MotionTexture2D</a>
</li><li><a href='cls_MotionTexture3D.md'>MotionTexture3D</a>
</li><li><a href='cls_OrientableMesh.md'>OrientableMesh</a>
</li><li><a href='cls_PolarLine.md'>PolarLine</a>
</li><li><a href='cls_SliceTexture.md'>SliceTexture</a>
</li><li><a href='cls_SliceTextureProxy.md'>SliceTextureProxy</a>
</li><li><a href='cls_Text.md'>Text</a>
</li><li><a href='cls_Texture2D.md'>Texture2D</a>
</li><li><a href='cls_Texture3D.md'>Texture3D</a>
</td>
<td valign='top'>
<b>Other classes:</b>
</li><li><a href='cls_Aarray.md'>Aarray</a>
</li><li><a href='cls_BaseCamera.md'>BaseCamera</a>
</li><li><a href='cls_BaseEvent.md'>BaseEvent</a>
</li><li><a href='cls_BaseMesh.md'>BaseMesh</a>
</li><li><a href='cls_BasePoints.md'>BasePoints</a>
</li><li><a href='cls_BaseText.md'>BaseText</a>
</li><li><a href='cls_EventDoubleClick.md'>EventDoubleClick</a>
</li><li><a href='cls_EventEnter.md'>EventEnter</a>
</li><li><a href='cls_EventKeyDown.md'>EventKeyDown</a>
</li><li><a href='cls_EventKeyUp.md'>EventKeyUp</a>
</li><li><a href='cls_EventLeave.md'>EventLeave</a>
</li><li><a href='cls_EventMotion.md'>EventMotion</a>
</li><li><a href='cls_EventMouseDown.md'>EventMouseDown</a>
</li><li><a href='cls_EventMouseUp.md'>EventMouseUp</a>
</li><li><a href='cls_EventPosition.md'>EventPosition</a>
</li><li><a href='cls_EventScroll.md'>EventScroll</a>
</li><li><a href='cls_FlyCamera.md'>FlyCamera</a>
</li><li><a href='cls_KeyEvent.md'>KeyEvent</a>
</li><li><a href='cls_Light.md'>Light</a>
</li><li><a href='cls_MotionMixin.md'>MotionMixin</a>
</li><li><a href='cls_MouseEvent.md'>MouseEvent</a>
</li><li><a href='cls_OrientationForWobjects_mixClass.md'>OrientationForWobjects_mixClass</a>
</li><li><a href='cls_Point.md'>Point</a>
</li><li><a href='cls_Pointset.md'>Pointset</a>
</li><li><a href='cls_Position.md'>Position</a>
</li><li><a href='cls_Quaternion.md'>Quaternion</a>
</li><li><a href='cls_Range.md'>Range</a>
</li><li><a href='cls_ThreeDCamera.md'>ThreeDCamera</a>
</li><li><a href='cls_Timer.md'>Timer</a>
</li><li><a href='cls_Transform_Rotate.md'>Transform_Rotate</a>
</li><li><a href='cls_Transform_Scale.md'>Transform_Scale</a>
</li><li><a href='cls_Transform_Translate.md'>Transform_Translate</a>
</li><li><a href='cls_TwoDCamera.md'>TwoDCamera</a>
</td>
</tr></table>