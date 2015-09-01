
---

#### <font color='#FFF'>motiontexture3d</font> ####
# <font color='#00B'>class MotionTexture3D</font> #

Inherits from [Texture3D](cls_Texture3D.md), [MotionMixin](cls_MotionMixin.md).

MotionTexture2D(parent, data)

A data type that represents a 3D texture in motion. The given data must be a list of the volumes that should be shown.

The motionIndex (i.e. time) can also be in between two images, in which case interpolation is applied (default linear).

Note that this can be rather slow. For faster display of multiple images, one can also use the MotionDataContainer.






---

