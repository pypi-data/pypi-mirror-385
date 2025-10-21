#!/usr/bin/env python3
'''
                    ┌───────────────────────────────────┐
                    │                                   ├─┐
                    │      │   │ ┌───┐ │   │ ┌───┐      │ │
                    │      │   │ │   │ │   │ │   │      │ │
                    │      └─┬─┘ ├───┤ │ │ │ ├───┘      │ │
                    │        │   │   │ │ │ │ │          │ │
                    │        │   │   │ └─┴─┘ │          │ │
                    │                                   │ │
                    └─┬─────────────────────────────────┘ │
                      └───────────────────────────────────┘
'''

#----- imports -----

from .__init__ import *
from .__init__ import __version__ as VERSION, __doc__ as DESCRIPTION
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pdfrw import PdfReader, PdfWriter, PageMerge
from random import random
from sys import argv, stderr, stdout
from threading import Thread, Event
from time import localtime, sleep, time
from traceback import format_exc
from warnings import simplefilter
import FreeSimpleGUI as psg

#----- record position constants -----

EMPT, TEXT, PICT, CONT, FIGU, CAPT, INDX, CHP1, CHP2, HEA1, HEA2 = range(11) # line kinds in buf.buffer[KIND]
KINDS = 'EMPT, TEXT, PICT, CONT, FIGU, CAPT, INDX, CHP1, CHP2, HEA1, HEA2'.split(', ') # values in buf.buffer[KIND]:
    # EMPT empty line
    # TEXT text line
    # PICT picture line
    # CONT contents chapter line
    # FIGU figure chapter line
    # CAPT figure caption line
    # INDX index chapter line
    # CHP1 numbered chapter line, level == 1
    # CHP2 numbered chapter line, level > 1
    # HEA1 page header, first line
    # HEA2 page header, second line

JINP, KIND, JPAG, LPIC, LINE = range(5) # positions in buf.buffer
    # JINP line index in input file
    # KIND line kind, see before
    # JPAG page number
    # LPIC number of lines in picture
    # LINE content of line

LABL, TITL, JOUT = range(3) # positions in buf.contents and buf.captions
    # LABL chapter label, like '1.' in buf.contents or '1.a.' in buf.captions
    # TITL chapter title
    # JOUT line index in buf.buffer

#----- characters -----

INDENT = 4 * ' ' # standard indentation
HEADER_CHARS = frozenset(FORMFEED + NBSPACE + DOTABOVE + MACRON + OVERLINE) # first chars of 1st and 2nd header lines
SECOND_LINE_CHARS = {'b': NBSPACE, 'p': DOTABOVE, 'd': MACRON, 's': OVERLINE} # first chars in second header lines
ZERO_WIDTH_CHARS = frozenset('\u200b\u200c\u200d') # to be discarded from input

#----- status indicator constants -----

STATUS  = '■'
WAITING = GREEN
RUNNING = RED

#----- scale factor constants -----

SCALE_2 = 0.5 ** 0.5 # -I = 2
SCALE_4 = 0.5        # -I = 4
SCALE_8 = 0.5 ** 1.5 # -I = 8

#----- file constants -----

YAWP_PATH = longpath('~/.config/yawp') # yawp's configuration directory
md(YAWP_PATH) # create if not exists
PDF_PATH = longpath('~/PDF') # directory for temporary PDF files
md(PDF_PATH) # create if not exists
CORR_FILE = longpath(f'{YAWP_PATH}/yawp.corr') # correction file
HIST_FILE = longpath(f'{YAWP_PATH}/yawp.hist') # file of history of recent files (GUI mode only)
SESS_FILE = longpath(f'{YAWP_PATH}/yawp.sess') # INSTANCE file containing pathfile of last text file of previous INSTANCE (GUI mode only)
MANUAL_FILE = local_file(f'docs/YAWP {VERSION} User Manual.txt.pdf') # YAWP User Manual

#----- PySimpleGUI constants -----

THEME = 'Default1' # window colour theme
TSIZE = 15 # text size
FSIZE = 34 # field size
NSIZE = 11 # number size
ASIZE = 33 # after number size
BSIZE = 10 # button size

#----- PySimpleGUI radio buttons -----

NON_RADIO_CHARS = 'ylwgbucifFmeEoOnaYPWASZLRTBJt' # chars of non-radio arguments
RADIO_CHARS = 'kpsXCI' # chars of radio arguments
RADIO_DICT = {'k': list('nlcr'), # domains of radio arguments, as a dict…
              'p': list('nfpcd'),
              's': list('nbpds'), 
              'X': list('neb'),
              'C': list('ndf'),        
              'I': list('1248')}
RADIO_LIST = [RADIO_DICT[c] for c in RADIO_CHARS] # …and as a list
SECOND_LINE = ''.join(RADIO_DICT['s']) # display domain of -s argument
MULTI_PAGES = '/'.join(RADIO_DICT['I']) # display domain of -I argument

#----- various constants -----

ERROR = 1 # error return code
USAGE_MODES = 'gcmdefnu' # domain of arg.usage_mode
QUOTES = "'" + '"' # single and double quotation marks
MAX_QUALITY = 5 # max lp print quality
ROUND = 6 # rounding factor in float display
MAX_HISTORY = 25 # max number of items in history of recent files
UNITS = ", unit: pt/in/mm/cm" # units in argument helps
BIGINT = 2 ** 31 - 1 # big integer
INSTANCE = evalchar('%i %Y-%m-%d %H:%M:%S.%u', 'iPpfeYmdHMSu', iPpfeYmdHMSu_of()) # unique instance signature for text file locking

#----- default correction file -----

CORR_DEFAULT = '''
# ┌──────────────────────────┐
# │ ~/.config/yawp/yawp.corr │
# └──────────────────────────┘

plm 0mm 6mm # portrait left margin
plm 10mm 16mm
plm 20mm 24mm
plm 30mm 35mm
plm 40mm 43mm
plm 50mm 52mm
plm 60mm 62mm
plm 70mm 72.5mm
plm 80mm 83mm
plm 90mm 92mm
plm 100mm 101mm

llm 0mm 12mm # landscape left margin
llm 5mm 16mm
llm 10mm 20.5mm
llm 20mm 29.5mm
llm 30mm 39mm
llm 40mm 48mm
llm 50mm 57mm
llm 60mm 66.5mm
llm 70mm 75.5mm
llm 80mm 84.5mm
llm 90mm 94mm
llm 100mm 104mm

prm 0mm 8.5mm # portrait right margin
prm 10mm 15mm
prm 20mm 25.5mm
prm 30mm 34.5mm
prm 40mm 44.5mm
prm 50mm 54.5mm
prm 60mm 64.5mm
prm 70mm 72mm
prm 80mm 81mm
prm 90mm 91.5mm
prm 100mm 100mm

lrm 0mm 12mm # landscape left margin
lrm 5mm 17mm
lrm 10mm 22mm
lrm 20mm 30mm
lrm 30mm 40mm
lrm 40mm 49.5mm
lrm 50mm 58mm
lrm 60mm 68mm
lrm 70mm 77.5mm
lrm 80mm 86mm
lrm 90mm 96mm
lrm 100mm 104mm

ptm 0mm 2mm # portrait top margin
ptm 10mm 11.5mm
ptm 20mm 21mm
ptm 30mm 30.5mm
ptm 40mm 39.5mm
ptm 50mm 49mm
ptm 60mm 59mm
ptm 70mm 68mm
ptm 80mm 77.5mm
ptm 90mm 87mm
ptm 100mm 96mm

ltm 0mm 2mm # landscape top margin
ltm 5mm 7mm
ltm 10mm 11mm
ltm 20mm 20.5mm
ltm 30mm 30mm
ltm 40mm 39mm
ltm 50mm 48.5mm
ltm 60mm 57.5mm
ltm 70mm 67mm
ltm 80mm 76mm
ltm 90mm 85mm
ltm 100mm 95mm

pbm 0mm 16mm # portrait bottom margin
pbm 10mm 24mm
pbm 20mm 34mm
pbm 30mm 43mm
pbm 40mm 52.5mm
pbm 50mm 62mm
pbm 60mm 71mm
pbm 70mm 81mm
pbm 80mm 90mm
pbm 90mm 100mm
pbm 100mm 109.5mm

lbm 0mm 14.5mm # landscape bottom margin
lbm 5mm 19mm
lbm 10mm 24mm
lbm 20mm 32mm
lbm 30mm 42mm
lbm 40mm 52mm
lbm 50mm 60mm
lbm 60mm 70mm
lbm 70mm 80mm
lbm 80mm 88mm
lbm 90mm 99mm
lbm 100mm 107mm

pcw 100mm 94.674mm # portrait character width

lcw 100mm 92.200mm # landscape character width

pch 100mm 94.358mm # portrait character height

lch 100mm 92.647mm # landscape character height
'''

#----- tooltip in GUI main window, others will be added later by get_arguments() -----

tooltip = { 
    'New':    'create a new empty text file\nwith default arguments',
    'Open':   'browse the file system\nto select an existing text file',
    'Recent': 'browse the list of recent files\nto select an existing text file',
    'Copy':   'copy the current text file\nwith its argument file',
    'Move':   'move the current text file\nwith its argument log and backup files',
    'Delete': 'delete the current text file\nwith its argument log and backup files',
    'Edit':   'edit the current text file\nby the text editor defined by -y',
    'Format': 'format the current text file and\nredraw and align pictures\nand export PDF',
    'Noform': "don't format the current text file but\nredraw and align pictures\nand export PDF",
    'Undo':   'restore the current text file\nto its previous content\nand export PDF',
    'Log':    'browse the log file of the current text file\nby the text editor defined by -y',
    'Help':   'browse the YAWP-generated YAWP User Manual\nby the PDF browser defined by -Y',
    'Exit':   'quit YAWP'}

#----- paper format names for -S --sheet-size -----

PAPERSIZE = { 
    'A0':  '841x1189mm',
    'A1':  '594x841mm',
    'A2':  '420x594mm',
    'A3':  '297x420mm',
    'A4':  '210x297mm',
    'A5':  '148x210mm',
    'A6':  '105x148mm',
    'A7':  '74x105mm',
    'A8':  '52x74mm',
    'A9':  '37x52mm',
    'A10': '26x37mm',
    'B0':  '1000x1414mm',
    'B1':  '707x1000mm',
    'B1+': '720x1020mm',
    'B2':  '500x707mm',
    'B2+': '520x720mm',
    'B3':  '353x500mm',
    'B4':  '250x353mm',
    'B5':  '176x250mm',
    'B6':  '125x176mm',
    'B7':  '88x125mm',
    'B8':  '62x88mm',
    'B9':  '44x62mm',
    'B10': '31x44mm',
    'C0':  '917x1297mm',
    'C1':  '648x917mm',
    'C2':  '458x648mm',
    'C3':  '324x458mm',
    'C4':  '229x324mm',
    'C5':  '162x229mm',
    'C6':  '114x162mm',
    'C7':  '81x114mm', 
    'C8':  '57x81mm',
    'C9':  '40x57mm',
    'C10': '28x40mm',
    'C11': '22x32mm',
    'C12': '16x22mm',
    'HALF-LETTER':  '5.5x8.5in',
    'LETTER':       '8.5x11.0in',
    'LEGAL':        '8.5x14.0in',
    'JUNIOR-LEGAL': '5.0x8.0in',
    'LEDGER':       '11.0x17.0in',
    'TABLOID':      '11.0x17.0in'}

#----- log_append inform warning error -----

def log_append(message, text_file=None):
    'append a message to the log file of text_file'
    text_file = text_file or arg.text_file
    if isfile(text_file):
        log_file = log_file_of(text_file)
        try:
            with open_file(log_file, 'a') as append:
                print(message, file=append)
        except:
            except_file(log_file, 'a')

def inform(message, text_file=None, verbose=True):
    if message:
        log_append(message, text_file)
        if not var.gui_mode and arg.verbose and verbose:
            print(message)

def warning(message):
    if message:
        if var.gui_mode:
            message += '.' * (not message.endswith('.'))
            if ask_yes('YAWP - WARNING', f'WARNING: {message}\nDo you want to continue anyway?', 'continue'):
                log_append('WARNING: ' + message)
            else:
                log_append('ERROR: ' + message)
                raise YawpError
        else:
            error(message)

def error(message, jline=None):
    if message:
        error_message = (f'ERROR IN LINE {jline}: ' if jline is not None else 'ERROR: ') + message + '.' * (not message.endswith('.'))
        log_append(error_message)
        if var.gui_mode:
            ask_ok('YAWP - ERROR', error_message)
            raise YawpError
        else:
            exit(error_message)

#----- i/o functions -----

def check_file(file, mode='r', must_exist=False):
    '''check file for 'Undefined file' 'Directory not found' and 'File is not a file' errors
check file for 'File not found error' too if must_exist is True'''
    process = {'r':'read', 'w':'writ', 'a':'append'}[mode[0]]
    file = strip(file)
    if not file:
        error(f"Undefined file error {process}ing file {file!r}")
    file = longpath(file)
    if not isdir(dirname(file)):
        error(f"Directory not found error {process}ing file {file!r}")
    if exists(file) and not isfile(file):
        error(f"File is not a file error {process}ing file {file!r}")
    if must_exist and not isfile(file):
        error(f"File not found error {process}ing file {file!r}")

def except_file(file, mode='r'):
    'redirect I/O exception to error()'
    process = {'r':'read', 'w':'writ', 'a':'append'}[mode[0]]
    for line in format_exc().split('\n'):
        if 'Error:' in line:
            message = '' # 'FileNotFoundError: ... ' -> 'File not found error'
            for jchar, char in enumerate(line.split(':')[0]):
                if jchar > 0 and char.isupper():
                    message += ' ' + char.lower()
                else:
                    message += char
            error(f'{message} {process}ing file {file!r}')
    else:
        error(f'Undefined error {process}ing file {file!r}')

def open_file(file, mode='r'):
    'like open(), but check file before'
    check_file(file, mode)
    return open(file, mode)

def read_file(file, on_error=None):
    'read file as a single string'
    try:
        return open_file(file).read()
    except:
        if on_error is None:
            except_file(file)
        else:
            return on_error
    
def write_file(file, string=''):
    'write file as a single string'
    try:
        open_file(file, 'w').write(string)
    except:
        except_file(file, 'w')


def read_file_lines(file):
    'yield lines in file'
    try:
        with open_file(file) as input:
            for line in input:
                yield rstrip(''.join(
                    INDENT if char == HORIZTAB else '' if char in ZERO_WIDTH_CHARS else char for char in line))
    except:
        except_file(file)

def write_file_lines(file, lines=[]):
    'write lines into file'
    try:
        with open_file(file, 'w') as output:
            for line in lines:
                print(rstrip(line), file=output)
    except:
        except_file(file, 'w')

def max_text_line_length_in(text_file):
    max_length = 0
    try:
        for line in open_file(text_file):
            if not line or line[0] not in HEADER_CHARS:
                max_length = max(max_length, len(rstrip(''.join(
                    INDENT if char == HORIZTAB else '' if char in ZERO_WIDTH_CHARS else char for char in line))))
    except:
        except_file(text_file)
    else:
        return max_length

def write_sess_file(text_file):
    try:
        open(SESS_FILE, 'w').write(text_file)
    except:
        pass

def read_sess_file():
    try:
        text_file = open(SESS_FILE).read()
    except:
        return ''
    else:
        return text_file

#----- reserved files -----

def lock_file_of(text_file):
    'create a filename for lock file of text_file'
    if not text_file:
        return ''
    path, name = splitpath(longpath(text_file))
    return normpath(f'{path}/.yawp.{name}.lock')

def log_file_of(text_file):
    'create a filename for log file of text_file'
    if not text_file:
        return ''
    path, name = splitpath(longpath(text_file))
    return normpath(f'{path}/.yawp.{name}.log')

def args_file_of(text_file):
    'create a filename for args file of text_file'
    if not text_file:
        return ''
    path, name = splitpath(longpath(text_file))
    return normpath(f'{path}/.yawp.{name}.args')

def new_temp_file():
    'create a unique filename for temporary text file'
    return new_file(f'~/PDF/.yawp.%i.%Y-%m-%d.%H-%M-%S.%u.temp')

def new_back_file_of(text_file):
    'create a timestamped filename for backup file of text_file'
    if not text_file:
        return ''
    path, name = splitpath(longpath(text_file))
    return new_file(f'{path}/.yawp.{name}.%Y-%m-%d.%H-%M-%S.back')
    # was: new_file(f'{path}/.yawp.{name}.%Y.%m.%d-%H.%M.%S.back') in YAWP 1.0.0

def last_back_file_of(text_file):
    "return filename of the newest timestamped backup of file, or '' if not found"
    if not text_file:
        return ''
    return max(back_files_of(text_file), default=None)

def back_files_of(text_file):
    "return list of filenames of all timestamped backups of text_file"
    if not text_file:
        return []
    path, name = splitpath(longpath(text_file))
    return get_files(f'{path}/.yawp.{name}.[0-9][0-9][0-9][0-9][-.][01][0-9][-.][0-3][0-9][-.][0-5][0-9][-.][0-5][0-9][-.][0-5][0-9].back')
    # compatible with backup files generated by YAWP 1.0.0

def is_reserved(file):
    'is file a YAWP-reserved file?'
    path, name = splitpath(shortpath(file))
    return path.startswith('~/.config/yawp') or name.startswith('.yawp.')

#----- dialog functions -----

def ask_yes(title, question, tooltip_yes, tooltip_no=''):
    "show a Yes/No window and return True if 'Yes' button, False if 'No' button or alt-F4 or 'x' button"
    lines = question.split('\n')
    text_width = max(FSIZE, max(len(line) for line in lines))
    text_height = len(lines)
    layout = [[psg.Text(question, size=(text_width, text_height))],
              [psg.Button('Yes', tooltip=tooltip_yes.title(), size=BSIZE),
               psg.Button('No', tooltip=tooltip_no or f"Don't {tooltip_yes.lower()}", size=BSIZE)]]
    return psg.Window(title, layout).read(close=True)[0] == 'Yes'

def ask_ok(title, message):
    "show a message window, exit by 'OK' button or alt-F4 or 'x' button"
    lines = message.split('\n')
    text_width = max(FSIZE, max(len(line) for line in lines))
    text_height = len(lines)
    layout = [[psg.Text(message, size=(text_width, text_height))],
              [psg.Button('OK', tooltip='go back', size=BSIZE)]]
    psg.Window(title, layout).read(close=True)

#----- other functions -----

def chapter_level(prefix):
    "level of a chapter prefix: '0.' -> 1, '0.0.' -> 2, …, else -> 0"
    status = 0; level = 0
    for char in prefix:
        if status == 0:
            if char.isdecimal():
                status = 1
            else:
                return 0
        else: # status == 1
            if char.isdecimal():
                pass
            elif char == '.':
                level += 1
                status = 0
            else:
                return 0
    return level if status == 0 else 0

def figure_level(prefix):
    "level of a figure caption: 'x.' -> 1, '0.x.' -> 2, '0.0.x.' -> 3, …, else -> 0"
    if fnmatchcase(prefix, '[a-z].'):
        return 1
    elif not fnmatchcase(prefix, '*[a-z].'):
        return 0
    else:
        chaplevel = chapter_level(prefix[:-2])
        return 0 if chaplevel == 0 else chaplevel + 1

def page_number2str(num_page, page_offset):
    'display page number, possibly by a Roman number'
    try:
        return int2roman(num_page) if num_page <= -page_offset else str(num_page + page_offset)
    except ValueError:
        error(f"Roman page number greater than 'mmmcmxcix' = 3999 is not allowed")

#----- class YawpError -----

class YawpError(Exception): pass # error control in GUI mode

#----- class Variables -----

class Variables: pass # global not-argument scalar variables

var = Variables()

#----- class Arguments -----

class Arguments:

    def __init__(arg):
        arg.name_default = {} # {name: default} filled by get_arguments()
        arg.blacklist = {'help','view_manual','version','usage_mode','verbose','text_file'} # don't read/write these args from/into arg file
        arg.shorts_longs = [] # [(short, long), …]

    def read_from_argv(arg, argv):
        parser = ArgumentParser(prog='yawp', formatter_class=RawDescriptionHelpFormatter, description=DESCRIPTION)
        #
        def varg(short, long, version):
            'version argument'
            # no need for arg.name_default tooltip NON_RADIO_CHARS arg shorts_longs
            parser.add_argument(short, long, action='version', version=f'YAWP {VERSION}')
        #
        def barg(short, long, help):
            'boolean (checkbox) argument'
            name = long[2:].replace('-','_')
            arg.name_default[name] = False
            letter = short[1]
            tooltip[letter] = help.replace(' (','\n(').replace(', ',',\n')
            help=help.replace('%','%%')
            parser.add_argument(short, long, action='store_true', help=help)
            arg.shorts_longs.append((short, long))
        #
        def sarg(short, long, default, help, note=''):
            'string or multiple choice (radio button) argument'
            name = long[2:].replace('-','_')
            arg.name_default[name] = default
            letter = short[1]
            help = f"{help} (default: '{default}'{note})"
            tooltip[letter] = help.replace(' (','\n(').replace(', ',',\n')
            help=help.replace('%','%%')
            parser.add_argument(short, long, default=default, help=help)
            arg.shorts_longs.append((short, long))
        #
        def parg(name, nargs, help):
            'positional argument, text_file or target_file)'
            arg.name_default[name] = '' # default is undefined
            letter = name[0] # == 't'
            if letter not in tooltip: # tooltip['t'] from text_file not from target_file 
                tooltip[letter] = help.replace(' (','\n(').replace(', ',',\n')
            help=help.replace('%','%%')
            parser.add_argument(name, nargs=nargs, help=help)
            arg.shorts_longs.append(('', name))
        #
        # usage arguments
        varg('-V', '--version',         f'YAWP {VERSION}')
        barg('-H', '--browse-manual',   'browse the YAWP-generated PDF YAWP User Manual and exit')
        barg('-v', '--verbose',         'write information messages on stdout too (CLI modes only)')
        sarg('-M', '--usage-mode',      'g', "run YAWP in this usage mode",
             "=GUI, 'c'=CLI Copy, 'm'=CLI Move, 'd'=CLI Delete, 'e'=CLI Edit, 'f'=CLI Format, 'n'=CLI Noform, 'u'=CLI Undo")
        # format arguments
        sarg('-y', '--text-editor',     'kwrite', "editor for text files")
        barg('-l', '--left-only-text',  'justify text lines at left only (default: at left and right)')
        sarg('-w', '--chars-per-line',  '0', 'line width in characters per line', '=automatic')
        barg('-g', '--graph_pictures',  "redraw '`'-segments and '^'-arrowheads")
        sarg('-b', '--left-blanks',     '1', "left blanks when -k is 'l'=left", ", min: '1'")
        sarg('-u', '--lines-per-page',  '0', 'page height in lines per page', '=automatic')
        sarg('-k', '--align-pictures',  'n', 'align pictures', "=no, 'l'=left, 'c'=center, 'r'=right")
        # chapter arguments
        sarg('-c', '--contents-title',  'Contents', 'title of Contents chapter')
        sarg('-i', '--index-title',     'Index', 'title of Index chapter')
        sarg('-f', '--figures-title',   'Figures', 'title of Figures chapter')
        sarg('-F', '--caption-prefix',  'Figure', 'first word of figure captions')
        sarg('-m', '--chapter-offset',  '0', 'numbering offset for level-1 chapters', ', min: -1')
        # paging arguments
        sarg('-p', '--page-headers',    'c', "insert page headers",
             ", 'n'=no, 'f'=on full page, 'p'=and on broken pictures, 'c'=and on level-1 chapters, 'd'=double if level-1 on even page")
        sarg('-e', '--even-left',       '%n', 'first line of headers of even pages, left')
        sarg('-E', '--even-right',      '%f', 'first line of headers of even pages, right')
        sarg('-o', '--odd-left',        '%c', 'first line of headers of odd pages, left')
        sarg('-O', '--odd-right',       '%n', 'first line of headers of odd pages, right')
        sarg('-n', '--page-offset',     '0', 'numbering offset for pages', ', if negative: Roman numbers')
        barg('-a', '--all-pages-E-e',   "put in all page headers -E at left and -e at right")
        sarg('-s', '--second_line',     's', 'second line of page headers', ", 'n'=no, 'b'=blanks, 'p'=points, 'd'=dashes, 's'=solid")
        # export arguments
        sarg('-X', '--export-pdf',      'b', 'export and browse PDF file', ", 'n'=no, 'e'=export, 'b'=export and browse")
        sarg('-C', '--correct',         'd', 'correct character size and page margins', ", 'n'=no, 'd'=by default values, 'f'=by correction file")
        sarg('-Y', '--pdf-browser',     'atril', 'browser for PDF files')
        sarg('-P', '--pdf-file',        '%f%e.pdf', 'exported PDF file')
        sarg('-W', '--char-width',      '0', 'character width', '=automatic' + UNITS)
        sarg('-A', '--char-aspect',     '3/5', 'character aspect ratio=width / height', ", '1'=square chars")
        sarg('-S', '--sheet-size',      'A4', "portrait paper size width x height", "≡'210x297mm'" + UNITS)
        barg('-Z', '--landscape',       "turn page by 90° (default: portrait)")
        sarg('-L', '--left-margin',     '2cm', "left margin", UNITS)
        sarg('-R', '--right-margin',    '2cm', "right margin", UNITS)
        sarg('-T', '--top-margin',      '2cm', "top margin", UNITS)
        sarg('-B', '--bottom-margin',   '2cm', "bottom margin", UNITS)
        sarg('-I', '--multi-pages',     '1', 'pages on each side of paper sheets', ", values: 1/2/4/8")
        sarg('-J', '--multi-sheets',    '0', 'paper sheets gathered together', "=export sequentially")
        # file arguments
        parg('text_files', '*', 'text file[s] to process, ASCII or UTF-8-encoded Unicode')
        # arguments → arg.*
        parser.parse_args(argv[1:], arg)
        arg.text_file = ''
        # -h is managed by ArgumentParser
        # -V is managed by ArgumentParser
        # -H
        if arg.browse_manual:
            arg.check_pdf_browser()
            shell(f'{arg.pdf_browser} {MANUAL_FILE!r}')
            exit(0)
        # -M, text_file, target_file
        if arg.usage_mode not in set(USAGE_MODES):
            error(f'Wrong -M {arg.usage_mode}, it must be a char in in {USAGE_MODES!r}')
        if arg.usage_mode == 'g' and len(argv) != 1 + len(arg.text_files):
            error(f"With -M g no argument is allowed, except possibly the text_file[s]")
        arg.text_files = [longpath(text_file) for text_file in arg.text_files] 
        if arg.usage_mode == 'g':
            arg.verbose = False
            if not arg.text_files:
                arg.text_file = read_sess_file()
            elif len(arg.text_files) == 1:
                arg.text_file = arg.text_files[0]
            else: # len(arg.text_files) > 1:
                jdup = finddup(arg.text_files)
                if jdup > -1:
                    error(f'Duplicated text file {arg.text_files[jdup]!r}')
                shell(' & '.join(f'yawp {text_file!r}' for text_file in arg.text_files))
                exit(0)
        elif arg.usage_mode in 'cm':
            if len(arg.text_files) != 2:
                error(f'Text files are {len(arg.text_files)} while with -M {arg.usage_mode} they should be exactly 2 (text file and target file)')
            arg.text_file, arg.target_file = arg.text_files
        else:
            if len(arg.text_files) != 1:
                error(f'Text files are {len(arg.text_files)} while with -M {arg.usage_mode} they should be exactly 1')
            arg.text_file = arg.text_files[0]
        arg.read_from_args_file_of(arg.text_file)

    def inform(arg, all=False):
        'display non-default arguments (or all arguments if all==True, for debug only)'
        if all:
            arg.verbose = True
        names_values = []; len_name = 0
        for short, long in arg.shorts_longs:
            name = replace(long, '--', '', '-', '_')
            if all or name not in arg.blacklist or name == 'verbose':
                value = eval(name, arg.__dict__, arg.__dict__)
                default = arg.name_default[name]
                if all or value != default:
                    len_name = max(len_name, len(name))
                    names_values.append((name, value))
        inform(('Arguments:\n' if all else 'Non-default arguments:\n') +
               '\n'.join(f'    {name:{len_name}} = {value!r}' for name, value in sorted(names_values)))

    def read_from_args_file_of(arg, text_file):
        '''if args_file_of(text_file) not found, all args get their default values
on error reading an arg, arg maintains its default value'''
        if arg.usage_mode == 'g':
            arg.set_default()
            if isfile(text_file):
                args_file = args_file_of(text_file)
                if isfile(args_file):
                    for line in read_file_lines(args_file):
                        stmt = line2stmt(line)
                        if stmt:
                            try:
                                name, value = stmt.split('=')
                                name, value = strip(name), strip(value)
                                if name in arg.name_default and name not in arg.blacklist:
                                    setattr(arg, name, eval(value, {}, {}))
                            except:
                                pass
                
    def write_into_args_file_of(arg, text_file):
        if arg.usage_mode == 'g' and isfile(text_file):
            lines = []
            for short, long in arg.shorts_longs:
                name = long.replace('--','').replace('-','_')
                if name not in arg.blacklist:
                    value = eval(name, arg.__dict__, arg.__dict__)
                    if value != arg.name_default[name]:
                        lines.append(f'{name} = {value!r}')
            write_file_lines(args_file_of(text_file), lines)
            
    def read_from_window(arg, window):
        (arg.text_editor, arg.left_only_text, arg.chars_per_line, arg.graph_pictures, arg.left_blanks, arg.lines_per_page, 
         arg.contents_title, arg.index_title, arg.figures_title, arg.caption_prefix, arg.chapter_offset,
         arg.even_left, arg.even_right, arg.odd_left, arg.odd_right, arg.page_offset, arg.all_pages_E_e,
         arg.pdf_browser, arg.pdf_file, arg.char_width, arg.char_aspect, arg.sheet_size, arg.landscape,
         arg.left_margin, arg.right_margin, arg.top_margin, arg.bottom_margin, arg.multi_sheets,
         arg.text_file) = [window[char].get() for char in NON_RADIO_CHARS]
        arg.align_pictures, arg.page_headers, arg.second_line, arg.export_pdf, arg.correct, arg.multi_pages = get_radios(window, RADIO_LIST)        

    def write_into_window(arg, window):
        for letter, value in zip(NON_RADIO_CHARS,
            (arg.text_editor, arg.left_only_text, arg.chars_per_line, arg.graph_pictures, arg.left_blanks, arg.lines_per_page,
             arg.contents_title, arg.index_title, arg.figures_title, arg.caption_prefix, arg.chapter_offset,
             arg.even_left, arg.even_right, arg.odd_left, arg.odd_right, arg.page_offset, arg.all_pages_E_e,
             arg.pdf_browser, arg.pdf_file, arg.char_width, arg.char_aspect, arg.sheet_size, arg.landscape,
             arg.left_margin, arg.right_margin, arg.top_margin, arg.bottom_margin, arg.multi_sheets,
             arg.text_file)):
            window[letter].update(value)
        put_radios(window, RADIO_LIST, (arg.align_pictures, arg.page_headers, arg.second_line, arg.export_pdf, arg.correct, arg.multi_pages))
        window.refresh()

    def shrink_all(arg):
        for name, default in arg.name_default.items():
            if name not in arg.blacklist:
                value = getattr(arg, name)
                if isinstance(value, str):
                    setattr(arg, name, shrink(value))

    def set_default(arg):
        for name, default in arg.name_default.items():
            if name not in arg.blacklist:
                setattr(arg, name, default)

    def set_default_if_empty(arg):
        for name, default in arg.name_default.items():
            if name not in arg.blacklist:
                value = getattr(arg, name)
                if isinstance(value, str) and not strip(value):
                    setattr(arg, name, default)

    def check(arg):
        arg.shrink_all()
        # -y
        arg.check_text_editor()
        # -w
        try:
            var.chars_per_line = str2int(arg.chars_per_line, min=0)
        except ValueError:
            error(f'Wrong -w --chars-per-line {arg.chars_per_line!r}, it must be an integer ≥ 0')
        # -u
        try:
            var.lines_per_page = str2int(arg.lines_per_page, min=0)
        except ValueError:
            error(f'Wrong -u --lines-per-page {arg.lines_per_page!r}, it must be an integer ≥ 0')
        # -b
        try:
            var.left_blanks = str2int(arg.left_blanks, min=1)
        except ValueError:
            error(f'Wrong -b --left-blanks {arg.left_blanks!r}, it must be an integer ≥ 1')
        # -c
        var.contents_title = shrink_alphaupper(arg.contents_title)
        if not var.contents_title:
            error(f"Wrong -c --contents-title '', it cannot be empty")
        # -i
        var.index_title = shrink_alphaupper(arg.index_title)
        if not var.index_title:
            error(f"Wrong -i --index-title '', it cannot be empty")
        # -f
        var.figures_title = shrink_alphaupper(arg.figures_title)
        if not var.figures_title:
            error(f"Wrong -f --figures-title '', it cannot be empty")
        # -c -i -f
        if len(set([var.contents_title, var.index_title, var.figures_title])) < 3:
            error(f'Wrong -c -i -f, they must be all different')
        # -F
        var.caption_prefix = shrink_alphaupper(arg.caption_prefix)
        if not var.caption_prefix:
            error(f"Wrong -F --caption-prefix '', it cannot be empty")
        if ' ' in var.caption_prefix:
            error(f"Wrong -F --caption-prefix {arg.caption_prefix!r}, it cannot contain blanks")
        # -m
        try:
            var.chapter_offset = str2int(arg.chapter_offset, min=-1)
        except ValueError:
            error(f'Wrong -m --chapter-offset {arg.chapter_offset!r}, it must be an integer ≥ -1')
        # -p
        if arg.page_headers not in RADIO_DICT['p']:
            error(f"Wrong -p --page-headers {arg.page_headers!r}, it must be in {RADIO_DICT['p']}")
        # -e
        try:
            evalchar(arg.even_left, 'iPpfeYmdHMSunNc', 'iPpfeYmdHMSunNc', '%')
        except ValueError as illegal:
            error(f'Wrong -e --even-left {arg.even_left!r}, illegal {str(illegal)!r}')
        # -E
        try:
            evalchar(arg.even_right, 'iPpfeYmdHMSunNc', 'iPpfeYmdHMSunNc', '%')
        except ValueError as illegal:
            error(f'Wrong -E --even-right {arg.even_right!r}, illegal {str(illegal)!r}')
        # -o
        try:
            evalchar(arg.odd_left, 'iPpfeYmdHMSunNc', 'iPpfeYmdHMSunNc', '%')
        except ValueError as illegal:
            error(f'Wrong -o --odd-left {arg.odd_left!r}, illegal {str(illegal)!r}')
        # -O
        try:
            evalchar(arg.odd_right, 'iPpfeYmdHMSunNc', 'iPpfeYmdHMSunNc', '%')
        except ValueError as illegal:
            error(f'Wrong -O --odd-right {arg.odd_right!r}, illegal {str(illegal)!r}')
        # -n
        try:
            var.page_offset = str2int(arg.page_offset, min=None)
        except ValueError:
            error(f'Wrong -n --page-offset {arg.page_offset!r}, it must be an integer')
        # -s
        if arg.second_line not in RADIO_DICT['s']:
            error(f"Wrong -s --second-line {arg.second_line!r}, it must be in {SECOND_LINE!r}")
        var.page_header_lines = 0 if arg.page_headers == 'n' else 1 if arg.second_line == 'n' else 2
        # -X
        if arg.export_pdf not in RADIO_DICT['X']:
            error(f"Wrong -X --export-view-pdf {arg.export_pdf!r}, it must be in {RADIO_DICT['X']}")
        # -C
        if arg.correct not in RADIO_DICT['C']:
            error(f"Wrong -C --correct {arg.correct!r}, it must be in {RADIO_DICT['C']}")
        # -Y
        arg.check_pdf_browser()
        # -P
        try:
            evalchar(arg.pdf_file, 'iPpfeYmdHMSu', 'iPpfeYmdHMSu', '%')
        except ValueError as illegal:
            error(f'Wrong -P --pdf-file {arg.pdf_file!r}, illegal {str(illegal)!r}')
        if not arg.pdf_file.endswith('.pdf'):
            error(f"Wrong -P --pdf-file {arg.pdf_file!r}, not ending with '.pdf'")
        # -W
        try:
            var.char_width = str2inch(arg.char_width)
        except ValueError:
            error(f"Wrong -W --char-width {arg.char_width!r}, it must be zero or unsigned float + 'in'/'pt'/'cm'/'mm'")
        # -A
        try:
            var.char_aspect = str2ratio(arg.char_aspect)
        except (ValueError, AssertionError):
            error(f"Wrong -A --char-aspect {arg.char_aspect!r}, it must be unsigned float or unsigned float + '/' + unsigned float ")
        # -S
        try:
            var.sheet_width, var.sheet_height = str2inxin(PAPERSIZE.get(arg.sheet_size.upper(), arg.sheet_size))
        except ValueError:
            error(f"Wrong -S --sheet-size {arg.sheet_size!r}, it must be a format name or width 'x' height + 'in'/'pt'/'cm'/'mm'")
        # -Z
        if arg.landscape:
            var.sheet_width, var.sheet_height = var.sheet_height, var.sheet_width
        # -L
        try:
            var.left_margin = str2inch(arg.left_margin)
        except ValueError:
            error(f"Wrong -L --left-margin {arg.left_margin!r}, it must be zero or unsigned float + 'in'/'pt'/'cm'/'mm'")
        # -R
        try:
            var.right_margin = str2inch(arg.right_margin)
        except ValueError:
            error(f"Wrong -R --right-margin {arg.right_margin!r}, it must be zero or unsigned float + 'in'/'pt'/'cm'/'mm'")
        # -T
        try:
            var.top_margin = str2inch(arg.top_margin)
        except ValueError:
            error(f"Wrong -T --top-margin {arg.top_margin!r}, it must be zero or unsigned float + 'in'/'pt'/'cm'/'mm'")
        # -B
        try:
            var.bottom_margin = str2inch(arg.bottom_margin)
        except ValueError:
            error(f"Wrong -B --bottom-margin {arg.bottom_margin!r}, it must be zero or unsigned float + 'in'/'pt'/'cm'/'mm'")
        # -I
        if arg.multi_pages not in RADIO_DICT['I']:
            error(f"Wrong -I --multi_pages {arg.multi_pages}, it must be in {MULTI_PAGES}")
        var.multi_pages = int(arg.multi_pages)
        if arg.page_headers == 'n' and var.multi_pages > 1:
            error(f"Wrong -I --multi_pages {arg.multi_pages}, it must be 1 when -p is 'n'")
        # -J
        try:
            var.multi_sheets = str2int(arg.multi_sheets, min=0)
        except ValueError:
            error(f"Wrong -J --many-sheets {arg.multi_sheets!r}, it must be an integer ≥ 0")
        if var.multi_pages == 1:
            var.multi_sheets = 0
        elif var.multi_pages == 2 and arg.landscape and var.multi_sheets > 1:
            var.multi_sheets = 1
        # text_file
        arg.text_file = strip(arg.text_file)
        if arg.text_file:
            arg.text_file = longpath(arg.text_file)
        
    def check_text_editor(arg):
        if not command_exists(arg.text_editor):
            error(f'Wrong -y --text-editor {arg.text_editor!r}, command not found')

    def check_pdf_browser(arg):
        if not command_exists(arg.pdf_browser):
            error(f'Wrong -Y --pdf-browser {arg.pdf_browser!r}, command not found')

arg = Arguments()

#----- class History -----

class History:
    'management of the list of recent text files'

    def __init__(hist):
        hist.files = []

    def read(hist):
        if isfile(HIST_FILE):
            hist.files = [file for file in read_file_lines(HIST_FILE) if isfile(file)][:MAX_HISTORY]
        else:
            hist.files = []

    def write(hist):
        write_file_lines(HIST_FILE, [file for file in hist.files if isfile(file)][:MAX_HISTORY])
        
    def clear(hist):
        rm(HIST_FILE)

    def add(hist, file):
        if arg.usage_mode == 'g' and isfile(file):
            hist.read()
            hist.files = unique([file] + hist.files)[:MAX_HISTORY]
            hist.write()

    def select(hist):
        hist.read()
        if not hist.files:
            error(f'List of recent files is empty')
        layout = [[psg.Text(f'{jfile+1:2}.'), psg.Button(file, size=0,
                    tooltip='Select this file as the current text file')]
                  for jfile, file in enumerate(hist.files)] + [
                      [psg.Button('Clear', tooltip='Clear the list of recent files', size=BSIZE),
                       psg.Button('Cancel', tooltip='Exit with no selection', size=BSIZE)]]
        window = psg.Window(f'YAWP - Recent', layout)
        while True:
            event, values = window.read()
            if event in [None, 'Cancel']:
                window.close()
                return ''
            elif event == 'Clear':
                if ask_yes('YAWP - Recent', 'History of recent text files will be lost.\nDo you want to clear history?', 'clear'):
                    hist.clear()
                    var.ok_message = ', list of recent files is empty'
                    window.close()
                    return ''
            else:
                file = longpath(event)
                hist.add(file)
                window.close()
                return file

hist = History()

#----- class Lock -----

class Lock:
    'seize and release text files'

    def __init__(lock):
        lock.locked_files = set()

    def seize(lock, file):
        'seize file by YAWP instance INSTANCE'
        check_file(file)
        lock_file = lock_file_of(file)
        if not isfile(lock_file):
            pass
        elif read_file(lock_file) == INSTANCE: 
            return
        else:
            warning(f'File {file!r} is locked.')
        write_file(lock_file, INSTANCE)
        lock.locked_files.add(file)

    def release(lock, file):
        'release file, if locked by this YAWP instance'
        if file:
            lock_file = lock_file_of(file)
            if isfile(lock_file) and read_file(lock_file) == INSTANCE:
                rm(lock_file)
            if file in lock.locked_files:
                lock.locked_files.remove(file)

    def release_all(lock):
        for file in lock.locked_files.copy():
            lock.release(file)

    def is_mine(lock, file):
        'file is locked by this YAWP instance?'
        if not isfile(file):
            return False
        lock_file = lock_file_of(file)
        return isfile(lock_file) and read_file(lock_file) == INSTANCE

lock = Lock()

#----- class Paragraph -----

class Paragraph:
    'text paragraph during formatting, indented or unindented'

    def __init__(par):
        par.string = ''
        par.jinp = 0
        par.indent = 0

    def assign(par, string, jinp, indent):
        assert not par.string
        par.string = shrink(string)
        par.jinp = jinp
        par.indent = indent
        if indent > var.chars_per_line // 2:
            error(f"Indent of indented paragraph = {indent} > -w / 2 = {var.chars_per_line // 2}", jinp)

    def append(par, string):
        assert par.string
        par.string += ' ' + shrink(string)

    def flush(par, buffer2):
        if not par.string:
            return
        prefix = (par.indent - 2) * ' ' + '• ' if par.indent else ''
        while len(par.string) > var.chars_per_line - par.indent:
            jchar = rfind(par.string[:var.chars_per_line-par.indent+1], ' ')
            if jchar <= 0:
                error(f'Impossible to left-justify', par.jinp)
            string, par.string = par.string[:jchar], par.string[jchar+1:]
            if not arg.left_only_text:
                try:
                    string = expand(string, var.chars_per_line - par.indent)
                except ValueError:
                    error(f'Impossible to right-justify', par.jinp)
            buffer2.append([par.jinp, TEXT, 0, 0, prefix + string])
            prefix = par.indent * ' '
        if par.string:
            buffer2.append([par.jinp, TEXT, 0, 0, prefix + par.string])
            par.string = ''

par = Paragraph()

#----- class Correction -----

class Correction:

    def __init__(corr):
        KEYS = 'plm llm prm lrm ptm ltm pbm lbm pcw lcw pch lch'.split()
        corr.points = {k: [] for k in KEYS}
        # read correction points from YAWP_CORR
        if arg.correct != 'n':
            for jline, line in enumerate(read_file_lines(YAWP_CORR) if arg.correct == 'f' else CORR_DEFAULT.split('\n')):
                stmt = line2stmt(line)
                if stmt:
                    kyx = stmt.split()
                    if len(kyx) != 3:
                        error(f'In correction file, found {len(kyx)} values instead of 3', jline)
                    k, sy, sx = kyx
                    if k not in corr.points:
                        error(f'In correction file, wrong key {k!r}', jline)
                    try:
                        x = str2inch(sx)
                        assert x >= 0.0 and (not corr.points[k] or x > corr.points[k][-1][0])
                    except (ValueError, AssertionError):
                        error(f'In correction file, wrong x-value {sx!r}, must be ', jline)
                    try:
                        y = str2inch(sy)
                        assert y >= 0.0 and (not corr.points[k] or x > corr.points[k][-1][1])
                    except (ValueError, AssertionError):
                        error(f'In correction file, wrong y-value {sy!r}', jline)
                    corr.points[k].append((x, y))
            for k in KEYS:
                corr.points[k].sort()

#----- class Pdf -----

class Pdf:

    def zoom(pdf, pdf_file):
        
        def upside_down(page):
            page.Rotate = (int(page.inheritable.Rotate or 0) + 180) % 360

        def p20(pages):
            pages = PageMerge() + pages
            dx, dy = (SCALE_2 * i for i in pages.xobj_box[2:])
            for jx, page in enumerate(pages):
                page.scale(SCALE_2)
                page.x = jx * dx
                page.y = 0
            yield pages.render()

        def p40(pages):
            pages = PageMerge() + pages
            dx, dy = (SCALE_4 * i for i in pages.xobj_box[2:])
            for k, page in enumerate(pages):
                page.scale(SCALE_4)
                jy, jx = divmod(k, 2)
                page.x = jx * dx
                page.y = (1 - jy) * dy
            yield pages.render()

        def p80(pages):
            pages = PageMerge() + pages
            dx, dy = (SCALE_8 * i for i in pages.xobj_box[2:])
            for k, page in enumerate(pages):
                page.scale(SCALE_8)
                jy, jx = divmod(k, 4)
                page.x = jx * dx
                page.y = (1 - jy) * dy
            yield pages.render()

        def p21(pages_pages):
            n = len(pages_pages)
            swap = [n - 1, 0, 1, n - 2]
            while len(swap) < n:
                for step in [-2, 2, 2, -2]:
                    swap.append(swap[-4] + step)
            pages_pages = [pages_pages[i] for i in swap]
            for i in range(0, n, 2):
                pages = pages_pages[i:i+2]
                pages = PageMerge() + pages
                dx, dy = (SCALE_2 * i for i in pages.xobj_box[2:])
                for jx, page in enumerate(pages):
                    page.scale(SCALE_2)
                    page.x = jx * dx
                    page.y = 0
                yield pages.render()

        def p41(pages_pages):
            n = len(pages_pages)
            h = n // 2
            swap = [h, h - 1, n - 1, 0, h - 2, h + 1, 1, n - 2]
            while len(swap) < n:
                for step in [2, -2, -2, 2, -2, 2, 2, -2]:
                    swap.append(swap[-8] + step)
            pages_pages = [pages_pages[i] for i in swap]
            for i, page in enumerate(pages_pages):
                if i % 4 < 2:
                    upside_down(page)
            for i in range(0, n, 4):
                pages = pages_pages[i:i+4]
                pages = PageMerge() + pages
                dx, dy = (SCALE_4 * i for i in pages.xobj_box[2:])
                for j, page in enumerate(pages):
                    page.scale(SCALE_4)
                    jy, jx = divmod(j, 2)
                    page.x = jx * dx
                    page.y = (1 - jy) * dy
                yield pages.render()

        def p81(pages_pages):
            n = len(pages_pages)
            swap = [4, n - 5, n - 8, 7, 3, n - 4, n - 1, 0, 6, n - 7, n - 6, 5, 1, n - 2, n - 3, 2]
            while len(swap) < n:
                for step in 4 * [8, -8, -8, 8]:
                    swap.append(swap[-16] + step)
            pages_pages = [pages_pages[i] for i in swap]
            for i, page in enumerate(pages_pages):
                if i % 8 < 4:
                    upside_down(page)
            for i in range(0, n, 8):
                pages = pages_pages[i:i+8]
                pages = PageMerge() + pages
                dx, dy = (SCALE_8 * i for i in pages.xobj_box[2:])
                for j, page in enumerate(pages):
                    page.scale(SCALE_8)
                    jy, jx = divmod(j, 4)
                    page.x = jx * dx
                    page.y = (1 - jy) * dy
                yield pages.render()

        def l20(pages):
            pages = PageMerge() + pages
            dx, dy = (SCALE_2 * i for i in pages.xobj_box[2:])
            for jy, page in enumerate(pages):
                page.scale(SCALE_2)
                page.x = 0
                page.y = (1 - jy) * dy
            yield pages.render()

        def l40(pages):
            pages = PageMerge() + pages
            dx, dy = (SCALE_4 * i for i in pages.xobj_box[2:])
            for i, page in enumerate(pages):
                page.scale(SCALE_4)
                jy, jx = divmod(i, 2)
                page.x = jx * dx
                page.y = (1 - jy) * dy
            yield pages.render()

        def l80(pages): 
            pages = PageMerge() + pages
            dx, dy = (SCALE_8 * i for i in pages.xobj_box[2:])
            for i, page in enumerate(pages):
                page.scale(SCALE_8)
                jy, jx = divmod(i, 2)
                page.x = jx * dx
                page.y = (3 - jy) * dy
            yield pages.render()

        def l21(pages_pages):
            n = len(pages_pages)
            pages_pages = [pages_pages[i] for i in [3, 0, 2, 1]]
            for i, page in enumerate(pages_pages):
                if i % 2 == 0:
                    upside_down(page)
            for i in range(0, n, 2):
                pages = pages_pages[i:i+2]
                pages = PageMerge() + pages
                dx, dy = (SCALE_2 * i for i in pages.xobj_box[2:])
                for jy, page in enumerate(pages):
                    page.scale(SCALE_2)
                    page.x = 0
                    page.y = (1 - jy) * dy
                yield pages.render()

        l41 = p41

        def l81(pages_pages):
            n = len(pages_pages)
            swap = [n - 4, 3, n - 5, 4, n - 8, 7, n - 1, 0, 2, n - 3, 5, n - 6, 6, n - 7, 1, n - 2]
            while len(swap) < n:
                for step in 4 * [-8, 8] + 4 * [8, -8]:
                    swap.append(swap[-16] + step)
            pages_pages = [pages_pages[i] for i in swap]
            for i, page in enumerate(pages_pages):
                if i % 4 < 2:
                    upside_down(page)
            for i in range(0, n, 8):
                pages = pages_pages[i:i+8]
                pages = PageMerge() + pages
                dx, dy = (SCALE_8 * i for i in pages.xobj_box[2:])
                for j, page in enumerate(pages):
                    page.scale(SCALE_8)
                    jy, jx = divmod(j, 2)
                    page.x = jx * dx
                    page.y = (3 - jy) * dy
                yield pages.render()

        if var.multi_pages > 1:
            yield_pages = {'p20': p20, 'p40': p40, 'p80': p80, 'p21': p21, 'p41': p41, 'p81': p81,
                           'l20': l20, 'l40': l40, 'l80': l80, 'l21': l21, 'l41': l41, 'l81': l81}[
                          f"{'pl'[arg.landscape]}{var.multi_pages}{min(1, var.multi_sheets)}"]
            pages = PdfReader(pdf_file).pages # read pdf_file
            writer = PdfWriter(pdf_file) # rewrite pdf_file
            for jpage in range(0, len(pages), var.len_pages_pages):
                for page in yield_pages(pages[jpage:jpage + var.len_pages_pages]):
                    writer.addpage(page)
            writer.write()

    def text2temp(pdf, text_file, target_file):
        'copy text_file into target_file adding final FORMFEED chars if needed'
        if not isfile(text_file):
            error(f'Text file {text_file!r} not found')
        lines = list(read_file_lines(text_file))
        num_pages = sum(line.startswith(FORMFEED) for line in lines) + 1
        var.min_multi_sheets = min(var.multi_sheets, ceildiv(num_pages, 2 * var.multi_pages))
        var.len_pages_pages = var.multi_pages if var.min_multi_sheets == 0 else 2 * var.multi_pages * var.min_multi_sheets
        while num_pages % var.len_pages_pages:
            lines.append(FORMFEED + LINEFEED)
            num_pages += 1
        write_file_lines(target_file, lines)
            
    def temp2pdf(pdf, temp_file, lp_page_left, sleep_seconds=0.33, len_blank_page=72):
        'export temp_file into pdf_file, wait lp completion, remove spurious blank pages, return pdf_file'
        shell(f'lp -d PDF ' # export temp_file into ~/PDF/.yawp.*.pdf
              f'-o print-quality={MAX_QUALITY} '
              f'-o media=Custom.{in2pt(var.sheet_width)}x{in2pt(var.sheet_height)} '
              f'-o cpi={pdf.lp_chars_per_inch} '
              f'-o lpi={pdf.lp_lines_per_inch} '
              f'-o page-top={in2pt(pdf.lp_page_top)} '
              f'-o page-left={in2pt(lp_page_left)} '
              f'-o page-right=0 ' 
              f'-o page-bottom={(arg.page_headers=="n")*in2pt(pdf.lp_page_bottom)} '
              f'{temp_file!r}')
        glob_pattern = f"{PDF_PATH}/{basename(temp_file).replace(' ','?')}*.pdf" # wait until pdf_file exists
        while True: 
            sleep(sleep_seconds)
            pdf_files = glob(glob_pattern)
            if pdf_files:
                pdf_file = pdf_files[0]
                break
        prev_size = getsize(pdf_file) # wait until size of pdf_file is stabilized
        while True:
            sleep(sleep_seconds)
            next_size = getsize(pdf_file)
            if next_size == prev_size:
                break
            prev_size = next_size      
        pages = PdfReader(pdf_file).pages # delete blank pages from pdf_file, except the initial and final ones
        is_not_blank = lambda page: len(page.Contents.stream) > len_blank_page 
        jpage_first_not_blank = None
        for jpage, page in enumerate(pages):
            if is_not_blank(page):
                jpage_first_not_blank = jpage; break
        if jpage_first_not_blank is None:
            error(f'not blank pages not found in PDF file')
        for jpage, page in retroenum(pages):
            if is_not_blank(page):
                jpage_last_not_blank = jpage; break
        pages2 = [page for jpage, page in enumerate(pages) if jpage < jpage_first_not_blank or jpage > jpage_last_not_blank or is_not_blank(page)]
        if len(pages2) < len(pages):
            pdf_writer = PdfWriter(pdf_file)
            for page in pages2:
                pdf_writer.addpage(page)
            pdf_writer.write()
        return pdf_file # return pdf_file

    def pdfpdf2pdf(pdf, even_pdf_file, odd_pdf_file, pdf_file):
        'merge even pages from even_pdf_file with odd pages from odd_pdf_file into pdf_file'
        even_pages = PdfReader(even_pdf_file).pages
        odd_pages = PdfReader(odd_pdf_file).pages
        pdf_writer = PdfWriter()
        for jpage, (even_page, odd_page) in enumerate(zip(even_pages, odd_pages)):
            pdf_writer.addpage(even_page if jpage % 2 else odd_page)
        pdf_writer.write(var.pdf_file)

    def correct(pdf):
        'compute parameters of lp commands, corrected (or not) following -C'
        corr = Correction()
        pl = 'pl'[arg.landscape]
        pdf.lp_page_left      = least_squares_line(corr.points[f'{pl}lm'], var.left_margin)
        pdf.lp_page_right     = least_squares_line(corr.points[f'{pl}rm'], var.right_margin)
        pdf.lp_page_top       = least_squares_line(corr.points[f'{pl}tm'], var.top_margin)
        pdf.lp_page_bottom    = least_squares_line(corr.points[f'{pl}bm'], var.bottom_margin)
        if pdf.lp_page_left < 0.0:
            warning(f'-L --left-margin {arg.left_margin} is too small, PDF file may be wrong')
            pdf.lp_page_left = 0.0
        if pdf.lp_page_right < 0.0:
            warning(f'-R --right-margin {arg.right_margin} is too small, PDF file may be wrong')
            pdf.lp_page_right = 0.0
        if pdf.lp_page_top < 0.0:
            warning(f'-T --top-margin {arg.top_margin} is too small, PDF file may be wrong')
            pdf.lp_page_top = 0.0
        if pdf.lp_page_bottom < 0.0:
            warning(f'-B --bottom-margin {arg.bottom_margin} is too small, PDF file may be wrong')
            pdf.lp_page_bottom = 0.0
        pdf.lp_page_left_odd_pages  = pdf.lp_page_left
        pdf.lp_page_left_even_pages = pdf.lp_page_left if arg.all_pages_E_e else pdf.lp_page_right
        pdf.lp_char_width     = least_squares_line(corr.points[f'{pl}cw'], var.char_width)
        if pdf.lp_char_width <= 0.0:
            error(f'Character width is too small, corrected value ≤ 0')
        pdf.lp_char_height    = least_squares_line(corr.points[f'{pl}ch'], var.char_height)
        if pdf.lp_char_height <= 0.0:
            error(f'Character height is too small, corrected value ≤ 0')
        pdf.lp_chars_per_inch = 1.0 / pdf.lp_char_width
        pdf.lp_lines_per_inch = 1.0 / pdf.lp_char_height
        if arg.correct != 'n':
            inform('\n'.join(['Corrections:',
                f'    left_margin    = {inch2str(pdf.lp_page_left, ROUND)}',  
                f'    right_margin   = {inch2str(pdf.lp_page_right, ROUND)}', 
                f'    top_margin     = {inch2str(pdf.lp_page_top, ROUND)}',   
                f'    bottom_margin  = {inch2str(pdf.lp_page_bottom, ROUND)}',
                f'    char_width     = {inch2str(pdf.lp_char_width, ROUND)}',
                f'    char_height    = {inch2str(pdf.lp_char_height, ROUND)}',
                f'    chars_per_inch = {round(pdf.lp_chars_per_inch, ROUND)}',
                f'    lines_per_inch = {round(pdf.lp_lines_per_inch, ROUND)}']))

    def export_and_browse(pdf, text_file):
        cd(dirname(arg.text_file)) # added in 2.1.2
        var.pdf_file = longpath(evalchar(arg.pdf_file, 'iPpfeYmdHMSu', var.iPpfeYmdHMSu, '%'))
        if not isdir(dirname(var.pdf_file)):
            error(f'Wrong -P --pdf-file {arg.pdf_file!r}, directory {dirname(var.pdf_file)!r} not found')
        pdf.correct()
        if arg.left_margin == arg.right_margin or arg.all_pages_E_e: # arg.text_file -> temp_file -> pdf_file -> var.pdf_file
            temp_file = new_temp_file()
            pdf.text2temp(arg.text_file, temp_file)
            pdf_file = pdf.temp2pdf(temp_file, pdf.lp_page_left)
            rm(temp_file)
            mv(pdf_file, var.pdf_file)
        else: # arg.text_file -> (even_temp_file -> odd_temp_file) -> (even_pdf_file, odd_pdf_file) -> var.pdf_file
            even_temp_file = new_temp_file()
            pdf.text2temp(arg.text_file, even_temp_file)
            even_pdf_file = pdf.temp2pdf(even_temp_file, pdf.lp_page_left_even_pages)
            odd_temp_file = new_temp_file() # new name
            mv(even_temp_file, odd_temp_file) # but same content
            odd_pdf_file = pdf.temp2pdf(odd_temp_file, pdf.lp_page_left_odd_pages)
            rm(odd_temp_file)
            pdf.pdfpdf2pdf(even_pdf_file, odd_pdf_file, var.pdf_file)
            rm(even_pdf_file)
            rm(odd_pdf_file)
        if var.multi_pages > 1:
            pdf.zoom(var.pdf_file)
        inform('\n'.join([f'Export:',
            f'    {arg.text_file!r} →',
            f'    {var.pdf_file!r}']))
        if arg.export_pdf == 'b':
            shell(f'{arg.pdf_browser} {var.pdf_file!r}')

pdf = Pdf()

#----- class Buffer -----

class Buffer:

    def dump(buf, title=''):
        'for debugging only'
        print('\n' + title.center(50, '<'))
        print("JOUT JINP KIND JPAG JLIN LPIC LINE") # jlin is line index in page
        jpag0 = None
        for jout, (jinp, kind, jpag, lpic, line) in enumerate(buf.buffer):
            if jpag != jpag0:
                jlin = 1
                jpag0 = jpag
            else:
                jlin += 1
            line2 = line.replace(NBSPACE,' ').replace(FORMFEED,'♩')
            print(f'{jout:4} {jinp:4} {KINDS[kind]} {jpag:4} {jlin:4} {lpic:4} {line2!r}')
        print(50 * '>' + '\n')

    def __init__(buf, file=''):
        buf.buffer = [] # [[jinp, kind, jpage, lpic, line]] # output buffer
        # jinp: line index in buf.input
        # kind: kind of line: TEXT, PICT, CONT, INDX, FIGU, CHP1, CHP2, HEA1, HEA2
        # jpage: page number
        # lpic: lines in picture (in first line of pictures only, else 0)
        # line
        buf.contents = [] # [[pref, title, jout]], if words == split(line):
        # pref: words[0], chapter numbering as '1.', '1.1.'…
        # title: ' '.join(words[1:])
        # jout: position of chapter line in buf.buffer
        buf.contents_found = False # file contains a contents chapter line?
        buf.contents_jout = -1 # position of contents chapter line in output
        buf.qsub_jouts = SetDict() # {subject: {jout}}
        # subject: subject between double quotes
        # jout: position of subject in buf.buffer
        buf.uqsub_jouts = SetDict() # {subject: {jout}}
        # subject: subject not between double quotes
        # jout: position of subject in buf.buffer
        buf.index_found = False # file contains an index chapter line?
        buf.index_jout = -1 # position of index chapter line in output
        buf.subjects = set()
        buf.figures_found = False # file contains a figures chapter line?
        buf.figures_jout = -1 # position of figures chapter line in buf.buffer
        buf.figures = [] # [[pref, title, jout]] , if words == split(line) …
        # words[0] == var.figures_title
        # pref: words[1], figure numbering as 'a.', '1.b.', '1.1.c.'…
        # title: ' '.join(words[2:])
        # jout: position of caption line in buf.buffer
        buf.head_lines, buf.head_chars, buf.head_words, buf.head_mxcpl, buf.num_pages = 0, 0, 0, 0, 1 # mxcpl = max chars per line
        buf.hea2_lines, buf.hea2_chars, buf.hea2_words, buf.hea2_mxcpl = 0, 0, 0, 0
        buf.body_lines, buf.body_chars, buf.body_words, buf.body_mxcpl = 0, 0, 0, 0
        if isfile(file):
            buf.read_from_file(file)

    def read_from_file(buf, file):
        buf.buffer = []
        buf.head_lines, buf.head_chars, buf.head_words, buf.head_mxcpl, buf.num_pages = 0, 0, 0, 0, 1
        buf.hea2_lines, buf.hea2_chars, buf.hea2_words, buf.hea2_mxcpl = 0, 0, 0, 0
        buf.body_lines, buf.body_chars, buf.body_words, buf.body_mxcpl = 0, 0, 0, 0
        for jinp, line in enumerate(read_file_lines(file)):
            buf.buffer.append([jinp, PICT, 1, 0, line])
            if line.startswith(FORMFEED):
                buf.head_chars += len(line) - 1
                buf.head_words += len(split(line[1:]))
                buf.head_mxcpl = max(buf.head_mxcpl, len(line) - 1)
                buf.head_lines += 1
                buf.num_pages += 1
            elif line and line[0] in HEADER_CHARS:
                buf.hea2_chars += len(line)
                buf.hea2_words += len(split(line))
                buf.hea2_mxcpl = max(buf.hea2_mxcpl, len(line))
                buf.hea2_lines += 1
            else:
                buf.body_chars += len(line)
                buf.body_words += len(split(line))
                buf.body_mxcpl = max(buf.body_mxcpl, len(line))
                buf.body_lines += 1

    def write_into_file(buf, file):
        buf.head_lines, buf.head_chars, buf.head_words, buf.head_mxcpl, buf.num_pages = 0, 0, 0, 0, 1 
        buf.hea2_lines, buf.hea2_chars, buf.hea2_words, buf.hea2_mxcpl = 0, 0, 0, 0
        buf.body_lines, buf.body_chars, buf.body_words, buf.body_mxcpl = 0, 0, 0, 0
        with open(file, 'w') as output:
            for record in buf.buffer:
                line = record[LINE]
                if line.startswith(FORMFEED):
                    buf.head_chars += len(line) - 1
                    buf.head_words += len(split(line[1:]))
                    buf.head_mxcpl = max(buf.head_mxcpl, len(line) - 1)
                    buf.head_lines += 1
                    buf.num_pages += 1
                elif line and line[0] in HEADER_CHARS:
                    buf.hea2_chars += len(line)
                    buf.hea2_words += len(split(line))
                    buf.hea2_mxcpl = max(buf.hea2_mxcpl, len(line))
                    buf.hea2_lines += 1
                else:
                    buf.body_chars += len(line)
                    buf.body_words += len(split(line))
                    buf.body_mxcpl = max(buf.body_mxcpl, len(line))
                    buf.body_lines += 1
                print(line, file=output)

    def copy(buf):
        buf2 = Buffer()
        buf.head_lines, buf.head_chars, buf.head_words, buf.head_mxcpl, buf.num_pages = 0, 0, 0, 0, 1 
        buf.hea2_lines, buf.hea2_chars, buf.hea2_words, buf.hea2_mxcpl = 0, 0, 0, 0 
        buf.body_lines, buf.body_chars, buf.body_words, buf.body_mxcpl = 0, 0, 0, 0
        for record in buf.buffer:
            rec2 = record[:] # deep copy
            buf2.buffer.append(rec2)
            line = rec2[LINE]
            if line.startswith(FORMFEED):
                buf.head_chars += len(line) - 1
                buf.head_words += len(split(line[1:]))
                buf.head_mxcpl = max(buf.head_mxcpl, len(line) - 1)
                buf.head_lines += 1
                buf.num_pages += 1
            elif line and line[0] in HEADER_CHARS:
                buf.hea2_chars += len(line)
                buf.hea2_words += len(split(line))
                buf.hea2_mxcpl = max(buf.hea2_mxcpl, len(line))
                buf.hea2_lines += 1
            else:
                buf.body_chars += len(line)
                buf.body_words += len(split(line))
                buf.body_mxcpl = max(buf.body_mxcpl, len(line))
                buf.body_lines += 1
        return buf2

    def inform(buf, title):
        'write informations about buf after last buf.read_from_file() or last buf.write_into_file() or last buf.copy()'
        buf.tota_lines = buf.head_lines + buf.hea2_lines + buf.body_lines
        buf.tota_words = buf.head_words + buf.hea2_words + buf.body_words
        buf.tota_chars = buf.head_chars + buf.hea2_chars + buf.body_chars
        buf.tota_mxcpl  = max(buf.head_mxcpl, buf.hea2_mxcpl, buf.body_mxcpl)
        l, w, c, m = [len(str(n)) for n in [buf.tota_lines, buf.tota_words, buf.tota_chars, buf.tota_mxcpl]]
        inform('\n'.join([title, 
            f'    header1: {buf.head_lines:{l}} lines, {buf.head_words:{w}} words, {buf.head_chars:{c}} chars, max {buf.head_mxcpl:{m}} chars per line, {many(buf.num_pages,"page")}',
            f'    header2: {buf.hea2_lines:{l}} lines, {buf.hea2_words:{w}} words, {buf.hea2_chars:{c}} chars, max {buf.hea2_mxcpl:{m}} chars per line',
            f'    body:    {buf.body_lines:{l}} lines, {buf.body_words:{w}} words, {buf.body_chars:{c}} chars, max {buf.body_mxcpl:{m}} chars per line',
            f'    total:   {buf.tota_lines:{l}} lines, {buf.tota_words:{w}} words, {buf.tota_chars:{c}} chars, max {buf.tota_mxcpl:{m}} chars per line']))
        
    def __eq__(buf, buf2):
        'text lines in buf.buffer == text lines in buf2.buffer?'
        return len(buf.buffer) == len(buf2.buffer) and all(record[LINE] == record2[LINE] for record, record2 in zip(buf.buffer, buf2.buffer))

    def char(buf, jout, jchar, default='*'):
        "return buf.buffer[jout][LINE][jchar], if not PICT or on IndexError return default, used by redraw_segments() and redraw_arroheads()"
        if jout < 0 or jchar < 0:
            return default
        else:
            try:
                line = buf.buffer[jout][LINE]
                return line[jchar] if buf.buffer[jout][KIND] == PICT else default
            except IndexError:
                return default

    def compute(buf):
        var.print_width = var.sheet_width - var.left_margin - var.right_margin
        var.print_height = var.sheet_height - var.top_margin - var.bottom_margin
        if var.print_width <= 0.0:
            error(f'-L and/or -R too large, no horizontal space on paper')
        if var.print_height <= 0.0:
            error(f'-T and/or -B too large, no vertical space on paper')
        w2W = lambda chars_per_line: var.print_width / chars_per_line
        u2W = lambda lines_per_page: var.print_height * var.char_aspect / lines_per_page
        W2w = lambda char_width: int(var.print_width / char_width)
        W2u = lambda char_width: int(var.print_height * var.char_aspect / char_width)
        if var.char_width == 0.0:
            if var.lines_per_page == 0:
                if var.chars_per_line == 0:
                    var.chars_per_line = max_text_line_length_in(arg.text_file)
                    if var.chars_per_line == 0:
                        error(f'Text file is empty, Format and Noform actions are impossible.') 
                    var.char_width = w2W(var.chars_per_line)
                    var.lines_per_page = W2u(var.char_width)
                else:
                    var.char_width = w2W(var.chars_per_line)
                    var.lines_per_page = W2u(var.char_width)
            else:
                if var.chars_per_line == 0:
                    var.char_width = u2W(var.lines_per_page)
                    var.chars_per_line = W2w(var.char_width)
                else:
                    var.char_width = min(w2W(var.chars_per_line), u2W(var.lines_per_page))
        else:
            if var.lines_per_page == 0:
                if var.chars_per_line == 0:
                    var.chars_per_line = W2w(var.char_width)
                    var.lines_per_page = W2u(var.char_width)
                else:
                    var.char_width = min(var.char_width, w2W(var.chars_per_line))
                    var.lines_per_page = W2u(var.char_width)
            else:
                if var.chars_per_line == 0:
                    var.char_width = min(var.char_width, u2W(var.lines_per_page))
                    var.chars_per_line = W2w(var.char_width)
                else:
                    var.char_width = min(var.char_width, w2W(var.chars_per_line), u2W(var.lines_per_page))
        var.char_height = var.char_width / var.char_aspect
        var.iPpfeYmdHMSu = iPpfeYmdHMSu_of(arg.text_file)
        inform('\n'.join(['Computations:',
            f'    print_width    = {inch2str(var.print_width, ROUND)}',
            f'    print_height   = {inch2str(var.print_height, ROUND)}',
            f'    chars_per_line = {var.chars_per_line}',
            f'    lines_per_page = {var.lines_per_page}',
            f'    char_width     = {inch2str(var.char_width, ROUND)}',
            f'    char_height    = {inch2str(var.char_height, ROUND)}',
            f'    chars_per_inch = {round(1.0/var.char_width, ROUND)}',
            f'    lines_per_inch = {round(1.0/var.char_height, ROUND)}']))
        
    def remove_page_headers(buf):
        buf.buffer = [record for record in buf.buffer if not startswithchars(record[LINE], HEADER_CHARS)]

    def justify_lines(buf):
        buffer2 = []
        for jinp, x, x, x, line in buf.buffer:
            if not line: # empty line
                par.flush(buffer2)
                buffer2.append([jinp, EMPT, 0, 0, ''])
            else:
                jdot = findchar(line, '[! ]')
                if jdot >= 0 and line[jdot:jdot+2] in ['• ','. ']: # dot line
                    if jdot + 2 > var.chars_per_line:
                        error(f'Dot line indentation {jdot+2} > chars per line {var.chars_per_line}')
                    par.flush(buffer2)
                    par.assign(strip(line[jdot+2:]), jinp, jdot + 2)
                elif line[0] == ' ': # indented line
                    if par.string:
                        par.append(line)
                    else:
                        buffer2.append([jinp, PICT, 0, 0, line])
                elif par.string: # unindented line
                    par.append(line)
                else:
                    par.assign(line, jinp, 0)
        par.flush(buffer2)
        buf.buffer = buffer2

    def redraw_segments(buf):
        charstr = '`─│┐│┘│┤──┌┬└┴├┼'
        #          0123456789ABCDEF
        charset = frozenset(charstr)
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if kind == PICT:
                chars = list(line)
                for jchar, char in enumerate(chars):
                    if char in charset:
                        kchar = (    (buf.char(jout, jchar - 1) in charset) +
                                 2 * (buf.char(jout + 1, jchar) in charset) +
                                 4 * (buf.char(jout - 1, jchar) in charset) +
                                 8 * (buf.char(jout, jchar + 1) in charset))
                        if kchar:
                            chars[jchar] = charstr[kchar]
                buf.buffer[jout][LINE] = ''.join(chars)

    def redraw_arrowheads(buf):
        charstr = '^▷△^▽^^^◁^^^^^^^'
        #          0123456789ABCDEF
        charset = frozenset(charstr)
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if kind == PICT:
                chars = list(line)
                for jchar, char in enumerate(chars):
                    if char in charset:
                        kchar = (    (buf.char(jout, jchar - 1) == '─') +
                                 2 * (buf.char(jout + 1, jchar) == '│') +
                                 4 * (buf.char(jout - 1, jchar) == '│') +
                                 8 * (buf.char(jout, jchar + 1) == '─'))
                        if kchar:
                            chars[jchar] = charstr[kchar]
                buf.buffer[jout][LINE] = ''.join(chars)

    def graph_pictures(buf):
        'redraw pictures by -g'
        buf.redraw_segments()
        buf.redraw_arrowheads()

    def align_pictures(buf):
        'align pictures at left/center/right by -k and -b'

        def ka_kz(ka, kz, line):
            for k, char in enumerate(line):
                if char != ' ':
                    ka = min(ka, k)
                    kz = max(kz, k)
            return ka, kz

        def flush():
            room = var.chars_per_line - (kz - ka + 1)
            blanks = max(1, {'l': min(room, var.left_blanks), 'c': room // 2, 'r': room}[arg.align_pictures]) * ' '
            for j in range(ja, jz + 1):
                buf.buffer[j][LINE] = blanks + buf.buffer[j][LINE][ka:kz+1]

        picture = False # align_pictures
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if picture:
                if kind == PICT:
                    jz = jout
                    ka, kz = ka_kz(ka, kz, line)
                else:
                    flush()
                    picture = False
            else:
                if kind == PICT:
                    ja, jz, ka, kz = jout, jout, BIGINT, -BIGINT
                    ka, kz = ka_kz(ka, kz, line)
                    picture = True
        if picture:
            flush()

    def renumber_chapters(buf):
        levels = [var.chapter_offset]; max_level = 1; nout = len(buf.buffer)
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            prev_line = buf.buffer[jout-1][LINE] if jout > 0 else ''
            next_line = buf.buffer[jout+1][LINE] if jout + 1 < nout else ''
            if kind == TEXT and line and not prev_line and not next_line:
                words = split(line)
                level = chapter_level(words[0])
                title = shrink_alphaupper(line)
                if level > 0: # numbered chapter line
                    if level > max_level:
                        error(f'Numbered chapter level is {level} > {max_level}', jinp)
                    elif level == len(levels) + 1:
                        levels.append(1)
                    else:
                        levels = levels[:level]
                        levels[-1] += 1
                    title = shrink_alphaupper(' '.join(words[1:]))
                    buf.buffer[jout][KIND] = CHP1 if level == 1 else CHP2
                    buf.buffer[jout][LINE] = '.'.join(str(level) for level in levels) + '. ' + title
                    max_level = len(levels) + 1
                elif title == var.contents_title: # contents chapter line
                    buf.buffer[jout][KIND] = CONT
                    buf.buffer[jout][LINE] = title
                    max_level = 1
                elif title == var.figures_title: # figures chapter line
                    buf.buffer[jout][KIND] = FIGU
                    buf.buffer[jout][LINE] = title
                    max_level = 1
                elif title == var.index_title: # index chapter line
                    buf.buffer[jout][KIND] = INDX
                    buf.buffer[jout][LINE] = title
                    max_level = 1
                else: # no chapter line
                    title = ''

    def add_chapters_to_contents_chapter(buf):
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if kind == CONT:
                if buf.contents_found:
                    error(f'More than one contents line in text file', jinp)
                buf.contents_found = True
                # contents chapter doesn't list itself
            elif kind == FIGU:
                if buf.figures_found:
                    error(f'More than one figures line in text file', jinp)
                buf.figures_found = True
                buf.contents.append(['', shrink_alphatitle(var.figures_title), jout])
            elif kind == INDX:
                if buf.index_found:
                    error(f'More than one index line in text file', jinp)
                buf.index_found = True
                buf.contents.append(['', shrink_alphatitle(var.index_title), jout])
            elif kind in [CHP1, CHP2]:
                prefix, title = (line.split(None, 1) + [''])[:2]
                buf.contents.append([prefix, shrink_alphatitle(title), jout])

    def add_captions_to_figures_chapter(buf):
        seek = False
        chapter = ''
        letter = prevchar('a')
        for jout, record in enumerate(buf.buffer):
            jinp, kind, jpage, lpic, line = record
            if kind in [CONT, INDX, FIGU]:
                seek = True
            elif kind in [CHP1, CHP2]:
                seek = False
                chapter = split(line)[0]
                letter = prevchar('a')
            elif not seek and kind == PICT and (
                jout == 0 or buf.buffer[jout-1][KIND] == EMPT) and (
                jout == len(buf.buffer) - 1 or buf.buffer[jout+1][KIND] == EMPT):
                words = shrink_alphatitle(line).split()
                if len(words) >= 2:
                    prefix, label, *leftovers = words
                    title = ' '.join(leftovers)
                    if prefix.upper() == var.caption_prefix and figure_level(label.lower()) > 0:
                        if letter == 'z':
                            error(f'in text file, more than 26 figure captions in a single chapter', jinp)
                        letter = nextchar(letter)
                        label = f'{chapter}{letter}.'
                        caption = f'{prefix} {label} {title}'
                        blanks = (var.chars_per_line - len(caption)) // 2 * ' '
                        buf.figures.append((label, title, jout))
                        record[LINE] = blanks + caption
                        record[KIND] = CAPT
                        if jout >= 2 and buf.buffer[jout - 2][KIND] == PICT:
                            buf.buffer[jout - 1][KIND] = PICT # paste caption with previous picture

    def add_quoted_subjects_to_index_chapter(buf):
        buf.qsub_jouts = SetDict() # {subject: jout}
        quote = False; subject = ''; seek = True
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if kind in [CONT, FIGU, INDX]:
                seek = False
            elif kind in [CHP1, CHP2]:
                seek = True
            elif seek and kind == TEXT:
                for jchar, char in enumerate(line + ' '):
                    if quote:
                        if (char == '"' and get(line, jchar-1, ' ') not in QUOTES and get(line, jchar+1, ' ') not in QUOTES):
                            subject = shrink(subject)
                            buf.qsub_jouts.add(subject, jout)
                            buf.subjects.add(subject)
                            quote = False
                        else:
                            subject += char
                            if len(subject) > var.chars_per_line // 2:
                                error(f'Length of subject = {len(subject)} > -w / 2 = {var.chars_per_line // 2}', jinp)
                    elif (char == '"' and get(line, jchar-1, ' ') not in QUOTES and get(line, jchar+1, ' ') not in QUOTES):
                        subject = ''
                        quote = True
            else:
                if quote:
                    error(f'Unpaired \'"\' found while filling the index')
        if quote:
            error(f'Unpaired \'"\' found while filling the index')

    def add_unquoted_subjects_to_index_chapter(buf):
        buf.uqsub_jouts = SetDict() # {subject: jout}
        charset = set(chars('[a-zA-Z0-9]') + ''.join(buf.qsub_jouts.keys()))
        word_jouts = [] # [(word, jout)]
        seek = True
        for jout, (jinp, kind, jpage, lpic, line) in enumerate(buf.buffer):
            if kind in [CONT, FIGU, INDX]:
                seek = False
            elif kind in [CHP1, CHP2]:
                seek = True
            elif seek and kind == TEXT:
                for word in take(line, charset, ' ').split():
                    word_jouts.append((word, jout))
        sub0_subws = ListDict() # {subject.word[0]: subject.word[1:]}
        for subject in buf.qsub_jouts.keys():
            subjectwords = split(subject)
            sub0_subws.append(subjectwords[0], subjectwords[1:])
        for jword_jouts, (sub0, jout) in enumerate(word_jouts):
            if sub0 in sub0_subws:
                for subw in sub0_subws[sub0]:
                    subject = sub0 + ' ' + ' '.join(subw) if subw else sub0
                    if subject == ' '.join(w for w, j in word_jouts[jword_jouts: jword_jouts + len(subw) + 1]):
                        buf.uqsub_jouts.add(subject, jout)
                        buf.subjects.add(subject)

    def insert_contents_figures_and_index_chapters(buf):

        def append_contents_to(buffer2):
            jinp = buffer2[-1][JINP]
            buffer2.append([jinp, TEXT, 0, 0, ''])
            label_width = max((len(label) for label, title, jpage in buf.contents), default=0)
            for label, title, jpage in buf.contents:
                line = f'{INDENT}• {label.ljust(label_width)} {title}'
                if arg.page_headers == 'n' and len(line) > var.chars_per_line:
                    error(f'Length of Contents chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
                buffer2.append([jinp, TEXT, 0, 0, line])
            buffer2.append([jinp, TEXT, 0, 0, ''])

        def append_index_to(buffer2):
            jinp = buffer2[-1][JINP]
            buffer2.append([jinp, TEXT, 0, 0, ''])
            for subject in sorted(buf.subjects):
                line = f'{INDENT}• {subject}'
                if arg.page_headers == 'n' and len(line) > var.chars_per_line:
                    error(f'Length of Index chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
                buffer2.append([jinp, TEXT, 0, 0, line])
            buffer2.append([jinp, TEXT, 0, 0, ''])

        def append_figures_to(buffer2):
            jinp = buffer2[-1][JINP]
            buffer2.append([jinp, TEXT, 0, 0, ''])
            label_width = max((len(label) for label, title, jpage in buf.figures), default=0)
            for label, title, jpage in buf.figures:
                line = f'{INDENT}• {label.ljust(label_width)} {title}'
                if arg.page_headers == 'n' and len(line) > var.chars_per_line:
                    error(f'Length of Figures chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
                buffer2.append([jinp, TEXT, 0, 0, line])
            buffer2.append([jinp, TEXT, 0, 0, ''])

        buffer2 = [] # insert_contents_figures_and_index_chapters
        copy = True
        for record in buf.buffer:
            kind = record[KIND]
            if kind == CONT:
                buf.contents_jout = len(buffer2)
                buffer2.append(record)
                append_contents_to(buffer2)
                copy = False
            elif kind == FIGU:
                buf.figures_jout = len(buffer2)
                buffer2.append(record)
                append_figures_to(buffer2)
                copy = False
            elif kind == INDX:
                buf.index_jout = len(buffer2)
                buffer2.append(record)
                append_index_to(buffer2)
                copy = False
            elif kind in [CHP1, CHP2]:
                buffer2.append(record)
                copy = True
            elif copy:
                buffer2.append(record)
        buf.buffer = buffer2

    def check_line_lengths(buf):
        for jinp, kind, zero, lpic, line in buf.buffer:
            if len(strip(line)) - line.startswith(FORMFEED) > var.chars_per_line:
                error(f'Line length = {len(line)} > -w --chars-per-line = {var.chars_per_line} in text file', jinp)

    def count_picture_lines(buf):
        jpic = 0
        for jout, record in retroenum(buf.buffer):
            if record[KIND] in [PICT, CAPT]:
                jpic += 1
                if jout == 0 or buf.buffer[jout-1][KIND] not in [PICT, CAPT]:
                    buf.buffer[jout][LPIC] = jpic
            else:
                jpic = 0

    def count_pages(buf):
        jpage, jpagline = 1, 0
        for jout, (jinp, kind, zero, lpic, line) in enumerate(buf.buffer):
            if (arg.page_headers in 'fpcd' and jpagline >= var.lines_per_page - var.page_header_lines or
                arg.page_headers in 'pcd' and lpic < var.lines_per_page and jpagline + lpic + 1 >= var.lines_per_page or
                arg.page_headers in 'cd' and kind in [CONT, INDX, FIGU, CHP1] and not (
                    jout >= 2 and not buf.buffer[jout-1][LINE] and buf.buffer[jout-1][JPAG] > buf.buffer[jout-2][JPAG])):
                jpage += 1 + (arg.page_headers == 'd' and kind in [CONT, INDX, FIGU, CHP1] and jpage % 2 == 1)
                jpagline = 1
            else:
                jpagline += 1
            buf.buffer[jout][JPAG] = jpage
        var.num_pages = jpage
        try:
            roman = 0 if var.page_offset >= 0 else roman_width(min(var.num_pages, -var.page_offset))
        except ValueError:
            error("Max page Roman number 'mmmcmxcix' ≡ 3999 exceeded")
        arab = 0 if -var.page_offset >= var.num_pages else len(str(var.num_pages + var.page_offset))
        var.num_page_width = max(roman, arab)
 
    def add_page_numbers_to_contents_chapter(buf): 
        if buf.contents_jout > -1:
            left_width = 0
            for jcontents, (prefix, title, jout) in enumerate(buf.contents):
                left = buf.buffer[buf.contents_jout + 2 + jcontents][LINE]
                left_width = max(left_width, len(left))
                line = buf.buffer[buf.contents_jout + 2 + jcontents][LINE] + ' ' + page_number2str(buf.buffer[jout][JPAG], var.page_offset).rjust(var.num_page_width)
                if len(line) > var.chars_per_line:
                    error(f'Length of Contents chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
            for jcontents, (prefix, title, jout) in enumerate(buf.contents):
                line = buf.buffer[buf.contents_jout + 2 + jcontents][LINE].ljust(left_width) + ' ' + page_number2str(buf.buffer[jout][JPAG], var.page_offset).rjust(var.num_page_width)
                buf.buffer[buf.contents_jout + 2 + jcontents][LINE] = line

    def add_page_numbers_to_figures_chapter(buf):
        if buf.figures_jout > -1:
            left_width = 0
            for jfigures, (prefix, title, jout) in enumerate(buf.figures):
                left = buf.buffer[buf.figures_jout + 2 + jfigures][LINE]
                left_width = max(left_width, len(left))
                line = buf.buffer[buf.figures_jout + 2 + jfigures][LINE] + ' ' + page_number2str(buf.buffer[jout][JPAG], var.page_offset).rjust(var.num_page_width)
                if len(line) > var.chars_per_line:
                    error(f'Length of Figures chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
            for jfigures, (prefix, title, jout) in enumerate(buf.figures):
                line = buf.buffer[buf.figures_jout + 2 + jfigures][LINE].ljust(left_width) + ' ' + page_number2str(buf.buffer[jout][JPAG], var.page_offset).rjust(var.num_page_width)
                buf.buffer[buf.figures_jout + 2 + jfigures][LINE] = line

    def add_page_numbers_to_index_chapter(buf):
        if buf.index_jout > -1:
            qsub_jpags = SetDict() # {quoted_subject: {jpage}}
            for subject, jouts in buf.qsub_jouts.items():
                for jout in jouts:
                    qsub_jpags.add(subject, buf.buffer[jout][JPAG])
            uqsub_jpags = SetDict() # {unquoted_subject: {jpage}}
            for subject, jouts in buf.uqsub_jouts.items():
                for jout in jouts:
                    jpage = buf.buffer[jout][JPAG]
                    if jpage not in qsub_jpags[subject]:
                        uqsub_jpags.add(subject, jpage)
            left_width = max(len(subject) for subject in buf.subjects)
            for jindex, subject in enumerate(sorted(buf.subjects)):
                jpag_strjs = sorted((jpage, f'"{page_number2str(jpage, var.page_offset)}"'
                                     if jpage in qsub_jpags[subject] else page_number2str(jpage, var.page_offset))
                    for jpage in (qsub_jpags[subject] | uqsub_jpags[subject])) # [(jpage, str(jpage))]
                line = buf.buffer[buf.index_jout + 2 + jindex][LINE].ljust(left_width + 6) + ' ' + ', '.join(strj for jpage, strj in jpag_strjs)
                if len(line) > var.chars_per_line:
                    while True:
                        line = line[:line.rfind(',')]
                        if len(line) + 3 <= var.chars_per_line:
                            break
                    line += ', …'
                if len(line) > var.chars_per_line:
                    error(f'Length of Index chapter line is {len(line)} > -w = {var.chars_per_line}:\n{line}')
                buf.buffer[buf.index_jout + 2 + jindex][LINE] = line

    def insert_page_headers(buf):

        def header1(jinp, jpage, npages, chapter):
            left, right = ((arg.even_right, arg.even_left) if arg.all_pages_E_e else
                           (arg.odd_left, arg.odd_right) if jpage % 2 else
                           (arg.even_left, arg.even_right))
            iPpfeYmdHMSunNc = var.iPpfeYmdHMSu + (page_number2str(jpage, var.page_offset), str(npages), chapter)
            left = evalchar(left, 'iPpfeYmdHMSunNc', iPpfeYmdHMSunNc, '%')
            right = evalchar(right, 'iPpfeYmdHMSunNc', iPpfeYmdHMSunNc, '%')
            blanks = ' ' * max(1, (var.chars_per_line - len(left) - len(right)))
            header = (left + blanks + right).replace(' ', NBSPACE) 
            return [jinp, HEA1, jpage, lpic, FORMFEED + header]

        def header2(jinp, jpage, npages, chapter):
            second_line = var.chars_per_line * SECOND_LINE_CHARS[arg.second_line]
            return [jinp, HEA2, jpage, lpic, second_line]
            
        if buf.buffer: # insert page headers
            buffer2 = []; jpag0 = 1; chapter = ''; npages = buf.buffer[-1][JPAG]
            for jinp, kind, jpage, lpic, line in buf.buffer:
                if kind in [CONT, INDX, FIGU, CHP1]:
                        chapter = shrink_alphatitle(line)
                if jpage == jpag0 + 2:
                    buffer2.append(header1(jinp, jpage - 1, npages, chapter))
                    if arg.second_line != 'n':
                        buffer2.append(header2(jinp, jpage - 1, npages, chapter))
                if jpage > jpag0:
                    buffer2.append(header1(jinp, jpage, npages, chapter))
                    if arg.second_line != 'n':
                        buffer2.append(header2(jinp, jpage, npages, chapter))
                jpag0 = jpage
                buffer2.append([jinp, kind, jpage, lpic, line])
            buf.buffer = buffer2
            
#----- main window -----

def gui_main_window():
    var.gui_mode = True
    psg.theme(THEME)
    button = 'Main'
    block = lambda text='': psg.Text(text, size=8)
    blank = lambda size=10: psg.Text(size=size)
    layout = [
        [block('Format'),    psg.Text('-y --text-editor',     size=TSIZE), psg.Input(arg.text_editor, size=FSIZE,         key='y', tooltip=tooltip['y']), blank(),
                             psg.Text('-l --left-only-text',  size=TSIZE), psg.Checkbox('', default=arg.left_only_text,   key='l', tooltip=tooltip['l']), blank(26),
                             psg.Text(STATUS, key='Status', tooltip='status indicator\n(GREEN=waiting,\nRED=running)', text_color=WAITING)],
        [block(),            psg.Text('-w --chars-per-line',  size=TSIZE), psg.Input(arg.chars_per_line, size=NSIZE,      key='w', tooltip=tooltip['w']), blank(ASIZE),
                             psg.Text('-g --graph-pictures',  size=TSIZE), psg.Checkbox('', default=arg.graph_pictures,   key='g', tooltip=tooltip['g']), blank(2),
                             psg.Text('-b --left-blanks',     size=0),     psg.Input(arg.left_blanks, size=NSIZE,         key='b', tooltip=tooltip['b']),],
        [block(),            psg.Text('-u --lines-per-page',  size=TSIZE), psg.Input(arg.lines_per_page, size=NSIZE,      key='u', tooltip=tooltip['u']), blank(ASIZE),
                             psg.Text('-k --align-pictures',  size=TSIZE),
                                 psg.Radio('no',       'k', default=arg.align_pictures=='n', tooltip="don't align pictures"),
                                 psg.Radio('left',     'k', default=arg.align_pictures=='l', tooltip='align pictures at left\nleaving at left -b blanks'),
                                 psg.Radio('center',   'k', default=arg.align_pictures=='c', tooltip='center pictures'),
                                 psg.Radio('right',    'k', default=arg.align_pictures=='r', tooltip='align pictures at right')],
        [block('Chapters'),  psg.Text('-c --contents-title',  size=TSIZE), psg.Input(arg.contents_title, size=FSIZE,      key='c', tooltip=tooltip['c']), blank(),
                             psg.Text('-i --index-title',     size=TSIZE), psg.Input(arg.index_title, size=FSIZE,         key='i', tooltip=tooltip['i'])],
        [block(),            psg.Text('-f --figures-title',   size=TSIZE), psg.Input(arg.figures_title, size=FSIZE,       key='f', tooltip=tooltip['f']), blank(),
                             psg.Text('-F --caption-prefix',  size=TSIZE), psg.Input(arg.caption_prefix, size=FSIZE,      key='F', tooltip=tooltip['F'])],
        [block(),            psg.Text('-m --chapter-offset',  size=TSIZE), psg.Input(arg.chapter_offset, size=NSIZE,      key='m', tooltip=tooltip['m'])],
        [block('Pages'),     psg.Text('-p --page-headers',    size=TSIZE),
                                 psg.Radio('no',       'p', default=arg.page_headers=='n', tooltip="don't insert page headers"),
                                 psg.Radio('fullpage', 'p', default=arg.page_headers=='f', tooltip='insert page headers on full page'),
                                 psg.Radio('picture',  'p', default=arg.page_headers=='p', tooltip='…and on broken picture'),
                                 psg.Radio('chapter',  'p', default=arg.page_headers=='c', tooltip='…and before level-1 chapters'),
                                 psg.Radio('double',   'p', default=arg.page_headers=='d', tooltip='…and double if level-1 chapter is on even page'),],
        [block(),            psg.Text('-e --even-left',       size=TSIZE), psg.Input(arg.even_left, size=FSIZE,           key='e', tooltip=tooltip['e']), blank(),
                             psg.Text('-E --even-right',      size=TSIZE), psg.Input(arg.even_right, size=FSIZE,          key='E', tooltip=tooltip['E'])],
        [block(),            psg.Text('-o --odd-left',        size=TSIZE), psg.Input(arg.odd_left, size=FSIZE,            key='o', tooltip=tooltip['o']), blank(),
                             psg.Text('-O --odd-right',       size=TSIZE), psg.Input(arg.odd_right, size=FSIZE,           key='O', tooltip=tooltip['O'])],
        [block(),            psg.Text('-n --page-offset',     size=TSIZE), psg.Input(arg.page_offset, size=NSIZE,         key='n', tooltip=tooltip['n']), blank(ASIZE),
                             psg.Text('-a --all-pages-E-e',   size=TSIZE), psg.Checkbox('', default=arg.all_pages_E_e,    key='a', tooltip=tooltip['a'])],
        [block(),            psg.Text('-s --second_line',     size=TSIZE),
                                 psg.Radio('no',       's', default=arg.second_line=='n', tooltip='no second line in page header'),       
                                 psg.Radio('blanks',   's', default=arg.second_line=='b', tooltip='blank second line in page header'),   
                                 psg.Radio('points',   's', default=arg.second_line=='p', tooltip='dotted second line in page header'),
                                 psg.Radio('dashes',   's', default=arg.second_line=='d', tooltip='dashed second line in page header'),
                                 psg.Radio('solid',    's', default=arg.second_line=='s', tooltip='solid second line in page header')],
        [block('Export'),    psg.Text('-X --export-pdf',      size=TSIZE),
                                 psg.Radio('no',       'X', default=arg.export_pdf=='n', tooltip="don't export"),
                                 psg.Radio('export',   'X', default=arg.export_pdf=='e', tooltip='export PDF file'),
                                 psg.Radio('browse',   'X', default=arg.export_pdf=='b', tooltip='export and browse PDF file'),                           blank(17),
                             psg.Text('-C --correct', size=TSIZE),
                                 psg.Radio('no',       'C', default=arg.correct=='n', tooltip='do not correct char size and page margins'),
                                 psg.Radio('default',  'C', default=arg.correct=='d', tooltip='correct char size and page margins by default values'),
                                 psg.Radio('file',     'C', default=arg.correct=='f', tooltip='correct char size and page margins by correction file')],   
        [block(),            psg.Text('-Y --pdf-browser',     size=TSIZE), psg.Input(arg.pdf_browser, size=FSIZE,         key='Y', tooltip=tooltip['Y']), blank(),
                             psg.Text('-P --pdf-file',        size=TSIZE), psg.Input(arg.pdf_file, size=FSIZE,            key='P', tooltip=tooltip['P'])],
        [block(),            psg.Text('-W --char-width',      size=TSIZE), psg.Input(arg.char_width, size=NSIZE,          key='W', tooltip=tooltip['W']), blank(ASIZE),
                             psg.Text('-A --char-aspect',     size=TSIZE), psg.Input(arg.char_aspect, size=NSIZE,         key='A', tooltip=tooltip['A'])],
        [block(),            psg.Text('-S --sheet-size',      size=TSIZE), psg.Input(arg.sheet_size, size=FSIZE,          key='S', tooltip=tooltip['S']), blank(),
                             psg.Text('-Z --landscape',       size=TSIZE), psg.Checkbox('', default=arg.landscape,        key='Z', tooltip=tooltip['Z'])],
        [block(),            psg.Text('-L --left-margin',     size=TSIZE), psg.Input(arg.left_margin, size=NSIZE,         key='L', tooltip=tooltip['L']), blank(ASIZE),
                             psg.Text('-R --right-margin',    size=TSIZE), psg.Input(arg.right_margin, size=NSIZE,        key='R', tooltip=tooltip['R'])],
        [block(),            psg.Text('-T --top-margin',      size=TSIZE), psg.Input(arg.top_margin, size=NSIZE,          key='T', tooltip=tooltip['T']), blank(ASIZE),
                             psg.Text('-B --bottom-margin',   size=TSIZE), psg.Input(arg.bottom_margin, size=NSIZE,       key='B', tooltip=tooltip['B'])],
        [block(),            psg.Text('-I --multi-pages',     size=TSIZE),
                                 psg.Radio('1',        'I', default=arg.multi_pages=='1', tooltip=f"export 1 page per sheet side"),
                                 psg.Radio('2',        'I', default=arg.multi_pages=='2', tooltip=f"export 2 pages per sheet side"),
                                 psg.Radio('4',        'I', default=arg.multi_pages=='4', tooltip=f"export 4 pages per sheet side"),
                                 psg.Radio('8',        'I', default=arg.multi_pages=='8', tooltip=f"export 8 pages per sheet side"),                      blank(21),
                             psg.Text('-J --multi-sheets',    size=TSIZE), psg.Input(arg.multi_sheets, size=NSIZE,        key='J', tooltip=tooltip['J'])],
        [block('Text File'), psg.Text(arg.text_file, key='t', tooltip=tooltip['t'])],
        [psg.Button(button, tooltip=tooltip[button]) for button in [
            'New','Open','Recent','Copy','Move','Delete','Edit','Format','Noform','Undo','Log','Help','Exit']]]
    window = psg.Window(f'YAWP - Main', layout, finalize=True)
    cd(dirname(arg.text_file)) # added in 2.2.0
    while True: 
        try:
            window['Status'].update(STATUS, text_color=WAITING)
            window.refresh()
            button, values = window.read()
            arg.read_from_window(window)
            arg.shrink_all()
            button = button or 'Exit'
            if button != 'Exit':
                window['Status'].update(STATUS, text_color=RUNNING)
                arg.write_into_window(window)
            var.ok_message = ''
            {'New':    new_button,
             'Open':   open_button,
             'Recent': recent_button,
             'Copy':   copy_button,
             'Move':   move_button,
             'Delete': delete_button,
             'Edit':   edit_button,
             'Format': format_button,
             'Noform': noform_button,
             'Undo':   undo_button,
             'Log':    log_button,
             'Help':   help_button,
             'Exit':   exit_button}[button]()
            window.refresh() # added in 2.2.0 
            cd(dirname(arg.text_file)) # added in 2.2.0
            arg.write_into_window(window)
            hist.add(arg.text_file)
            cd(dirname(arg.text_file))
        except YawpError:
            pass

#----- buttons for text file definition: New Open Recent Copy Move Delete -----

def new_button():
    'create a new empty text file with default arguments, which becomes the new current text file'
    old_text_file = arg.text_file
    new_text_file = psg.popup_get_file('', no_window=True, save_as=True)
    # if new file aready exists, confirmation window is issued by psg.popup_() itself
    if not new_text_file:
        return
    new_text_file = longpath(new_text_file)
    check_file(new_text_file, must_exist=False)
    if arg.text_file == new_text_file:
        error(f'The new text file can not be the current text file')
    arg.write_into_args_file_of(old_text_file)
    lock.seize(new_text_file)
    write_file(new_text_file) 
    rm(args_file_of(new_text_file)) 
    arg.set_default()
    rm(log_file_of(new_text_file))
    for back_file in back_files_of(new_text_file): rm(back_file)
    lock.release(old_text_file)
    arg.text_file = new_text_file

def open_button():
    'browse the file system and select the new current text file'
    old_text_file = arg.text_file
    new_text_file = psg.PopupGetFile('', no_window=True, save_as=False)
    # if new_text_file doesn't exist, error window is issued by psg.PopupGetFile() itself
    if not new_text_file:
        return
    new_text_file = longpath(new_text_file)
    check_file(new_text_file, must_exist=True)
    if arg.text_file == new_text_file:
        error(f'The selected text file can not be the current text file')
    arg.write_into_args_file_of(old_text_file)
    lock.seize(new_text_file)
    arg.read_from_args_file_of(new_text_file)
    lock.release(old_text_file)
    arg.text_file = new_text_file

def recent_button():
    'browse the list of recent existing files and select the new current text file'
    old_text_file = arg.text_file
    new_text_file = hist.select()
    # if list of recent files is empty, error window is issued by hist.select() itself
    if not new_text_file:
        return
    new_text_file = longpath(new_text_file)
    check_file(new_text_file, must_exist=True)
    if arg.text_file == new_text_file:
        error(f'The selected text file can not be the current text file')
    arg.write_into_args_file_of(old_text_file)
    lock.seize(new_text_file)
    arg.read_from_args_file_of(new_text_file)
    lock.release(old_text_file)
    arg.text_file = new_text_file
        
def copy_button():
    'copy current text file (and its args file) into a copy, which becomes the new current text file'
    infos = [frame(f'Copy - {now()}')]
    check_file(arg.text_file, must_exist=True)
    lock.seize(arg.text_file)
    old_text_file = arg.text_file
    if var.gui_mode:
        new_text_file = psg.popup_get_file('', no_window=True, save_as=True)
        # if target file aready exists, confirmation window is issued by psg.popup_get_file() itself
        if not new_text_file:
            return
    else:
        new_text_file = arg.target_file
    new_text_file = longpath(new_text_file)
    check_file(new_text_file, must_exist=False)
    if arg.text_file == new_text_file:
        error(f'The target text file can not be the current text file')
    arg.write_into_args_file_of(old_text_file)
    lock.seize(new_text_file)
    infos.append(cp(old_text_file, new_text_file))
    infos.append(cp(args_file_of(old_text_file), args_file_of(new_text_file)))
    infos.append(rm(log_file_of(new_text_file)))
    for back_file in back_files_of(new_text_file):
        infos.append(rm(back_file))
    info = '\n'.join(line for line in infos if line)
    inform(info, old_text_file)
    inform(info, new_text_file, verbose=False)
    lock.release(old_text_file)
    arg.text_file = new_text_file

def move_button():
    'move the current text file with all its associated files'
    infos = [frame(f'Move - {now()}')]
    check_file(arg.text_file, must_exist=True)
    lock.seize(arg.text_file)
    old_text_file = arg.text_file
    if var.gui_mode:
        new_text_file = psg.popup_get_file('', no_window=True, save_as=True)
        # if target file aready exists, confirmation window is issued by psg.PopupGetFile() itself
        if not new_text_file:
            return
    else:
        new_text_file = arg.target_file
    new_text_file = longpath(new_text_file)
    check_file(new_text_file, must_exist=False)
    if arg.text_file == new_text_file:
        error(f'The target text file can not be the current text file')
    arg.write_into_args_file_of(old_text_file)
    lock.seize(new_text_file)
    infos.append(mv(old_text_file, new_text_file)) 
    infos.append(mv(args_file_of(old_text_file), args_file_of(new_text_file)))
    infos.append(mv(log_file_of(old_text_file), log_file_of(new_text_file)))
    new_path, new_name = splitpath(new_text_file)
    for old_back_file in back_files_of(old_text_file):
        new_back_file =  f'{new_path}/.yawp.{new_name}{old_back_file[-25:]}'
        infos.append(mv(old_back_file, new_back_file))
    info = '\n'.join(line for line in infos if line)
    inform(info, new_text_file)
    lock.release(old_text_file)
    arg.text_file = new_text_file
        
def delete_button():
    'permanently delete the text file with all its associated files'
    inform(frame(f'Delete - {now()}'))
    check_file(arg.text_file)
    if arg.usage_mode == 'd' or ask_yes('YAWP - Delete',
        f'File {arg.text_file!r}\nwill be permanently deleted with all its associated files.\nDo you want to delete it?', 'delete'):
        if isfile(arg.text_file):
            lock.seize(arg.text_file)
        arg.check()
        arg.inform()
        lines = ['Deleted:']
        for file in [arg.text_file, args_file_of(arg.text_file), lock_file_of(arg.text_file), log_file_of(arg.text_file)] + back_files_of(arg.text_file):
            message = rm(file)
            if message:
                lines.append(INDENT + message)
        arg.text_file = ''
        if len(lines) == 1:
            error(f'Files to delete not found')
        inform('\n'.join(lines))

#----- buttons for text file processing: Edit Format Noform Undo Log -----

def edit_button():
    'edit current text file, if not found: create as a new empty text file with default arguments'
    check_file(arg.text_file, must_exist=False)
    lock.seize(arg.text_file)
    if not isfile(arg.text_file):
        if arg.usage_mode == 'e' or ask_yes(
                f'YAWP - Edit', f'File {arg.text_file!r} does not exist.\nDo you want to create it as an empty file?', 'create'):
            write_file(arg.text_file) 
            inform(rm(args_file_of(arg.text_file))) 
            inform(rm(log_file_of(arg.text_file)))
            for back_file in back_files_of(arg.text_file):
                inform(rm(back_file))
        else:
            return
    inform(frame(f'Edit - {now()}'))
    arg.check()
    arg.inform()
    old = Buffer(arg.text_file)
    old.inform('Before:')
    shell(f'{arg.text_editor} {arg.text_file!r}')
    new = Buffer(arg.text_file)
    if old == new:
        inform('Backup:\n    Text file not altered, backup not performed')
    else:
        back_file = new_back_file_of(arg.text_file)
        old.write_into_file(back_file)
        inform(f'Backup:\n    {arg.text_file!r} →\n    {back_file!r}')
        new.inform('After:')

def format_button(format=True):
    'format current text file and redraw and align pictures and export and browse PDF format'
    button = "Format" if format else "Noform"
    inform(frame(f'{button} - {now()}'))
    check_file(arg.text_file, must_exist=True)
    lock.seize(arg.text_file)
    if not format and not arg.graph_pictures and arg.align_pictures == 'n' and arg.export_pdf == 'n':
        error(f"With -g off and -k = 'n' and -X = 'n', Noform doesn't do anything") 
    if is_reserved(arg.text_file):
        error(f'{button} on reserved file is not allowed')
    arg.check()
    arg.inform()
    old = Buffer(arg.text_file)
    inform(f'Read:\n    YAWP ← {arg.text_file!r}')
    old.inform('Before:')
    old.compute()
    new = old.copy()
    if format: # -M f?
        new.remove_page_headers()
        new.justify_lines()
        new.renumber_chapters()
        new.add_chapters_to_contents_chapter()
        new.add_captions_to_figures_chapter()
        new.add_quoted_subjects_to_index_chapter()
        new.add_unquoted_subjects_to_index_chapter()
        new.insert_contents_figures_and_index_chapters()
        if arg.page_headers != 'n': # -p ?
            new.count_picture_lines()
            new.count_pages()
            new.add_page_numbers_to_contents_chapter()
            new.add_page_numbers_to_figures_chapter()
            new.add_page_numbers_to_index_chapter()
            new.insert_page_headers()
        new.check_line_lengths()
    if arg.graph_pictures: # -g ?
        new.graph_pictures()
    if arg.align_pictures != 'n': # -k ?
        new.align_pictures()    
    if old == new:
        inform(f'Backup:\n    text file not altered, backup not performed')
    else:
        back_file = new_back_file_of(arg.text_file)
        old.write_into_file(back_file)
        inform(f'Backup:\n    {arg.text_file!r} →\n    {back_file!r}\n' +
               f'Rewrite:\n    YAWP → {arg.text_file!r}')
        new.write_into_file(arg.text_file)
        new.inform('After:')
    if arg.export_pdf != 'n': # -p ?
        pdf.export_and_browse(arg.text_file)

def noform_button():
    "don't format current text file but redraw and align pictures and export and browse PDF format"
    format_button(format=False)

def undo_button():
    'restore current text file to its previous version'
    inform(frame(f'Undo - {now()}'))
    check_file(arg.text_file, must_exist=False)
    lock.seize(arg.text_file)
    arg.check()
    arg.inform()
    back_file = last_back_file_of(arg.text_file)
    if not back_file:
        error(f'Backup file for text file {arg.text_file!r} not found')
    check_file(back_file)
    if arg.usage_mode == 'u' or not isfile(arg.text_file) or ask_yes('YAWP - Undo',
            f'File {arg.text_file!r} exists,\ncurrent content will be lost. Do you want to restore previous content?','restore'):
        old = Buffer(arg.text_file)
        old.inform('Before:')
        rm(arg.text_file)
        mv(back_file, arg.text_file)
        inform(f'Restore:\n    {back_file!r} →\n    {arg.text_file!r}')
        new = Buffer(arg.text_file)
        if old == new:
            inform('Undo:\n    Text file not altered')
        else:
            inform('Undo:\n    Text file altered')
            new.inform('After:')
        if arg.export_pdf != 'n':
            new.compute()
            pdf.export_and_browse(arg.text_file)

def log_button():
    'browse current log file'

    def log_inform(label, log_file):
        l, w, c, m, a = 0, 0, 0, 0, 0
        log = tryfunc(lambda: open(log_file).read()) or ''
        if log:
            for line in log.split('\n'):
                line = line.rstrip() 
                l += 1
                w += len(line.split())
                c += len(line)
                m = max(m, len(line))
                a += line.startswith(FRAME1ST)
        inform(f'{label}:\n    {many(l,"line")}, {many(w,"word")}, {many(c,"char")}, max {many(m,"char")} per line, {many(a,"action")}')
        
    inform(frame(f'Log - {now()}'))
    check_file(arg.text_file, must_exist=True)
    lock.seize(arg.text_file)
    arg.check()
    if arg.text_editor != arg.name_default['text_editor']:
        inform(f'Non-default argument:\n    text_editor = {arg.text_editor!r}')
    log_file = log_file_of(arg.text_file)
    if not isfile(log_file):
        write_file(log_file)
    log_inform('Before', log_file)
    shell(f'{arg.text_editor} {log_file!r}')
    log_inform('After', log_file)

#----- buttons for other actions: Help, Exit

def help_button():
    'show colophon and possibly browse the YAWP User Manual'
    if ask_yes('YAWP - Help', f'''
                          YAWP {VERSION}
              Yet Another Word Processor
                           {VERSION_DATE}
              https://pypi.org/project/yawp
                  Carlo Alessandro Verre
          carlo.alessandro.verre@gmail.com

Do you want to browse the YAWP User Manual?''', 'browse'):
        arg.check_pdf_browser()
        shell(f'{arg.pdf_browser} {MANUAL_FILE!r}')

def exit_button(return_code=0):
    'quit YAWP'
    if var.gui_mode:
        arg.write_into_args_file_of(arg.text_file)
        write_sess_file(arg.text_file)
    lock.release_all()
    exit(return_code)

#----- main -----

def main():
    var.gui_mode = False
    simplefilter('ignore')
    if not isfile(CORR_FILE):
        open(CORR_FILE, 'w').write(CORR_DEFAULT)
    arg.read_from_argv(argv)
    {'g': gui_main_window,
     'c': copy_button,
     'm': move_button,
     'd': delete_button,
     'e': edit_button,
     'f': format_button,
     'n': noform_button,
     'u': undo_button}[arg.usage_mode]()
    exit_button()

if __name__ == '__main__':
    main()

#----- end -----
