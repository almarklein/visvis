# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders

Loads the code for the shaders and defines the GlslProgram class.

"""

import os

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla

from visvis.core.misc import getResourceDir, getOpenGlCapable
from visvis.core.shaders_src import *
import visvis as vv

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
            gl.glUniform1i(loc, values[0])
        elif len(values) == 2:
            gl.glUniform2i(loc, values[0], values[1])            
        elif len(values) == 3:
            gl.glUniform3i(loc, values[0], values[1], values[2])
        elif len(values) == 4:
            gl.glUniform4i(loc, values[0], values[1], values[2], values[3])
    
    
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


class ShaderCode(object):
    """ ShaderCode()
    
    This class represents the source code for a GLSL shader program, 
    composed of multiple parts. By describing programs as a composition
    of different parts, pieces of code can be more easily re-used,
    and programs can be altered in a very flexible way. This allows 
    users to for example modify existing volume renderers.
    
    Composition
    -----------
    The parts are inserted in one another. The first part
    is the base code, the next is inserted into it, and the next is
    inserted in the result, etc.
    
    Every part (except the base part) consists of several sections,
    which are identified by a line as such: ">>section-identifier>>".
    
    Sections are inserted in the base code by an inclusion line:
    "<<section-identifier<<". Note the direction of the arrows.
    
    Standard sections
    -----------------
    For clarity we define a few standard sections: uniforms, varying, functions.
    When defining a function/uniform/varying, don't forget to include 
    the functions/uniforms/varyings of any next parts:
    {{{
        >>uniforms>>
        uniform vec3 some_vector
        <<uniforms<< // enables the next parts to set uniforms
    }}}
    
    """
    
    def __init__(self):
        
        # Init uniforms
        self._uniforms = {}
        
        # Init sub codes
        self._parts = []
        
        # Init buffer. None means it's dirty
        self._buffer = None
        
        # Flag for the program. Is set to True by the isDirty property. Is 
        # only set to False by the special private property _isDirtyForProgram.
        self._dirtyForProgramFlag = True
    
    
    @property
    def parts(self):
        """ Get a list of the part names in the shader. 
        """
        return [part[0] for part in self._parts]
    
    
    @property
    def _isDirty(self):
        """ Get whether this code is dirty and needs compiling.
        """
        
        # Check self
        dirty = self._buffer is None
        
        # Update flag for program
        if dirty:
            self._dirtyForProgramFlag = True
        
        # Done
        return dirty
    
    
    @property
    def _isDirtyForProgram(self):
        """ Gets whether this code was changed since this method was last used.
        """
        dummy = self._isDirty # Sets _dirtyForProgramFlag if it is really dirty
        dirty = self._dirtyForProgramFlag
        self._dirtyForProgramFlag = False
        return dirty
    
    
    def _IndexOfPart(self, name):
        
        parts = self.parts
        if name not in self.parts:
            raise ValueError('part does not exist: %s' % name)
        else:
            return parts.index(name)
    
    
    def AddPart(self, name, code, before=None, after=None):
        """ AddPart(name, code, before=None, after=None)
        
        Add a part of code. It can be placed before or after an
        existing part. The default places the part at the end.
        
        It is an error to add a part with a name that is already
        present in the shader.
        
        """
        
        # Check
        if not isinstance(name, basestring) or len(name) == 0:
            raise ValueError('name for ShaderCode part must be a nonempty string.')
        if not isinstance(code, basestring) or len(name) ==0:
            raise ValueError('code for ShaderCode part must be a nonempty string.')
        
        # Check if already exists
        if name in self.parts:
            raise ValueError('part already exists: %s' % name)
        
        # Add
        if before and after:
            raise ValueError('Can only specify before or after; not both.')
        elif before:
            i = self._IndexOfPart(before)
            self._parts.insert( i, (name, code) )
        elif after:
            i = self._IndexOfPart(after)
            self._parts.insert( i+1, (name, code) )
        else:
            self._parts.append( (name, code) )
        
        # Signal dirty
        self._buffer = None
    
    
    def ReplacePart(self, name, code):
        """ ReplacePart(name, code)
        
        Replace the code of an existing part.
        """
        
        # Replace
        i = self._IndexOfPart(name)
        self._parts[i] = name, code
        
        # Signal dirty
        self._buffer = None
    
    
    def AddOrReplace(self, name, code, before=None, after=None):
        """ AddOrReplace(name, code, before=None, after=None)
        
        Convenience function to add a code part or replace it if 
        a part with this name already exists.
        
        """
        if self.HasPart(name):
            return self.ReplacePart(name, code)
        else:
            return self.AddPart(name, code, before, after)
    
    
    def RemovePart(self, name):
        """ RemovePart(name)
        
        Remove a part. Returns True on success, and False if no part exists 
        for the given name. 
        
        """
        try:
            i = self._IndexOfPart(name)
        except Exception:
            return False
        else:
            # Signal dirty
            self._buffer = None
            # Pop
            self._parts.pop(i)
            return True
        
    
    
    def HasPart(self, name):
        """ HasPart(name)
        
        Check whether a part with the given name exists at this shader.
        
        """
        if name in self.parts:
            return True
        else:
            return False
    
    
    def Clear(self):
        """ Clear()
        
        Clear all parts.
        
        """
        self._parts = []
        
        # Signal dirty
        self._buffer = None
    
    
    def GetCode(self, name=None):
        """ GetCode(name=None)
        
        Show the code of this shader. If name is given, show the
        code of that part. Otherwise show the total code.
        
        """
        if name is None:
            # Return full code
            if self._isDirty:
                self._Compile()
            return self._buffer
        else:
            i = self._IndexOfPart(name)
            return self._parts[i][1]
    
    
    def _CollectSections(self, text, kind='>>'):
        """ _CollectSections(text)
        
        Check what sections are in the given text.
        
        """
        # Collect all section names
        sections = []
        indents = []
        for line in text.splitlines():
            line2 = line.lstrip()
            indent = len(line)-len(line2)
            line = line2.rstrip()
            if line.startswith(kind) and line.endswith(kind):
                if ' ' not in line:
                    sections.append(line[len(kind):-len(kind)])
                    indents.append(indent)
        return sections, indents
    
    
    def _Compile(self):
        """ _Compile()
        
        Compile the full code by filling composing all parts/sections.
        
        """
        
        # Init code
        totalCode = ''
        
        for name, code in self._parts:
            
            # If totalCode is empty, simply replace code
            if not totalCode:
                totalCode = code
                continue
            
            # Get base sections in total code
            baseSections, baseIndents = self._CollectSections(totalCode, '<<')
            indent_per_section = {}
            for section, indent in zip(baseSections, baseIndents):
                indent_per_section[section] = indent
            
            # Get sections in this part
            partSections, partIndents = self._CollectSections(code, '>>')
            
            # Get code for each section in this part
            partCodes = []
            for section in partSections:
                code2, dummy, code = code.partition('>>%s>>'%section)
                partCodes.append(code2)
            partCodes.append(code)
            partCodes.pop(0)
            
            for section, indent, code in zip(partSections, partIndents, partCodes):
                
                # Valid section?
                if section not in baseSections:
                    #print 'Warning: code section <%s> not known.' % section
                    continue
                
                # Fix indentation
                lines = []
                section_indent = indent_per_section[section]
                for line in code.splitlines():
                    line2 = line.lstrip()
                    line_indent = len(line) - len(line2)
                    if line_indent >= indent:
                        line = ' '*section_indent + line[indent:]
                    else:
                        line = ' '*section_indent + line
                    lines.append(line)
                
                # Remove empty trailing lines
                lines2 = []
                for line in reversed(lines):
                    if lines2 or line.strip():
                        lines2.append(line)
                lines = [line for line in reversed(lines2)]
                
                # Combine to get code
                code = '\n'.join(lines[1:])
                
                # Insert section
                needle ='%s<<%s<<' % (' '*section_indent, section)
                totalCode = totalCode.replace(needle, code)
        
        # Fill any leftover sections with blanks
        baseSections, baseIndents = self._CollectSections(totalCode, '<<')
        for section in baseSections:
            totalCode = totalCode.replace('<<%s<<'%section, '')
        
        # Done
        self._buffer = totalCode
    
    
    def SetUniform(self, name, value):
        """ SetUniform(name, value)
        Can be:
          * float or int
          * tuple/list of float or ints (up to 4)
          * texture
          * a callable that returns any of the above.
        """
        # Check name
        if not isinstance(name, basestring):
            raise ValueError('Uniform name for ShaderCode must be a string.')
        if not name:
            raise ValueError('Uniform name must be at least 1 character.')
        
        # Check value
        if isinstance(value, (float, int)):
            pass
        elif isinstance(value, (list, tuple)):
            pass
        elif isinstance(value, vv.core.baseTexture.TextureObject):
            pass
        elif hasattr(value, '__call__'):
            pass        
        else:
            raise ValueError('Uniform value for ShaderCode must be a list/tuple.')
        self._uniforms[name] = value
    
    
    def _ApplyUniforms(self, program):
        """ _ApplyUniforms(program)
        
        Apply all uniforms to the given GlslProgram instance.
        To be used inside a Draw() method.
        
        Also enables all textures that are registered as a uniform.
        
        """
        
        texture_id = [1]
        
        def setuniform(name, value):
            if isinstance(value, float):
                program.SetUniformf(name, [value])
            elif isinstance(value, int):
                program.SetUniformi(name, [value])
            elif isinstance(value, (list, tuple)):
                if isinstance(value[0], float):
                    program.SetUniformf(name, value)
                elif isinstance(value[0], int):
                    program.SetUniformi(name, value)        
            elif isinstance(value, vv.core.baseTexture.TextureObject):
                value.Enable(texture_id[0])
                program.SetUniformi(name, [texture_id[0]])
                texture_id[0] += 1
            elif hasattr(value, '__call__'):
                setuniform(name, value())
            else:
                raise ValueError('Invalid uniform value: %s' % repr(value))
        
        for name in self._uniforms:
            setuniform(name, self._uniforms[name])
    
    
    def _DisableUniformTextures(self):
        """ _DisableUniformTextures(program)
        
        Disable any texture objects that were enabled with the call
        to _ApplyUniforms().
        
        """
        
        def setuniform(value):
            if isinstance(value, vv.core.baseTexture.TextureObject):
                value.Disable()
            elif hasattr(value, '__call__'):
                setuniform(value())
        
        for name in self._uniforms:
           setuniform(self._uniforms[name])


if __name__ == '__main__':
    s = ShaderCode()
    s.AddPart('type', SH_MIP)
    s.AddPart('color', SH_COLOR_COLORMAP)
    print s.GetCode()
