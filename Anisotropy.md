If the pixels/voxels of a dataset do not have the same size in all dimensions, the data is  called anisotropic. CT data, for example, often has a different voxel distance in the z-dimension as in the x and y dimensions.

Visvis provides two methods to visualize anisotropic data. The first (simple but ugly) method is the Axes.daspect property. It represents the data aspect ratio as shown in the Axes. If you use this, the whole scene is stretched.

The second (beautiful) method is to use the vv.Aarray class. It inherits from np.ndarray but implements methods to deal with anisotropy. Visvis recognizes when the data to visualize is an Aarray and will stretch (and translate) the texture according to its Aarray.sampling and Aarray.origin properties. Note that this means that scene itself is not stretched.

See the [anisotropicData](example_anisotropicData.md) and [anisotropicData2](example_anisotropicData2.md) examples.