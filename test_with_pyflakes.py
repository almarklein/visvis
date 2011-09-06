

"""
Implementation of the command-line I{pyflakes} tool.
"""

import compiler, sys
import os

from pyflakes import checker


def check(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    # Since compiler.parse does not reliably report syntax errors, use the
    # built in compiler first to detect those.
    try:
        try:
            compile(codeString, filename, "exec")
        except MemoryError:
            # Python 2.4 will raise MemoryError if the source can't be
            # decoded.
            if sys.version_info[:2] == (2, 4):
                raise SyntaxError(None)
            raise
    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    else:
        # Okay, it's syntactically valid.  Now parse it into an ast and check
        # it.
        tree = compiler.parse(codeString)
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        warnings = []
        for warning in w.messages:
            ignore_warning = False
            for needle in IGNORE_STRINGS:
                if needle in str(warning):
                    ignore_warning = True
                    break
            if '__init__.py' in filename and 'imported but unused' in str(warning):
                ignore_warning = True
            if not ignore_warning:
                warnings.append(warning)
        for warning in warnings:
            print warning
        return len(warnings)

IGNORE_STRINGS = []
# IGNORE_STRINGS.extend(['but unused', 'but never used', 'redefinition of unused'])
IGNORE_STRINGS.append('from visvis.core.shaders_src import *')
IGNORE_STRINGS.append('from visvis.core.constants import *')
IGNORE_STRINGS.append('from functions import *')
IGNORE_STRINGS.append('from visvis.wobjects import *')
IGNORE_STRINGS.append('from visvis.wibjects import *')
IGNORE_STRINGS.append('from visvis.core import *')
#
IGNORE_STRINGS.append("redefinition of unused 'np'")
IGNORE_STRINGS.append("redefinition of unused 'vv'")
IGNORE_STRINGS.append("redefinition of unused 'PIL'")
IGNORE_STRINGS.append("redefinition of unused 'np'")


def checkPath(filename):
    """
    Check the given path, printing out any warnings detected.

    @return: the number of warnings printed
    """
    try:
        return check(file(filename, 'U').read() + '\n', filename)
    except IOError, msg:
        print >> sys.stderr, "%s: %s" % (filename, msg.args[1])
        return 1


def main():
    warnings = 0
    args = sys.argv[1:]
    if args:
        for arg in args:
            if os.path.isdir(arg):
                for dirpath, dirnames, filenames in os.walk(arg):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            warnings += checkPath(os.path.join(dirpath, filename))
            else:
                warnings += checkPath(arg)
    else:
        warnings += check(sys.stdin.read(), '<stdin>')

    raise SystemExit(warnings > 0)


if __name__ == '__main__':
    
    # Where is visvis?
    if os.path.isdir('wibjects') and os.path.isdir('wobjects'):
        visvis_dir = os.getcwd()
    else:
        import visvis as vv
        visvis_dir = os.path.dirname( vv.__file__ )
    
    warnings = 0
    for dirpath, dirnames, filenames in os.walk(visvis_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filename = os.path.join(dirpath, filename)
                filename_short = filename[len(visvis_dir)+1:]
                text = file(filename, 'U').read() + '\n'
                warnings += check(text, filename_short)
    
    print 'pyflakes found %i warnings.' % warnings
    