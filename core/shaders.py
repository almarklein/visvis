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
        """ Get a list of the parts in the shader. 
        """
        return [part for part in self._parts]
    
    @property
    def partTypes(self):
        """ Get a list of the part types in the shader. 
        """
        return [part.type for part in self._parts]
    
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
        
        parts, types = self.parts, self.partTypes
        
        if isinstance(part, basestring):
            if part not in types:
                raise ValueError('part not present: %s' % part)
            else:
                return types.index(part)
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
        
        It is an error to add a part with of a type that is already
        present in the shader.
        
        """
        
        # Check
        if not isinstance(part, ShaderCodePart):
            raise ValueError('AddPart needs a ShaderCodePart.')
        
        # Check if already exists
        if part.type in self.partTypes:
            raise ValueError('part of that type already exists: %s' % part.type)
        
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
    
    
    def ReplacePart(self, part):
        """ ReplacePart(part)
        
        Replace an existing part, based on the type.
        
        """
        
        # Check
        if not isinstance(part, ShaderCodePart):
            raise ValueError('ReplacePart needs a ShaderCodePart.')
        
        # Replace
        i = self._IndexOfPart(part.type)
        self._parts[i] = part
        
        # Signal dirty
        self._buffer = None
    
    
    def AddOrReplace(self, part, before=None, after=None):
        """ AddOrReplace(part, before=None, after=None)
        
        Convenience function to add a part or replace it if 
        a part of this type already exists.
        
        """
        if self.HasPart(part.type):
            return self.ReplacePart(part)
        else:
            return self.AddPart(part, before, after)
    
    
    def RemovePart(self, part):
        """ RemovePart(part)
        
        Remove a part. Returns True on success, and False if no part exists 
        for the given type. Also accepts a part type-name.
        
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
        
        If part is a string, checks whether a part with the given type is
        present. If part is a ShaderCodePart instance, checks whether that
        exact part is present.
        
        """
        if isinstance(part, basestring):
            return part in self.partTypes
        elif isinstance(part, ShaderCodePart):
            return part in self.parts
        else:
            raise ValueError('HasPart needs type or part.')
    
    
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
        given part type. The 'part' argument can also be a string with
        the type name.
        
        """
        # Make sure that there is code
        self.GetCode()
        
        # Get type
        if part is None:
            type = None
        elif isinstance(part, basestring):
            type = part
        elif isinstance(part, ShaderCodePart):
            type = part.type
        else:
            raise ValueError('ShowCode needs type name or ShaderCodePart instance.')
        
        # Test type
        if type  and type not in self.partTypes:
            raise ValueError('Given type not present.')
        
        # Iterate through lines
        linenr = 0
        lines = []
        for line, partType in self._buffer:
            linenr += 1
            line2 = '%03i|%s' % (linenr, line)
            if len(line2) > columnLimit:
                line2 = line2[:columnLimit-3] + '...'
            if (not type) or (type == partType):
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
        totalLines = [] # code lines: (line, indent, part-type)
        totalCode = '' # code without indentation or trailing whitespace
        
        for part in self.parts:
            
            # If totalCode is empty, simply set code
            if not totalLines:
                for line in part.code.splitlines():
                    indent = len(line) - len(line.lstrip())
                    totalLines.append( (line, part.type) )
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
                        totalLines.insert( nr1, (line, part.type) )
                
                # Set total code
                totalCode = dedentCode(totalLines)
        
        # Done
        self._buffer = totalLines
    
    
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

# todo: doc
class ShaderCodePart(object):
    def __init__(self, type, name, code):
        self._type = str(type)
        self._name = str(name)
        self._code = self._stripCode(code)
    
    def _stripCode(self, code):
        
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
    def type(self):
        return self._type
    @property
    def name(self):
        return self._name
    @property
    def code(self):
        return self._code
    def __repr__(self):
        return '<Shaderpart %s: %s>' % (self.type, self.name)
    def __str__(self):
        return self._code
    def CollectSections(self):
        
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
from visvis.core.shaders_src import *

if __name__ == '__main__':
    
    S1 = ShaderCodePart('s1','',
    """ 
        // Cast ray. For some reason the inner loop is not iterated the whole
        // way for large datasets. Thus this ugly hack. If you know how to do
        // it better, please let me know!
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

