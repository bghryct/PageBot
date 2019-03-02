#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#     www.pagebot.io
#     Licensed under MIT conditions
#
#     Supporting DrawBot, www.drawbot.com
#     Supporting Flat, xxyxyz.org/flat
# -----------------------------------------------------------------------------
#
#     pbimage.py
#


import os

from pagebot.elements.element import Element
from pagebot.constants import ORIGIN, CACHE_EXTENSIONS #
from pagebot.toolbox.units import pointOffset, point2D, point3D, units, pt, upt
from pagebot.toolbox.color import noColor
from pagebot.toolbox.transformer import path2Extension


class Image(Element):
    """The Image contains the reference to the actual binary image data. eId
    can be (unique) file path or eId.

    >>> from pagebot.toolbox.units import mm, p, point3D
    >>> from pagebot import getResourcesPath
    >>> imageFilePath = '/images/peppertom_lowres_398x530.png'
    >>> imagePath = getResourcesPath() + imageFilePath
    >>> from pagebot.contexts.drawbotcontext import DrawBotContext
    >>> from pagebot.constants import A4
    >>> from pagebot.document import Document
    >>> from pagebot.conditions import *
    >>> doc = Document(size=A4, originTop=False, padding=30)
    >>> page = doc[1]
    >>> e = Image(imagePath, xy=pt(220, 330), w=512, parent=page, conditions=[Fit2Sides()])
    >>> e.xy # Position of the image
    (220pt, 330pt)
    >>> (e.w, e.h), e.size, (e.iw, e.ih) # Identical result, width is the lead.
    ((512pt, 681.81pt), (512pt, 681.81pt), (398pt, 530pt))
    >>> e.h = 800 # Width is proportionally calculated, height is the lead.
    >>> e.size
    (600.75pt, 800pt)
    >>> e.h *= 1.5
    >>> e.size, e._w, e._h
    ((901.13pt, 1200pt), None, 1200pt)
    >>> e.size = mm(50), p(100) # Disproportional size setting
    >>> e.size
    (50mm, 100p)
    >>> e.size = None # Force answering the original image size
    >>> e.size # Initialize from file
    (398pt, 530pt)
    >>> page.w = mm(150)
    >>> e.conditions = [Top2Top(), Fit2Width()] # Set new condition, fitting on page padding of 30pt
    >>> doc.solve()
    Score: 2 Fails: 0
    """
    """
    >>> e.xy, e.size # Now disproportionally fitting the full page size of the A4-doc
    ((30pt, 286.42mm), (128.83mm, 486.32pt))
    """
    isImage = True

    def __init__(self, path=None, alt=None, name=None, w=None, h=None, size=None, z=0, mask=None,
        imo=None, proportional=True, index=1, **kwargs):
        Element.__init__(self, **kwargs)

        # Initialize the self.im and self.ih sizes of the image file, defined by path.
        # If the path does not exist, then self.im = self.ih = pt(0)
        # This is calling self.initImageSize() to set self.im and slef.ih from the image file size.
        self.path = path # If path is omitted or file does not exist, a gray/crossed rectangle will be drawn.

        if self.iw and self.ih:
            #print(size, w, h, units(w, self.ih/self.iw * (w or 0)), units(self.iw/self.ih * (h or 0), h))
            if proportional:
                if size is not None:
                    w, h = point2D(size)
                if w is not None:
                    self.size = w, w * (self.ih/self.iw) # Brackets: Divide into ratio number before multiplying
                elif h is not None:
                    self.size = h * (self.iw/self.ih), h # Brackets: Divide into ratio number before multiplying 
                else: 
                    self.size = units(w, h)
            else: # No proportional flag, try to figure out from the supplied propotions
                if size is not None:
                    w, h = point2D(size)
                    self.size = w, h       
                # One of the two needs to be defined, the other can be None.
                # If both are set, then the image scales disproportional.
                if size is None and w is not None and h is not None: # Disproportional scaling
                    self.size = units(w, h)
            #print('#@@##@@#', self._w, self._h, self.iw, self.ih, w, h, size, self.w, self.h, self.size, self.path)
        else:
            print('Image: Missing image at path "%s"' % path)

        self.name = name
        self.alt = alt
        self.mask = mask # Optional mask element.
        self.imo = imo # Optional ImageObject with filters defined. See http://www.drawbot.com/content/image/imageObject.html
        self.index = index # In case there are multiple images in the file (e.g. PDF), use this index. Default is first = 1

    def _get_size(self):
        """Get/Set the size of the image. If one of (self._w, self._h) values
        is None, then it is calculated by propertion. If both are None, the
        original size of the image is returned. If both are not None, then that
        size is answered disproportionally."""
        return self.w, self.h
    def _set_size(self, size):
        if size is None: # Reset to original size by single None value.
            size = None, None, None
        self._w, self._h, self.d = units(point3D(size))
    size = property(_get_size, _set_size)

    def _get_size3D(self):
        return self.w, self.h, self.d
    size3D = property(_get_size3D, _set_size)

    def _get_w(self):
        """Get the intended width and calculate the new scale, validating the
        width to the image minimum width and the height to the image minimum
        height. If not self._h is defined, then the proportion is recalculated,
        depending on the ratio of the image."""
        u = None
        if not self._w: # Width is undefined
            iwpt, ihpt = upt(self.iw, self.ih)
            if self.defaultImageWidth and iwpt:
                u = min(self.defaultImageWidth, iwpt)  # Width overrules, avoid enlargements
            elif self.defaultImageHeight and ihpt:
                u = self.iw * upt(min(self.defaultImageHeight, ihpt) / ihpt)  # Height is lead, calculate width.
            elif self._h and ihpt:
                u = self.iw * upt(self._h / ihpt)  # Height is lead, calculate width.
            else:
                u = self.iw # Undefined and without parent, answer original image width.
        else:
            base = dict(base=self.parentW, em=self.em) # In case relative units, use the right kind of base.
            u = units(self._w, base=base) # Width is lead and defined as not 0 or None.
        return u
    def _set_w(self, w):
        # If self._h is set too, do disproportional sizing. Otherwise set to 0 or None.
        if w:
            w = units(w)
        self._w = w # Width is lead, height is undefined.
        self._h = None
    w = property(_get_w, _set_w)

    def _get_h(self):
        u = None
        if not self._h: # Height is undefined
            iwpt, ihpt = upt(self.iw, self.ih)
            if self.defaultImageHeight and ihpt:
                u = min(self.defaultImageHeight, ihpt)  # Height overrules, avoid enlargements
            elif self.defaultImageWidth and iwpt:
                u = self.ih * upt(min(self.defaultImageWidth, iwpt) / iwpt)  # Height is lead, calculate width.
            elif self._w and iwpt:
                u = self.ih * upt(self._w / iwpt)  # Width is lead, calculate height.
            else:
                u = self.ih # Undefined and without parent, answer original image width.
        else:
            base = dict(base=self.parentH, em=self.em) # In case relative units, use the right kind of base.
            u = units(self._h, base=base) # Height is lead and defined as not 0 or None.
        return u
    def _set_h(self, h):
        # If self._w is set too, do disproportional sizing. Otherwise set to 0 or None.
        if h:
            h = units(h)
        self._w = None # Height is lead, width is undefined.
        self._h = h

    h = property(_get_h, _set_h)

    def __len__(self):
        u"""Answers the number of pages in the the current image file."""
        if self.path:
            return self.context.numberOfImages(self.path)
        return 0

    def __repr__(self):
        return '<%s eId:%s path:%s>' % (self.__class__.__name__, self.eId, self.path)

    def addFilter(self, filters):
        """Add the filter to the self.imo image object. Create the image object
        in case it doest not exist yet. To be extended into a better API. More
        feedback needed for what the DrawBot values in the filters do and what
        their ranges are."""
        if self.imo is None and self.path is not None:
            self.imo = self.context.ImageObject(self.path)
            for filter, params in filters:
                getattr(self.imo, filter)(**params)

    def setPath(self, path):
        """Set the path of the image. If the path exists, the get the real
        image size and store as self.iw, self.ih."""
        self._path = path
        self.initImageSize() # Get real size from the file.

    def _get_path(self):
        return self._path
    def _set_path(self, path):
        self.setPath(path)
    path = property(_get_path, _set_path)

    def initImageSize(self):
        """Initialize the image size. Note that this is done with the
        default/current Context, as there may not be a view availabe yet."""
        if self.path is not None and os.path.exists(self.path):
            self.iw, self.ih = self.context.imageSize(self.path)
        else:
            self.iw = self.ih = pt(0) # Undefined or non-existing, there is no image file.

    def _get_imageSize(self):
        """Answers the Point2D image size in pixels."""
        return self.iw, self.ih
    imageSize = property(_get_imageSize)

    def getPixelColor(self, p, scaled=True):
        """Answers the color in either the scaled point (x, y) or original
        image size point."""
        assert self.path is not None
        x, y = point2D(p)
        if scaled:
            x = self.w / self.iw
            y = self.h / self.ih
        p = x, y
        return self.doc.context.imagePixelColor(self.path, p)

    def _getAlpha(self):
        """Use alpha channel of the fill color as opacity of the image."""
        sFill = self.css('fill', noColor)
        if isinstance(sFill, (tuple, list)) and len(sFill) == 4:
            _, _, _, alpha = sFill
        else:
            alpha = 1
        return alpha

    def scaleImage(self, view):
        """If the self.saveScaled is True and the reduction scale is inside the range,
        then create a new cached image file, if it does not already exist. Scaling images in
        the DrawBot context is a fast operation, so always worthwhile to creating PNG from
        large export PDF files.
        In case the source is a PDF, then use self.index to request for the page.
        # TODO: Add clipPath and filter as parameters.
        """
        if self.path is None or not self.scaleImage:
            return
        if not self.iw or not self.ih: # Make sure image exists and not zero, to avoid division
            print('Image.scaleImage: %dx%d zero size for image "%s"' % (self.iw, self.ih, self.path))
            return
        extension = path2Extension(self.path)
        resolutionFactor = self.resolutionFactors.get(extension, 1)
        # Translate the extension to the related type of output.
        exportExtension = CACHE_EXTENSIONS.get(extension, extension)
        
        resW = self.w * resolutionFactor
        resH = self.h * resolutionFactor

        sx, sy = upt(resW / self.iw, resH / self.ih)

        if self.proportional: 
            sx = sy = max(sx, sy)
            
        if not self.scaleImage and self.cacheScaledImageFactor <= sx and self.cacheScaledImageFactor <= sy: 
            # If no real scale reduction, then skip. Never enlarge.
            return
        # Scale the image the cache does not exist already.
        # A new path is saved for the scaled image file. Reset the (self.iw, self.ih)
        self.path = self.context.scaleImage(
            path=self.path.lower(), w=resW, h=resH, index=self.index,
            showImageLoresMarker=self.showImageLoresMarker or view.showImageLoresMarker,
            exportExtension=exportExtension
        )

    def prepare_html(self, view):
        """Respond to the top-down element broadcast to prepare for build_html.
        If the original image needs scaling, then prepare the build by letting the context
        make a new cache file with the scaled images.
        If the cache file already exists, then ignore, just continue the broadcast
        towards the child elements.
        """
        self.scaleImage(view)
        for e in self.elements:
            e.prepare_html(view)

    def build_html(self, view, path, drawElements=True):
        context = view.context # Get current context.
        b = context.b

        # Use self.cssClass if defined, otherwise self class. #id is ignored if None
        b.div(cssClass=self.cssClass or self.__class__.__name__.lower(), cssId=self.cssId)

        if self.drawBefore is not None: # Call if defined
            self.drawBefore(self, view)

        b.img(src=self.path, alt=self.alt)

        b.div(cssClass='caption') # Allow CSS to address the captions separately.
        if drawElements: # Draw captions if they are there.
            for e in self.elements:
                e.build_html(view, path)
        b._div() # .caption

        if self.drawAfter is not None: # Call if defined
            self.drawAfter(self, view)

        b._div() # self.cssClass or self.__class__.__name__

    def build_flat(self, view, origin=ORIGIN, drawElements=True):
        print('[%s.build_flat] Not implemented yet' % self.__class__.__name__)

    def prepare(self, view):
        """Respond to the top-down element broadcast to prepare for build.
        If the original image needs scaling, then prepare the build by letting the context
        make a new cache file with the scaled images.
        If the cache file already exists, then ignore, just continue the broadcast
        towards the child elements.
        """
        self.scaleImage(view)
        for e in self.elements:
            e.prepare(view)

    def build(self, view, origin=ORIGIN, drawElements=True):
        """Draw the image in the calculated scale. Since we need to use the
        image by scale transform, all other measure (position, lineWidth) are
        scaled back to their original proportions.

        If stroke is defined, then use that to draw a frame around the image.
        Note that the (sx, sy) is already scaled to fit the padding position
        and size."""

        context = self.context # Get current context and builder.
        b = context.b # This is a bit more efficient than self.b once we got context

        p = pointOffset(self.origin, origin)
        p = self._applyScale(view, p)
        px, py, _ = p = self._applyAlignment(p) # Ignore z-axis for now.

        self._applyRotation(view, p)

        if self.path is None or not os.path.exists(self.path) or not self.iw or not self.ih:
            # TODO: Also show error, in case the image does not exist, to differentiate from empty box.
            if self.path is not None and not os.path.exists(self.path):
                print('Warning: cannot find image file %s' % self.path)
            # Draw missing element as cross
            xpt, ypt, wpt, hpt = upt(px, py, self.w, self.h)
            context.stroke(0.5)
            context.strokeWidth(0.5)
            context.fill(None)
            context.rect(xpt, ypt, wpt, hpt)
            context.line((xpt, ypt), (xpt+wpt, ypt+hpt))
            context.line((xpt+wpt, ypt), (xpt, ypt+hpt))
        else:
            context.save()
            # Check if scaling exceeds limit, then generate a cached file and update the path
            # and (self.iw, self.ih) accordingly.

            sx = self.w / self.iw
            sy = self.h / self.ih
            context.scale(sx, sy)

            # If there is a clipRect defined, create the bezier path
            """
            if self.clipPath is not None:
                clipRect = context.newPath()
                clX, clY, clW, clH = upt(self.clipRect)
                sclX = clX/sx
                sclY = clY/sx
                sclW = clW/sx
                sclH = clH/sy
                # move to a point
                clipRect.moveTo((sclX, sclY))
                # line to a point
                clipRect.lineTo((sclX, sclY+sclH))
                clipRect.lineTo((sclX+sclW, sclY+sclH))
                clipRect.lineTo((sclX+sclW, sclY))
                # close the path
                clipRect.closePath()
                # set the path as a clipping path
                b.clipPath(clipRect)
                # the image will be clipped inside the path
                #b.fill(0, 0, 0.5, 0.5)
                #b.drawPath(clipRect)
            elif self.clipPath is not None:
                #Otherwise if there is a clipPath, then use it.
                b.clipPath(self.clipPath)
            """
            if self.imo is not None:
                with self.imo:
                    b.image(self.path, (0, 0), pn=1, alpha=self._getAlpha())
                b.image(self.imo, upt(px/sx, py/sy), pageNumber=self.index, alpha=self._getAlpha())
            else:
                #print(self.x, self.y, self.w, self.h, self.iw, self.ih, px, py, sx, sy, px/sx, py/sy)
                #b.image(self.path, (upt(px)/sx+100, upt(py)/sy+100), pageNumber=self.index, alpha=self._getAlpha())
                b.image(self.path, upt(px/sx, py/sy), pageNumber=self.index, alpha=self._getAlpha())
            # TODO: Draw optional (transparant) forground color?

            context.restore()

        self.buildFrame(view, p) # Draw optional frame or borders.

        #if drawElements:
        #    self.buildChildElements(view, p)

        self._restoreRotation(view, p)

        self._restoreScale(view)
        view.drawElementInfo(self, origin)

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
