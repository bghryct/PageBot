# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Type Network, www.typenetwork.com, www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#     Made for usage in Drawbot, www.drawbot.com
# -----------------------------------------------------------------------------
#
#     thesisBot.py
#
#     This script generates an automatic Thesis composition.
#
import pagebot
reload(pagebot)
from pagebot import getFormattedString, findMarkers, textBoxBaseLines

import pagebot.style
reload(pagebot.style)
from pagebot.style import getRootStyle, LEFT_ALIGN

import pagebot.document 
reload(pagebot.document)
from pagebot.document import Document

import pagebot.page
reload(pagebot.page)
from pagebot.page import Page, Template

import pagebot.composer
reload(pagebot.composer)
from pagebot.composer import Composer

import pagebot.typesetter
reload(pagebot.typesetter)
from pagebot.typesetter import Typesetter

import pagebot.elements
reload(pagebot.elements)
from pagebot.elements import Galley

import pagebot.fonttoolbox.variationbuilder
reload(pagebot.fonttoolbox.variationbuilder)
from pagebot.fonttoolbox.variationbuilder import generateInstance

DEBUG = True

SHOW_GRID = DEBUG
SHOW_GRID_COLUMNS = DEBUG
SHOW_BASELINE_GRID = DEBUG
SHOW_FLOW_CONNECTIONS = DEBUG

if SHOW_GRID:
    BOX_COLOR = (0.8, 0.8, 0.8, 0.4)
else:
    BOX_COLOR = None
    
# Get the default root style and overwrite values for this document.
U = 7
baselineGrid = 2*U
listIndent = 1.5*U

RS = getRootStyle(
    u = U, # Page base unit
    # Basic layout measures altering the default rooT STYLE.
    w = 595, # Om root level the "w" is the page width 210mm, international generic fit.
    h = 11 * 72, # Page height 11", international generic fit.
    ml = 12*U, # Margin leftrs.mt = 7*U # Margin top
    baselineGrid = 14,#baselineGrid,
    g = U, # Generic gutter.
    # Column width. Uneven means possible split in 5+1+5 or even 2+1+2 +1+ 2+1+2
    # Uneven a the best in that respect for column calculation,
    # as it is possible to make micro columsn with the same gutter.
    cw = 9*U, 
    ch = 6*baselineGrid - U, # Approx. square and fitting with baseline.
    listIndent = listIndent, # Indent for bullet lists
    listTabs = [(listIndent, LEFT_ALIGN)], # Match bullet+tab with left indent.
    # Display option during design and testing
    showGrid = SHOW_GRID,
    showGridColumns = SHOW_GRID_COLUMNS,
    showBaselineGrid = SHOW_BASELINE_GRID,
    showFlowConnections = SHOW_FLOW_CONNECTIONS,
    BOX_COLOR = BOX_COLOR,
    # Text measures
    leading = 14,
    rLeading = 0,
    fontSize = 9
)
FS = getFormattedString(FormattedString(''), RS)
# LANGUAGE-SWITCH Language settings
RS['language'] = 'en'
MD_PATH = 'thesis.md'
EXPORT_PATH = 'export/Thesis.pdf'

MAIN_FLOW = 'main' # ELement id of the text box on pages the hold the main text flow.

# Tracking presets
H1_TRACK = H2_TRACK = 0.015 # 1/1000 of fontSize, multiplier factor.
H3_TRACK = 0.030 # Tracking as relative factor to font size.
P_TRACK = 0.030

VARS = True

if VARS:
    FONT_PATH = '../../fonts/'

    FONT_LOCATIONS = {
        #'PromisePageBot-BoldCondensed': {"wght": 750, "wdth": 500, },
        #'PromisePageBot-LightCondensed': {"wght": 0, "wdth": 500},
        'PromisePageBot-Light': {"wght": 0, "wdth": 1000},
        'PromisePageBot-Book': {"wght": 200, "wdth": 1000},
        'PromisePageBot-Regular': {"wght": 300, "wdth": 1000},    
        'PromisePageBot-Medium': {"wght": 400, "wdth": 1000},    
        'PromisePageBot-Semibold': {"wght": 500, "wdth": 1000},    
        'PromisePageBot-SemiboldCondensed': {"wght": 500, "wdth": 100},    
        'PromisePageBot-Bold': {"wght": 700, "wdth": 1000},
        'PromisePageBot-UltraBlack': {"wght": 1000, "wdth": 1000},
    }
    FONTS = {}
    VFONT_PATH = 'PromisePageBot-GX.ttf'
    # Install the test V-font
    if not 'PromisePageBot-Bold' in installedFonts():
        installFont(FONT_PATH + VFONT_PATH)
    for name, location in FONT_LOCATIONS.items():
        fontName, fontPath = generateInstance(FONT_PATH + VFONT_PATH, 
            location, targetDirectory=FONT_PATH + 'instances')
        FONTS[name] = fontName#fontPath # Instead of fontName, no need to uninstall.
    LIGHT = FONTS['PromisePageBot-Light']
    BOOK = FONTS['PromisePageBot-Book']
    BOOK_ITALIC = FONTS['PromisePageBot-Book']
    MEDIUM = FONTS['PromisePageBot-Medium']
    SEMIBOLD = FONTS['PromisePageBot-Semibold']
    SEMIBOLD_CONDENSED = FONTS['PromisePageBot-SemiboldCondensed'] 
    BOLD = FONTS['PromisePageBot-Bold']
    BLACK = FONTS['PromisePageBot-UltraBlack']
else:
    BOOK = MEDIUM = 'Georgia'
    BOOK_ITALIC = 'Georgia-Italic'
    BOLD = SEMIBOLD = 'Georgia-Bold'

RS['font'] = BOOK

# -----------------------------------------------------------------         
def makeDocument(rs):
    u"""Demo page composer."""

    # Set some values of the default template (as already generated by the document).
    # Make squential unique names for the flow boxes inside the templates
    flowId1 = MAIN_FLOW+'1' 
    flowIds = [flowId1] # Names of boxes that contain footnote text in flow.
    footnotesId = 'footnotes' # Id of target textBox containing footnotes per page. 
    tocId = 'toc' # Id of target textBox, containing the table of content.
    # Template 1
    template1 = Template(rs) # Create template of main size. Front page only.
    # Show grid columns and margins if rootStyle.showGrid or rootStyle.showGridColumns are True
    template1.grid(rs) 
    # Show baseline grid if rs.showBaselineGrid is True
    template1.baselineGrid(rs)
    # Create empty image place holders. To be filled by running content on the page.
    #template1.cContainer(4, 0, 2, 4, rs)  # Empty image element, cx, cy, cw, ch
    #template1.cContainer(0, 5, 2, 3, rs)
    # Create linked text boxes. Note the "nextPage" to keep on the same page or to next.
    template1.cTextBox(FS, 2, 0, 3, 8, rs, flowId1, nextBox=flowId1, nextPage=1, fill=BOX_COLOR)
    template1.cTextBox('', 0, 0, 2, 6, rs, tocId, fill=BOX_COLOR) # For now, keep on the first page.
    template1.cTextBox('', 0, 6, 2, 2, rs, footnotesId, fill=BOX_COLOR)
    # Create page number box. Pattern pageNumberMarker is replaced by actual page number.
    template1.cText(FS+rs['pageIdMarker'], 6, 0, rs, font=BOOK, fontSize=12, fill=BOX_COLOR)
   
    # Create new document with (w,h) and fixed amount of pages.
    # Make number of pages with default document size.
    # Initially make all pages default with template2
    doc = Document(rs, pages=3, template=template1) 
 
    # Cache some values from the root style that we need multiple time to create the tag styles.
    fontSize = rs['fontSize']
    leading = rs['leading']
    rLeading = rs['rLeading']
    listIndent = rs['listIndent']
    language = rs['language']

    # Add styles for whole document and text flows.  
    # Note that some values are defined here for clarity, even if their default root values
    # are the same.             
    doc.newStyle(name='chapter', font=BOOK)    
    doc.newStyle(name='title', fontSize=3*fontSize, font=BOLD)
    doc.newStyle(name='subtitle', fontSize=2.6*fontSize, font=BOOK_ITALIC)
    doc.newStyle(name='author', fontSize=2*fontSize, font=BOOK, fill=(1, 0, 0))
    doc.newStyle(name='h1', fontSize=4*fontSize, font=BLACK, fill=(1, 0, 0), 
        leading=4*fontSize, tracking=H1_TRACK, postfix='\n')
    doc.newStyle(name='h2', fontSize=1.5*fontSize, font=SEMIBOLD_CONDENSED, 
        fill=0, leading=1*leading, rLeading=0, tracking=H2_TRACK, 
        prefix='', postfix='')
    doc.newStyle(name='h3', fontSize=1.1*fontSize, font=MEDIUM, fill=0, 
        leading=leading, rLeading=0, rNeedsBelow=2*rLeading, tracking=H3_TRACK,
        prefix='\n', postfix='\n')
    doc.newStyle(name='h4', fontSize=1.1*fontSize, font=BOOK, fill=0, 
        leading=leading, rLeading=0, rNeedsBelow=2*rLeading, tracking=H3_TRACK,
        paragraphTopSpacing=U, paragraphBottomSpacing=U, prefix='\n', postfix='\n')
    
    # Spaced paragraphs.
    doc.newStyle(name='p', fontSize=fontSize, font=BOOK, fill=0.1, prefix='', postfix='\n',
        rTracking=P_TRACK, leading=14, rLeading=0, align=LEFT_ALIGN, hyphenation=True)
    doc.newStyle(name='b', font=SEMIBOLD)
    doc.newStyle(name='em', font=BOOK_ITALIC)
    doc.newStyle(name='hr', stroke=(1, 0, 0), strokeWidth=4)
    doc.newStyle(name='br', postfix='\n') # Simplest way to make <br/> show newline
    doc.newStyle(name='a', prefix='', postfix='')
    doc.newStyle(name='img', leading=leading, fontSize=fontSize, font=BOOK,
        stroke=1, fill=None)
    
    # Footnote reference index.
    doc.newStyle(name='sup', font=MEDIUM, rBaselineShift=0.6, prefix='', postfix=' ',
        fontSize=1.6*fontSize)
    doc.newStyle(name='li', fontSize=fontSize, font=BOOK, 
        tracking=P_TRACK, leading=leading, hyphenation=True, 
        # Lists need to copy the listIndex over to the regalar style value.
        tabs=[(listIndent, LEFT_ALIGN)], indent=listIndent, 
        firstLineIndent=1, postfix='\n')
    doc.newStyle(name='ul', prefix='', postfix='')
    doc.newStyle(name='literatureref', fill=0.5, rBaselineShift=0.2, fontSize=0.8*fontSize)
    doc.newStyle(name='footnote', fill=0, fontSize=0.9*fontSize, font=BOOK,
        tracking=P_TRACK,
        tabs=[(listIndent, LEFT_ALIGN)], indent=listIndent, 
        firstLineIndent=1, postfix='\n')
    doc.newStyle(name='caption', tracking=P_TRACK, language=language, fill=0.2, 
        leading=leading*0.8, fontSize=0.8*fontSize, font=BOOK_ITALIC, 
        indent=U/2, tailIndent=-U/2, hyphenation=True)
    
    # Change template of page 1
    page1 = doc[1]
    page1.setTemplate(template1)
    
    # Create main Galley for this page, for pasting the sequence of elements.    
    g = Galley() 
    t = Typesetter(doc, g)
    t.typesetFile(MD_PATH)
    
    if 0: # Preview the galley. Needs something generic to proof any volume of galley.
        gw, gh = g.getSize()
        previewPage = doc[2]
        previewPage.w = gw + 60
        previewPage.h = gh + 40
        previewPage.place(g, 40, 20)

    # Fill the main flow of text boxes with the ML-->XHTML formatted text. 
    c = Composer(doc)
    c.compose(g, page1, flowId1)
    
    # Now all text is composed on pages, scan for the pages that contain footnotes.
    # TODO: This will be implemented a function of composer in a later version.
    # Get the tocBox as located on the first page.
    tocBox, (_, _) = page1[tocId]
    for pageId, page in sorted(doc.pages.items()):
        # Get page box for footnotes
        fnBox, (_, _) = page[footnotesId]
        assert fnBox is not None # Otherwise there is a template error. Footnote box needs to exist.
        for flowId in flowIds:
            # BUG: Need to check if the marker was really found in the textbox area. 
            # If it is part of the overflow, then it should not be found here.
            for marker, arguments in findMarkers(page[flowId][0].fs):
                if marker == 'footnote': 
                    # Process the foot note.
                    footnoteId = int(arguments) # Footnode ids are numbers. 
                    # Process the footnote id and content, usng the “footnote“ content style.
                    # We are re-using the typesetter here. This may become a separate typesetter, if this code
                    # becomes a method of the composer.
                    # TODO: Make this into Galley, in case footnote <p> has child nodes. 
                    footnoteText = getFormattedString('%d\t%s\n' % (footnoteId, doc.footnotes[footnoteId]['p'].text),
                        style=t.getCascadedStyle(doc.getStyle('footnote')))
                    # Add the footnote content to the box (it may not be the first to be added.
                    fnBox.append(footnoteText)
                elif marker in ('h1', 'h2', 'h3', 'h4'): # For now we want them all
                    #doc.addToc(marker, page)
                    pass
                    
    return doc
        
d = makeDocument(RS)
d.export(EXPORT_PATH) 

