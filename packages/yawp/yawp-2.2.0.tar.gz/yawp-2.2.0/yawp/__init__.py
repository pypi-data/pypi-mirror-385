#!/usr/bin/env python3

'''Yet Another Word Processor, a Windows/Linux word processor for plain text files, with PDF export

"YAWP" here means Yet Another Word Processor, and YAWP is a pure-Python Linux-only free
and  open-source  word  processor  for plain text files, with PDF export. If you really
need  all  the endless features of a full-fledged WYSIWYG word processor as LibreOffice
Writer,  YAWP  is  not  for  you.  But  if  you just want to create a draft or a simple
quick-and-dirty no-frills document, give YAWP a try.

YAWP's main features are:

    • YAWP has a GUI interface, but can be used as a CLI command too
    • YAWP  processes in place a single plain text file, hereinafter referred to simply
      as the "text file"
    • YAWP's  default  editor  allows  you to edit the text file and check its spelling
      correctness
    • YAWP  before  rewriting the text file creates a timestamped backup, allowing Undo
      operation
    • YAWP justifies text at left and right in:
        • unindented paragraphs
        • dot-marked indented paragraphs (as this one)
    • YAWP  text  processing  is  driven  by the text in the text file and by arguments
      only, not by commands or tags embedded in text
    • YAWP  accepts  unjustified pictures (as schemas, tables and code examples) freely
      intermixed with text
    • YAWP  performs  automatic  multi-level  renumbering  of  chapters  and inserts an
      automatic Contents chapter in the text file
    • YAWP  recognizes relevant subjects (quoted by '"') and inserts an automatic Index
      chapter in the text file
    • YAWP performs automatic multi-level renumbering of figure captions and inserts an
      automatic Figures chapter in the text file
    • YAWP  cuts  the text file in pages, by inserting two-lines page headers, allowing
      page numbering control and insertion of initial Roman-numbered pages
    • YAWP also has some graphics capabilities, you can sketch pictures with horizontal
      and  vertical  segments  (by  '`')  and arrowheads (by '^'), YAWP redraws them by
      suitable Unicode graphic characters
    • pictures can also be left-aligned, centered or right-aligned
    • YAWP  exports  the  text file in PDF format, with control over character size and
      page  layout,  and  lets  you browse the generated PDF file, allowing preview and
      printing
    • YAWP  can export 2, 4 or 8 pages on each paper sheet side, allowing you to create
      in folio, in quarto and in octavo booklets
    • YAWP writes information and error messages on terminal and on the log file of the
      text file
    • YAWP  tries  to correct errors made by CUPS-PDF about font size and page margins,
      you can use default corrections or redefine them by a correction file
    • YAWP locks text files while they are processed, in order to avoid interference by
      other concurrent YAWP executions
    • YAWP in GUI mode keeps a distinct argument file for each text file
    • YAWP  in  GUI mode saves the name of the last processed text file and restores it
      at next invocation
    • YAWP  in  GUI mode saves a list of the 25 most recent processed text files, among
      which you can select the next current text file

As an example of CLI usage, the YAWP User Manual has been generated as

    'YAWP 2.2.0 User Manual.txt.pdf'

from the text file

    'YAWP 2.2.0 User Manual.txt'

by typing at terminal:

    │ $ yawp -M f -v -w 97 -n -4 -X e -L 3cm 'YAWP 2.2.0 User Manual.txt'

where arguments mean:

    • -M f: run YAWP in CLI Format mode
    • -v: write messages not only into log file but also on terminal
    • -w 97: set 97 characters per line
    • -n -4: first four pages are numbered by Roman numbers
    • -X e: export in PDF format
    • -L 3cm: set left margins on odd pages and right margins on even pages to 3 cm
    • 'YAWP 2.2.0 User Manual.txt': set the text file to process

To install YAWP, if your Linux belongs to the Debian family, type at terminal:

    │ $ sudo apt install kwrite idle atril printer-driver-cups-pdf pipx

On other platforms you will use the specific installer instead, for instance:

    │ $ sudo yum install …        # on RHEL/CentOS/Fedora/Rocky/Alma Linux
    │ $ sudo emerge -a sys-apps/… # on Gentoo Linux
    │ $ sudo apk add …            # on Alpine Linux
    │ $ sudo pacman -S …          # on Arch Linux
    │ $ sudo zypper install …     # on OpenSUSE Linux

Then run:

    │ $ pipx ensurepath
    │ $ pipx install yawp

Later you can type:

    │ $ pipx upgrade yawp

in order to upgrade YAWP to a later version.

Now you can close the terminal, open another one, and call YAWP. Syntax is:

    │ $ yawp -h               # show a help message and exit
    │ $ yawp -V               # show program's version number and exit
    │ $ yawp -H […arguments…] # browse the PDF YAWP User Manual and exit

    │ $ yawp # run YAWP in GUI mode, text file from last closed session, no arguments
    │ $ yawp text_file [text_file [...]] # GUI mode, explicit text file[s]
    │                                    # no other arguments

    │ $ yawp -M c […arguments…] text_file target_file # run YAWP in CLI Copy mode
    │ $ yawp -M m […arguments…] text_file target_file # run YAWP in CLI Move mode
    │ $ yawp -M d […arguments…] text_file             # run YAWP in CLI Delete mode
    │ $ yawp -M e […arguments…] text_file             # run YAWP in CLI Edit mode
    │ $ yawp -M f […arguments…] text_file             # run YAWP in CLI Format mode
    │ $ yawp -M n […arguments…] text_file             # run YAWP in CLI Noform mode
    │ $ yawp -M u […arguments…] text_file             # run YAWP in CLI Undo mode

This is the GUI Main window, with default argument values:

 ┌───┬────────────────────────────────────────────────────────────────────────┬───┬───┐
 │   │                                 YAWP - Main                            │ _ │ x │
 ├───┴────────────────────────────────────────────────────────────────────────┴───┴───┤
 │ Format   -y --text-editor    [kwrite…………]        -l --left-only-text □           ■ │
 │          -w --chars-per-line [0……] -g --graph-pictures □   -b --left-blanks [1……]  │
 │          -u --lines-per-page [0……] -k --align-pictures ◎ no ○ left ○ center ○ right│
 │ Chapters -c --contents-title [Contents……]        -i --index-title    [Index……………]  │
 │          -f --figures-title  [Figures………]        -F --caption-prefix [Figure…………]  │
 │          -m --chapter-offset [0……]                                                 │
 │ Pages    -p --page-headers ○ no ○ fullpage ○ pture ◎ chapter ○ double              │
 │          -e --even-left      [%n……………………]        -E  --even-right    [%f……………………]  │
 │          -o --odd-left       [%c……………………]        -O --odd-right      [%n……………………]  │
 │          -n --page-offset    [0……]               -a --all-pages-E-e  □             │
 │          -s --second-line ○ no ○ blank ○ points ○ dashes ◎ solid                   │
 │ Export   -X --export-pdf ◎ no ○ export ○ browse  -C --correct ○ no ◎ default ○ file│
 │          -Y --pdf-browser    [atril……………]        -P --pdf-file       [%f%e.pdf……]  │
 │          -W --char-width     [0……]               -A --char-aspect    [3/5]         │
 │          -S --sheet-size     [A4……………………]        -Z --landscape      □             │
 │          -L --left-margin    [2cm]               -R --right-margin   [2cm]         │
 │          -T --top-margin     [2cm]               -B --bottom-margin  [2cm]         │
 │          -I --multi-pages ◎ 1 ○ 2 ○ 4 ○ 8        -J --multi-sheets   [0……]         │
 │ Text File ……………………………………………………………………………………………………………………………………………………………………………………………… │
 │┌───┐┌────┐┌──────┐┌────┐┌────┐┌──────┐┌────┐┌──────┐┌──────┐┌────┐┌───┐┌────┐┌────┐│
 ││New││Open││Recent││Copy││Move││Delete││Edit││Format││Noform││Undo││Log││Help││Exit││
 │└───┘└────┘└──────┘└────┘└────┘└──────┘└────┘└──────┘└──────┘└────┘└───┘└────┘└────┘│
 └────────────────────────────────────────────────────────────────────────────────────┘

These are the 13 buttons in GUI Main window:

    • text file definition:
        • New: create a new empty text file
        • Open: browse the file system to select an existing text file
        • Recent: browse the list of recent files to select an existing text file
        • Copy: copy the current text file into a new target text file
        • Move: move or rename the current text file
        • Delete: permanently delete the current text file
    • text file processing:
        • Edit: edit the current text file by the text editor defined by -y
        • Format: format the current text file and redraw and align pictures and export
          PDF
        • Noform:  don't  format  current  text  file but redraw and align pictures and
          export PDF
        • Undo: restore the current text file to its previous content
        • Log:  browse  the log file of current text file by the text editor defined by
          -y
    • other actions:
        • Help:  browse  the YAWP-generated YAWP User Manual by the PDF browser defined
          by -Y
        • Exit: quit YAWP

'''

#----- constants -----

__version__ = '2.2.0' # YAWP present version
VERSION_DATE = '2025-10-20' # 'YYYY-mm-dd' date of YAWP present version
ECHO = False # echo at console the commands passed to shell() (for debug only!)
ROUND = 5 # decimal digits in float representation
phi = 1.618033988749895 # golden ratio
STRIP_CHARS = ' \n\r\t' # chars for strip(), no other whitespace chars (as formfeed '\f' or no-break space '\xa0') are stripped

#----- characters -----

BELLCHAR  = '\a' # bell
BACKSPACE = '\b' # backspace
HORIZTAB  = '\t' # horizontal tab
LINEFEED  = '\n' # line feed
VERTTAB   = '\v' # vertical tab
FORMFEED  = '\f' # form feed
CARRETURN = '\r' # carriage return
NBSPACE   = '\xa0' # no-break space
DOTABOVE  = '˙'  # dot above
MACRON    = '¯'  # macron
OVERLINE  = '‾'  # overline
FRAME1ST  = '┌'  # first char of the string returned by frame()

#----- 8 colors -----

#          '#RRGGBB'
BLACK     ='#000000'
BLUE      ='#0000FF'
GREEN     ='#00FF00'
TURQUOISE ='#00FFFF'
RED       ='#FF0000'
CYAN      ='#FF00FF'
YELLOW    ='#FFFF00'
WHITE     ='#FFFFFF'

#----- imports -----

from fnmatch import fnmatchcase
from glob import glob
from itertools import count
from os import chdir, getpid, lstat, makedirs, rename, popen, remove, sep as pathsep
from os.path import split as splitpath, abspath, expanduser, getmtime, getsize, normpath, splitext, exists, isfile, isdir, islink, basename, dirname
from shutil import copy2, which
from subprocess import run, PIPE
from sys import exit, stdout, stderr
from time import localtime, sleep, time

from sys import platform
windows = platform.startswith('win')

if windows:
    getpwuid = lambda uid: ['']
    getgrgid = lambda gid: ['']
else:
    from pwd import getpwuid
    from grp import getgrgid
    import readline

#----- two-chars functions -----

def cp(file, file2):
    'copy file into file2, if existing, else remove file2'
    if isfile(file):
        try:
            copy2(file, file2)
            return f'Copy:\n    {file!r} →\n    {file2!r}'
        except:
            return None
    elif isfile(file2):
        try:
            remove(file2)
            return f'Remove:\n    {file2!r}'
        except:
            return None

def mv(file, file2):
    'move file into file2, if existing'
    try:
        rename(file, file2)
        return f'Move:\n    {file!r} →\n    {file2!r}'
    except:
        return None

def rm(file):
    'remove file, if existing'
    try:
        remove(file)
        return f'Remove:\n    {file!r}'
    except:
        return None
    
def cd(path):
    'change directory to path, if possible'
    try:
        chdir(path)
    except:
        pass

def md(path):
    'make directory, if possible'
    try:
        makedirs(path)
    except:
        pass

#----- various functions -----

def tryfunc(func, *args):
    'try: return func(*args); except: return None'
    try:
        return func(*args)
    except:
        return None

def timefunc(n, func, *args):
    'howmany seconds to call func(*args) n times?'
    t0 = time()
    for j in range(n):
        func(*args)
    return time() - t0

def check(assertion):
    'if not assertion: raise ValueError'
    if not assertion:
        raise ValueError

def types(*args):
    '>>> types(var1, typ1, var2, (typ2a, typ2b))'
    check(len(args) % 2 == 0)
    for var, type in slices(args, 2):
        if not isinstance(var, type):
            raise TypeError

def ints(*args):
    '''integer generator similar to range(), but endless if stop is None
it can be:
    ints() -> ints(0, None, 1)
    ints(stop) -> ints(0, stop, 1)
    ints(start, stop) -> ints(start, stop, 1)
    ints(start, stop, step)'''
    if not args:
        index, stop, step = 0, None, 1
    elif len(args) == 1:
        index, stop, step = 0, args[0], 1
    elif len(args) == 2:
        index, stop = args; step = 1
    elif len(args) == 3:
        index, stop, step = args
    else:
        raise ValueError('ints: args must be less than 4')
    if stop is None:
        while True:
            yield index
            index += step
    elif step > 0:
        while index < stop:
            yield index
            index += step
    elif step < 0:
        while index > stop:
            yield index
            index += step
    else:
        raise ValueError('ints: if stop is not None then step can not be zero')

def pid_date_time():
    'unique instance signature'
    return f'{getpid()} {now(digits=6)}'

def show(names, values):
    types(names, str, values, list)
    names = [name.strip() for name in names.split(',')]
    check(len(names) == len(values))
    width = max(len(name) for name in names)
    for name, value in zip(names, values):
        print(f'{name:{width}} = {value!r}')

#----- string functions -----

def hold(string, charpattern, default='', joinby=''):
    'hold charpattern-matching chars in string and replace not matching chars with default'
    return joinby.join(char if fnmatchcase(char, charpattern) else default for char in string)

def take(string, charset, default='', joinby=''):
    'take chars in string found in charset and replace not found chars with default'
    return joinby.join(char if char in charset else default for char in string)

def drop(string, charset, default='', joinby=''):
    'drop chars in string found in charset and replace not found chars with default'
    return joinby.join(default if char in charset else char for char in string)

def chars(charpattern):
    'return a sorted string of all charpattern-matching characters'
    kernel = charpattern[1:-1]
    a, z = ord(min(kernel)), ord(max(kernel)) + 1
    return ''.join(chr(j) for j in range(a, z) if fnmatchcase(chr(j), charpattern))

def line2stmt(line):
    """return stripped statement, removing '#'-comments,
but preserving '#' quoted by "'" or '"' or '\…' """
    auto = 0; value = ''
    for char in line:
        if auto == 0:
            if char == '#': break
            elif char == '\\': value += char; auto = 10
            elif char == "'": value += char; auto = 1
            elif char == '"': value += char; auto = 2
            else: value += char
        elif auto == 1:
            if char == '\\': value += char; auto = 11
            elif char == "'": value += char; auto = 0
            else: value += char
        elif auto == 2:
            if char == '\\': value += char; auto = 12
            elif char == '"': value += char; auto = 0
            else: value += char
        elif auto == 10:
            value += char; auto = 0
        elif auto == 11:
            value += char; auto = 1
        elif auto == 12:
            value += char; auto = 2
    return value.strip()

def ispattern(string):
    'is string a fnmatch pattern?'
    return bool(take(string, '?*['))

def split_lines(string):
    "split_lines('aaa \nbbb \n') -> ['aaa', 'bbb'], split_lines('') -> []"
    string = rstrip(string)
    return [] if not string else [rstrip(line) for line in string.split('\n')]

def replace(string, *oldsnews):
    'replace(string, a, b, c, d, ...) == string.replace(a, b).replace(c, d)...'
    for old, new in slices(oldsnews, 2):
        string = string.replace(old, new)
    return string

def evalchar(string, olds, news, char='%'):
    '''for old, new in zip(olds, news): string = string.replace(char + old, new)
on error raise ValueError('%x')'''
    trans = {old: new for old, new in zip(olds, news)}
    trans[char] = char # char + char → char
    value = ''
    skip = False
    j = 0
    while j < len(string):
        charj = string[j]
        if charj == char:
            try:
                value += trans[string[j+1]]
            except (KeyError, IndexError):
                raise ValueError(string[j:j+2])
            else:
                j += 1
        else:
            value += charj
        j += 1
    return value

def just(string, length, align='^'):
    "align: '<'=left, '^'=center, '>'=right"
    return {'<': str.ljust, '^': str.center, '>': str.rjust}[align](string, length)

def expand(string, width):
    "insert blanks into string until len(string) == width, on error return ''"
    string = shrink(string)
    if len(string) == width:
        return string
    if ' ' not in string[1:] or len(string) > width:
        raise ValueError(f'Impossible to right-justify: {string!r}')
    chars = list(string)
    jchar = 0
    while True:
        if chars[jchar] != ' ' and chars[jchar + 1] == ' ':
            chars.insert(jchar + 1, ' ')
            if len(chars) == width:
                return ''.join(chars)
        jchar = jchar + 1 if jchar < len(chars) - 2 else 0

def findchar(string, pattern):
    'return index of first pattern-matching char found in string, or -1 if not found'
    for j, char in enumerate(string):
        if fnmatchcase(char, pattern):
            return j
    else:
        return -1

def rfindchar(string, pattern):
    'return index of last pattern-matching char found in string, -1 if not found'
    for j, char in retroenum(string):
        if fnmatchcase(char, pattern):
            return j
    else:
        return -1

def prevchar(char):
    """return chr(ord(char) - 1)
>>> prevchar('b')
'a'"""
    return chr(ord(char) - 1)

def nextchar(char):
    """return chr(ord(char) + 1)
>>> nextchar('a')
'b'"""
    return chr(ord(char) + 1)

def chrs(jj):
    """return ''.join(chr(j) for j in jj)
>>> chrs([97, 98, 99])
'abc'"""
    return ''.join(chr(j) for j in jj)

def ords(s):
    """return [ord(c) for c in s]
>>> ords('abc')
[97, 98, 99]"""
    return [ord(c) for c in s]

def many(number, single, plural=''):
    '''return f'1 {single}' if number == 1 else f'{number} {plur}' if plur else f'{number} {single}s'
>>> many(1, 'cat')
1 cat
>>> many(3, 'cat')
3 cats
>>> many(1, 'mouse')
1 mouse
>>> many(3, 'mouse')
3 mouses
>>> many(3, 'mouse', 'mice')
3 mice
'''
    return f'1 {single}' if number == 1 else f'{number} {plural}' if plural else f'{number} {single}s'

def edit(item, width=0, ndig=None, right=False):
    if isinstance(item, int):
        return str(item).rjust(width)
    elif isinstance(item, float):
        string = str(item if ndig is None else round(item, ndig))
        return (string[:-2] if string.endswith('.0') else string).rjust(width)
    elif right:
        return str(item).rjust(width)
    else:
        return str(item).ljust(width)

def startswithchars(string, chars):
    'does string start with a char in chars?'
    try:
        return string[0] in chars
    except IndexError:
        return False

def endswithchars(string, chars):
    'does string end with a char in chars?'
    try:
        return string[-1] in chars
    except IndexError:
        return False

#----- roman numbers -----

def int2roman(number):
    """
>>> int2roman(0) # min
''
>>> int2roman(3888) # longest (15 chars)
'mmmdccclxxxviii'
>>> int2roman(3999) # max
'mmmcmxcix'
>>> all(n == roman2int(int2roman(n)) for n in range(4000))
True
"""
    check(number in range(4000))
    m, c, x, i = [int(digit) for digit in f'{number:04}']
    return (['','m','mm','mmm'][m] +
            ['','c','cc','ccc','cd','d','dc','dcc','dccc','cm'][c] +
            ['','x','xx','xxx','xl','l','lx','lxx','lxxx','xc'][x] +
            ['','i','ii','iii','iv','v','vi','vii','viii','ix'][i])

def roman_width(number):
    'return max(len(int2roman(j) for j in range(number + 1))'
    check(number in range(4000))
    for max_number, width in [(1, 0), (2, 1), (3, 2), (8, 3), (18, 4), (28, 5), (38, 6), (88, 7), (188, 8),
                              (288, 9), (388, 10), (888, 11), (1888, 12), (2888, 13), (3888, 14), (4000, 15)]:
        if number < max_number:
            return width

def roman2int(roman):
    """
>>> roman2int('') # min
0
>>> roman2int('mmmdccclxxxviii') # longest (15 chars)
3888
>>> roman2int('mmmcmxcix') # max
3999
>>> all(n == roman2int(int2roman(n)) for n in range(4000))
True
"""
    num = 0
    for char in replace(roman.strip().lower(), 'cd','cccc','cm','dcccc','xl','xxxx','xc','lxxxx','iv','iiii','ix','viiii'):
        try:
            num += {'m': 1000, 'd': 500, 'c': 100, 'l': 50, 'x': 10, 'v': 5, 'i': 1}[char]
        except KeyError:
            raise ValueError
    return num

#----- *strip split shrink* eq/ne_upper() -----

def lstrip(string):
    'strip leading STRIP_CHARS'
    return string.lstrip(STRIP_CHARS)

def rstrip(string):
    'strip trailing STRIP_CHARS'
    return string.rstrip(STRIP_CHARS)

def strip(string):
    'strip leading and trailing STRIP_CHARS'
    return string.strip(STRIP_CHARS)

def split(string):
    "split string into a list of notempty words separated by space ' ' and tab '\t'"
    return [word for word in string.replace('\t',' ').split(' ') if word]

def shrink(string):
    "strip leading trailing and intermediate multiple space ' ' and tab '\t' chars"
    return ' '.join(split(string))

def shrink_alphaupper(string):
    'shrink and uppercase alphabetic words'
    return ' '.join(word.upper() if word.isalpha() else word for word in split(string))

def shrink_alphalower(string):
    'shrink and lowercase alphabetic words'
    return ' '.join(word.lower() if word.isalpha() else word for word in split(string))

def shrink_alphatitle(string):
    'shrink and titlecase alphabetic words'
    return ' '.join(word.title() if word.isalpha() else word for word in split(string))

def eq_alphaupper(string, string2):
    'return shrink_alphaupper(string) == shrink_alphaupper(string2)'
    return shrink_alphaupper(string) == shrink_alphaupper(string2)

def ne_alphaupper(string, string2):
    'return shrink_alphaupper(string) != shrink_alphaupper(string2)'
    return shrink_alphaupper(string) != shrink_alphaupper(string2)

#----- frame xframe table xtable -----

def frame(lines, align='^'):
    """lines is a list of strings or a single string
align is '<', '^' or '>'
return frame as a single string"""
    return '\n'.join(xframe(lines, align=align))
                     
def xframe(lines, align='^'):
    """lines is a list of strings or a single string
align is '<', '^' or '>'
yield frame as strings"""
    if isinstance(lines, str):
        lines = lines.split('\n')
    length = max(len(line) for line in lines)
    updown = (length + 2) * '─'
    yield f'┌{updown}┐'
    for line in lines:
        yield f'│ {just(line, length, align)} │'
    yield f'└{updown}┘'

def table(head, body):
    '''head is a tuple of column names, optionally followed by ':' and format
body is a list of tuples of items
an item is bool int float or str
return table as a single string
>>> print(table(('N', 'N/7:.3f'), [(n, n/7) for n in range(11)]))
┌──┬─────┐
│N │ N/7 │
├──┼─────┤
│ 0│0.000│
│ 1│0.143│
│ 2│0.286│
│ 3│0.429│
│ 4│0.571│
│ 5│0.714│
│ 6│0.857│
│ 7│1.000│
│ 8│1.143│
│ 9│1.286│
│10│1.429│
└──┴─────┘'''
    return '\n'.join(xtable(head, body))

def xtable(head, body):
    '''head is a tuple of column columns,
    optionally followed by ':' and format
body is a list of tuples of items
an item is bool int float or str
yield table as strings'''
    convert = lambda value, formatj, length: (str.ljust if isinstance(value, str) else str.rjust)(format(value, formatj), length)
    columns = [word.split(':')[0] for word in head]
    formats = [(word+':').split(':')[1] for word in head]
    lengths = [len(column) for column in columns]
    length = len(head)
    for values in body:
        values = long(values, length, '')
        for jcol, (value, formatj) in enumerate(zip(values, formats)):
            lengths[jcol] = max(lengths[jcol], len(format(value, formatj)))
    yield '┌' + '┬'.join(length * '─' for length in lengths) + '┐'
    yield '│' + '│'.join(column.center(length) for column, length in zip(columns, lengths)) + '│'
    yield '├' + '┼'.join(length * '─' for length in lengths) + '┤'
    for values in body:
        yield '│' + '│'.join(convert(value, formatj, length) for value, formatj, length in zip(values, formats, lengths)) + '│'
    yield '└' + '┴'.join(length * '─' for length in lengths) + '┘'

#----- time functions -----

def now(seconds=None, format='%04d-%02d-%02d %02d:%02d:%02d', micro=False):
    """return 'YYYY-mm-dd HH:MM:SS' from seconds or current time,
or 'YYYY-mm-dd HH:MM:SS.uuuuuu' if micro is True"""
    t = time() if seconds is None else seconds
    value = format % localtime(t)[:6]
    return value + '.%06d' % round(t % 1.0 * 1e6) if micro else value

def get_YmdHMS(seconds=None):
    "return ('YYYY','mm','dd','HH','MM','SS') from seconds or current time"
    t = time() if seconds is None else seconds
    Y, m, d, H, M, S = localtime(t)[:6]
    return tuple(f'{Y:04d} {m:02d} {d:02d} {H:02d} {M:02d} {S:02d}'.split())
    
def is_leap_year(Y):
    """
is Y a leap year? (proleptic gregorian calendar)
>>> [y for y in range(1000, 3001, 100) if is_leap_year(y)]
[1200, 1600, 2000, 2400, 2800]
>>> [y for y in range(1980, 2021) if is_leap_year(y)]
[1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020]
"""
    return Y % 4 == 0 and (Y % 100 != 0 or Y % 400 == 0)

def year_days(Y):
    "number of days in year Y (proleptic gregorian calendar)"
    return 365 + is_leap_year(Y)

def month_days(Y, m):
    "number of days in month m of year Y (proleptic gregorian calendar)"
    return [31, 28 + is_leap_year(Y), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]

def is_date_time(Y, m, d, H=0, M=0, S=0, Ymin=0, Ymax=9999):
    "is date (and time) correct?"
    return (Ymin <= Y <= Ymax and 1 <= m <= 12 and 1 <= d <= month_days(Y, m) and
            0 <= min(H, M, S) <= max(H, M, S) <= 59)

def easter_month_day(Y):
    """return Easter date of year Y as (month, day)
>>> for Y in range(2020, 2030): print(Y, easter_month_day(Y))
2020, (4, 12)
2021, (4, 4)
2022, (4, 17)
2023, (4, 9)
2024, (3, 31)
2025, (4, 20)
2026, (4, 5)
2027, (3, 28)
2028, (4, 16)
2029, (4, 1)
"""
    a = Y % 19
    b = Y // 100
    c = Y % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    return f // 31, f % 31 + 1

#----- path & file functions -----

def filesize(file):
    'return size of file in bytes'
    return getsize(file)

def filetime(file):
    "return last modification time of file in 'YYYY-mm-dd HH:MM:SS' format"
    return now(getmtime(file))

def longpath(path='.'):
    'return abspath(expanduser(path))'
    if not path:
        return ''
    return abspath(expanduser(path.strip()))

def shortpath(path='.'):
    "return '~/...' if applicable"
    if not path:
        return ''
    path = longpath(path)
    home = longpath('~')
    return '~' + path[len(home):] if path.startswith(home) else path

def get_files(path='./*'):
    "return a list of absolute paths to path-matching files ('**' in path is allowed)"
    return sorted(file for file in glob(longpath(path), recursive=True) if isfile(file) and not islink(file))

def get_file(path='./*'):
    "return unique path-matching file, or '' if not found or ambiguous"
    files = get_files(path)
    return files[0] if len(files) == 1 else ''

def get_lines(file):
    "like lines in open(file).readlines(), but normalized"
    return [line.rstrip().replace('\t','    ') for line in open(file)]

def max_file(pattern):
    "return the max path_file among matching path_files, or raise FileNotFoundError if not found"
    return max(get_files(pattern), default=None)

def last_file(pattern):
    "return the newest path_file among matching path_files, or raise FileNotFoundError if not found"
    files = get_files(pattern)
    if files:
        return max((lstat(file).st_mtime, file) for file in files)[1]
    else:
        raise FileNotFoundError

def new_file(pattern, char='%'):
    'return not existing %-expanded pathfile, initialize file as empty'
    while True:
        file = longpath(evalchar(pattern, 'iPpfeYmdHMSu', iPpfeYmdHMSu_of(), char=char))
        if char in pattern and isfile(file):
            sleep(0.1)
        else:
            open(file, 'w').write('')
            return file
        
def iPpfeYmdHMSu_of(file=''):
    '''return (i, P, p, f, e, Y, m, d, H, M, S, u), where:
    • i is current PID
    • P is long path to file, with final '/'
    • p is short ('~/...') path to file, with final '/'
    • f is file name, with no extension
    • e is file extension, starting with '.'
    • Y is 4-digit current year
    • m, d, H, M, S are 2-digit current month day hour minute and second
    • u is 6-digits current microsecond'''
    i = str(getpid())
    if file:
        P, fe = splitpath(longpath(file))
        p = shortpath(P) + '/'
        P += '/'
        f, e = splitext(fe)
    else:
        P, p, f, e = '', '', '', ''
    t = time()
    Y, m, d, H, M, S = ('%04d %02d %02d %02d %02d %02d' % localtime(t)[:6]).split()
    u = '%06d' % round(t % 1.0 * 1e6)
    sleep(0.001)
    return (i, P, p, f, e, Y, m, d, H, M, S, u)

def local_file(pathfile):
    'return absolute path of a package pathfile'
    return normpath(f'{dirname(__file__)}/{pathfile}')

def get_dirs(pattern):
    "return a list of absolute paths to pattern-matching dirs ('**' in path is allowed)"
    return [path for path in glob(longpath(pattern), recursive=True) if isdir(path)]

def get_dir(pattern):
    "return unique pattern-matching dir, or '' if not found or ambiguous"
    dirs = get_dirs(pattern)
    return dirs[0] if len(dirs) == 1 else ''

def chdir2(pattern='~'):
    '''like os.chdir(), but it accepts '~' '.' '..' '?' '*' '**' etc'''
    paths = get_dirs(pattern)
    if not paths:
        print(f'cd: path {pattern!r} not found', file=stderr)
    elif len(paths) > 1:
        print(f'cd: path {pattern!r} is ambiguous', file=stderr)
    else:
        chdir(paths[0])

#----- sequence functions -----

def find(xx, x):
    'find min j such that xx[j] == x, return -1 if not found'
    for j, xj in enumerate(xx):
        if xj == x:
            return j
    else:
        return -1
        
def rfind(xx, x):
    'find max j such that xx[j] == x, return -1 if not found'
    jok = -1
    for j, xj in enumerate(xx):
        if xj == x:
            jok = j
    return jok

def finddup(xx):
    'find min j such that xx[j] == xx[i] for some i < j, return -1 if not found'
    xset = set()
    for j, xj in enumerate(xx):
        if xj in xset:
            return j
        xset.add(xj)
    else:
        return -1
        
def findmin(xx):
    'find min j such that xx[j] == min(xx), return -1 if not found'
    jmin, xmin = -1, None
    for j, xj in enumerate(xx):
        if j == 0 or xj < xmin:
            jmin = j
            xmin = xj
    return jmin, xmin

def rfindmin(xx):
    'find max j such that xx[j] == min(xx), return -1 if not found'
    jmin, xmin = -1, None
    for j, xj in enumerate(xx):
        if j == 0 or xj <= xmin:
            jmin = j
            xmin = xj
    return jmin, xmin

def findmax(xx):
    'find min j such that xx[j] == max(xx), return -1 if not found'
    jmax, xmax = -1, None
    for j, xj in enumerate(xx):
        if j == 0 or xj > xmax:
            jmax = j
            xmax = xj
    return jmax, xmax

def rfindmax(xx):
    'find max j such that xx[j] == max(xx), return -1 if not found'
    jmax, xmax = -1, None
    for j, xj in enumerate(xx):
        if j == 0 or xj >= xmax:
            jmax = j
            xmax = xj
    return jmax, xmax

def slices(xx, n):
    """>>> list(slices('0123456789', 2)) # str
['01', '23', '45', '67', '89']
>>> list(slices(list('0123456789'), 2)) # list
[['0', '1'], ['2', '3'], ['4', '5'], ['6', '7'], ['8', '9']]
>>> list(slices(tuple('0123456789'), 2)) # tuple
[('0', '1'), ('2', '3'), ('4', '5'), ('6', '7'), ('8', '9')]
>>> list(slices((str(j) for j in range(10)), 2)) # generator
[['0', '1'], ['2', '3'], ['4', '5'], ['6', '7'], ['8', '9']]"""
    check(n > 0)
    func = tuple if isinstance(xx, tuple) else (lambda yy: ''.join(yy)) if isinstance(xx, str) else (lambda yy: yy)
    slice = []
    for x in xx:
        slice.append(x)
        if len(slice) == n:
            yield func(slice)
            slice = []
    check(not slice)

def retroenum(xx):
    'like enumerate(xx), but backwards from last to first item'
    if '__getitem__' not in dir(xx):
        xx = list(xx)
    for j in range(len(xx) - 1, -1, -1):
        yield j, xx[j]

def get(xx, j, default=None):
    'return xx[j] if 0 <= j < len(xx) else default'
    return xx[j] if 0 <= j < len(xx) else default

def unique(xx):
    'return a list of items in xx discarding duplicates'
    zz = set()
    yy = []
    for x in xx:
        if x not in zz:
            zz.add(x)
            yy.append(x)
    return yy

def long(xx, length, default):
    if len(xx) == length:
        return xx
    elif len(xx) > length:
        return xx[:length]
    elif isinstance(xx, list):
        return xx + (length - len(xx)) * [default]
    elif isinstance(xx, tuple):
        return xx + (length - len(xx)) * (default,)
    elif isinstance(xx, str):
        return xx + (length - len(xx)) * default
    else:
        raise TypeError

#----- shell functions -----

def shell(line, echo=ECHO, stdout=False):
    'execute shell command in line, print errors into stderr, return output as list of strings'
    if echo:
        print('$ ' + line)
    command = line2stmt(line)
    if command == 'exit':
        raise SystemExit
    elif command == 'cd' or command.startswith('cd '):
        where = command[3:].strip() or '~'
        paths = glob(longpath(where))
        if not paths:
            print(f'cd: {where!r}: No such file or directory', file=stderr)
        elif len(paths) > 1:
            print(f'cd: too many arguments', file=stderr)
        else:
            chdir(paths[0])
        return []
    else:
        result = run(command, shell=True, text=True, capture_output=True)
        for line in split_lines(result.stderr):
            print(line, file=stderr)
        return [line.rstrip() for line in split_lines(result.stdout)]

def term():
    " minimalistic terminal, type 'exit' to exit "
    print(70 * '(')
    while True:
        try:
            inline = input(f"{shortpath('.')} $ ")
            try:
                for outline in shell(inline):
                    print(outline)
            except SystemExit:
                print(70 * ')')
                return
        except KeyboardInterrupt:
            print('^C')

def command_exists(command):
    return bool(shell(f'which {command}'))

#----- conversion functions -----

in2in = lambda In: float(In) # inch converters
in2pt = lambda In: In * 72.0
pt2in = lambda pt: pt / 72.0
in2cm = lambda In: In * 2.54
cm2in = lambda cm: cm / 2.54
in2mm = lambda In: In * 25.4
mm2in = lambda mm: mm / 25.4
cc2in = {'pt': pt2in, 'in': in2in, 'mm': mm2in, 'cm': cm2in}

def inch2str(inch, digits=ROUND):
    'convert float inch into a multi-unit human-readable string'
    return ' = '.join(str(round(in2cc(inch), digits)) + unit for in2cc, unit in [(in2pt, 'pt'), (in2in, 'in'),(in2mm, 'mm'),(in2cm, 'cm')])

def str2inch(string):
    "convert unsigned '{float}{suffix}' into float, on error raise ValueError"
    check('-' not in string)
    string = replace(string, ',', '.')
    if tryfunc(float, string) == 0.0:
        return 0.0
    else:
        x, cc = string[:-2], string[-2:]
        check(cc in cc2in)
        return cc2in[cc](float(x))

def str2inxin(string):
    "convert unsigned '{float}x{float}{suffix}' into (float, float), on error raise ValueError"
    check('-' not in string)
    string = replace(string, ',', '.')
    xy, cc = string[:-2], string[-2:]
    check(cc in cc2in)
    x, y = [float(s) for s in xy.split('x')]
    check(x > 0.0 < y)
    return (cc2in[cc](x), cc2in[cc](y))

def str2ratio(string):
    "convert unsigned '{float}' or '{float}/{float}' into float, on error raise ValueError"
    check('-' not in string)
    string = replace(string, ',', '.')
    if '/' not in string:
        return float(string)
    else:
        x, y = [float(s) for s in string.split('/')]
        check(x > 0.0 < y)
        return x / y

def str2int(string, min=0):
    "convert '{int}' into int, on error raise ValueError"
    n = int(string)
    check(min is None or n >= min)
    return n

#----- numeric functions -----

def is_perm(xx):
    'is xx a permutation of list(range(len(xx)))?'
    return sorted(xx) == list(range(len(xx)))

def ceildiv(x, y):
    'return ceil(x / y) # but by integer arithmetic only'
    q, r = divmod(x, y)
    return q + bool(r)

def prod(xx):
    'product of all x in xx'
    p = 1
    for x in xx:
        p *= x
    return p

def fact(n):
    'factorial'
    return prod(range(2, n + 1)) if n >= 0 else 0

def disp(n, k):
    'dispositions'
    return prod(range(n - k + 1, n + 1)) if 0 <= k <= n else 0

def comb(n, k):
    'combinations = binomial coefficient'
    return disp(n, k) // fact(k) if 0 <= k <= n else 0

def frange(start, stop=None, step=1.0, first=True, last=False):
    """float range
>>> list(frange(0, 1, 1/3, last=True))
[0.0, 0.3333333333333333, 0.6666666666666666, 1.0]
>>> list(frange(1, 0, -1/3, last=True))
[1.0, 0.6666666666666667, 0.33333333333333337, 0.0]"""
    if stop is None:
        start, stop = 0.0, start
    start, stop, step = float(start), float(stop), float(step)
    if first:
        yield start
    for j in range(1, round((stop - start) / step)):
        yield start + j * step
    if last:
        yield stop

def difs(xx):
    '''return [xx[0], xx[1] - xx[0], xx[2] - xx[1], ...]
difs(sums(xx)) == sums(difs(xx)) == xx'''
    return [xj - xx[j-1] if j else xj for j, xj in enumerate(xx)]
            
def sums(xx):
    '''return [xx[0], xx[0] + xx[1], xx[0] + xx[1] + xx[2], ...]
difs(sums(xx)) == sums(difs(xx)) == xx'''
    yy = xx[:]
    for j in range(1, len(yy)):
        yy[j] += yy[j - 1]
    return yy

def mean(xx):
    n, sx = 0, 0.0
    for x in xx:
        n += 1
        sx += x
    return sx / n

def variance(xx):
    n, sx, sx2 = 0, 0.0, 0.0
    for x in xx:
        n += 1
        sx += x
        sx2 += x * x
    return sx2 / n - (sx / n) ** 2

def mean_var(xx):
    n, sx, sx2 = 0, 0.0, 0.0
    for x in xx:
        n += 1
        sx += x
        sx2 += x * x
    ex = sx / n
    return ex, sx2 / n - ex * ex

def quantile(xx, n):
    yy = sorted(xx); m = len(yy)
    return [yy[j] for j in range(0, m, m // n)] + [yy[-1]]

def plus(xx, yy):
    '''return [xx[0] + yy[0], xx[1] + yy[1], xx[2] + yy[2], ...]'''
    check(len(xx) == len(yy))
    return [(x + y) for x, y in zip(xx, yy)]

def mins(xx, yy):
    '''return [xx[0] - yy[0], xx[1] - yy[1], xx[2] - yy[2], ...]'''
    check(len(xx) == len(yy))
    return [(x - y) for x, y in zip(xx, yy)]

def broken_line(xyxy, x):
    '''linear interpolation by broken line
xyxy = [(x0, y0), (x1, y1), (x2, y2),...]
0.0 <= x0 < x1 < x2 ...
0.0 <= y0 < y1 < y2 ...'''
    n = len(xyxy)
    if n == 0: # straight line by [(0.0, 0.0), (1.0, 1.0)]
        return  x
    elif n == 1: # straight line by [(0.0, 0.0), (x0, y0)]
        x0, y0 = xyxy[0]
        return (y0 / x0) * x
    elif n == 2: # straight line by [(x0, y0), (x1, y1)]
        x0, y0 = xyxy[0]
        x1, y1 = xyxy[1]
        d = x1 - x0
        a = (y1 - y0) / d
        b = (y0 * x1 - y1 * x0) / d
        return a * x + b
    else: # broken line by [(x0, y0), (x1, y1), (x2, y2),...]
        for j, (x0, y0) in enumerate(xyxy):
            x1, y1 = xyxy[j + 1]
            if j >= n - 2 or x <= x1:
                return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def least_squares_line(xyxy, x=None):
    '''linear interpolation by least-squares straight line
xyxy = [(x0, y0), (x1, y1), (x2, y2),...]'''
    n = len(xyxy)
    if n == 0: # straight line by [(0.0, 0.0), (1.0, 1.0)]
        a, b = 1.0, 0.0
    elif n == 1: # straight line by [(0.0, 0.0), (x0, y0)]
        x0, y0 = xyxy[0]
        a, b = y0 / x0, 0.0
    elif n == 2: # straight line by [(x0, y0), (x1, y1)]
        x0, y0 = xyxy[0]
        x1, y1 = xyxy[1]
        d = x1 - x0
        a = (y1 - y0) / d
        b = (y0 * x1 - y1 * x0) / d
    else: # least-squares straight line by [(x0, y0), (x1, y1), (x2, y2),...]
        sx = sum(x for x, y in xyxy)
        sx2 = sum(x * x for x, y in xyxy)
        sy = sum(y for x, y in xyxy)
        sxy = sum(x * y for x, y in xyxy)
        d = n * sx2 - sx * sx
        a = (n * sxy - sx * sy) / d
        b = (sx2 * sy - sx * sxy) / d
    return (a, b) if x is None else a * x + b 

def moving_means(xx, n=7):
    """return [yy[j] = sum(xx[j+1-n:j+1]) / n]
>>> moving_means(list(range(10)))
[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
>>> moving_means(list(range(10)), 3)
[0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
"""
    return [sum(xx[max(0, j + 1 - n): j + 1]) / min(n, j + 1) for j in range(len(xx))]

def zerofunc(f, xa, xz, max_iter=100, trace=False):
    '''return x such that f(x) = 0 by regula falsi
f in [xa, xz] interval must:
    1. be continuous and monotonic
    2. have one and only one zero
>>> zerofunc(lambda x: 1 / x - (x - 1), 0.5, 2.0) # golden ratio, 1 / x = x - 1
1.618033988749895
>>> zerofunc(lambda x: 1 / x - (x + 1), 0.5, 2.0) # inverse of golden ratio, 1 / x = x + 1
0.6180339887498948
'''
    ya = f(xa); yz = f(xz); xh0 = None
    for iter in range(max_iter):
        xh = xa - ya * (xz - xa) / (yz - ya)
        if xh == xh0:
            return xh
        xh0 = xh
        yh = f(xh)
        if trace:
            print(f'x = {xh}, y = {yh}')
        if yh == 0.0:
            return xh
        if yh * yz < 0.0:
            xz = xh; yz = yh
        else:
            xa = xh; ya = yh
    raise ValueError(f'Convergence not reached after {max_iter} iterations')

#----- dict functions and classes -----

def sorted_items(dic, by_value=False, reverse=False):
    'return dic.items() = [(key, value), ...] sorted by value if by_value else by key'
    types(dic, dict)
    key = (lambda kv: (kv[1], kv[0])) if by_value else None
    return sorted(dic.items(), key=key, reverse=reverse)

class IntDict(dict):
    'dictionary of integers'

    def __init__(getitem, keys=[]):
        'initialize intdict by a sequence of keys'
        for key in keys:
            intdict.add(key)

    def __getitem__(intdict, key):
        'return intdict[key] if key in intdict else 0'
        return intdict.get(key, 0)

    def add(intdict, key):
        'add a key to intdict'
        if key not in intdict:
            intdict[key] = 0
        intdict[key] += 1

    def extend(intdict, keys):
        'extend intdict by a sequence of keys'
        for key in keys:
            intdict.add(key)

class ListDict(dict):
    'dictionary of lists'

    def __getitem__(listdict, key):
        return listdict.get(key, [])

    def append(listdict, key, value):
        if key not in listdict:
            listdict[key] = []
        listdict[key].append(value)

class SetDict(dict):
    'dictionary of sets'

    def __getitem__(setdict, key):
        return setdict.get(key, set())

    def add(setdict, key, value):
        if key not in setdict:
            setdict[key] = set()
        setdict[key].add(value)

#----- PySimpleGUI-related functions -----

def get_radio(window, start, domain):
    ntrue = 0
    for j, valuej in enumerate(domain):
        if window[start + j].get():
            ntrue += 1
            value = valuej
    check(ntrue == 1)
    return value

def get_radios(window, domains):
    start = 0
    for domain in domains:
        yield get_radio(window, start, domain)
        start += len(domain)

def put_radio(window, start, domain, value):
    ntrue = 0
    for j, valuej in enumerate(domain):
        if valuej == value:
            ntrue += 1
            window[start + j].update(True)
        else:
            window[start + j].update(False)
    check(ntrue == 1)
    
def put_radios(window, domains, values):
    start = 0
    for domain, value in zip(domains, values):
        put_radio(window, start, domain, value)
        start += len(domain)

#----- end -----




