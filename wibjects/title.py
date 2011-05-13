from visvis import Label

class Title(Label):
    """ Title(axes, text)
    
    A label wibject that places itself at the top of its parent (which
    should be an Axes). The axes' position is corrected so the title
    will fit on screen.
    
    A Title can be created with the function vv.title().
    
    """
    
    def __init__(self, axes, text):
        Label.__init__(self, axes, text)
        
        # set textsize and align
        self.halign = 0
        self.fontSize = 12
        
        # set back color to be transparant
        self.bgcolor = ''
        
        # set position
        self.position = 0, -20, 1, 15
        
        # correct axes' position
        dy = -20        
        axes.position.Correct(0, -dy, 0, dy) 
    
    
    def OnDestroy(self):
        Label.OnDestroy(self)
        
        # correct axes' position
        axes = self.parent
        if axes:
            dy = 20
            axes.position.Correct(0, -dy, 0, dy) 
