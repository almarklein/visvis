import os

def test_im_read_write():
    import visvis as vv
    im = vv.imread('astronaut.png')
    assert im.shape == (512, 512, 3)
    vv.imwrite(os.path.expanduser('~/astronaut2.png'), im)


def test_mesh_read_write():
    import visvis as vv
    m = vv.meshRead('bunny.ssdf')
    assert isinstance(m, vv.BaseMesh)
    vv.meshWrite(os.path.expanduser('~/bunny2.stl'), m)
