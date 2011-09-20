# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders

Defines the classes that manage shading:
  * GlslProgram: represents a GLSL program by wrapping the OpenGl stuff.
  * ShaderCode: represents the code for one GLSL program (vertex or fragment).
  * ShaderCodePart: a part of GLSL code. Multiple parts combined form a program.

"""

import os

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla

from visvis.core.misc import getResourceDir, getOpenGlCapable
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


class Shader(object):
    """ Shader()
    
    A Shader object represents the shading code for a GLSL shader. It 
    provides the main interface for users to control the code, set uniforms
    etc.
    
    This class wraps three objects which can be accessed easily via 
    properties: 
      * program: the relatively low level interface to OpenGl.
      * vertex: represents the source code for the vertex shader.
      * fragment: represents the source code for the fragment shader.
    
    """
    
    def __init__(self):
        self._vertex = ShaderCode()
        self._fragment = ShaderCode()
        self._program = GlslProgram()
        
        self._staticUniforms = {}
        self._pendingUniforms = {}
        self._textureId = -1 # -1 means disabled
        self._texturesToDisable = []
    
    @property
    def vertex(self):
        """ Get the vertex ShaderCode object for this shader.
        """
        return self._vertex
    
    @property
    def fragment(self):
        """ Get the vertex ShaderCode object for this shader.
        """
        return self._fragment
    
    @property
    def program(self):
        """ Get the glsl program for this shading code. This is the low
        level object that compiles and enables the glsl code.
        """
        return self._program
    
    @property
    def isUsable(self):
        """ Get whether this shader is usable. If not, the hardware
        does not support glsl.
        """
        return self._program.IsUsable()
    
    @property
    def hasCode(self):
        """ Get whether this shader has any code in it.
        """
        
        # Update source code?
        if self.vertex._isDirtyForProgram:
            self.program.SetVertexShader(self.vertex.GetCode())
        if self.fragment._isDirtyForProgram:
            self.program.SetFragmentShader(self.fragment.GetCode())
        
        # Check
        return bool( self._program.HasCode() )
    
    
    def Enable(self):
        """ Enable()
        
        Enable this shader. This does  number of things:
          * Update source code of vertex and fragment shader (if necessary).
          * Compile and bind shader programs (if necessary).
          * Enables the glsl program.
          * Applies any static and pending uniforms.
          * Enables all textures that were given as uniforms.
        
        """
        
        # Init
        self._textureId = 0
        
        # Update source code?
        if self.vertex._isDirtyForProgram:
            self.program.SetVertexShader(self.vertex.GetCode())
        if self.fragment._isDirtyForProgram:
            self.program.SetFragmentShader(self.fragment.GetCode())
        
        # Enable program (compiles if necessary
        self.program.Enable()
     
        # Apply static and pending uniforms
        # Note that more uniforms can be set after this function returns.
        for name, value in self._GetStaticAndPendingUniforms().items():
            self._ApplyUniform(name, value)
    
    
    def EnableTextureOnly(self, *args):
        """ EnableTextureOnly(name0, name1, name2)
        
        Enable only any textures that were registered as a uniform.
        This is a convenience function that can be useful when you don't
        want to use the shader, but the fixed pipeline needs the texture
        enabled.
        
        name0 is enabled with texture-unit 0, name1 with texture-unit 1, etc.
        If the names are invalid, they are ignored.
        
        Use the normal Disable() method to disable the texture.
        
        """
        if self._textureId >= 0:
            raise RuntimeError('Shader already enabled.')
        
        # Enable
        self._textureId = 0
        
        # Get uniforms
        uniforms = self._GetStaticAndPendingUniforms()
        
        # Find textures, ignore if not present
        for i in range(len(args)):
            # Get name
            name = args[i]
            if name not in uniforms:
                continue
            # Get value
            value = uniforms[name]
            if not isinstance(value, vv.core.baseTexture.TextureObject):
                continue
            # Enable and prepare for disabling
            value.Enable(i)
            self._texturesToDisable.append(value)
    
        
    def Disable(self):
        """ Disable()
        
        Disable this shading program. This does a couple of things:
          * Disables all textures that were given as uniforms.
          * Disables the glsl program.
        
        """
        
        # Disable textures
        for value in self._texturesToDisable:
            value.Disable()
        
        # Disable program
        self.program.Disable()
        
        # Clean up
        self._textureId = -1
        self._texturesToDisable = []
    
    
    def SetUniform(self, name, value):
        """ SetUniform(name, value)
        
        Set uniform value for shader code. This is the glsl system for 
        getting data into the GLSL shader.
        
        The given uniform is used during the next or current draw. This 
        method is therefore to be used inside OnDraw() methods.
        
        The value can be:
            * float or int: becomes float/int in glsl
            * tuple of up to 4 elements: becomes vec/ivec, based on first value
            * vv.TextureObject: becomes sampler1D, sampler2D or sampler3D
        
        In the case of a texture, the texture is automatically enabled/disabled.
        
        """
        
        # Check
        self._CheckUniform(name, value)
        
        if self._textureId < 0:
            # Disabled; add to pending uniforms
            self._pendingUniforms[name] = value
        else:
            # Enabled; apply now
            self._ApplyUniform(name, value)
    
    
    def SetStaticUniform(self, name, value):
        """ SetStaticUniform(name, value)
        
        Set uniform value for shader code. This is the glsl system for 
        getting data into the GLSL shader.
        
        The given uniform is used in all draws. This method provides
        a way to set uniforms from outside the OnDraw method, and still
        be dynamic, because the value can be a callable that returns the
        actual value.
        
        The value can be:
            * float or int: becomes float/int in glsl
            * tuple of up to 4 elements: becomes vec/ivec, based on first value
            * vv.TextureObject: becomes sampler1D, sampler2D or sampler3D
            * callable that returns one of the above.
        
        In the case of a texture, the texture is automatically enabled/disabled.
        
        """
        # Check value
        if hasattr(value, '__call__'):
            # Only check name (dummy value)
            # Value is checked during applying the uniform
            self._CheckUniform(name, 1.0)
        else:
            # Check name and value
            self._CheckUniform(name, value)
        
        # Store
        self._staticUniforms[name] = value
    
    
    def RemoveStaticUniform(self, name):
        """ RemoveStaticUniform(name)
        
        Remove a static uniform.
        
        """
        self._staticUniforms.pop(name)
    
    
    def _CheckUniform(self, name, value):
        
        # Check name
        if not isinstance(name, basestring):
            raise ValueError('Uniform name must be a string.')
        if not name:
            raise ValueError('Uniform name must be at least 1 character.')
        
        # Check value
        if not ((   isinstance(value, (float, int))    ) or 
                (   isinstance(value, (list, tuple)) and len(value)<5   ) or
                (   isinstance(value, vv.core.baseTexture.TextureObject) )
                ):
            raise ValueError('Invalid value for uniform.')
    
    
    def _ApplyUniform(self, name, value):
        # No hard checks, it is assumed that these have been performed
        
        if isinstance(value, float):
            self.program.SetUniformf(name, [value])
        elif isinstance(value, int):
            self.program.SetUniformi(name, [value])
        elif isinstance(value, (list, tuple)):
            if isinstance(value[0], float):
                self.program.SetUniformf(name, value)
            elif isinstance(value[0], int):
                self.program.SetUniformi(name, value)        
        elif isinstance(value, vv.core.baseTexture.TextureObject):
            # Enable and register as uniform
            value.Enable(self._textureId)
            self.program.SetUniformi(name, [self._textureId])
            # Prepare for disabling, and for next texture
            self._texturesToDisable.append(value)
            self._textureId += 1
    
    
    def _GetStaticAndPendingUniforms(self):
        
        # Collect static uniforms
        uniforms = {}
        for name, value in self._staticUniforms.items():
            if hasattr(value, '__call__'):
                value = value()
                self._CheckUniform(name, value)
            uniforms[name] = value
        
        # Update with pending uniforms (override static uniforms with same name)
        uniforms.update(self._pendingUniforms)
        
        return uniforms



class GlslProgram:
    """ GlslProgram()
    
    A low level class representing a GLSL (OpenGL Shading Language) program.
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
        """ Returns whether the program is usable. In other words, whether
        the OpenGl driver supports GLSL.
        """ 
        return self._usable
    
    
    def HasCode(self):
        """ Returns whether the program has any code associated with it.
        If not, you shoul probably not enable it.
        """
        return self._fragmentCode or self._vertexCode
    
    
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
        
        try:
            # set values
            if len(values) == 1:
                gl.glUniform1f(loc, values[0])
            elif len(values) == 2:
                gl.glUniform2f(loc, values[0], values[1])            
            elif len(values) == 3:
                gl.glUniform3f(loc, values[0], values[1], values[2])
            elif len(values) == 4:
                gl.glUniform4f(loc, values[0], values[1], values[2], values[3])
        except:
            print 'Could not set uniform in shader. "%s": %s' % (varname, repr(values))
    
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
    
    Parts
    -----
    A ShaderCode instance has one or more parts which are inserted in 
    one another. The first part is the base code, the next is "inserted" 
    into it, and the next is inserted in the result, etc.
    
    Every part has a name, representing what it does or represents. 
    Different parts that do the same thing (but in different ways) 
    have the same way. This enables replacing parts (such as the render
    style for 3D textures) in a very easy and natural way. All parts
    in a ShaderCode instance must have unique names.
    
    Composition
    -----------
    Insertion of one part in the base code happens via replacement. 
    The code of a ShaderCodePart consists of multiple sections, where
    each section starts with a specification of what is removed. For
    this we use two greater than characters '>>':
    {{{
    >>someValue = 3;
    someValue = 4;
    }}}
    
    All code following the replacement-lines is inserted in the base 
    code. Note that both the replace-code as the replacing code may
    consist of multiple lines. 
    
    The matching of code is based on the stripped code, so spaces do not
    matter. The replace-code (the code behind '>>') needs to be an exact 
    match, but in the source there may be other code in front and after 
    the code; this works:
    {{{
    // == Base code ==
    a = b+3;
    // insert more code here
    c = a-b;
    d = a+b;
    }}}
    {{{
    // == Code to insert ==
    >>more code
    float tmp = a;
    a = b;
    b = tmp;
    }}}
    
    
    Standard sections
    -----------------
    For clarity we define a few standard sections: '--uniforms--', 
    '--varying--', '--functions--'. When defining a function/uniform/varying, 
    don't forget to include the functions/uniforms/varyings of any next parts:
    {{{
        >>--uniforms--
        uniform vec3 some_vector
        // --uniforms-- // enables the next parts to set uniforms
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
        """ Get a list of the parts in the shader. 
        """
        return [part for part in self._parts]
    
    @property
    def partNames(self):
        """ Get a list of the part names in the shader. 
        """
        return [part.name for part in self._parts]
    
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
    
    
    def _IndexOfPart(self, part):
        
        parts, names = self.parts, self.partNames
        
        if isinstance(part, basestring):
            if part not in names:
                raise ValueError('part not present: %s' % part)
            else:
                return names.index(part)
        elif isinstance(part, ShaderCodePart):
            if part not in parts:
                raise ValueError('part not present: %s' % repr(part))
            else:
                return parts.index(part)
        else:
            raise ValueError('Inalid part description (must be string or ShaderCodePart).')
    
    
    def AddPart(self, part, before=None, after=None):
        """ AddPart(part, before=None, after=None)
        
        Add a ShaderCodePart instance. It can be placed before or after an
        existing part. The default places the part at the end.
        
        It is an error to add a part with of a name that is already
        present in the shader.
        
        """
        
        # Check
        if not isinstance(part, ShaderCodePart):
            raise ValueError('AddPart needs a ShaderCodePart.')
        
        # Check if already exists
        if part.name in self.partNames:
            raise ValueError('part of that name already exists: %s' % part.name)
        
        # Add
        if before and after:
            raise ValueError('Can only specify before or after; not both.')
        elif before:
            i = self._IndexOfPart(before)
            self._parts.insert(i, part)
        elif after:
            i = self._IndexOfPart(after)
            self._parts.insert(i+1, part)
        else:
            self._parts.append(part)
        
        # Signal dirty
        self._buffer = None
    
    # todo: make it such that replacing a part that is exactly the same wongt trigger recompile
    def ReplacePart(self, part):
        """ ReplacePart(part)
        
        Replace an existing part, based on the name.
        
        """
        
        # Check
        if not isinstance(part, ShaderCodePart):
            raise ValueError('ReplacePart needs a ShaderCodePart.')
        
        # Replace
        i = self._IndexOfPart(part.name)
        self._parts[i] = part
        
        # Signal dirty
        self._buffer = None
    
    
    def AddOrReplace(self, part, before=None, after=None):
        """ AddOrReplace(part, before=None, after=None)
        
        Convenience function to add a part or replace it if 
        a part of this name already exists.
        
        """
        if self.HasPart(part.name):
            return self.ReplacePart(part)
        else:
            return self.AddPart(part, before, after)
    
    
    def RemovePart(self, part):
        """ RemovePart(part)
        
        Remove a part. Returns True on success, and False if no part exists 
        for the given name. Also accepts a part name.
        
        """
        try:
            i = self._IndexOfPart(part)
        except Exception:
            return False
        else:
            # Signal dirty
            self._buffer = None
            # Pop
            self._parts.pop(i)
            return True
    
    
    def HasPart(self, part):
        """ HasPart(part)
        
        If part is a string, checks whether a part with the given name is
        present. If part is a ShaderCodePart instance, checks whether that
        exact part is present.
        
        """
        if isinstance(part, basestring):
            return part in self.partNames
        elif isinstance(part, ShaderCodePart):
            return part in self.parts
        else:
            raise ValueError('HasPart needs name or part.')
    
    
    def Clear(self):
        """ Clear()
        
        Clear all parts.
        
        """
        self._parts = []
        
        # Signal dirty
        self._buffer = None
    
    
    def GetCode(self):
        """ GetCode()
        
        Get the total code for this shader.
        
        """
        if self._isDirty:
            self._Compile()
        return '\n'.join( [t[0] for t in self._buffer] )
    
    
    def ShowCode(self, part=None, columnLimit=79):
        """ ShowCode(part=None, columnLimit=79)
        
        Print the code with line numbers, and limiting long lines.
        Can be useful when debugging glsl code.
        
        When part is given, only print the lines that belong to the
        given part name. The 'part' argument can also be a string with
        the part name.
        
        """
        # Make sure that there is code
        self.GetCode()
        
        # Get name
        if part is None:
            name = None
        elif isinstance(part, basestring):
            name = part
        elif isinstance(part, ShaderCodePart):
            name = part.name
        else:
            raise ValueError('ShowCode needs part name or ShaderCodePart instance.')
        
        # Test name
        if name and name not in self.partNames:
            raise ValueError('Given name not present.')
        
        # Iterate through lines
        linenr = 0
        lines = []
        for line, partName in self._buffer:
            linenr += 1
            line2 = '%03i|%s' % (linenr, line)
            if len(line2) > columnLimit:
                line2 = line2[:columnLimit-3] + '...'
            if (not name) or (name == partName):
                lines.append(line2)
        print '\n'.join(lines)
    
    
    def _Compile(self):
        """ _Compile()
        
        Compile the full code by filling composing all parts/sections.
        
        """
        def dedentCode(lines):
            lines2 = []
            for line in lines:
                if isinstance(line, tuple):
                    line = line[0]
                lines2.append(line.strip())
            return '\n'.join(lines2)
        
        # Init code
        totalLines = [] # code lines: (line, partName)
        totalCode = '' # code without indentation or trailing whitespace
        
        for part in self.parts:
            
            # If totalCode is empty, simply set code
            if not totalLines:
                for line in part.code.splitlines():
                    indent = len(line) - len(line.lstrip())
                    totalLines.append( (line, part.name) )
                totalCode = dedentCode(totalLines)
                continue
            
            # Get sections in this part
            partSections, partCodes = part.CollectSections()
            
            for section, code in zip(partSections, partCodes):
                
                # Find sections
                splittedCode = totalCode.split(section)
                
                # Section present?
                if len(splittedCode) == 1:
                    #print 'Warning: code section <%s> not known.' % section
                    continue
                
                # For every occurance ...
                for i in range(len(splittedCode)-1):
                    
                    # Count where we need to insert
                    nr1 = splittedCode[i].count('\n')
                    nr2 = nr1 + 1 + section.count('\n')
                    
                    # Calculate original indentation
                    line = totalLines[nr1][0]
                    originalIndent = len(line) - len(line.lstrip())
                    
                    # Remove lines that we replace
                    for ii in reversed(range(nr1, nr2)):
                        totalLines.pop(ii)
                    
                    # Insert new lines
                    for line in reversed(code.splitlines()):
                        line = originalIndent*' ' + line
                        indent = len(line) - len(line.lstrip())
                        totalLines.insert( nr1, (line, part.name) )
                
                # Set total code
                totalCode = dedentCode(totalLines)
        
        # Done
        self._buffer = totalLines
    
    
#     def SetUniform(self, name, value):
#         """ SetUniform(name, value)
#         Can be:
#           * float or int
#           * tuple/list of float or ints (up to 4)
#           * texture
#           * a callable that returns any of the above.
#         """
#         # Check name
#         if not isinstance(name, basestring):
#             raise ValueError('Uniform name for ShaderCode must be a string.')
#         if not name:
#             raise ValueError('Uniform name must be at least 1 character.')
#         
#         # Check value
#         if isinstance(value, (float, int)):
#             pass
#         elif isinstance(value, (list, tuple)):
#             pass
#         elif isinstance(value, vv.core.baseTexture.TextureObject):
#             pass
#         elif hasattr(value, '__call__'):
#             pass        
#         else:
#             raise ValueError('Uniform value for ShaderCode must be a list/tuple.')
#         self._uniforms[name] = value
#     
#     
#     def _ApplyUniforms(self, program):
#         """ _ApplyUniforms(program)
#         
#         Apply all uniforms to the given GlslProgram instance.
#         To be used inside a Draw() method.
#         
#         Also enables all textures that are registered as a uniform.
#         
#         """
#         
#         texture_id = [1]
#         
#         def setuniform(name, value):
#             if isinstance(value, float):
#                 program.SetUniformf(name, [value])
#             elif isinstance(value, int):
#                 program.SetUniformi(name, [value])
#             elif isinstance(value, (list, tuple)):
#                 if isinstance(value[0], float):
#                     program.SetUniformf(name, value)
#                 elif isinstance(value[0], int):
#                     program.SetUniformi(name, value)        
#             elif isinstance(value, vv.core.baseTexture.TextureObject):
#                 value.Enable(texture_id[0])
#                 program.SetUniformi(name, [texture_id[0]])
#                 texture_id[0] += 1
#             elif hasattr(value, '__call__'):
#                 setuniform(name, value())
#             else:
#                 raise ValueError('Invalid uniform value: %s' % repr(value))
#         
#         for name in self._uniforms:
#             setuniform(name, self._uniforms[name])
#     
#     
#     def _DisableUniformTextures(self):
#         """ _DisableUniformTextures(program)
#         
#         Disable any texture objects that were enabled with the call
#         to _ApplyUniforms().
#         
#         """
#         
#         def setuniform(value):
#             if isinstance(value, vv.core.baseTexture.TextureObject):
#                 value.Disable()
#             elif hasattr(value, '__call__'):
#                 setuniform(value())
#         
#         for name in self._uniforms:
#            setuniform(self._uniforms[name])


class ShaderCodePart(object):
    """ ShaderCodePart(name, version, code)
    
    A ShaderCodePart instance represents a part of GLSL code. Multiple 
    parts can be combined by replacing lines in the preceding parts. 
    This makes code-reuse much easier, and allows users to for example
    implement a volume renderer without the hassle of calculating ray
    direction etc.; they can simply modify an existing renderer.
    
    Parameters
    ----------
    name : str
      The name of the part, showing what it does. Different parts that
      have the same purpose have the same name. The different render 
      styles are for example implemented using parts all having the
      name 'renderstyle'.
    version : str
      What version of the part this is. For the render styles, this would
      be 'mip', 'ray', 'iso', etc. This is purely for the developer/user
      to better identify this different parts.
    code : str
      The source code. Consists of different sections. Each section starts
      with one or more lines that start with '>>'. The text behind the lines
      is what shall be replaced in the preceding code part. The following
      lines are the one that shall be inserted. Indentation does not matter.
      See core/shaders_src.py for examples.      
    
    """
    def __init__(self, name, version, code):
        self._name = str(name)
        self._version = str(version)
        self._rawCode = code
        self._code = self._stripCode(code)
    
    def _stripCode(self, code):
        """ Strip the code of its minimum indentation. Also strip empty
        lines before and after the actual code.
        """
        # Strip empy trailing lines
        code = code.rstrip()
        
        # Find minimum indentation, skip first empty lines
        lines1 = []
        minIndent = 99999999
        encounteredRealLine = False
        for line1 in code.splitlines():
            line2 = line1.lstrip()
            line3 = line2.rstrip()
            if encounteredRealLine or line3:
                lines1.append(line1)
            if line3:
                encounteredRealLine = True
                indent = len(line1) - len(line2)
                minIndent = min(minIndent, indent)
        
        # Remove minimum indentation and trailing whitespace
        lines2 = []
        for line1 in lines1:
            lines2.append(line1[minIndent:].rstrip())
        return '\n'.join(lines2)
    
    @property
    def name(self):
        """ Get the name of this ShaderCodePart instance.
        """
        return self._name
    @property
    def version(self):
        """ Get the version of this ShaderCodePart instance.
        """
        return self._version
    @property
    def rawCode(self):
        """ Get the original unprocessed code of this ShaderCodePart instance.
        """
        return self._rawCode
    @property
    def code(self):
        """ Get the code of this ShaderCodePart instance.
        """
        return self._code
    def __repr__(self):
        return '<Shaderpart %s: %s>' % (self.name, self.version)
    def __str__(self):
        return self._code
    def CollectSections(self):
        """ CollectSections()
        
        Returns a two-element tuple with two list elements:
          * the replace-code for each section (can be multi-line)
          * the corresponding code to replace it with. 
          
        """
        
        # Init
        sections = []
        sections_raw = []
        codes = []
        
        # Collect all section needles
        linenr = 0    
        lastLinenr = -10
        for line in self.code.splitlines():
            linenr += 1
            if line.startswith('>>'):
                if linenr == lastLinenr + 1:
                    sections[-1] += '\n' + line[2:].lstrip()
                    sections_raw[-1] += '\n' + line
                else:
                    sections.append(line[2:].lstrip())
                    sections_raw.append(line)
                lastLinenr = linenr
        
        # Collect code
        code = self.code
        for section_raw in sections_raw:
            code2, dummy, code = code.partition(section_raw)
            codes.append(code2)
        codes.append(code)
        codes.pop(0)
        
        # Clean up codes
        codes2 = []
        for code in codes:
            code = code[1:].rstrip() + '\n'
            codes2.append(code)
        
        # Done
        return sections, codes2


# Import all shaders. Can only do the import after the ShaderCodePart is deffed
from visvis.core.shaders_2 import *
from visvis.core.shaders_3 import *
from visvis.core.shaders_m import *


if __name__ == '__main__':
    
    S1 = ShaderCodePart('s1','',
    """ 
        // Cast ray. 
        int i=0;
        while (i<n)
        {
            for (i=i; i<n; i++)
            {
                // Calculate location.
                vec3 loc = edgeLoc + float(i) * ray;
    """)
    
    S2 = ShaderCodePart('s2','',
    """
    >>int i=0;
    >>while (i<n)
    >>{
    >>for (i=i; i<n; i++)
    // reversed loop
    int i = n-1;
    while (i>0)
    {
        for (i=i; i>=0; i--)
    """)
    
    s = ShaderCode()
    s.AddPart(S1)
    s.AddPart(S2)
    print s.GetCode()

