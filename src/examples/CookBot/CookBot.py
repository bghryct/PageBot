import os
import weakref
import fontTools
import copy
import xml.etree.ElementTree as ET

import document
reload(document)
from document import Document, Page, Composer, Template, Galley


# Basic layout measures 
U = 7
PW = 595 # Page width 210mm, international generic fit.
PH = 11 * 72 # Page height 11", international generic fit.
ML = 7*U # Margin left
MT = 7*U # Margin top
BASELINE_GRID = 2*U
CW = 11*U # Column width. 
G = U # Generic gutter.
CH = 6*BASELINE_GRID - G # Approx. square. Fit with baseline.
Utab = U*0.8 # Indent for bullet lists
# Display option
SHOW_GRID = False
SHOW_BASELINEGRID = False
# Text measures
LEADING = BASELINE_GRID
BODYTEXT_SIZE = 10
# Tracking presets
H1_TRACK = H2_TRACK = 0.015
H3_TRACK = 0.030 # Tracking as relative factor to font size.
P_TRACK = 0.030
# Language settings
LANGUAGE = 'nl-be'
MAIN_FLOW = 'main' # ELement id of the text box on pages the hold the main text flow.
FILENAME = 'automaticLayout_nl.md' # 'automaticLayout_nl.md'
PAGE_ID_MARKER = '#?#' # Placeholder pattern to be substituted by page.eId
NO_COLOR= -1
BOX_COLOR = NO_COLOR #0.9 # Debug color for textbox columns.
MISSING_ELEMENT_FILL = 0.5
JUSTIFIED = 'justified'
LEFT = 'left'

if 1:
    BOOK = 'Productus-Book'
    BOOK_ITALIC = 'Productus-BookItalic'
    BOLD = 'Productus-Bold'
    SEMIBOLD = 'Productus-Semibold'
    MEDIUM = 'Productus-Medium'
else:
    BOOK = MEDIUM = 'Georgia'
    BOOK_ITALIC = 'Georgia-Italic'
    BOLD = SEMIBOLD = 'Georgia-Bold'
# -----------------------------------------------------------------         
def makeDocument():
    u"""Demo page composer."""

    # Set some values of the default template (as already generated by the document).
    # Make squential unique names for the flow boxes inside the templates
    flowId0 = MAIN_FLOW+'0' 
    flowId1 = MAIN_FLOW+'1'
    flowId2 = MAIN_FLOW+'2'
    
    # Template 1
    template1 = Template(PW, PH) # Create template of main size. Front page only.
    if SHOW_GRID: # Enable to show grid columns and margins.
        template1.grid() 
    if SHOW_BASELINEGRID: # Enable to show baseline grid.
        template1.baselineGrid()
    # Create empty image place holders. To be filled by running content on the page.
    template1.cImage(None, 4, 0, 2, 4) 
    template1.cImage(None, 0, 5, 2, 3)
    # Create linked text boxes. Note the "nextPage" to keep on the same page or to next.
    template1.cTextBox('', 0, 0, 2, 5, flowId0, nextBox=flowId1, nextPage=0, fill=BOX_COLOR)
    template1.cTextBox('', 2, 0, 2, 8, flowId1, nextBox=flowId2, nextPage=0, fill=BOX_COLOR)
    template1.cTextBox('', 4, 4, 2, 4, flowId2, nextBox=flowId0, nextPage=1, fill=BOX_COLOR)
    # Create page number box. Pattern PAGENUMBER is replaced by actual page number.
    template1.cText(PAGE_ID_MARKER, 6, 0, font=BOOK, fontSize=12, fill=BOX_COLOR)

    # Template 2
    template2 = Template(PW, PH) # Create second template. This is for the main pages.
    if SHOW_GRID: # Enable to show grid columns and margins.
        template2.grid() 
    if SHOW_BASELINEGRID: # Enable to show baseline grid.
        template2.baselineGrid()
    template2.cImage(None, 4, 0, 2, 3)
    template2.cImage(None, 0, 5, 2, 3)
    template2.cImage(None, 2, 2, 2, 2)
    template2.cImage(None, 2, 0, 2, 2)
    template2.cImage(None, 4, 6, 2, 2)
    template2.cTextBox('', 0, 0, 2, 5, flowId0, nextBox=flowId1, nextPage=0, fill=BOX_COLOR)
    template2.cTextBox('', 2, 4, 2, 4, flowId1, nextBox=flowId2, nextPage=0, fill=BOX_COLOR)
    template2.cTextBox('', 4, 3, 2, 3, flowId2, nextBox=flowId0, nextPage=1, fill=BOX_COLOR)
    # Create page number box. Pattern PAGENUMBER is replaced by actual page number.
    template2.cText(PAGE_ID_MARKER, 6, 0, font=BOOK, fontSize=12, fill=BOX_COLOR)
   
    # Create new document with (w,h) and fixed amount of pages.
    # Make number of pages with default document size.
    # Initially make all pages default with template2
    doc = Document(PW, PH, ml=ML, mt=MT, cw=CW, ch=CH, g=G, 
        gridStroke=0.8, pages=2, template=template2,
        baselineGrid=BASELINE_GRID, 
        missingElementFill=MISSING_ELEMENT_FILL)
     
    # Add styles for whole document and text flows.               
    doc.newStyle(name='chapter', font=BOOK)    
    doc.newStyle(name='title', fontSize=32, font=BOLD)
    doc.newStyle(name='subtitle', fontSize=16, font=BOOK_ITALIC)
    doc.newStyle(name='author', fontSize=16, font=BOOK, fill=(1, 0, 0))
    doc.newStyle(name='h1', fontSize=20, font=SEMIBOLD, fill=0.1, stroke=None,
        leading=20, rLeading=0, tracking=H1_TRACK, needsBelow=LEADING*3)
    doc.newStyle(name='h2', fontSize=16, font=SEMIBOLD, fill=0.2, stroke=None, 
        leading=20, rLeading=0, tracking=H2_TRACK, needsBelow=LEADING*3)
    doc.newStyle(name='h3', fontSize=12, font=MEDIUM, fill=0, 
        leading=15, rLeading=0, needsBelow=LEADING*3,
        tracking=H3_TRACK,
        paragraphTopSpacing=U, paragraphBottomSpacing=U/2)
    
    # Spaced paragraphs.
    doc.newStyle(name='p', fontSize=BODYTEXT_SIZE, font=BOOK, fill=0.1, 
        stroke=None, tracking=P_TRACK, language=LANGUAGE, align=LEFT,
        leading=BASELINE_GRID, rLeading=0, hyphenation=True, 
        stripWhiteSpace=' ')
    doc.newStyle(name='b', font=SEMIBOLD, stripWhiteSpace=' ')
    doc.newStyle(name='em', font=BOOK_ITALIC, stripWhiteSpace=' ')
    doc.newStyle(name='img', leading=BASELINE_GRID, rLeading=0,
        fontSize=BODYTEXT_SIZE, font=BOOK,)
    
    # Footnote reference index.
    doc.newStyle(name='sup', font=MEDIUM, 
         rBaselineShift=0.6, fontSize=14*0.65, stripWhiteSpace=' ')
    doc.newStyle(name='li', fontSize=BODYTEXT_SIZE, font=BOOK, 
        tracking=P_TRACK, leading=BASELINE_GRID, rLeading=0, hyphenation=True, tabs=[(Utab, 'left')], 
        indent=Utab, firstLineIndent=1, #tailIndent=U, 
        stripWhiteSpace=' ')
    doc.newStyle(name='ul', stripWhiteSpace=' ',)
    doc.newStyle(name='literatureref', stripWhiteSpace=False,
        fill=0.5, rBaselineShift=0.2, fontSize=14*0.8)
    doc.newStyle(name='footnote', stripWhiteSpace=False,
        fill=(1, 0, 0), fontSize=0.8*U, font=BOOK)
    doc.newStyle(name='caption', stripWhiteSpace=False, tracking=P_TRACK, 
        language=LANGUAGE, 
        fill=0.2, leading=BASELINE_GRID*0.8, fontSize=BODYTEXT_SIZE*0.8,
        font=BOOK_ITALIC, indent=U/2, tailIndent=-U/2, hyphenation=True)

    # Create main Galley for this page, for pasting the sequence of elements.    
    g = Galley() 

    # Change template of page 1
    doc[0].setTemplate(template1)
    
    # Fill the main flow of text boxes with the ML-->XHTML formatted text. 
    c = Composer(doc)
    c.typesetFile(FILENAME, doc[0], flowId0)
     
    return doc
        
d = makeDocument()
d.export('examples/AutomaticLayout.pdf') 

