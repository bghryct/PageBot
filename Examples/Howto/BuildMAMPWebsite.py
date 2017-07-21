# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens & Font Bureau
#     www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#     Made for usage in DrawBot, www.drawbot.com
# -----------------------------------------------------------------------------
#
#     ExportCSS.py
#
import os
import pagebot # Import to know the path of non-Python resources.

# Creation of the RootStyle (dictionary) with all available default style parameters filled.
from pagebot.style import getRootStyle, A4, CENTER, RIGHT, LEFT, NO_COLOR,TOP, BOTTOM, MM
# Document is the main instance holding all information about the document togethers (pages, styles, etc.)
from pagebot import newFS

from pagebot.conditions import *
from pagebot.elements import *
from pagebot.document import Document

DoTextFlow = False   
PagePadding = 32
PageSize = 500

# Export in _export folder that does not commit in Git. Force to export PDF.
# The .html and .css extensions triggers the HtmlBuilder and CssBuilder to be used for file export.
# If the MAMP server application not installed, a browser is opened on their website to download it.
MAMP_PATH = '/Applications/MAMP/htdocs/'
MAMP_PAGEBOT_PATH = MAMP_PATH + 'pagebot/examplewebsite/'
EXPORT_PATH_HTML = MAMP_PAGEBOT_PATH + 'index.html'
EXPORT_PATH_CSS = MAMP_PAGEBOT_PATH + 'main.css'
MAMP_LOCAL_URL = 'http://localhost:8888/pagebot/'
MAMP_SHOP_URL = 'https://www.mamp.info/en/' # In cade MAMP does not exist, open on their website to download and install.

def makeDocument():
    u"""Make a new document."""

    W = H = PageSize

    # Create a new document, default to the defined page size. 
    doc = Document(w=W, h=H, originTop=False, title='Text Flow', autoPages=2)
    
    view = doc.getView()
    view.padding = 0 # Aboid showing of crop marks, etc.
    view.showPageCropMarks = True
    view.showPageRegistrationMarks = True
    view.showPageFrame = True
    view.showPagePadding = True
    view.showElementOrigin = True
    view.showElementDimensions = False
    
    # Get list of pages with equal y, then equal x.    
    #page = doc[0][0] # Get the single page from te document.
    page0 = doc.getPage(0) # Get page on pageNumber, first in row (this is only one now).
    page0.name = 'Page 1'
    page0.padding = PagePadding
    
    s = ''
    for n in range(10):
        s += '(Line %d) Volume of text defines the box height. Volume of text defines the box height. \n' % (n+1)
        h1 = None  
          
    e1 = newTextBox(s, 
        name='CSSTextBox1',
        parent=page0, padding=4, x=100, font='Verdana', h=h1,
        maxW=W-2*PagePadding, minW=100, mb=20, mr=10,       # Conditions make the element move to top-left of the page.
        # And the condition that there should be no overflow, otherwise the text box
        # will try to solve it.     
        conditions=[Left2Left(), Fit2Width(), Float2Top()],
        # Position of the origin of the element. Just to show where it is.
        # Has no effect on the position conditions. 
        yAlign=BOTTOM, xAlign=LEFT,
        leading=5, fontSize=9, textFill=0, strokeWidth=0.5, fill=0.9, stroke=None,
    )
    e2 = newTextBox('', # Empty box, will get the overflow from e1, if there is any.
        name='CSSTextBox2', # Flow reference by element.name 
        parent=page0, padding=4, x=100, h=200, 
        maxW=W-2*PagePadding, minW=100,
        conditions=[Left2Left(), Fit2Width(), Float2Top()],
        yAlign=TOP, fill=1, stroke=None,
    )
        
    score = doc.solve() # Try to solve all pages.
    if score.fails:
        print score.fails
            
    return doc # Answer the doc for further doing.

if not os.path.exists(MAMP_PATH):
    print 'The local MAMP server application does not exist. Download and in stall from %s.' % MAMP_SHOP_URL 
    os.system(u'open %s' % MAMP_SHOP_URL)
else:
    # Document current view will recognize .css extension to call the CssBuilder.
    d = makeDocument()
    
    d.export(EXPORT_PATH_CSS)
    print 'Generated CSS code saved as file', EXPORT_PATH_CSS
    d.export(EXPORT_PATH_HTML)
    print 'Generated HTML and CSS code saved as files', EXPORT_PATH_HTML
    # Open the css file in the default editor of your local system.
    os.system(u'open "%s"' % MAMP_LOCAL_URL + EXPORT_PATH_HTML)
    print 'Done' 

