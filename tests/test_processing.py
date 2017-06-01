

def test_line2mesh():
    import visvis as vv
    
    pp = vv.Pointset(3)
    pp.append((1, 2, 3))
    pp.append((3, 1, 5))
    pp.append((4, 4, 7))
    pp.append((6, 7, 9))
    
    m = vv.processing.lineToMesh(pp, 3, 10)
    assert isinstance(m, vv.BaseMesh)


def test_unwindfaces():
    import visvis as vv
    
    pp = vv.Pointset(3)
    pp.append((1, 2, 3))
    pp.append((3, 1, 5))
    pp.append((4, 4, 7))
    pp.append((6, 7, 9)) 
    m = vv.BaseMesh(pp, faces=[0, 1, 2, 0, 2, 3])
    
    assert m._faces is not None
    assert m._vertices.shape == (4, 3)
    
    vv.processing.unwindFaces(m)
    
    assert m._faces is None
    assert m._vertices.shape == (6, 3)
    assert tuple(m._vertices[0]) == tuple(pp[0])
    assert tuple(m._vertices[1]) == tuple(pp[1])
    assert tuple(m._vertices[2]) == tuple(pp[2])
    assert tuple(m._vertices[3]) == tuple(pp[0])
    assert tuple(m._vertices[4]) == tuple(pp[2])
    assert tuple(m._vertices[5]) == tuple(pp[3])


def test_combine_meshes():
    import visvis as vv
    
    pp = vv.Pointset(3)
    pp.append((1, 2, 3))
    pp.append((3, 1, 5))
    pp.append((4, 4, 7))
    pp.append((6, 7, 9)) 
    m = vv.BaseMesh(pp, faces=[0, 1, 2, 0, 2, 3])
    
    assert m._vertices.shape == (4, 3)
    
    m2 = vv.processing.combineMeshes([m, m, m])
    assert m2 is not m
    
    assert m2._vertices.shape == (12, 3)


def test_calculate_normals():
    import visvis as vv
    
    pp = vv.Pointset(3)
    pp.append((1, 2, 3))
    pp.append((3, 1, 5))
    pp.append((4, 4, 7))
    pp.append((6, 7, 9)) 
    m = vv.BaseMesh(pp, faces=[0, 1, 2, 0, 2, 3])
    
    assert m._normals is None
    
    vv.processing.calculateNormals(m)
    normals1 = m._normals
    
    assert m._normals is not None
    assert m._normals.shape == (4, 3)
    
    vv.processing.calculateFlatNormals(m)
    normals2 = m._normals
    
    assert m._normals is not None
    assert m._normals.shape == (6, 3)
    
    assert normals1 is not normals2
    assert normals1.shape != normals2.shape  # because faces have been unwound


def test_statistics():
    import numpy as np
    import visvis as vv
    
    data = np.array([-0.213,  0.282, -0.382, -1.409, -0.477, -1.233, -1.465,
                     -0.686,  1.246,  0.566, 0.786, -1.231, -0.587,  1.552,
                     0.359, 0.353,  0.052,  1.718,  0.291, -0.093])
    
    d = vv.processing.statistics(data)
    
    assert d.size == 20
    assert d.std > 0.9 and d.std < 1.1
    assert d.mean > -0.1 and d.mean < +0.1
    
    assert d.dmin
    assert d.dmax
    assert d.drange
    assert d.median
    assert d.Q1
    assert d.Q2
    assert d.Q3
    assert d.IQR
    
    assert d.histogram_np()
    assert d.percentile(0.7)
    assert d.histogram()
    assert d.kde()
