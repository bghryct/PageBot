# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2017 Thom Janssen <https://github.com/thomgb>
#     www.pagebot.io
#     Licensed under MIT conditions
#
#     Supporting DrawBot, www.drawbot.com
#     Supporting Flat, xxyxyz.org/flat
# -----------------------------------------------------------------------------
#
#from pagebot.contexts.flatcontext import FlatContext
from pagebot.contexts.platform import getContext

from pagebot.fonttoolbox.objects.font import findFont
from pagebot.document import Document
from pagebot.elements import * # Import all types of page-child elements for convenience
from pagebot.toolbox.color import color
from pagebot.toolbox.units import em, p, pt
from pagebot.conditions import * # Import all conditions for convenience.
from pagebot.constants import GRID_COL, GRID_ROW, GRID_SQR

#context = FlatContext()
context = getContext()

W = H = pt(1000) # Document size
PADDING = pt(100) # Page padding on all sides
G = p(2) # 2 Pica gutter
PW = W - 2*PADDING # Usable padded page width
PH = H - 2*PADDING # Usable padded page height
CW = (PW - G)/2 # Column width
CH = PH
# Hard coded grid, will be automatic in later examples.
GRIDX = ((CW, G), (CW, 0))
GRIDY = ((CH, 0),)

text = """Considering the fact that the application allows individuals to call a phone number and leave a voice mail, which is automatically translated into a tweet with a hashtag from the country of origin. """

font = findFont('Roboto-Regular')

style = dict(font=font, fontSize=24, leading=em(1.4), textFill=0.3)
# Make long text to force box overflow
t = context.newString(text * 3 + str(list(range(100))), style=style)
# Create a new document with 1 page. Set overall size and padding.
doc = Document(w=W, h=H, padding=PADDING, gridX=GRIDX, gridY=GRIDY, context=context)
# Get the default page view of the document and set viewing parameters
view = doc.view
view.showTextOverflowMarker = True # Shows as [+] marker on bottom-right of page.
view.showGridBackground = [GRID_COL, GRID_ROW, GRID_SQR] # Set types of grid lines to show

# Get the page
page = doc[1]
# Make text box as child element of the page and set its layout conditions
# to fit the padding of the page and the condition that checks on text overflow.
c1 = newTextBox(t, w=CW, name='c1', parent=page, nextElement='c2',
    conditions=[Left2Left(), Top2Top(), Fit2Height(), Overflow2Next()])
# Text without initial content, will be filled by overflow of c1.
# Not showing the [+] marker, as the overflow text fits in the second column.
c2 = newTextBox(w=CW, name='c2', parent=page, 
    conditions=[Right2Right(), Top2Top(), Fit2Height()])
# Solve the page/element conditions
doc.solve()
print(c1.getOverflow())

# Export the document to this PDF file.
doc.export('_export/SingleColumn.pdf')

