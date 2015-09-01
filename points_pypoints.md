### Introduction ###

From version 1.4, Visvis uses pypoints.py instead of points.py.

I created points.py for my research and am using it increasingly.

I started this module when I was still a Python rooky, and did not really conform to PEP8. Now Visvis does neither, but in visvis' case it can be argued that it helps in usability to be able to easily distinguish properties from methods. For the small points module, this argument does not hold.

Since I want to be able to use this module in new projects, I decided to change all method names to conform to PEP8.


### How to convert ###

Basically, any name like `Normal()` or `Append()` is now `normal()` or `append()`.

If you use the visvis points.py module, you'll need to convert some code as well. Given that few people use uppercase method names, this should be relatively easy.

Hint: a case sensitive search to `.Append` (including the dot) should get you all Pointset.Append() methods.


### List of names to convert ###

To help people convert, I made a list of names that changed.

Point and Pointset classes:
  * Copy
  * Norm
  * Normalize
  * Normal
  * Distance
  * Angle
  * Angle2
  * Dot
  * Cross


Pointset class:
  * Append
  * Extend
  * Insert
  * Remove
  * RemoveAll (now remove\_all)
  * Pop
  * Clear
  * Contains

Quaternion class:
  * Copy
  * Norm
  * Normalize
  * Conjugate
  * Inverse
  * Exp
  * Log
  * RotatePoint (now rotate\_points)
  * GetMatrix (now get\_matrix)
  * GetAxisAngle (you get the idea ...)
  * CreateFromAxisAngle
  * CreateFromEulerAngles