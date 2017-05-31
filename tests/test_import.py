
def test_visvis_import():
    import visvis as vv
    import visvis.vvio
    
    assert vv
    assert vv.vvio
    assert vv.imread
    assert vv.imshow
    assert vv.plot
    assert vv.Slider
    assert vv.Axes
