from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Text, Keyword, Name, String, Comment, Literal

class PlumedCLtoolLexer(RegexLexer):
    name = 'plumedcltool'
    aliases = ['plumedcltool']
    filenames = ['*.plmd']

    tokens = {
        'root': [
            # Find the start of a shortcut with a nested default
            (r'#NODEFAULT plumed\n',Comment.Special),
            # Find the start of a default section
            (r'#DEFAULT plumed\n',Comment.Special),
            # Find the end of a default section
            (r'#ENDDEFAULT plumed\n',Comment.Special),
            # Find commands that use MPI and that take an input file
            (r'(^\s*mpirun\s+-np)(\s+[0-9]+\s+)(plumed)(\s+)(\S+\b)(\s*<\s*)(\S+\b)', bygroups(Literal, Text, String, Text, Keyword, Text, Name.Decorator)), 
            # With plumed-runtime and MPI
            (r'(^\s*mpirun\s+-np)(\s+[0-9]+\s+)(plumed-runtime)(\s+)(\S+\b)', bygroups(Literal, Text, String, Text, Keyword)),
            # Find commands that use MPI
            (r'(^\s*mpirun\s+-np)(\s+[0-9]+\s+)(plumed)(\s+)(\S+\b)', bygroups(Literal, Text, String, Text, Keyword)),
            # Find commands that use the nompi flag
            (r'(^\s*plumed)(\s+)(--no-mpi)(\s+)(\S+\b)', bygroups(String, Text, Literal, Text, Keyword)),
            # Find commands that take an input file
            (r'(^\s*plumed)(\s+)(\S+\b)(\s*<\s*)(\S+\b)', bygroups(String, Text, Keyword, Text, Name.Decorator)),
            # Find direct out to file
            (r'(\s*>\s*)(\S+\b)', bygroups(Text, Name.Entity)),
            # Find the name of the command if we are using plumed-runtime
            (r'(^\s*plumed-runtime)(\s+)(\S+\b)', bygroups(String, Text, Keyword)),
            # Find the name of the command
            (r'(^\s*plumed)(\s+)(\S+\b)', bygroups(String, Text, Keyword)),
            # Deals with keywords with argument in inverted commas
            (r'(-\S+)(=)(".+")', bygroups(Name.Attribute, Text, Text)),
            # Deals with keywords with equals sign
            (r'(-\S+)(=)(\S+\b)', bygroups(Name.Attribute, Text, Text)),
            # Flag at end of line
            (r'(--\S+\b)(\s*\n)', bygroups(Name.Attribute, Text)),
            # Deals with keywords
            (r'(--\S+)(\s+)([^-\s]+\b)', bygroups(Name.Attribute, Text, Text)),
            # Deals with flags
            (r'(--\S+\b)', Name.Attribute),
            # find the -h command
            (r'(-h)', Name.Attribute),
            # Find any left over white space
            (r'\s+',Text)
        ]
    }
