import subprocess 
import os
import re
import json
import pathlib
import zipfile
import warnings
import glob
from lxml import etree
from io import StringIO
from bs4 import BeautifulSoup
from contextlib import contextmanager
from pygments import highlight
from pygments.lexers import load_lexer_from_file
from pygments.formatters import load_formatter_from_file 
# Uncomment this line if it is required for tests  
#from pygments.formatters import HtmlFormatter

def zip(path):
    """ Zip a path removing the original file """
    with zipfile.ZipFile(path + ".zip", "w") as f_out:
        f_out.write(path)
    os.remove(path)

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def getPlumedSyntax( plumedexe ) :
    """
       Get the plumed syntax information from the syntax.json file

       This function reurns a dictionary that contains all the information on the plumed syntax that was read in from the 
       syntax.json file.

       Keyword arguments:
       plumedexe -- The plumed executibles that were used.  The last one is the one whose syntax.json file we retrieve
    """
    cmd = [plumedexe[-1], 'info', '--root']
    plumed_info = subprocess.run(cmd, capture_output=True, text=True )
    keyfile = plumed_info.stdout.strip() + "/json/syntax.json"
    with open(keyfile) as f :
        try:
           keyword_dict = json.load(f)
        except ValueError as ve:
           raise InvalidJSONError(ve)
    return keyword_dict  

def test_and_get_html( inpt, name, actions=set({}), test_plumed_kwargs={}) :
    """
        Test if the plumed input is broken and generate the html syntax

        This function wraps test_plumed and get_html

        Keyword arguments:
        inpt -- A string containing the PLUMED input
        name -- The name to use for this input in the html
        actions -- Set that is filled with the actions that were used in this input
    """
    # Check if this is to be included by another input
    filename, keepfile = name + ".dat", False
    for line in inpt.splitlines() :
        if "#SETTINGS" in line :
           for word in line.split() :
               if "FILENAME=" in word : filename, keepfile = word.replace("FILENAME=",""), True
    # Manage incomplete inputs
    test_inpt, incomplete = manage_incomplete_inputs( inpt )
    # Write the plumed input to a file
    iff = open( filename, "w+")
    iff.write(test_inpt + "\n")
    iff.close()
    # Now do the test
    broken = test_plumed( "plumed", filename, header="", printjson=True, **test_plumed_kwargs)
    # Retrieve the html that is output by plumed
    html = get_html( inpt, filename, filename, ("master",), (broken,), ("plumed",), actions=actions )
    # Remove the tempory files that we created
    if not keepfile : os.remove(filename)

    return html

def test_plumed( executible, filename, header="", printjson=False, jsondir="./", cmdTimeout:"None|float"=None, ghmarkdown=True ) :
    """
        Test if plumed can parse this input file

        This function can be used to test if PLUMED can parse an input file.  It calls plumed using subprocess

        Keyword arguments:
        executible   -- A string that contains the command for running plumed
        filename     -- A string that contains the name of the plumed input file to parse
        header       -- A string to put at the top of the error page that is output
        printjson    -- Set true if you want to used plumed to print the files containing the expansions of shortcuts and the value dictionary 
        jsondir      -- The directory in which to output the files containing the expansions of the shortcuts and the value dictionaries
        cmdTimeout   -- Set the timeout for the plumed test 
    """
    # Get the information for running the code
    run_folder = str(pathlib.PurePosixPath(filename).parent)
    plumed_file = os.path.basename(filename)
    # Read in the plumed inpt
    nreplicas, natoms, ifile = 1, 100000, open( filename ) 
    for line in ifile.readlines() :
        if "#SETTINGS" in line :
            for word in line.split() :
                if "NREPLICAS=" in word : nreplicas = word.replace("NREPLICAS=","")
                elif "NATOMS=" in word : natoms = word.replace("NATOMS=","")
    ifile.close()
    cmd = [executible, 'driver', '--plumed', plumed_file, '--natoms', str(natoms), '--parse-only', '--kt', '2.49']
    # Add everything to ensure we can run with replicas if needs be
    if int(nreplicas)>1 : cmd = ['mpirun', '--oversubscribe', '-np', str(nreplicas)] + cmd + ['--multi', str(nreplicas)]
    if printjson :
       plumed_file = os.path.basename(filename)
       # Add the shortcutfile output if the user has asked for it 
       cmd = cmd + ['--shortcut-ofile', jsondir + plumed_file + ".json"]
       # Add the value dictionary if the user has asked for it
       cmd = cmd + ['--valuedict-ofile', jsondir + plumed_file + "_values.json"] 
    # raw std output - to be zipped
    outfile=filename + "." + executible + ".stdout.txt"
    # raw std error - to be zipped
    errtxtfile=filename + "." + executible + ".stderr.txt"
    # std error markdown page (with only the first 1000 lines of stderr.txt)
    errfile=filename + "." + executible + ".stderr.md"
    with open(outfile,"w") as stdout:
        with open(errtxtfile,"w") as stderr:
             with cd(run_folder):
                 for bkpf in glob.glob("bck.*") : 
                     if os.path.isfile(bkpf) : os.remove(bkpf)
                 try:
                     plumed_out = subprocess.run(cmd, text=True, stdout=stdout, stderr=stderr, timeout=cmdTimeout )
                     returnCode = plumed_out.returncode
                 except subprocess.TimeoutExpired:
                     returnCode=-1
                    
    # write header and preamble to errfile
    with open(errfile,"w") as stderr:
        if len(header)>0 : 
            print(header,file=stderr)
        print("Stderr for source: ",re.sub("^data/","",filename),"  ",file=stderr)
        print("Download: [zipped raw stdout](" + plumed_file + "." + executible + ".stdout.txt.zip) - [zipped raw stderr](" + plumed_file + "." + executible + ".stderr.txt.zip) ",file=stderr)
        if ghmarkdown : print("{% raw %}\n<pre style=\"overflow:scroll;\">",file=stderr)
        else : print("<pre style=\"overflow:scroll;\">",file=stderr)
        # now we print the first 1000 lines of errtxtfile to errfile
        with open(errtxtfile, "r") as stdtxterr:
          # line counter
          lc = 0
          # print comment
          print("#! Only the first 1000 rows of the error file are shown below", file=stderr)
          print("#! To inspect the full error file, please download the zipped raw stderr file above", file=stderr)
          while True:
            lc += 1
            # read line by line
            line = stdtxterr.readline()
            # if end of file or max number of lines reached, break
            if(not line or lc>1000): break
            # print line to stderr
            print(line.strip(), file=stderr)
          # close stderr
          if ghmarkdown : print("</pre>\n{% endraw %}",file=stderr)
          else : print("</pre>\n",file=stderr)
    # compress both outfile and errtxtfile
    zip(outfile)
    zip(errtxtfile)
    return returnCode

def manage_incomplete_inputs( inpt ) :
   """
      Managet the PLUMED input files for tutorials that should contain solution

      In a tutorial you can create PLUMED input files with the instruction __FILL__
      This tells the tutees they need to add something to that input in order to make the 
      calculation work.  When you add these you should add a corrected input after the version
      with __FILL__ and after the instruction #SOLUTION.  It is this completed input that will be 
      tested

      Keyword arguments:
      inpt -- A string containing the incomplete and complete PLUMED inputs
   """
   if "__FILL__" in inpt :
       insolution, complete, incomplete = False, "", ""
       for line in inpt.splitlines() :
           if "#SOLUTION" in line : insolution=True
           elif insolution : complete += line + "\n"
           elif not insolution : incomplete += line + "\n"
       return complete, incomplete
   return inpt, ""

def get_cltoolfile_html( inpt, name, plumedexe ) :
    """
       Generate an html representation of the input file for a PLUMED command line tool
    
       The html representation of the input to a command line tool has toopltips that tell you what the keywords do.

       Keyword arguments:
       inpt -- A string containing the input you want to get the html for
       name -- The name to use for this input in the html
       plumedexe -- The plumed executibles that were used.  The last one is the one that is used to create the input file annotations
    """ 
    # need to get the name of the command 
    if inpt.splitlines()[0].split("=")[0]!="#TOOL" : raise Exception("could not find tool that this input file is for")
    tool = inpt.splitlines()[0].split("=")[1]
    # Create the lexer that will generate the pretty plumed input
    lexerfile = os.path.join(os.path.dirname(__file__),"PlumedCLFileLexer.py")
    plumed_lexer = load_lexer_from_file(lexerfile, "PlumedCLFileLexer" )
     # Get the plumed syntax file
    defstr, keyword_dict = inpt, getPlumedSyntax( plumedexe )
    # Find the default values in the dictionary
    for key, dicti in keyword_dict["cltools"][tool]["syntax"].items() :
        if "default" not in dicti.keys() or dicti["default"]=="off" or key in inpt : continue
        defstr += "\n" + key + " " + dicti["default"]
    if defstr!=inpt :
        inpt = "#NODEFAULT plumed\n" + inpt + " \n#DEFAULT plumed\n" + defstr + " \n#ENDDEFAULT plumed\n"
    # Setup the formatter 
    formatfile = os.path.join(os.path.dirname(__file__),"PlumedFormatter.py")
    valuedict, actions = {}, set()
    plumed_formatter = load_formatter_from_file(formatfile, "PlumedFormatter", keyword_dict=keyword_dict["cltools"], input_name=name, hasload=False, broken=False, auxinputs=[], auxinputlines=[], valuedict=valuedict, actions=actions, checkaction="" )  
    return highlight( inpt, plumed_lexer, plumed_formatter )

def get_cltoolarg_html( inpt, name, plumedexe ) :
    """
       Generate an html representation of the input to PLUMED command line tool

       The html representation of the input to a command line tool has toopltips that tell you what the keywords do.

       Keyword arguments:
       inpt -- A string containing the input you want to get the html for
       name -- The name to use for this input in the html
       plumedexe -- The plumed executibles that were used.  The last one is the one that is used to create the input file annotations
    """
    # Get the cltool that we are using
    pl, tool = inpt.split()[0], inpt.split()[1]
    if re.search("^mpirun\s+-np\s+[0-9]+\s+plumed",inpt) : 
       tool = inpt.split()[4]
       pl = inpt.split()[3]
    if re.search("^plumed\s+\--no-mpi\s+", inpt) :
       tool = inpt.split()[2]  
    if pl!="plumed" and pl!="plumed-runtime" :
       raise Exception("first word in the command should be plumed or plumed-runtime")
    # Create the lexer that will generate the pretty plumed input
    lexerfile = os.path.join(os.path.dirname(__file__),"PlumedCLtoolLexer.py")
    plumed_lexer = load_lexer_from_file(lexerfile, "PlumedCLtoolLexer" )
    # Get the plumed syntax file
    fileoutstr, defstr, keyword_dict = "", inpt, getPlumedSyntax( plumedexe )
    if ">" in inpt :
       fileoutstr = ">" + inpt.split(">")[1]
       defstr = inpt.split(">")[0]
    # Find the default values in the dictionary
    ishelp = False
    if len(inpt.split())>2 and (inpt.split()[2]=="-h" or inpt.split()[2]=="--help") :
       ishelp = True 
    if not ishelp and keyword_dict["cltools"][tool]["inputtype"]!="file" : 
       for key, dicti in keyword_dict["cltools"][tool]["syntax"].items() :
           if "default" not in dicti.keys() or dicti["default"]=="off" or key in inpt : continue
           defstr += " " + key + " " + dicti["default"]
       if (defstr+fileoutstr)!=inpt :
           inpt = "#NODEFAULT plumed\n" + inpt + " \n#DEFAULT plumed\n" + defstr + fileoutstr + " \n#ENDDEFAULT plumed\n"
    # Setup the formatter
    formatfile = os.path.join(os.path.dirname(__file__),"PlumedFormatter.py")
    valuedict, actions = {}, set()
    plumed_formatter = load_formatter_from_file(formatfile, "PlumedFormatter", keyword_dict=keyword_dict["cltools"], input_name=name, hasload=False, broken=False, auxinputs=[], auxinputlines=[], valuedict=valuedict, actions=actions, checkaction="" )  
    return highlight( inpt, plumed_lexer, plumed_formatter )

def get_html( inpt, name, outloc, tested, broken, plumedexe, usejson=None, maxchecks=None, actions=set({}), ghmarkdown=True, checkaction="", checkactionkeywords=set({}) ) :
    """
       Generate the html representation of a PLUMED input file

       The html representation of a PLUMED input file has tooltips that 
       tell you what the keywords represent, a badge that shows whether the input
       works and clickable labels that provide information about the quantities that 
       are calculated.  This function uses test_plumed to check if the plumed inpt can be parsed.

       Keyword arguments:
       inpt -- A string containing the PLUMED input
       name -- The name to use for this input in the html
       outloc -- The location of the output files that were generated by test_plumed relative to the file that contains the input
       tested -- The versions of plumed that were testd
       broken -- The outcome of running test plumed on the input
       plumedexe -- The plumed executibles that were used.  The first one is the one that should be used to create the input file annotations
       usejson -- Bool that tells you whether or not to look for json files that are generated by plumed driver
       maxchecks -- Maximum number of checks to perform on plumed input.  Set this to reduce computational expense
       actions -- Set to store all the actions that have been used in the input
    """
    
    # Check if we are looking for json files
    if usejson is None :
       searchjson = False
       if not any(broken) : searchjson = True
    else : searchjson = usejson

    # If we find the fill command then split up the input file to find the solution
    inpt, incomplete = manage_incomplete_inputs( inpt )

    # Create a list of all the auxiliary input files that are needed by the plumed input 
    inputfiles, inputfilelines, nreplicas = [], [], 1
    for line in inpt.splitlines() :
        if "#SETTINGS" in line :
           for word in line.split() :
               if "NREPLICAS=" in word : 
                   nreplicas = int(word.replace("NREPLICAS=",""))
               elif "MOLFILE=" in word : 
                   molfile = word.replace("MOLFILE=","")
                   if os.path.isfile(molfile) : 
                      iff = open( molfile, 'r' )
                      content = iff.read()
                      iff.close()
                      inputfiles.append(molfile)
                      inputfilelines.append("1-5")
                      inputfilelines.append( str(len(content.splitlines())-4) + "-" + str(len(content.splitlines())) ) 
                   else :
                      warnings.warn("file " + molfile + " found in MOLFILE setting but file is not present")
               elif "INPUTFILES=" in word : 
                   for n in word.replace("INPUTFILES=","").split(",") : 
                      if os.path.isfile(n) : inputfiles.append( n )
                      else : raise Exception("file " + n + " found in list of INPUTFILES but file is not present")
               elif "INPUTFILELINES=" in word : 
                   inputfilelines = word.replace("INPUTFILELINES=","").split(",")

    # Check for include files
    foundincludedfiles, srcdir = True, str(pathlib.PurePosixPath(name).parent)
    if not any(broken) and "INCLUDE" in inpt : foundincludedfiles, inpt = resolve_includes( srcdir, inpt, nreplicas, foundincludedfiles )

    # Check if there is a LOAD command in the input
    found_load = "LOAD " in inpt

    # Check for shortcut file and build the modified input to read the shortcuts
    if os.path.exists( name + '.json' ) and searchjson :
       # Read json file containing shortcuts
       with open(name + '.json') as f :
           try:
              shortcutdata = json.load(f)
           except json.JSONDecodeError as ve:
              raise Exception("invalid json for shortcut dictionary", ve)
       # Put everything in to resolve the expansions.  We call this function recursively just in case there are shortcuts in shortcuts
       final_inpt = resolve_expansions( inpt, shortcutdata )
    else : final_inpt = inpt  
    # Remove the tempory files that we created
    if os.path.exists( name + '.json' ) : os.remove( name + ".json")  

    # Check for value dictionary to use to create labels
    if os.path.exists( name + '_values.json') and searchjson :
       with open( name + '_values.json') as f :
           try:
              valuedict = json.load(f)
           except json.JSONDecodeError as ve:
              raise Exception("invalid json for value dictionary", ve)
    else : valuedict = {}
    # Remove the tempory files that we created
    if os.path.exists( name + '_values.json') : os.remove( name + "_values.json")

    # Create the lexer that will generate the pretty plumed input
    lexerfile = os.path.join(os.path.dirname(__file__),"PlumedLexer.py")
    plumed_lexer = load_lexer_from_file(lexerfile, "PlumedLexer" )
    # Get the plumed syntax file
    keyword_dict = getPlumedSyntax( plumedexe )
    # Setup the formatter
    formatfile = os.path.join(os.path.dirname(__file__),"PlumedFormatter.py")
    plumed_formatter = load_formatter_from_file(formatfile, "PlumedFormatter", keyword_dict=keyword_dict, input_name=name, hasload=found_load, broken=any(broken), auxinputs=inputfiles, auxinputlines=inputfilelines, valuedict=valuedict, actions=actions, checkaction=checkaction )

    # Now generate html of input
    html = '<div class="plumedInputContainer">\n'
    html += '<div class="plumedpreheader">\n'
    html += f'<div class="headerInfo" id="value_details_{name}"> Click on the labels of the actions for more information on what each action computes </div>\n'
    html += '<div class="containerBadge">\n'
    for i in range(len(tested)) :
        html +='<div class="headerBadge">'
        btype = 'passing-green.svg'
        if broken[i] :
           btype = 'failed-red.svg'
        #this if can be collapsed in a f'<a href="{"" if ghmarkdown else "../"}{outloc}.{plumedexe[i]}.stderr">'
        #but like this it might be clearer, what do you think?
        if ghmarkdown :
           html += f'<a href="{outloc}.{plumedexe[i]}.stderr">'
        else :
           html += f'<a href="../{outloc}.{plumedexe[i]}.stderr">'
        html += f'<img src="https://img.shields.io/badge/{tested[i]}-{btype}" alt="tested on{tested[i]}" />'
        html += '</a>'
        html += '</div>\n'

    if found_load :
       html += '<div class="headerBadge">'
       html += '<img src="https://img.shields.io/badge/with-LOAD-yellow.svg" alt="tested on master" />'
       html += '</div>\n'

    if len(incomplete)>0 : 
       html += '<div class="headerBadge">'
       html += f'<img class="toggler" src="https://img.shields.io/badge/{tested[-1]}-incomplete-yellow.svg" alt="tested on {tested[-1]}"'
       html += f" onmouseup='toggleDisplay(\"{name}\")' onmousedown='toggleDisplay(\"{name}\")'/>"
       html += "</div>\n"

    html += '</div>\n</div>\n' 

    if len(incomplete)>0 : 
       # This creates the input with the __FILL__ 
       html += "<div id=\"" + name + "_short\">\n"
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( incomplete, plumed_lexer, plumed_formatter )
       html += "</div>\n"
       # This is the solution with the commplete input
       html += "<div style=\"display:none;\" id=\"" + name + "_long\">"
       plumed_formatter.egname = plumed_formatter.egname + "_sol"
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( final_inpt, plumed_lexer, plumed_formatter )
       html += '</div>\n'
    else : 
       # html += highlight( final_inpt, plumed_lexer, HtmlFormatter() )
       html += highlight( final_inpt, plumed_lexer, plumed_formatter )
    #close the html = '<div class="plumedInputContainer">\n'
    html += '</div>\n'
    # Now remove keywords that appear in examples
    mykeywords = plumed_formatter.getCheckActionKeywords()
    for key in mykeywords : 
        if key in checkactionkeywords :
           checkactionkeywords.remove(key)

    # Test output is valid parsable html
    try :
       etree.parse(StringIO(html), etree.HTMLParser(recover=False))
    except etree.XMLSyntaxError as e:
       raise Exception("Generated html is invalid as " + str(e.error_log) + " plumed input is \n\n" + final_inpt ) from e

    # Check everything that is marked as a clickable value has something that will appear
    # when you click it
    nchecks, soup = 0, BeautifulSoup( html, "html.parser" )
    for val in soup.find_all("b") :
        if "onclick" in val.attrs.keys() :
           nchecks, vallabels = nchecks + 1, val.attrs["onclick"].split("\"")
           if maxchecks is not None and nchecks>maxchecks : 
              warnings.warn("Only checked the html for the first " + str(maxchecks) + " of the " + str(len(soup.find_all("b"))) + " labels in input file to reduce computational expense. The output is most likely fine but has not been checked as carefully as inputs with fewer values")
              break
           if not soup.find("span", {"id": vallabels[3]}) : warnings.warn("Problems with generated as label hidden box for label " + vallabels[3] + " is missing")
           if not soup.find("div", {"id": "value_details_" + vallabels[1]}) : raise Exception("Generated html is invalid as there is no place to show data for " + vallabell[1])

    # Now check the togglers
    nchecks = 0 
    for val in soup.find_all(attrs={'class': 'toggler'}) :
        nchecks = nchecks + 1 
        if maxchecks is not None and nchecks>maxchecks : 
           warnings.warn("Only checked the html for the first " + str(maxchecks) + " of the " + str(len(soup.find_all(attrs={'class': 'toggler'}))) + " shortcuts in the input file to reduce computational expense. The output is most likely fine but has not been checked as carefully as inputs with fewer shortcuts")
           break
        if "onclick" in val.attrs.keys() :
           switchval = val.attrs["onclick"].split("\"")[1]
           if not soup.find("span",{"id": switchval + "_long"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_long") 
           if not soup.find("span",{"id": switchval + "_short"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_short")
        elif "onmousedown" in val.attrs.keys() :
           switchval = val.attrs["onmousedown"].split("\"")[1]
           if not soup.find("div",{"id": switchval + "_long"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_long")
           if not soup.find("div",{"id": switchval + "_short"} ) : raise Exception("Generated html is invalid as could not find " + switchval + "_short")
        else : raise Exception("Could not find toggler command for " + val)
    return html

def get_mermaid( executible, inpt, force,*, test_plumed_kwargs={} ) :
    """
     Generate the mermaid graph showing how data passes through PLUMED input file

     Keyword arguments:
     inpt -- A string containing the PLUMED input
     force -- Bool that if true ensures we show the graph for the backwards pass through the action list
     test_plumed_kwargs -- a dictionary of extra keywords to pass to the test_plumed utility, useful for passing an"header"
    """
    # Write the plumed input to a file
    iff = open( "mermaid_plumed.dat", "w+")
    iff.write(inpt+ "\n")
    iff.close()
    # Now check the input is OK
    broken = test_plumed( executible, "mermaid_plumed.dat",**test_plumed_kwargs)
    if broken!=0 : raise Exception("invalid plumed input file -- cannot create mermaid graph")
    # Run mermaid
    cmd = [executible, 'show_graph', '--plumed', 'mermaid_plumed.dat', '--out', 'mermaid.md']
    if force : cmd.append("--force")
    plumed_out = subprocess.run(cmd, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT )
    if plumed_out.returncode!=0 : raise Exception("error running plumed show_graph")
    mf = open("mermaid.md")
    mermaid = mf.read()
    mf.close()
    # Remove stuff that was created
    os.remove("mermaid_plumed.dat")
    os.remove("mermaid.md")
    return mermaid 

def resolve_includes( srcdir, inpt, nreplicas, foundfiles ) :
    if not foundfiles or "INCLUDE" not in inpt : return foundfiles, inpt

    incontinuation, final_inpt, clines = False, "", "" 
    for line in inpt.splitlines() :
        # Empty the buffer that holds the input for this line if we are not in a continuation
        if not incontinuation : clines = ""
        # Check for start and end of continuation
        if "..." in line and incontinuation : incontinuation=False
        elif "..." in line and not incontinuation : incontinuation=True
        # Build up everythign that forms part of input for one action
        clines += line + "\n"
        # Just continue if we don't have the full line
        if incontinuation : continue

        # Now check if there is an include
        if "INCLUDE" in clines :
           # Split up the line 
           iscomment, filename = False, ""
           for w in clines.split():
               if "#" in w and filename=="" : iscomment=True
               elif "FILE=" in w : filename = w.replace("FILE=","") 
           if iscomment : 
              final_inpt += clines 
              continue
           if filename=="" : raise Exception("could not find name of file to include")
           if not os.path.exists(filename) : foundfiles = False 
           splitname = filename.rsplit(".",1)
           if len(splitname)>2 : raise Exception("cannot deal with included file named " + filename )

           final_inpt += "#SHORTCUT " + filename + "\n" + clines + "#EXPANSION " + filename + "\n# The command:\n"
           final_inpt += "# " + clines+ "# ensures PLUMED loads the contents of the file called " + filename + "\n" 
           if nreplicas>1 and os.path.exists( srcdir + "/" + splitname[0] + ".0." + splitname[1] ) :
              final_inpt += "# There are different versions of this file on each replica\n"
              for i in range(nreplicas) : 
                  f = open( srcdir + "/" + splitname[0] + "." + str(i) + "." + splitname[1], "r" )
                  include_contents = f.read()
                  f.close() 
                  final_inpt += "# The contents of the version of this file (" + splitname[0] + "." + str(i) + "." + splitname[1] + ") on replica " + str(i) + " is shown below.\n"
                  foundfiles, parsed_inpt = resolve_includes( srcdir, include_contents, nreplicas, foundfiles )
                  final_inpt += parsed_inpt
              final_inpt += "#(click the red comment to hide this expanded text).\n"
              if final_inpt.endswith("\n") : final_inpt += "#ENDEXPANSION " + filename + "\n"
              else : final_inpt += "\n#ENDEXPANSION " + filename + "\n"
           else : 
              f = open( srcdir + "/" + filename, "r" )
              include_contents = f.read()
              f.close()
              final_inpt += "# The contents of this file are shown below (click the red comment to hide them).\n" 
              foundfiles, parsed_inpt = resolve_includes( srcdir, include_contents, nreplicas, foundfiles )
              if parsed_inpt.endswith("\n") : final_inpt += parsed_inpt + "#ENDEXPANSION " + filename + "\n"
              else : final_inpt += parsed_inpt + "\n#ENDEXPANSION " + filename + "\n"
        else : final_inpt += clines         
    return foundfiles, final_inpt


def resolve_expansions( inpt, jsondata ) :
    # Stop expanding if we have reached the bottom 
    if len(jsondata.keys())==0 : return inpt + "\n"

    incontinuation, final_inpt, clines = False, "", ""
    for line in inpt.splitlines() :        
        # Empty the buffer that holds the input for this line if we are not in a continuation
        if not incontinuation : clines = ""
        # Check for start and end of continuation
        if "..." in line and incontinuation : incontinuation=False
        elif "..." in line and not incontinuation : incontinuation=True
        # Build up everythign that forms part of input for one action
        clines += line + "\n"
        # Just continue if we don't have the full line
        if incontinuation : continue
        # Find the label of this line if it has one
        label = ""
        if "LABEL=" in clines :
           afterlab = clines[clines.index("LABEL=") + len("LABEL="):]
           label = afterlab.split()[0]
        elif clines.find(":") : label = clines.split(":")[0].strip()
        if len(label)>0 and label in jsondata :
           if "expansion" in jsondata[label] :
              final_inpt += "#SHORTCUT " + label + "\n"
              if "defaults" in jsondata[label] : final_inpt += "#NODEFAULT " + label + "\n" + clines
              else : final_inpt += clines
              # Add long version with defaults to input 
              if "defaults" in jsondata[label] and "..." in clines :
                 alldat, bef = clines.split("\n"), ""
                 for i in range(len(alldat)-2) : bef += alldat[i] + "\n"
                 final_inpt += "#DEFAULT " + label + "\n" + bef + jsondata[label]["defaults"] + "\n" + alldat[-2] + "\n#ENDDEFAULT " + label + "\n"
              elif "defaults" in jsondata[label]  : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jsondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
              # Add stuff for long version of input in collapsible
              final_inpt += "#EXPANSION " + label + "\n# PLUMED interprets the command:\n"
              for gline in clines.splitlines() : final_inpt += "# " + gline + "\n"
              local_json = dict(jsondata[label]) 
              local_json.pop("expansion", "defaults" )
              final_inpt += "# as follows (Click the red comment above to revert to the short version of the input):\n" + resolve_expansions( jsondata[label]["expansion"], local_json )
              final_inpt += "#ENDEXPANSION " + label + "\n"
           elif "defaults" in jsondata[label] :
              final_inpt += "#NODEFAULT " + label + "\n" + clines
              if "..." in clines :
                 alldat, bef = clines.split("\n"), ""
                 for i in range(len(alldat)-2) : bef += alldat[i] + "\n"
                 final_inpt += "#DEFAULT " + label + "\n" + bef + jsondata[label]["defaults"] + "\n" + alldat[-2] + "\n#ENDDEFAULT " + label + "\n"
              else : final_inpt += "#DEFAULT " + label + "\n" + clines.strip() + " " + jsondata[label]["defaults"] + "\n#ENDDEFAULT " + label + "\n"
        else : final_inpt += clines
    return final_inpt

def get_html_header() :
    """
       Get the information that needs to go in the header of the html file to make the interactive PLUMED
       inputs work
    """
    headerfilename = os.path.join(os.path.dirname(__file__),"assets/header.html")
    hfile = open( headerfilename )
    codes = hfile.read()
    hfile.close()
    return codes

def get_javascript() :
    """
       Get the javascript from the header of the html file to make the interactive PLUMED inputs work
    """
    inscript, fullheader, jscode = False, get_html_header().splitlines(), ""
    for line in fullheader :
        if "</script>" in line and inscript :
            inscript = False
            break
        elif "<script>" in line :
            inscript = True
        elif inscript :
            if ("<style>" in line) or ("</style>" in line) or ("<script>" in line) or ("</script>" in line) : 
               raise Exception('found invalid html tag in javascript line ' + line)
            jscode += line + "\n"
    return jscode

def get_css() :
    """
       Get the css from the header of the html file to make the interactive PLUMED inputs work
    """
    inscript, fullheader, css = False, get_html_header().splitlines(), ""
    for line in fullheader :
        if "</style>" in line and inscript :
            inscript = False
            break
        elif "<style>" in line :
            inscript = True
        elif inscript :
            if ("<style>" in line) or ("</style>" in line) or ("<script>" in line) or ("</script>" in line) : 
               raise Exception('found invalid html tag in css line ' + line)
            css += line + "\n"               
    return css 

def compare_to_reference( output, reference ) :
    """
      Compare the html that is output by PlumedFormatter with the reference data.  This function is used for 
      testing PlumedToHMTL
    """
    soup = BeautifulSoup( output, "html.parser" ) 
    # Check that comments in PLUMED input have been detected correctly
    if "comment" in reference.keys() :
       soup_comments = soup.find_all(attrs={'class': 'comment'})
       if len(soup_comments)!=len(reference["comments"]) : return False
       for i in range(len(soup_comments)) :
           if soup_comments[i].get_text()!=reference["comments"][i] : return False

    print("Comments fine")
    # Check that everything that should be rendered as a tooltip has been rendered as a tooltip
    # This is action names and keywords
    if "tooltips" in reference.keys() :
       soup_tooltips = soup.find_all(attrs={'class': 'plumedtooltip'})
       print("CHECK TOOLTIP",  soup_tooltips )
       print("TOOLTIP NUMBER CORRECT", len(soup_tooltips), len(reference["tooltips"]))
       if len(soup_tooltips)!=len(reference["tooltips"]) :
         print ("REFERENCE tooltips: ",reference["tooltips"])
         print ("FOUND tooltips:     ",[x.contents[0] for x in soup_tooltips])
         return False
       for i in range(len(soup_tooltips)) :
           print("COMPARISON", soup_tooltips[i].contents[0], reference["tooltips"][i] )
           if soup_tooltips[i].contents[0]!=reference["tooltips"][i] : return False

    return True

def processMarkdown( filename, plumedexe, plumed_names, actions, jsondir="./", ghmarkdown=True,
        *,test_plumed_kwargs={} ) :
    """
        Process a markdown file that contains PLUMED input files using PlumedtoHTML

        Keyword arguments:
        filename -- the name of the markdown file
        plumedexe -- a tuple of plumed executible names for testing plumed.
        plumed_names -- the names of the plumed executibles to use in the badges
        actions -- names of actions used in the plumed inputs in this markdown file
        jsondir -- The directory in which to output the files containing the expansions of the shortcuts and the value dictionaries 
        test_plumed_kwargs -- a dictionary of extra keywords to pass to the test_plumed utility, only "header" and "cmdTimeout" works
    """
    if not os.path.exists(filename) :
       raise RuntimeError("Found no file called " + filename + " in lesson")

    with open( filename, "r" ) as f:
       inp = f.read()

    with open( filename, "w+" ) as ofile: 
       ninputs, nfail = processMarkdownString( inp, filename, plumedexe, plumed_names,
               actions, ofile, jsondir, ghmarkdown, test_plumed_kwargs=test_plumed_kwargs )
    return ninputs, nfail

def processMarkdownString( inp, filename, plumedexe, plumed_names, actions, ofile,
        jsondir="./", ghmarkdown=True, checkaction="ignore", checkactionkeywords=set({}),
        *,test_plumed_kwargs={}) :
    """
       Process a string of markdown that contains LUMED input files using PlumedtoHTML

        Keyword arguments:
        inp -- the string that contains the plumed input file
        filename -- a name to use for the plumed inputs we create 
        plumedexe -- a tuple of plumed executible names for testing plumed.
        plumed_names -- the names of the plumed executibles to use in the badges
        actions -- names of actions used in the plumed inputs in this markdown file
        dirname -- the directory in which to find solution files
        ofile -- the file on which to output the processed markdown
        jsondir -- The directory in which to output the files containing the expansions of the shortcuts and the value dictionaries 
        test_plumed_kwargs -- a dictionary of extra keywords to pass to the test_plumed utility, only "header" and "cmdTimeout" works
    """
    dirname = os.path.dirname(filename)
    if dirname=="" : dirname = "." 

    ninputs = 0
    nfail = len(plumedexe)*[0]
    inplumed = False
    plumed_inp = ""
    solutionfile = None
    incomplete = False
    usemermaid = ""
    # Create a collection of cltools to regexp for
    plumed_syntax = getPlumedSyntax( plumedexe )
    cltoolregexps, clfileregexps = [], []
    for key, data in plumed_syntax["cltools"].items() :
        cltoolregexps.append("plumed\s+" + key )
        cltoolregexps.append("plumed\s+--no-mpi\s+" + key )
        cltoolregexps.append("plumed-runtime\s+" + key )
        if data["inputtype"]=="file" :
           clfileregexps.append( "#TOOL\s*=\s*" + key )

    for line in inp.splitlines() :
       # Detect and copy plumed input files 
       if "```plumed" in line :
          inplumed = True
          plumed_inp = ""
          solutionfile = None
          incomplete = False
          ninputs = ninputs + 1 
    
       # Test plumed input files that have been found in tutorial 
       elif inplumed and "```" in line :
          skipplumedfile, inplumed = False, False
          # Create mermaid graphs from PLUMED inputs if this has been requested
          if usemermaid!="" :
             skipplumedfile, mermaidinpt = True, ""
             if usemermaid=="value" :
                mermaidinpt = get_mermaid( plumedexe[-1], plumed_inp, False,
                        test_plumed_kwargs=test_plumed_kwargs)
             elif usemermaid=="force" :
                mermaidinpt = get_mermaid( plumedexe[-1], plumed_inp, True,
                        test_plumed_kwargs=test_plumed_kwargs)
             else :
                raise RuntimeError(usemermaid + "is invalid instruction for use mermaid")
             if ghmarkdown : ofile.write("```mermaid\n" + mermaidinpt + "\n```\n")
             else : ofile.write("<pre class=\"mermaid\">\n" + mermaidinpt + "\n</pre>\n")
             usemermaid = ""

          # Check if this is the input for a command line tool and render accordingly
          for tool in cltoolregexps :
              if re.search( tool, plumed_inp ) :
                 html = get_cltoolarg_html( plumed_inp, "cltool" + str(ninputs), plumedexe )
                 if ghmarkdown : ofile.write( "{% raw %}\n" + html + "\n {% endraw %} \n" )
                 else : ofile.write( html )
                 skipplumedfile = True

          # Check if this the input file for a command line tool and render accordingly
          for tool in clfileregexps :
              if re.search( tool, plumed_inp ) :
                 html = get_cltoolfile_html( plumed_inp, "cltool" + str(ninputs), plumedexe )
                 if ghmarkdown : ofile.write( "{% raw %}\n" + html + "\n {% endraw %} \n" )
                 else : ofile.write( html )
                 skipplumedfile = True 

          if incomplete :
                if solutionfile:
                   # Read solution from solution file
                   try:
                      with open( dirname + "/" + solutionfile, "r" ) as sf:
                         solution = sf.read()
                         plumed_inp += "#SOLUTION \n" + solution
                      solutionfile = dirname + "/" + solutionfile
                   except:
                      raise RuntimeError(f"error in opening {solutionfile} as solution"
                                        f" for an incomplete input from file {filename}")
                else:
                   raise RuntimeError(f"an incomplete input from file {filename}"
                                     " does not have its solution file")
          # Create the full input for PlumedToHTML formatter 
          else :
                solutionfile = filename + "_working_" + str(ninputs) + ".dat"
                with open( solutionfile, "w+" ) as sf:
                   sf.write( plumed_inp )
    
          # Test whether the input solution can be parsed
          if not skipplumedfile : 
             success = len(plumedexe)*[False] 
             for i in range(len(plumedexe)) : 
                 if i==len(plumedexe)-1 : 
                    # Json files are put in directory one up from us to ensure that
                    # PlumedToHTML finds them when we do get_html (i.e. these will be in
                    # the data directory where the calculation is run)
                    if incomplete :
                       success[i]=test_plumed(plumedexe[i], solutionfile, ghmarkdown=ghmarkdown,
                               **test_plumed_kwargs)
                    else :                        
                       success[i]=test_plumed(plumedexe[i], solutionfile,
                                                  printjson=True, jsondir=jsondir, ghmarkdown=ghmarkdown,
                                                  **test_plumed_kwargs)
                 else : 
                    success[i]=test_plumed( plumedexe[i],
                            solutionfile,
                            ghmarkdown=ghmarkdown,
                            **test_plumed_kwargs,)
                 if(success[i]!=0 and success[i]!="custom") : nfail[i] = nfail[i] + 1
             # Use PlumedToHTML to create the input with all the bells and whistles
             html = get_html(plumed_inp,
                               solutionfile,
                               os.path.basename(solutionfile),
                               plumed_names,
                               success,
                               plumedexe, 
                               usejson=(not success[-1]),
                               actions=actions,
                               ghmarkdown=ghmarkdown,
                               checkaction=checkaction,
                               checkactionkeywords=checkactionkeywords )
             # Print the html for the solution
             if ghmarkdown : ofile.write( "{% raw %}\n" + html + "\n {% endraw %} \n" )
             else : ofile.write( html )
       # This finds us the solution file
       elif inplumed and "#SOLUTIONFILE=" in line :
          solutionfile=line.strip().replace("#SOLUTIONFILE=","")
       elif inplumed and "#MERMAID=" in line :
          usemermaid = line.replace("#MERMAID=","").strip()
       elif inplumed :
          if "__FILL__" in line :
             incomplete = True
          plumed_inp += line + "\n"
       # Just copy any line that isn't part of a plumed input
       elif not inplumed :
          ofile.write( line + "\n")

    return ninputs, nfail 

