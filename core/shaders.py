# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders

Loads the code for the shaders and defines the GlslProgram class.

"""

import os, sys, time

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla

from visvis.core.misc import getResourceDir, getOpenGlCapable

# Variable for debugging / developing to display shader info logs always.
alwaysShowShaderInfoLog = False


def loadShaders():
    """ loadShaders()
    
    load shading code from the files in the resource dir.
    Returns two dicts with the vertex and fragment shaders, respectively. 
    
    """
    
    path = getResourceDir()
    vshaders = {}
    fshaders = {}
    for filename in os.listdir(path):
        
        # only glsl files
        if not filename.endswith('.glsl'):
            continue
        
        # read code
        f = open( os.path.join(path, filename) )
        tekst = f.read()
        f.close()
        
        # insert into this namespace
        if filename.endswith('.vertex.glsl'):
            varname = filename[:-12].lower()
            vshaders[varname] = tekst
        elif filename.endswith('.fragment.glsl'):
            varname = filename[:-14].lower()
            fshaders[varname] = tekst
    
    return vshaders, fshaders

# load shaders
vshaders, fshaders = loadShaders()


# todo: also make CG shaders? they say on the web they are more predictable.
class GlslProgram:
    """ GlslProgram()
    
    A class representing a GLSL (OpenGL Shading Language) program.
    It provides an easy interface for adding vertex and fragment shaders
    and setting variables used in them.
    Note: On systems that do not support shading, this class will go in
    invalid mode.
    
    """
    
    def __init__(self):
        # ids
        self._programId = 0
        self._shaderIds = []
        
        # code for the shaders        
        self._fragmentCode = ''
        self._vertexCode = ''
        
        # is usable?
        self._usable = True
        if not getOpenGlCapable('2.0',
            'anti-aliasing, the clim property, colormaps and 3D rendering'):
            self._usable = False
    
    def IsUsable(self):
        """ Returns whether the program is usable. 
        """ 
        return self._usable
    
    def _IsCompiled(self):
        if not self._usable:
            return False
        else:
            return ( self._programId>0 and gl.glIsProgram(self._programId) )
    
    
    def Enable(self):
        """ Start using the program. 
        """
        if not self._usable:
            return
        
        if (self._fragmentCode or self._vertexCode) and not self._IsCompiled():
            self._CreateProgramAndShaders()
        
        if self._IsCompiled():
            gla.glUseProgramObjectARB(self._programId)
        else:
            gla.glUseProgramObjectARB(0)
    
    
    def Disable(self):
        """ Stop using the program. 
        """
        if not self._usable:
            return
        gla.glUseProgramObjectARB(0)
    
    
    def SetVertexShader(self, code):
        """ Create a vertex shader from code and attach to the program.
        """
        self._vertexCode = code
        self.DestroyGl()


    def SetFragmentShader(self, code):
        """ Create a fragment shader from code and attach to the program.
        """
        self._fragmentCode = code
        self.DestroyGl()
    
    
    def SetVertexShaderFromFile(self, path):
        try:
            f = open(path, 'r')
            code = f.rad()
            f.close()
        except Exception, why:
            print "Could not create shader: ", why            
        self.SetVertexShader(code)
    
    
    def SetFagmentShaderFromFile(self, path):
        try:
            f = open(path, 'r')
            code = f.read()
            f.close()            
        except Exception, why:
            print "Could not create shader: ", why            
        self.SetFragmentShader(code)
   
    
    def _CreateProgramAndShaders(self):
        # clear any old programs and shaders
        
        if self._programId < 0:
            return
        
        # clear to be sure
        self.DestroyGl()
        
        if not self._fragmentCode and not self._vertexCode:
            self._programId = -1  # don't make a shader object
            return
        
        try:
            # create program object
            self._programId = gla.glCreateProgramObjectARB()
            
            # the two shaders
            codes = [self._fragmentCode, self._vertexCode]
            types = [gl.GL_FRAGMENT_SHADER, gl.GL_VERTEX_SHADER]
            for code, type in zip(codes, types):
                # only attach shaders that do something
                if not code:
                    continue
                
                # create shader object            
                myshader = gla.glCreateShaderObjectARB(type)
                self._shaderIds.append(myshader)
                
                # set its source            
                gla.glShaderSourceARB(myshader, [code])
                
                # compile shading code
                gla.glCompileShaderARB(myshader)
                
                # If it went well, attach!
                if not self._CheckForErrors(myshader, True, False):
                    gla.glAttachObjectARB(self._programId, myshader)
            
            # link shader and check for errors
            gla.glLinkProgramARB(self._programId)
            if self._CheckForErrors(self._programId, False, True):
                self._programId = -1
        
        except Exception, why:
            self._programId = -1
            print "Unable to initialize shader code.", why
    
    
    def SetUniformf(self, varname, values):
        """ SetUniformf(varname, values)
        
        A uniform is a parameter for shading code.
        Set the parameters right after enabling the program.
        values should be a list of up to four floats ( which 
        are converted to float32).
        
        """
        if not self._IsCompiled():
            return
        
        # convert to floats
        values = [float(v) for v in values]
        
        # get loc
        loc = gla.glGetUniformLocationARB(self._programId, varname)        
        
        # set values
        if len(values) == 1:
            gl.glUniform1f(loc, values[0])
        elif len(values) == 2:
            gl.glUniform2f(loc, values[0], values[1])            
        elif len(values) == 3:
            gl.glUniform3f(loc, values[0], values[1], values[2])
        elif len(values) == 4:
            gl.glUniform4f(loc, values[0], values[1], values[2], values[3])
    
    
    def SetUniformi(self, varname, values):
        """ SetUniformi(varname, values)
        
        A uniform is a parameter for shading code.
        Set the parameters right after enabling the program.
        values should be a list of up to four ints ( which 
        are converted to int).
        
        """
        if not self._IsCompiled():
            return
        
        # convert to floats
        values = [int(v) for v in values]
        
        # get loc
        loc = gla.glGetUniformLocationARB(self._programId, varname)        
        
        # set values
        if len(values) == 1:
            gla.glUniform1iARB(loc, values[0])
        elif len(values) == 2:
            gl.glUniform2iARB(loc, values[0], values[1])            
        elif len(values) == 3:
            gl.glUniform3iARB(loc, values[0], values[1], values[2])
        elif len(values) == 4:
            gl.glUniform4iARB(loc, values[0], values[1], values[2], values[3])
    
    
    def _CheckForErrors(self, glObject, checkCompile=True, checkLink=True):
        """ Check for errors in compiling and linking the given shader.
        Prints the info log if there's an error.
        Returns True if an error was found.
        """         
        if checkCompile:
            ok = gl.glGetShaderiv(glObject, gl.GL_COMPILE_STATUS)
            if not ok:
                self._PrintInfoLog(glObject, "Error compiling shading code:")
                return True
            elif alwaysShowShaderInfoLog:
                self._PrintInfoLog(glObject, "Compile info log:")
        if checkLink:
            ok = gl.glGetProgramiv(glObject, gl.GL_LINK_STATUS)
            if not ok:
                self._PrintInfoLog(glObject, "Error linking shading code:")
                return True
            elif alwaysShowShaderInfoLog:
                self._PrintInfoLog(glObject, "Link info log:")
    
    
    def _PrintInfoLog(self, glObject, preamble=""):
        """ Print the info log. 
        """
        log = gla.glGetInfoLogARB(glObject)
        if log:
            print preamble, log            
    
    
    def DestroyGl(self):
        """ DestroyGl()
        
        Clear the program. 
        
        """
        # clear OpenGL stuff
        if not self._usable:
            return
        if self._programId>0:
            try: gla.glDeleteObjectARB(self._programId)
            except Exception: pass
        for shaderId in self._shaderIds:
            try:  gla.glDeleteObjectARB(shaderId)
            except Exception: pass
        # reset
        self._programId = 0
        self._shaderIds[:] = []
    
    
    def __del__(self):
        " You never know when this is called."
        self.DestroyGl()
