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



# todo: proper documentation on how to use this class
class ShaderCode(object):
    """ This class represents a shader program, composed of multiple
    parts. The parts are inserted in one another. The first part
    is the base code, the next is inserted into it, and the next is
    inserted in the result, etc.
    
    To signal that a section of code should be inserted at a spot in 
    the code, use:
    "<<section-identifier<<"
    
    In a part, use the following directive to define a section of code
    to be inserted in the base code:
    ">>secton-identifier>>"
    
    """
    
    def __init__(self, wobject=None):
        
        # Store wobject being shaded
        self._wobject = wobject
        
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
            self._SetUniform(self._uniforms[name])


## SH_CALCSTEPS
SH_CALCSTEPS = """

>>functions>>
<<functions<<

float d2P(vec3 p, vec3 d, vec4 P)
{
    // calculate the distance of a point p to a plane P along direction d.
    // plane P is defined as ax + by + cz = d    
    // line is defined as two points on that line
    
    // calculate nominator and denominator
    float nom = -( dot(P.rgb,p) - P.a );
    float denom =  dot(P.rgb,d);
    // determine what to return
    if (nom*denom<=0.0)
       return 9999999.0; // if negative, or ON the plane, return ~inf
    else
        return nom / denom; // return normally
}

int calculateSteps(vec3 edgeLoc)
{
    // Given the start pos, returns a corrected version of the ray
    // and the number of steps combined in a vec4.
    
    // Check for all six planes how many rays fit from the start point.
    // Take the minimum value (not counting negative and 0).
    float smallest = 9999999.0;
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 0.0)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 0.0)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 0.0)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 1.0)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 1.0)));
    smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 1.0)));
    
    // round-off errors can cause the value to be very large.
    // an n of 100.000 is pretty save
    if (smallest > 9999.0)
        smallest = 0.0;
    
    // determine amount of steps
    return int( ceil(smallest) );
}

"""

## SH_STYLE MIP
SH_STYLE_MIP = """

    >>uniforms>>
    <<uniforms<<
    
    >>pre-loop>>
    
    // Remember that we made sure that the total range of the data is 
    // mapped between 0 and 1 (also for signed data types).
    float val; // to store the current value
    float maxval = -99999.0; // the maximum encountered value
    float maxi = 0.0;   // where the maximum value was encountered
    vec4 maxcolor; // the color found at the maximum value (needed because resampling is inconsistent for some odd reason)
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    
    
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make value
    color1 = texture3D( texture, loc );
    <<color1-to-val<<
    // Bookkeeping (avoid if statements)
    float r = float(val>maxval);
    maxval = (1.0-r)*maxval + r*val;
    maxi = (1.0-r)*maxi + r*float(i);
    maxcolor = (1.0-r)*maxcolor + r*color1;
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(maxi);
    
    // Resample color and make display-color
    //color1 = texture3D( texture, edgeLoc + float(maxi)*ray );
    color1 = maxcolor;
    <<color1-to-color2<<
    gl_FragColor = color2;
    
"""

## SH_STYLE RAY
SH_STYLE_RAY = """
    
    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    <<color1-to-color2<<
    
    // Update value  by adding contribution of this voxel
    // Put bias in denominator so the first voxels dont contribute too much
    //float a = color2.a / ( color2.a + color3.a + 1.0); 
    //a /= stepRatio;
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    
    >>post-loop>>
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    
"""

## SH_STYLE ISO
SH_STYLE_ISO = """

    >>uniforms>>
    uniform float th; // isosurface treshold
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    val = colorToVal(color1);
    
    if (val > th)
    {
        // Set color
        color3 = calculateColor(color1, loc, step);
        
        // Set depth
        iter_depth_f =  float(i);
        
        // Break
        i = n;
        break;
    }
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    // Set color
    color3.a = float(iter_depth_f>0.0);
    gl_FragColor = color3;
    
"""

## SH_STYLE ISORAY
SH_STYLE_ISORAY = """

    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );

    // Set color
    color2 = calculateColor(color1, loc, step);
    
    // Update value by adding contribution of this voxel
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    //float a = color2.a / ( color2.a + color3.a + 0.00001); 
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    
    // Set depth
    iter_depth_f =  float(iter_depth==0.0) * float(color3.a>0) * float(i);
    
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    
"""

## SH_LITVOXEL
SH_LITVOXEL = """
    >>uniforms>>
    varying vec3 L; // light direction
    varying vec3 V; // view direction
    // lighting
    uniform vec4 ambient;
    uniform vec4 diffuse;
    uniform vec4 specular;
    uniform float shininess;
    <<uniforms<<
    
    
    >>functions>>
    <<functions<<
    
    float colorToVal(vec4 color1)
    {
        //return color1.r;
        float val;
        <<color1-to-val<<
        //val = color1.r;
        return val;
    }
    
    vec4 calculateColor(vec4 betterColor, vec3 loc, vec3 step)
    {   
        // Calculate color by incorporating lighting
        vec4 color1;
        vec4 color2;
        
        // calculate normal vector from gradient
        vec3 N; // normal
        color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
        color2 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
        N[0] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
        color2 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
        N[1] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
        color2 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
        N[2] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        float gm = length(N); // gradient magnitude
        N = normalize(N);
        
        // Init total color and strengt variable
        vec4 totalColor;
        float str;
        
        // Apply ambient and diffuse light
        totalColor = ambient * gl_LightSource[0].ambient;
        str = clamp(dot(L,N),0.0,1.0);
        totalColor += str * diffuse * gl_LightSource[0].diffuse;
        
        // Apply color of the texture
        color1 = betterColor;
        <<color1-to-color2<<
        totalColor *= color2;
        
        // Apply specular color
        vec3 H = normalize(L+V);
        str = pow( max(dot(H,N),0.0), shininess);
        totalColor += str * specular * gl_LightSource[0].specular;
        
        totalColor.a = color2.a * gm;
        return totalColor;
    }
    
"""

## SH Color *

SH_COLOR_SCALAR_NOCMAP = """

    >>uniforms>>
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>pre-loop>>
    float _colorval;
    
    >>color1-to-val>>
    val = color1.r;
    
    >>color1-to-color2>>
    _colorval = ( color1.r + scaleBias[1] ) * scaleBias[0];
    color2 = vec4(_colorval, _colorval, _colorval, 1.0);
    
    """

SH_COLOR_SCALAR = """
    
    >>uniforms>>
    uniform sampler1D colormap;
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>color1-to-val>>
    val = color1.r;
    
    >>color1-to-color2>>
    color2 = texture1D( colormap, (color1.r + scaleBias[1]) * scaleBias[0]);
    
    """

SH_COLOR_RGB = """

    >>uniforms>>
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>color1-to-val>>
    val = max(color1.r, max(color1.g, color1.b));
    
    >>color1-to-color2>>
    color2 = ( color1 + scaleBias[1] ) * scaleBias[0];
    
    """

if __name__ == '__main__':
    s = ShaderCode()
    s.AddPart('type', SH_MIP)
    s.AddPart('color', SH_COLOR_COLORMAP)
    print s.GetCode()
    