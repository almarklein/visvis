_Note that [points.py is replace by pypoints.py](points_pypoints.md), and that many method names have changed._

The module visvis.pypoints defines several classes useful for describing points, pointsets, anisotropic arrays and Quaternions. It is designed as a stand-alone module to be distributed under the BDS license. Since Visvis depends on this module, it is distributed along with Visvis. It is embedded in visvis in such a way, that if you have a copy of the module somewhere on your PYTHONPATH, that copy is used instead of the version that came with Visvis. That way, you can use the module and for example plot pointsets without worrying about isinstance tests failing.

The classes defined in points.py are the following:
  * [Point](cls_Point.md) - represents a single point of any dimension (at least 2)
  * [Pointset](cls_Pointset.md) - represents a set of points, stored in a contiguous numpy array
  * [Aarray](cls_Aarray.md) - a subclass of numpy.ndarray that implements anisotropy
  * [Quaternion](cls_Quaternion.md) - a quaternion is a mathematically convenient way to describe rotations