# What is PageBot®?

**Homepage: [pagebot.io](http://pagebot.io)**

PageBot is a page layout program that enables designers to create high quality
documents using Python programming. It is available both as Python library
working with [DrawBot](http://www.drawbot.com) and as part of a collection of
stand-alone desktop applications. Other contexts such as
[Flat](http://xxyxyz.org/flat) and InDesign are currently being developed. They
will allow PageBot to output to print-ready formats and to run in environments
other than Mac OS X such as Posix web servers. The aim of the developers of
PageBot is to create a system of scriptable applications to generate
professionally designed documents that make use of high quality typography.



# Installation

    pip install pagebot

# Usage

    from pagebot.document import Document
    from pagebot.elements import newRect
    from pagebot.conditions import Center2Center, Middle2Middle
    from pagebot.toolbox.units import pt
    from pagebot.toolbox.color import color
    
    W, H = pt(500, 400)
    doc = Document(w=W, h=H, originTop=False, autoPages=1)
    page = doc[1]
    
    # Create a new rectangle element with position conditions
    newRect(parent=page, fill=color('red'), size=pt(240, 140),
        # Show measure lines on the element.
        showDimensions=True, 
        conditions=[Center2Center(), Middle2Middle()])
    # Make the page apply all conditions.
    page.solve() 
    # Export the document page as png, so it shows as web image.
    doc.export('_export/RedSquare.png') 
       
    
# Issue Tracking 

Bugs, enhancements and requested features can be added to the GitHub issue tracker:

 * [issues](https://github.com/PageBot/PageBot/issues)
 * [projects](https://github.com/PageBot/PageBot/projects)
 * [milestones](https://github.com/PageBot/PageBot/milestones)

# External Links

- Download: [PyPi](https://pypi.org/project/pagebot/)
- Continuous Integration: [Travis](https://travis-ci.org/PageBot/PageBot)
- Documentation: [ReadTheDocs](https://pagebot.readthedocs.io/en/latest/)
- Examples repository: [PageBotExamples](https://github.com/PageBot/PageBotExamples)

# Related

- PageBot generated website: [designdesign.space](http://designdesign.space). It also includes entry points
for studies and workshops on how to work with PageBot.
- The TYPETR Upgrade website [upgrade.typenetwork.com](https://upgrade.typenetwork.com) is an example where
the HTML/CSS code and all illustrations are generated by PageBot scripts.

# Feature Description

## Current Functionality

Current features include:

* Various types of Element objects can be placed on a page or inside other
  Element objects.
* Grids can be defined through style measurements and views.
* Page templates (or templates for any other element combination) can be
  defined and applied.
* Automatic layout conditions for elements, for example even distribution
  across or floating down parent elements.
* Specialized views on a Document, such as plain pages, spreads and other
  layout of page groups, optional with crop-marks, registration-mark,
color-strips, file name, etc. The result of all views can be placed on pages as
illustration.
* Graphics - using all Drawbot drawing tools.
* All image filtering supplied by Drawbot ImageObject.
* Access and modify images on pixel-level.
* Cascading styles, where Element values inherit from parent Elements, similar
  to CSS behavior.   
* Text flows are using the macOS FormattedString for all typographic
  parameters.
* Random Text generator for headlines and articles.
* Read text from MarkDown and XML (.MD .XML)
* Support large amount of text processing functions:
   * centered, left, right and justified
   * Text to fit a box and elastic box to fit text
   * Tabular setting
   * Text Flow from one element to another. 
   * Variable Font UI access and instance creation, as the whole "fonttools"
     Python library is available.
   * Access to all font metrics.
   * Outline Font access modification.
   * Space, groups and kerning access and modifcation.
   * OT layout and feature access and modification.
* 3D Positioning of points, for future usage.
* Motion Graphics, export as animated .gif and .mov files, keyframing timeline, 
* Export to PDF, PNG, JPG, SVG, (animated) GIF, MOV, XML, through programmable
  views.
* Build web sites, pre-compiling all images used into the formats that can be
  displayed by browsers (.PNG .JPG .SVG)
* Automatic table of contents, image references, quote references, etc. from
  composed documents.

## Types of Publications

* PageBot stationary and publications as scripted templates
* Specimens for TN library
* Recreation of legacy type specimens as PageBot templates
* Magazines
* Newspapers
* Newsletters
* Books
* Parametric corporate identities including their styleguides, stationary and
  business card templates.
* Parametric advertizements (connecting to existing ad-systems)
* Online documents, such as single page websites
* Wayfindng templates for signs and maps
* T-Shirt templates
* Templates with embedded information for graphic- and typographic education.

## Unit Testing

PageBot uses Python's native `doctest` library to perform unit tests:

* [https://docs.python.org/2/library/doctest.html](https://docs.python.org/2/library/doctest.html)

Note: doctest can be run in Sublime with `cmd-B`   

## Future Developments

* Element classes supporting various types of graphs, info-graphics, maps,
  PageBot document layout, Variable Font axes layout, font metrics.
* Font class supporting CFF (.otf) and UFO.
* Views for thumbnail page overview, combined booklet-sheets for print,
  site-maps, etc.
* Add export of text to MarkDown .md files.
* Add export to online documents, such as HTML/CSS/JS for specific designs of
  web pages, such as Kirby.
* Export to WordPress® PHP sites.
* Export to Ruby®/Sketchup® data files.
* Add export to Angular® files.
* Export to InDesign® and Illustrator®, as close as possible translating
  PageBot elements to the native file format of these applications.
* Time line, definition and editing, length and fps.
* Integrate the PageBot manual builder with other export functions of the library.
* Add more unit-tests to guarantee the integrity of the library and output
  consistency.
* Automatic support of ornament frames, in connection to the Element borders
  and the layout of exiting (TN) border fonts.

# Licencing

- The core library, tutorials and basic examples for PageBot are available
  under the MIT Open Source license. Some depencendies have been included in
  this repository and are available under their own licenses. See also the
  [LICENSE](https://github.com/PageBot/PageBot/blob/master/LICENSE.md).

> PageBot® is a registered trademark 
> U.S. Serial Number: 87-457,280
> Owner: Buro Petr van Blokland + Claudia Mens VOF
> Docket/Reference Number: 1538-25     
