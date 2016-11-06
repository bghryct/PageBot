# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Type Network, www.typenetwork.com, www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#     Made for usage in Drawbot, www.drawbot.com
# -----------------------------------------------------------------------------
#
#     VariableFontDesign.py
#
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

# Get the default root stule.
rs = getRootStyle()

# Basic layout measures altering the default rooT STYLE.
rs.u = U = 7
rs.pw = 595  # Page width 210mm, international generic fit.
rs.ph = 11 * 72  # Page height 11", international generic fit.
rs.ml = 7 * U  # Margin leftrs.mt = 7*U # Margin top
rs.baselineGrid = 2 * U
rs.g = U  # Generic gutter.
rs.cw = 11 * U  # Column width.
rs.ch = 6 * rs.baselineGrid - rs.g  # Approx. square. Fit with baseline.
rs.listIndent = U * 0.8  # Indent for bullet lists
rs.listTabs = [(rs.listIndent, LEFT_ALIGN)]
# Display option
rs.showGrid = True
rs.showBaselineGrid = True
# Text measures
rs.leading = rs.baselineGrid
rs.rLeading = 0
rs.fontSize = 10
# Language settings
rs.language = 'nl-be'
MAIN_FLOW = 'main'  # ELement id of the text box on pages the hold the main text flow.
FILENAME = 'variableFontDesign.md'  # 'automaticLayout_nl.md'
BOX_COLOR = 0.8

# Tracking presets
H1_TRACK = H2_TRACK = 0.015
H3_TRACK = 0.030  # Tracking as relative factor to font size.
P_TRACK = 0.030

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
    flowId0 = MAIN_FLOW + '0'
    flowId1 = MAIN_FLOW + '1'
    flowId2 = MAIN_FLOW + '2'

    # Template 1
    template1 = Template(rs)  # Create template of main size. Front page only.
    if rs.showGrid:  # Enable to show grid columns and margins.
        template1.grid()
    if rs.showBaselineGrid:  # Enable to show baseline grid.
        template1.baselineGrid()
    # Create empty image place holders. To be filled by running content on the page.
    # Future nerdy enhancement: automatic compensate for OSX-screenshort window shadow :)
    template1.cImage(None, 2, 2, 4, 4)
    template1.cImage(None, 2, 6, 2, 2) 
    template1.cImage(None, 4, 6, 2, 2) 
    # Create linked text boxes. Note the "nextPage" to keep on the same page or to next.
    template1.cTextBox('', 0, 0, 2, 5, flowId0, nextBox=flowId1, nextPage=0, fill=BOX_COLOR)
    template1.cTextBox('', 2, 0, 2, 8, flowId1, nextBox=flowId2, nextPage=0, fill=BOX_COLOR)
    template1.cTextBox('', 4, 4, 2, 4, flowId2, nextBox=flowId0, nextPage=1, fill=BOX_COLOR)
    # Create page number box. Pattern PAGENUMBER is replaced by actual page number.
    template1.cText(rs.pageIdMarker, 6, 0, font=BOOK, fontSize=12, fill=BOX_COLOR)

    # Template 2
    template2 = Template(rs)  # Create second template. This is for the main pages.
    if rs.showGrid:  # Enable to show grid columns and margins.
        template2.grid()
    if rs.showBaselineGrid:  # Enable to show baseline grid.
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
    template2.cText(rs.pageIdMarker, 6, 0, font=BOOK, fontSize=12, fill=BOX_COLOR)

    # Create new document with (w,h) and fixed amount of pages.
    # Make number of pages with default document size.
    # Initially make all pages default with template2
    doc = Document(rs, pages=2, template=template2)

    # Add styles for whole document and text flows.
    doc.newStyle(name='chapter', font=BOOK)
    doc.newStyle(name='title', fontSize=3 * rs.fontSize, font=BOLD)
    doc.newStyle(name='subtitle', fontSize=2 * rs.fontSize, font=BOOK_ITALIC)
    doc.newStyle(name='author', fontSize=2 * rs.fontSize, font=BOOK, fill=(1, 0, 0))
    doc.newStyle(name='h1', fontSize=rs.fontSize, font=SEMIBOLD, fill=0.1, stroke=None,
        leading=3 * rs.fontSize, rLeading=0, tracking=H1_TRACK, needsBelow=3 * rs.leading)
    doc.newStyle(name='h2', fontSize=16, font=SEMIBOLD, fill=0.2, stroke=None,
        leading=2 * rs.fontSize, rLeading=0, tracking=H2_TRACK, needsBelow=3 * rs.leading)
    doc.newStyle(name='h3', fontSize=1.2 * rs.fontSize, font=MEDIUM, fill=0,
        leading=1.5 * rs.fontSize, rLeading=0, rNeedsBelow=2 * rs.leading,
        tracking=H3_TRACK,
        paragraphTopSpacing=U, paragraphBottomSpacing=U / 2)

    # Spaced paragraphs.
    doc.newStyle(name='p', fontSize=rs.fontSize, font=BOOK, fill=0.1,
        stroke=None, tracking=P_TRACK, language=rs.language, align=rs.LEFT_ALIGN,
        leading=rs.leading, rLeading=0, hyphenation=True,
        stripWhiteSpace=' ')
    doc.newStyle(name='b', font=SEMIBOLD, stripWhiteSpace=' ')
    doc.newStyle(name='em', font=BOOK_ITALIC, stripWhiteSpace=' ')
    doc.newStyle(name='img', leading=rs.leading, rLeading=0,
        fontSize=rs.fontSize, font=BOOK, )

    # Footnote reference index.
    doc.newStyle(name='sup', font=MEDIUM,
        rBaselineShift=0.6, fontSize=14 * 0.65, stripWhiteSpace=' ')
    doc.newStyle(name='li', fontSize=rs.fontSize, font=BOOK,
        tracking=P_TRACK, leading=rs.leading, rLeading=0, hyphenation=True,
        tabs=[(rs.listIndent, LEFT_ALIGN)], indent=rs.listIndent, firstLineIndent=1,  # tailIndent=U,
        stripWhiteSpace=' ')
    doc.newStyle(name='ul', stripWhiteSpace=' ', )
    doc.newStyle(name='literatureref', stripWhiteSpace=False,
        fill=0.5, rBaselineShift=0.2, fontSize=14 * 0.8)
    doc.newStyle(name='footnote', stripWhiteSpace=False,
        fill=(1, 0, 0), fontSize=0.8*U, font=BOOK)
    doc.newStyle(name='XXXcaption', stripWhiteSpace=False, tracking=P_TRACK, 
        language=LANGUAGE, 
        fill=0.2, leading=BASELINE_GRID*0.8, fontSize=BODYTEXT_SIZE*0.8,
        font=BOOK_ITALIC, indent=U/2, tailIndent=-U/2, hyphenation=True)
    doc.newStyle(name='caption', stripWhiteSpace=False, tracking=P_TRACK, 
        language=LANGUAGE, baselineShift=0.5*U,
        fill=0, leading=BASELINE_GRID*0.8, fontSize=BODYTEXT_SIZE*0.8,
        font=BOOK_ITALIC, indent=32, tailIndent=-32, hyphenation=True)

    # Create main Galley for this page, for pasting the sequence of elements.    
    g = Galley() 
    # Change template of page 1
    doc[0].setTemplate(template1)

    # Create main Galley for this page, for pasting the sequence of elements.
    g = Galley()
    t = Typesetter(doc, g)
    t.typesetFile(FILENAME)

    # Fill the main flow of text boxes with the ML-->XHTML formatted text.
    c = Composer(doc)
    c.compose(g, doc[0], flowId0)

    return doc

d = makeDocument()
d.export('export/VariableFontDesign.pdf') 

