# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens & Font Bureau
#     www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#     
#     Supporting usage of DrawBot, www.drawbot.com
#     Supporting usage of Flat, https://github.com/xxyxyz/flat
# -----------------------------------------------------------------------------
#
#     TheBWPhotographer.py
#
#     Example photobook/portfolio for B&W photography
#
from __future__ import division
from datetime import datetime # Make date on magazine cover fit today.
from drawBot import ImageObject

import pagebot
from pagebot import newFS, Gradient, Shadow
from pagebot.style import getRootStyle, LEFT, TOP, RIGHT, A4
from pagebot.elements import *
from pagebot.conditions import *
from pagebot.document import Document
from pagebot.composer import Composer
from pagebot.typesetter import Typesetter
from pagebot.toolbox.transformer import s2Color, int2Color, lighter
# Import other than default view class, showing double pages spread
from pagebot.elements.views.spreadview import SpreadView

from pagebot.fonttoolbox.variablefontbuilder import getVariableFont, Font 
W = H = A4[0] # Square of height of A4.
PADDING = (24, 24, 40, 24) # General page padding.

EXPORT_PATH = '../_export/TheBWPhotographer.png' # Export path of the document.
COVER_IMAGE_PATH1 = '../images/BitcountRender3.png' # Path of the cover image.

# Use this color to show "error" debugging, e.g. to show bounding box of an element.
debugColor = (1, 1, 0, 0.5)

# Set some values of the default template (as already generated by the document).
# Make squential unique names for the flow boxes inside the templates
MAIN_FLOW = 'main' # ELement id of the text box on pages the hold the main text flow.
FLOWID1 = MAIN_FLOW+'1' 
FLOWID2 = MAIN_FLOW+'2'
FLOWID3 = MAIN_FLOW+'3'

# Get the root path of open source fonts, enclosed in PageBot.
ROOT_PATH = pagebot.getRootPath()
# Main Variable Font for all text in the magazine. Change this line to build with
# another Variable Font. Using Optical Size (opsz), Weight (wght) and Width (wdth) axes.
FONT_PATH = ROOT_PATH + '/Fonts/fontbureau/AmstelvarAlpha-VF.ttf'

# Open the font, so we can query values that are not available in standard DrawBot functions,
# such as stem width, overshoot of roundings, etc.
f = Font(FONT_PATH)
#print f.axes Uncomment to see the available axes printed.

# Pre-calculate instances of locations in the Variable Font.
LIGHT72 = getVariableFont(FONT_PATH, dict(wght=0.5, wdth=0.6, opsz=72))
BOOK_LIGHT = getVariableFont(FONT_PATH, dict(wght=0.5, wdth=0.7))
BOOK_CONDENSED = getVariableFont(FONT_PATH, dict(wght=0.7, wdth=0.4))
BOOK = getVariableFont(FONT_PATH, dict(wght=0.25, wdth=0))
BOOK_ITALIC = getVariableFont(FONT_PATH, dict(wght=0.25, wdth=1))
MEDIUM = getVariableFont(FONT_PATH, dict(wght=0.40, wdth=0))
SEMIBOLD = getVariableFont(FONT_PATH, dict(wght=0.40, wdth=1))
SEMIBOLD_CONDENSED = getVariableFont(FONT_PATH, dict(wght=0.40, wdth=0.5))
BOLD = getVariableFont(FONT_PATH, dict(wght=0.70, wdth=1))
BOLD_ITALIC = getVariableFont(FONT_PATH, dict(wght=0.7, wdth=1))

shadow = Shadow(offset=(6, -6), blur=10, color=(0.2, 0.2, 0.2, 0.5))
imo = ImageObject()
imo.photoEffectTonal()
#imo.lineOverlay()
#imo.pixellate()
#imo.convolution7X7()
#imo.rowAverage()
#imo.flashTransition()
#imo.spotLight()
imo.edges()
#imo.hexagonalPixellate()
#imo.gloom()


def makeCoverTemplate(imagePath, w, h):
    bleed = 0
    textColor = 1
    # Make styles
    # TODO: Make this fit, using size/wdth axis combination of Amstelvar
    coverTitleSize = 160
    # Not optical size yet. Play more with the axes
    coverTitleFont = getVariableFont(FONT_PATH, 
        dict(wght=0.9, wdth=0.02))#, opsz=coverTitleSize))
    coverTitleStyle = dict(font=coverTitleFont.installedName, fontSize=coverTitleSize, 
        textShadow=shadow, textFill=textColor, tracking=-3)

    coverSubTitleSize = 80
    # Not optical size yet. Play more with the axes
    coverSubTitleFont = getVariableFont(FONT_PATH, dict(wght=0.6, wdth=0.02)) #opsz=coverSubTitleSize))
    coverSubTitleStyle = dict(font=coverSubTitleFont.installedName, fontSize=coverSubTitleSize,         
        textFill=(1, 1, 1, 0.3), tracking=0)

    # Cover
    coverTemplate = Template(w=w, h=h, padding=PADDING) # Cover template of the magazine.
    newImage(imagePath, parent=coverTemplate, imo=imo, conditions=[Fit2WidthSides(), Bottom2BottomSide()])
    # Title of the magazine cover.
    coverTitle = newFS('Fashion', style=coverTitleStyle)
    # Calculate width if single "F" for now, to align "Slow"
    # TODO: Change in example to go through the coverTitle to get positions and widths.
    FWidth, _ = textSize(newFS('F', style=coverTitleStyle))
        
    coversubTitle = newFS('Slow', style=coverSubTitleStyle)
    newTextBox(coversubTitle, parent=coverTemplate, pl=FWidth*0.5, 
        conditions=[Left2Left(), Fit2Width(), Top2TopSide()])
    
    tw, th = textSize(coverTitle)
    newText(coverTitle, parent=coverTemplate, z=20, h=th*0.4, 
        textShadow=shadow, conditions=[Fit2Width(), Top2TopSide()])

    # Make actual date in top-right with magazine title. Draw a bit transparant on background photo.
    dt = datetime.now()
    d = dt.strftime("%B %Y")
    fs = newFS(d, style=dict(font=MEDIUM.installedName, fontSize=17,
        textFill=(1, 1, 1, 0.6), tracking=0.5))
    # TODO: padding righ could come from right stem of the "n"
    newTextBox(fs, parent=coverTemplate, xTextAlign=RIGHT, pr=10, pt=6, conditions=[Top2Top(), Right2Right()])

    # Titles could come automatic from chapters in the magazine.
    fs = newFS('$6.95',  style=dict(font=BOOK.installedName, fontSize=12, 
        textFill=textColor, tracking=1, leading=12 ))
    newText(fs, parent=coverTemplate, mt=8, conditions=[Top2Bottom(), Right2Right()])
  
    makeCoverTitles(coverTemplate)
    
    return coverTemplate

def makeCoverTitles(coverTemplate):
    u"""Build the text box elements in the coverTemplate, containing the chapter titles
    of the magazine."""

    # TODO: Titles should come automatic from random blurb chapter titles in the magazine.
    pl = 8 # Generic offset as padding left from the page padding to aligh with cover title.
    fs = newFS('Skirts &\nScarves', style=dict(font=BOOK_CONDENSED.installedName, 
        fontSize=64, textFill=1, tracking=0.5, leading=0, rLeading=0.9))
    newTextBox(fs, z=20, pl=15, pt=-40, parent=coverTemplate, 
        conditions=[Left2Left(), Fit2Width(), Float2Top()])
        
    # TODO: Titles should come automatic from random blurb chapter titles in the magazine.
    fs = newFS('Ideal style:\n', style=dict(font=MEDIUM.installedName, fontSize=32, 
        textFill=1, tracking=0.5, leading=50))
    fs += newFS('The almost nothing', style=dict(font=BOOK.installedName, 
        fontSize=45, textFill=1, tracking=0.5, leading=48))
    newTextBox(fs, z=20, pl=8, w=400, pt=0, parent=coverTemplate, 
        textShadow=shadow, 
        conditions=[Left2Left(), Float2Top()])
        
    # TODO: Titles should come automatic from random blurb chapter titles in the magazine.
    fs = newFS('Findings\non vineyard island', style=dict(font=BOOK_LIGHT.installedName, 
        fontSize=72, textFill=1, tracking=0.5, leading=74))
    newTextBox(fs, z=20, pl=8, pt=40, parent=coverTemplate, 
        style=dict(shadowOffset=(4, -4), shadowBlur=20, shadowFill=(0,0,0,0.6)),
        textShadow=shadow, 
        conditions=[Left2Left(), Fit2Width(), Float2Top()])
      
    # TODO: Titles should come automatic from random blurb chapter titles in the magazine.
    c = (1, 1, 0, 1) #lighter(int2Color(0x99CBE9)) # Pick from light spot in the photo
    fs = newFS('Exclusive:\n', style=dict(font=MEDIUM.installedName, fontSize=32, 
        textFill=c, tracking=0.5, lineHeight=34))
    fs += newFS('Interview with Pepper+Tom ', style=dict(font=BOOK.installedName, 
        fontSize=32, textFill=c, tracking=0.5, lineHeight=34))
    newTextBox(fs, z=20, pl=pl, pt=20, parent=coverTemplate, 
        style=dict(shadowOffset=(4, -4), shadowBlur=20, shadowFill=(0,0,0,0.6)),
        textShadow=shadow, 
        conditions=[Left2Left(), Fit2Width(), Float2Bottom()])

def makeTemplate1(w, h):
    # Template 16
    template = Template(w=w, h=h, padding=PADDING) # Create template of main size. Front page only.
    # Show grid columns and margins if rootStyle.showGrid or rootStyle.showGridColumns are True
    """
    # Create empty image place holders. To be filled by running content on the page.
    template.cContainer(2, -0.7, 5, 4)  # Empty image element, cx, cy, cw, ch
    template.cContainer(0, 5, 2, 3)
    # Create linked text boxes. Note the "nextPage" to keep on the same page or to next.
    template.cTextBox('', 0, 0, 2, 5, eId=FLOWID1, nextBox=FLOWID2, nextPage=0, fill=BOX_COLOR)
    template.cTextBox('', 2, 3, 2, 5, eId=FLOWID2, nextBox=FLOWID3, nextPage=0, fill=BOX_COLOR)
    template.cTextBox('', 4, 3, 2, 5, eId=FLOWID3, nextBox=FLOWID1, nextPage=1, fill=BOX_COLOR)
    # Create page number box. Pattern pageNumberMarker is replaced by actual page number.
    template.text(rs['pageIdMarker'], (template.css('w',0)-template.css('mr',0), 20), style=rs, font=BOOK, fontSize=12, fill=BOX_COLOR, align='right')
    """
    return template
 
def makeTemplate2(w, h):
    # Template 2
    template = Template(w=w, h=h, padding=PADDING) # Create second template. This is for the main pages.
    # Show grid columns and margins if rootStyle.showGrid or rootStyle.showGridColumns are True
    """
    template.cContainer(4, 0, 2, 3)  # Empty image element, cx, cy, cw, ch
    template.cContainer(0, 5, 2, 3)
    template.cContainer(2, 2, 2, 2)
    template.cContainer(2, 0, 2, 2)
    template.cContainer(4, 6, 2, 2)
    template.cTextBox('', 0, 0, 2, 5, eId=FLOWID1, nextBox=FLOWID2, nextPage=0, fill=BOX_COLOR)
    template.cTextBox('', 2, 4, 2, 4, eId=FLOWID2, nextBox=FLOWID3, nextPage=0, fill=BOX_COLOR)
    template.cTextBox('', 4, 3, 2, 3, eId=FLOWID3, nextBox=FLOWID1, nextPage=1, fill=BOX_COLOR)
    # Create page number box. Pattern pageNumberMarker is replaced by actual page number.
    template.text(rs['pageIdMarker'], (template.css('w',0) - template.css('mr',0), 20), style=rs, font=BOOK, fontSize=12, fill=BOX_COLOR, align='right')
    """
    return template
           
# -----------------------------------------------------------------         
def makeDocument():
    u"""Demo page composer."""

    coverTemplate1 = makeCoverTemplate(COVER_IMAGE_PATH1, W, H)
    template1 = makeTemplate1(W, H) 
    template2 = makeTemplate2(W, H)
       
    # Create new document with (w,h) and fixed amount of pages.
    # Make number of pages with default document size, start a page=1 to make SpreadView work.
    # Initially make all pages default with template2.
    # Oversized document (docW, docH) is defined in the rootStyle.
    doc = Document(title=EXPORT_PATH, w=W, h=H, autoPages=1, originTop=False,
        template=template1, startPage=1) 
 
    # TODO Will be expanded with more pages later.
    view = doc.getView()
    #view = SpreadView(parent=doc) # Show as spread, not a single pages.
    view.padding = 40
    view.showPageCropMarks = True
    view.showPageRegistrationMarks = True
    view.showPageFrame = False
    view.showPagePadding = False
    view.showElementOrigin = False
    view.showElementDimensions = False
    
    # Cache some values from the root style that we need multiple time to create the tag styles.
    """
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
    doc.newStyle(name='h1', fontSize=3.85*fontSize, font=SEMIBOLD_CONDENSED, textFill=(1, 0, 0), 
        leading=2.5*leading, tracking=H1_TRACK, postfix='\n')
    doc.newStyle(name='h2', fontSize=1.5*fontSize, font=SEMIBOLD, textStroke=None,
        fill=(0, 0, 1), leading=1*leading, rLeading=0, tracking=H2_TRACK, 
        prefix='', postfix='\n')
    doc.newStyle(name='h3', fontSize=1.1*fontSize, font=MEDIUM, textFill=(1, 0, 0), textStroke=None,
        leading=leading, rLeading=0, rNeedsBelow=2*rLeading, tracking=H3_TRACK,
        prefix='\n', postfix='\n')
    doc.newStyle(name='h4', fontSize=1.1*fontSize, font=BOOK, textFill=(0, 1, 0), textStroke=None,
        leading=leading, rLeading=0, rNeedsBelow=2*rLeading, tracking=H3_TRACK,
        paragraphTopSpacing=U, paragraphBottomSpacing=U, prefix='\n', postfix='\n')
    
    # Spaced paragraphs.
    doc.newStyle(name='p', fontSize=fontSize, font=BOOK, textFill=0.1, prefix='', postfix='\n',
        rTracking=P_TRACK, leading=14, rLeading=0, align=LEFT_ALIGN, hyphenation=True)
    doc.newStyle(name='b', font=SEMIBOLD)
    doc.newStyle(name='em', font=BOOK_ITALIC)
    doc.newStyle(name='hr', stroke=(1, 0, 0), strokeWidth=4)
    doc.newStyle(name='br', postfix='\n') # Simplest way to make <br/> show newline
    doc.newStyle(name='a', prefix='', postfix='')
    doc.newStyle(name='img', leading=leading, fontSize=fontSize, font=BOOK)
    
    # Footnote reference index.
    doc.newStyle(name='sup', font=MEDIUM, rBaselineShift=0.6, prefix='', postfix=' ',
        fontSize=0.6*fontSize)
    doc.newStyle(name='li', fontSize=fontSize, font=BOOK, 
        tracking=P_TRACK, leading=leading, hyphenation=True, 
        # Lists need to copy the listIndex over to the regalar style value.
        tabs=[(listIndent, LEFT_ALIGN)], indent=listIndent, 
        firstLineIndent=1, postfix='\n')
    doc.newStyle(name='ul', prefix='', postfix='')
    doc.newStyle(name='literatureref', fill=0.5, rBaselineShift=0.2, fontSize=0.8*fontSize)
    doc.newStyle(name='footnote', fill=(1, 0, 0), fontSize=0.8*U, font=BOOK)
    doc.newStyle(name='caption', tracking=P_TRACK, language=language, fill=0.2, 
        leading=leading*0.8, fontSize=0.8*fontSize, font=BOOK_ITALIC, 
        indent=U/2, tailIndent=-U/2, hyphenation=True)
    """
    # Change template of page 1
    page1 = doc[0]
    page1.applyTemplate(coverTemplate1)
    
    if 0: #NOT NOW
        page2 = doc[2] # Default is template1, as defined in Document creation.
        page2.applyTemplate(template1)
    
        page3 = doc[3] # Default is template1, as defined in Document creation.
        page3.applyTemplate(template2)
    
    # Show thumbnail of entire paga4 on cover. 
    # TODO: Needs to be masked still.
    # TODO: Scale should not be attribute of style, but part of placement instead.
    #page3.style['scaleX'] = page3.style['scaleY'] = 0.1
    #page1.place(page3, 500, 48)# sx, sy)
    """
    # Create main Galley for this page, for pasting the sequence of elements.    
    g = Galley() 
    t = Typesetter(g)
    t.typesetFile(MD_PATH)
    
    # Fill the main flow of text boxes with the ML-->XHTML formatted text. 
    c = Composer(doc)
    c.compose(g, page2, FLOWID1)
    """
    doc.solve()
    
    return doc

d = makeDocument()
d.export(EXPORT_PATH, view=SpreadView.viewId) 

