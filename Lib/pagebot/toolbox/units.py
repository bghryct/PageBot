#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
#     units.py
#
#     Implements basic intelligent spacing units with build-in conversions.
#
#     units, Units # Basic contextual converter and interpretor
#
#     Absolute units
#     Millimeters MM = 0.0393701 * INCH
#     mm, Mm       Millimeters
#     p, P         Picas 1/6"
#     pt, Pt       Points 1/72"
#     inch, Inch 
#
#     Relative units, using base and gutter as reference
#     em, Em       Relative to e.fontSize as base
#     perc, Perc   Relative to 100%
#     fr, Fr       Fraction columns for CSS-grid, without gutter
#     col, Col     Same as fr, using gutter. Works vertical as rows as well.
#     px, Px       Equal to points (for now)

from __future__ import division # Make integer division result in float.

import re
import sys
from copy import copy
from pagebot.toolbox.transformer import asNumberOrNone, asFormatted, asIntOrFloat

# max/max values for element sizes. Makes sure that elements dimensions never get 0
XXXL = sys.maxsize

INCH = 72
MM = 0.0393701 * INCH # Millimeters as points. E.g. 3*MM --> 8.5039416 pt.

# Basic layout measures
U = 6 # Some basic unit grid to use as default.
EM_FONT_SIZE = U*2 # 12pt
BASELINE_GRID = U*2+3 # 2.5U = 15pt 

def ru(uu, *args, **kwargs):
    u"""Render to uu.r or (u1.r, u2.r, ...) if uu is a list or tuple.
    If maker is defined, then use that to render towards.

    >>> ru(pt(100), pt(120))
    (100, 120)
    >>> ru(pt(100), 121, (p(5), p(6), units('5"')), maker=pt)
    (100, 121, (60, 72, 360))
    """
    maker = kwargs.get('maker')
    if not isinstance(uu, (list, tuple)):
        uu = [uu]
    if args:
        uu += args
    ruu = []
    for u in uu:
        if isinstance(u, (list, tuple)):
            ruu.append(ru(u, maker=maker))
        elif maker is not None:
            ruu.append(units(u, maker=maker).r)
        else:
            ruu.append(u.r)
    return tuple(ruu)

def isUnit(u):
    u"""Answer the boolean flag is u is a Unit instance.

    >>> isUnit(Em(2))
    True
    >>> isUnit(2)
    False
    """
    # isinstance(u, Unit) # Does not seem to work right for units created in other sources such as A4
    return hasattr(u, '_v') and hasattr(u, 'base')

def uRound(u):
    u"""Anwer a unit with rounded value. Or the rounded value if u is not a Unit instance.

    >>> uRound(u = Em(3.2))
    3em
    >>> uRound(4.2)
    4
    """
    if isUnit(u):
        return u.round()
    return int(round(u))

def classOf(u):
    u"""Answer the class of the Unit instance. Otherwise answer None.

    >>> u = Em(2)
    >>> classOf(u) is Em
    True
    """
    if isUnit(u):
        return u.__class__
    return None

def uString(u, maker=None):
    u"""Answer the unit u as string. In case it is not a Unit instance, convert to Unit first.

    >>> u = Em(2)
    >>> uString(u)
    '2em'
    >>> uString(2, fr) # Maker function works
    '2fr'
    >>> uString(2, Inch) # Unit class works
    '2"'
    """
    return str(units(u, maker))

us = uString # Convenience abbreviaion

def uValue(u):
    u"""Answer the clipped value of u. Otherwise use u. Convert to int if whole number.

    >>> uValue(3)
    3
    >>> uValue(Pt(10))
    10
    >>> uValue(Em(2, min=10, max=20))
    10
    """
    if isUnit(u):
        u = u.v
    return asIntOrFloat(u)

uv = uValue # Convenience abbreviaion

def rValue(u):
    u"""Answer the clipped and rendered value of u. Otherwise use u. Convert to int if whole number."""
    if isUnit(u):
        u = u.r
    return asIntOrFloat(u)

rv = rValue # Convenience abbreviaion

class Unit(object):
    u"""Base class for units, implementing most of the logic.
        Unit classes can be absolute (Pt, Px, Pica/P, Mm, Inch) and relative, which need the definintion of a
        base reference value (Perc, Fr) or em (Em).

        >>> mm(1)
        1mm
        >>> mm(10) * 8
        80mm
        >>> fr(2) * 3
        6fr
        >>> px(5) + 2
        7px
        >>> perc(20) + 8
        28%
        >>> perc(12.4) * 2
        24.8%
        >>> u = perc(15) + 5
        >>> u
        20%
        >>> u.base = pt(440)
        >>> u, u.r # Respectively: instance to str, rendered to u.base
        (20%, 88pt)
        >>> # 3 + px(3) # Gives error. 
        >>> px(3) + 3
        6px
        >>> px(12) + px(10)
        22px
        >>> mm(10) + px(1)
        10.35mm
        >>> (mm(10) + mm(5)) * 2
        30mm
        >>> inch(4)
        4"
        >>> inch(4).pt # Convert inches to point value
        288
        >>> pt(inch(4)) # Convert inches to point unit
        288pt
        >>> isUnit(mm(2))
        True
        >>> isUnit(2)
        False
        >>> x, y = pt(100, 300) # Creating list of pt as batch
        >>> x.pt, y.pt
        (100, 300)
        >>> x, (y, z) = pt(100, (150, 300)) # Creating nested list of pt as batch
        >>> x.pt, y.pt, z.pt
        (100, 150, 300)
        >>> x, (y, z) = pt(100, (150, 300), min=200, max=250) # Creating nested list of pt as batch with generic min/max
        >>> x.pt, y.pt, z.pt
        (200, 200, 250)
        >>> u = units('100mm', min=10, max=30)
        >>> u._v, u.v, u.r, u # Respectively: Raw value, clipped to min/max, clipped and rendered (in case relative), clipped unit instance as str.
        (100, 30, 30, 30mm)
        >>> us(20) # Convert to unit string, default for number is pt
        '20pt'
        >>> us(pt(20)) # Value can be Unit instance
        '20pt'
        >>> us(20, mm) # Usage of a maker function (all lc)
        '20mm'
        >>> us(20, 'mm') # Or can be string name of maker function (caps or lc)
        '20mm'
        >>> us(20, 'MM') # Or can be string name of maker function (caps or lc)
        '20mm'
        >>> us(20, Mm) # Or can be real class (initial cap)
        '20mm'
    """
    BASE = None # Default "base reference for relative units. Unused None for absolute units."

    isAbsolute = True
    isRelative = False
    isEm = False

    def __init__(self, v=0, base=None, g=0, min=None, max=None):
        assert isinstance(v, (int, float)) # Otherwise do a cast first as pt(otherUnit)
        self._v = v
        # Base can be a unit value, ot a dictionary, where self.UNIT is the key.
        # This way units(...) can decide on the type of unit, where the base has multiple entries.
        if base is None:
            base = self.BASE
        self.base = base # Default base value for reference by relative units.
        self.g = g # Default gutter for reference by relative units. Ignored by absolute units.
        self.min = min # Used when rendered towards pt or clipped.
        self.max = max

    def _get_min(self):
        return self._min
    def _set_min(self, min):
        if isinstance(min, str):
            min = units(min)
        if isUnit(min):
            min = min.pt
        if min is None: 
            min = -XXXL
        self._min = min
    min = property(_get_min, _set_min)

    def _get_max(self):
        return self._max
    def _set_max(self, max):
        if isinstance(max, str):
            max = units(max)
        if isUnit(max):
            max = max.pt
        if max is None:
            max = XXXL
        self._max = max
    max = property(_get_max, _set_max)  

    def _get_uName(self):
        return self.__class__.__name__
    uName = property(_get_uName)

    def round(self):
        u"""Answer a new instance of self with rounded value.

        >>> u = pt(12.2)
        >>> ru = u.round()
        >>> u, ru # Did not change original
        (12.2pt, 12pt)
        """
        u = copy(self)
        u._v = int(round(self._v))
        return u
        
    def __repr__(self):
        v = asIntOrFloat(self.v) # Clip to min/max.
        if isinstance(v, int):
            return '%d%s' % (v, self.uName.lower())
        return '%s%s' % (asFormatted(v), self.uName.lower())

    def _get_pt(self):
        u"""Answer the clipped value in pt. Base value for absolute unit values is ignored.

        >>> p(1).pt
        12
        >>> pt(1), pt(1).pt
        (1pt, 1)
        >>> 10 + inch(1).pt + 8 # Rendered to a number
        90
        >>> mm(1).pt
        2.8346472
        >>> inch(1).pt
        72
        """
        return asIntOrFloat(self.v * self.PT_FACTOR) # Factor to points
    def _set_pt(self, v):
        self._v = v / self.PT_FACTOR
    pt = property(_get_pt, _set_pt) 

    def _get_px(self):
        u"""Answer the clipped value in px. Base value for absolute unit values is ignored.

        >>> p(1).px
        12
        >>> px(1), px(1).pt
        (1px, 1)
        >>> 10 + inch(1).pt + 8 # Rendered to a number
        90
        >>> mm(1).pt
        2.8346472
        """
        return px(self.pt).v
    px = property(_get_px)
    
    def _get_inch(self):
        return inch(self.pt).v
    inch = property(_get_inch)

    def _get_p(self):
        return p(self.pt).v
    p = property(_get_p)
        
    def _get_v(self):
        u"""Answer the raw unit value, clipped to the self.min and self.max local values.
        For absolute inits u.v and u.r are identical.
        For relative units u.v answers the clipped value and u.r answers the value rendered by u.base

        >>> u = Inch(2)
        >>> u.v
        2
        >>> u.min = 10
        >>> u.max = 20
        >>> u.v
        10
        """
        return min(self.max, max(self.min, self._v))
    def _set_v(self, v):
        u"""Set the raw unit value.

        >>> u = Inch(2)
        >>> u.v = 3
        >>> u, u.v
        (3", 3)
        """
        self._v = v
    v = property(_get_v, _set_v)
    r = property(_get_v) # Read only

    def __abs__(self):
        u"""Answer the an absolute value copy of self.

        >>> abs(units('-10pt'))
        10pt
        >>> abs(mm(-1000))
        1000mm
        """
        u = copy(self)
        u.v = abs(u.v)
        return u

    def __eq__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v == u
        if isinstance(u, self.__class__):
            return self._v == u.v
        return self.pt == u.pt # Incompatible unit types, compare via points

    def __ne__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v != u
        if isinstance(u, self.__class__):
            return self._v != u.v
        return self.pt != u.pt # Incompatible unit types, compare via points

    def __le__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v <= u
        if isinstance(u, self.__class__):
            return self._v <= u.v
        return self.pt <= u.pt # Incompatible unit types, compare via points

    def __lt__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v < u
        if isinstance(u, self.__class__):
            return self._v < u.v
        return self.pt < u.pt # Incompatible unit types, compare via points

    def __ge__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v >= u
        if isinstance(u, self.__class__):
            return self._v >= u.v
        return self.pt >= u.pt # Incompatible unit types, compare via points

    def __gt__(self, u):
        if isinstance(u, (int, float)): # One is a scalar, just compare
            return self._v > u
        if isinstance(u, self.__class__):
            return self._v > u.v
        return self.pt > u.pt # Incompatible unit types, compare via points

    def __add__(self, u):
        u"""Add self to u, creating a new Unit instance with the same type as self.

        >>> u = units('10pt')
        >>> u + 20 # Create a new Unit instance of the same type
        30pt
        >>> u + mm(10) # Add another type of unit
        38.35pt
        >>> u = p(2)
        >>> u + 1, u + pt(1) # Numbers are interpeted as adding picas. Otherwise use pt(1)
        (3p, 2p1)
        """
        u0 = copy(self) # Keep values of self
        if isinstance(u, (int, float)): # One is a scalar, just add
            u0.v += u
        elif u0.__class__ == u.__class__:
            u0.v += u.v # Same class, just add
        elif isUnit(u):
            u0.pt += u.pt # Adding units, calculate via points
        else:
            raise ValueError('Cannot Add "%s" by "%s"' % (self, u))
        return u0

    def __sub__(self, u):
        u"""Subract u from self, creating a new Unit instance with the same type as self.

        >>> u = units('50pt')
        >>> u - 20 # Create a new Unit instance of the same type
        30pt
        >>> u - mm(10) # Subtract another type of unit
        21.65pt
        """
        u0 = copy(self) # Keep values of self
        if isinstance(u, (int, float)): # One is a scalar, just subtract
            u0.v -= u
        elif u0.__class__ == u.__class__:
            u0.v -= u.v # Same class, just subtract
        elif isUnit(u):
            u0.pt -= u.pt # Subtracting units, calculate via points
        else:
            raise ValueError('Cannot Subtract "%s" by "%s"' % (self, u))
        return u0

    def __div__(self, u):
        u"""Divide self by u, creating a new Unit instance with the same type as self.
        Unit / Unit creates a float number.

        >>> u = units('60pt')
        >>> u / 2 # Create a new Unit instance of the same type
        30pt
        >>> asFormatted(u / mm(1.5)) # Unit / Unit create ratio float number
        '14.11'
        >>> u / units('120pt') # Unit / Unit create a float ratio number.
        0.5
        """
        u0 = copy(self) # Keep values of self
        if isinstance(u, (int, float)): # One is a scalar, just divide
            assert u, ('Zero division "%s/%s"' % (u0, u))
            u0.v /= u
        elif isUnit(u):
            upt = u.pt
            assert upt, ('Zero division "%s/%s"' % (u0, u))
            u0 = u0.pt / upt # Dividing units, create ratio float number.
        else:
            raise ValueError('Cannot divide "%s" by "%s"' % (u0, u))
        return u0

    __truediv__ = __div__

    def __mul__(self, u):
        u"""Multiply self by u, creating a new Unit instance with the same type as self.
        Units can only be multiplied by numbers.
        Unit * Unit raises a ValueError.

        >>> u = units('60pt')
        >>> u / 2 # Create a new Unit instance of the same type
        30pt
        >>> asFormatted(u / mm(1.5)) # Unit / Unit create ratio float number
        '14.11'
        >>> u / units('120pt') # Unit / Unit create a float ratio number.
        0.5
        """
        u0 = copy(self) # Keep values of self
        if isinstance(u, (int, float)): # One is a scalar, just multiply
            u0.v *= u
        else:
            raise ValueError('Cannot multiply "%s" by "%s"' % (u0, u))
        return u0

    def __neg__(self):
        return self.__class__(-self._v)

#   Mm

def mm(v, *args, **kwargs):
    u = None
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(mm(uv, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float)):
        u = Mm(v, min=minV, max=maxV)
    elif isUnit(v):
        u = Mm(min=minV, max=maxV) # New Mm and convert via pt
        u.pt = v.pt
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Mm.UNIT):
            v = asNumberOrNone(v[:-2])
            if v is not None:
                u = Mm(v, min=minV, max=maxV)
        else: # Something else, try again.
            u = mm(units(v), min=minV, max=maxV)
    return u

class Mm(Unit):
    u"""Answer the mm instance.

    >>> u = Mm(210)
    >>> u
    210mm
    >>> u = mm('297mm') # A4
    >>> u
    297mm
    >>> u/2
    148.5mm
    >>> u-100
    197mm
    >>> u+100
    397mm
    >>> u.v # Raw value of the Unit instance
    297
    >>> isinstance(u.v, (int, float))
    True
    >>> round(u.pt) # Rounded A4 --> pts
    842.0
    >>> mm(10, 11, 12) # Multiple arguments create a list of tuple mm
    (10mm, 11mm, 12mm)
    >>> mm((10, 11, 12, 13)) # Arguments can be submitted as list or tuple
    (10mm, 11mm, 12mm, 13mm)
    >>> mm(pt(5), p(6), '3"') # Arguments can be a list of other units types.
    (1.76mm, 25.4mm, 76.2mm)
    """
    PT_FACTOR = MM # mm <---> points
    UNIT = 'mm'

    def _get_mm(self):
        return self.v
    mm = property(_get_mm)

#   Pt

def pt(v, *args, **kwargs):
    u = None
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(pt(uv, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float)): # Simple value as input, use class
        u = Pt(v, min=minV, max=maxV)
    elif isUnit(v): # It's already a Unit instance, convert via points.
        u = Pt(v.pt, min=minV, max=maxV)
    elif isinstance(v, str): # Value is a string, interpret from unit extension.
        v = v.strip().lower()
        if v.endswith(Pt.UNIT):
            v = asNumberOrNone(v[:-2])
            if v is not None:
                u = Pt(v, min=minV, max=maxV)
        else: # Something else, recursively try again.
            u = pt(units(v), min=minV, max=maxV)
    return u

class Pt(Unit):
    u"""pt is the base unit size of all PageBot measures.

    >>> Pt(6) # Create directly as class, only takes numbers or Unit instances
    6pt
    >>> pt(6) # Create through interpreting values (int, float, Unit, str)
    6pt
    >>> pt('6pt') 
    6pt
    >>> u = units('6pt') # unit function auto-detects matching unit class.
    >>> u
    6pt
    >>> u/2
    3pt
    >>> u-1
    5pt
    >>> pt(12).pt
    12
    >>> u = pt(12)
    >>> u.pt = 120
    >>> u
    120pt
    >>> pt(10, 11, 12) # Multiple arguments create a list of tuple pt
    (10pt, 11pt, 12pt)
    >>> pt((10, 11, 12, 13)) # Arguments can be submitted as list or tuple
    (10pt, 11pt, 12pt, 13pt)
    >>> pt(mm(5), p(6)) # Arguments can be a list of other units types.
    (14.17pt, 72pt)
    >>> pt('11"', '12"') # Arguments interpreted from other unit type string.
    (792pt, 864pt)
    >>> pt(10, 12, 13, (20, 21)) # Nested lists, created nested list of pt
    (10pt, 12pt, 13pt, (20pt, 21pt))
    """
    PT_FACTOR = 1 # pt <--> pt factor
    UNIT = 'pt'

    def _get_pt(self):
        return self.v
    def _set_pt(self, v):
        self.v = v
    pt = property(_get_pt, _set_pt)

#   P(ica)

def p(v, *args, **kwargs):
    u"""Create a new instance of P, using v as source value. In case v is already 
    a Unit instance, then convert to that P needs, through the amount of points.

    >>> p(20)
    20p
    >>> p('20p6')
    20p6
    >>> p(pt(72)), p(pt(73)), p(pt(73.5)), p(pt(73.55)), p(pt(73.555))
    (6p, 6p1, 6p1.5, 6p1.55, 6p1.56)
    >>> p('0p1000')
    83p4
    >>> p(mm(3)) # Argument can be another Unit instance.
    0p8.5
    >>> p(123.88)
    123p10.56
    >>> p(inch(1))
    6p
    >>> p(inch(1.5))
    9p
    >>> p(inch(1.6))
    9p7.2
    >>> p(pt(36))
    3p
    >>> pica(20)
    20p
    >>> units('p6')
    0p6
    >>> p(10, 11, 12) # Multiple arguments create a list of tuple p
    (10p, 11p, 12p)
    >>> p((10, 11, 12, 13)) # Arguments can be submitted as list or tuple
    (10p, 11p, 12p, 13p)
    >>> p(mm(5), pt(24), inch(5)) # Arguments can be a list of other units types.
    (1p2.17, 2p, 30p)
    >>> p('10pt', '1"', '1.5"', units('1.5"')+3) # Arguments can be a list of other units types.
    (0p10, 6p, 9p, 27p)
    >>> p(10, 12, 13, (20, 21)) # Nested lists, created nested list of p
    (10p, 12p, 13p, (20p, 21p))
    """
    u = None
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(p(uv, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float)):
        u = P(v, min=minV, max=maxV)
    elif isUnit(v):
        u = P(min=minV, max=maxV) # Make new Pica and convert via pt
        u.pt = v.pt 
    elif isinstance(v, str):
        v = v.strip().lower().replace('pica', P.UNIT)
        if not 'pt' in v: # Hack to avoid confusion with '10pt')
            vv = VALUE_PICA.findall(v)
            if vv:
                v0 = asNumberOrNone(vv[0][0] or '0')
                v1 = asNumberOrNone(vv[0][1][1:] or '0')
                if v0 is not None and v1 is not None:
                    u = P(min=minV, max=maxV)
                    u.pt = v0*P.PT_FACTOR+v1
            else:
                u = p(units(v, min=minV, max=maxV))
        else: # Something else, recursively try again.
            u = p(units(v), min=minV, max=maxV)
    return u

class P(Unit):
    u"""P (pica) class.

    >>> u = P(2)
    >>> u.v
    2
    >>> u = p(1)
    >>> u, u+2, u+pt(2), u+pt(100), u*5, u/2
    (1p, 3p, 1p2, 9p4, 5p, 0p6)
    >>> p('2.8p')
    2p9.6
    """
    PT_FACTOR = 12  # 12 points = 1p
    UNIT = 'p'

    def _get_p(self):
        return self.v
    p = property(_get_p)

    def __repr__(self):
        v0 = int(self.v * self.PT_FACTOR // self.PT_FACTOR)
        v1 = asIntOrFloat((self.v - v0) * self.PT_FACTOR)
        if v1:
            if isinstance(v1, int):
                return '%dp%d' % (v0, v1)
            return '%dp%s' % (v0, asFormatted(v1))
        return '%dp' % v0

Pica = P
pica = p

#   Inch

def inch(v, *args, **kwargs):
    u = None
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(inch(uv))
        u = tuple(u)
    elif isinstance(v, (int, float)):
        return Inch(v, min=minV, max=maxV)
    elif isUnit(v):
        u = Inch(min=minV, max=maxV) # New Inch and convert via pt
        u.pt = v.pt 
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Inch.UNITC): # "-character
            v = asNumberOrNone(v[:-1])
            if v is not None:
                u = Inch(v, min=minV, max=maxV)
        elif v.endswith(Inch.UNIT):
            v = asNumberOrNone(v[:-4])
            if v is not None:
                u = Inch(v, min=minV, max=maxV)
        else: # Something else, recursively try again.
            u = inch(units(v), min=minV, max=maxV)
    return u

class Inch(Unit):
    u"""Inch 72 * the base unit size of all PageBot measures.

    >>> units('0.4"')
    0.40"
    >>> Inch(0.4)
    0.40"
    >>> inch('0.4"')
    0.40"
    >>> u = units('0.4inch')
    >>> u
    0.40"
    >>> u*2
    0.80"
    >>> u/2
    0.20"
    >>> u-0.1
    0.30"
    >>> inch(10, 11, 12) # Multiple arguments create a list of tuple inch
    (10", 11", 12")
    >>> inch((10, 11, 12, 13)) # Arguments can be submitted as list or tuple
    (10", 11", 12", 13")
    >>> inch(mm(5), pt(24), px(5)) # Arguments can be a list of other units types.
    (0.20", 0.33", 0.07")
    >>> inch('10pt', '11mm') # Arguments can interprete from strings of other units types.
    (0.14", 0.43")
    """
    PT_FACTOR = INCH # 72pt = 1"
    UNIT = 'inch' # Alternative is "
    UNITC = '"'

    def _get_inch(self):
        return self.v
    inch = property(_get_inch)

    def __repr__(self):
        v = asIntOrFloat(self.v)
        if isinstance(v, int):
            return '%d%s' % (self._v, self.UNITC)
        return '%0.2f%s' % (self._v, self.UNITC)

class Formula(Unit):
    u"""Unit class that contains a sequence of other units and rules how to apply them.
    This gives users the opportunity to combine absolute and relative measures.
    The API of a Formula instance is the same as with normal units.

    TODO: More rules to be added. Usage of labelled self.units dictionary.
    TODO: The Formula needs more thinking

    >>> f = Formula(f='addAll', units=[pt(10), pt(22)])
    >>> f.f
    'addAll'
    """
    PT_FACTOR = 1 # Formulas behave as points by default, but that can be changed.
    UNIT = 'f'

    def __init__(self, v=0, base=None, g=0, min=None, f=None, max=None, units=None):
        Unit.__init__(self, v=v, base=base, g=g, min=min, max=max)
        self.f = f
        if units is None:
            units = {}
        self.units = units # Key is id, value is unit

    def addAll(self):
        result = None
        for unitId, unit in self.units.items():
            if result is None:
                result = copy(unit)
            else:
                result += unit
        return result


#   Relative Units (e.g. for use in CSS)

class RelativeUnit(Unit):
    u"""Abstract class to avoid artihmetic between absolute and relative units.
    Needs absolute reference to convert to absolute units.

    >>> u = units('12%')
    >>> 
    """
    BASE = 1 # Default "base reference for relative units."
    GUTTER = U*2 # Used as default gutter measure for Col units.
    BASE_KEY = 'base' # Key in optional base of relative units.
    isAbsolute = False # Cannot do arithmetic with absolute Unit instances.
    isRelative = True

    def _get_r(self):
        u"""Answer the rendered clipped value, clipped to the self.min and self.max local values.
        For absolute inits u.v and u.r are identical.
        For relative units u.v answers the clipped value and u.r answers the value rendered by self.base.
        self.base can be a unit or a number.

        >>> u = Inch(2)
        >>> u.v
        2
        >>> u.min = 10
        >>> u.max = 20
        >>> u.v
        10
        """
        return self.base * self.v / self.BASE
    r = property(_get_r)

    def _get_pt(self):
        u"""Answer the rendered value in pt. 

        >>> u = fr(2, base=12)
        >>> u, u.pt
        (2fr, 6)
        """
        return asIntOrFloat(pt(self.r).v) # Clip rendered value to min/max and factor to points
    pt = property(_get_pt) 

    def _get_mm(self):
        u"""Answer the rendered value in mm. 

        >>> u = fr(2, base=mm(10))
        >>> u, u.mm, mm(u)
        (2fr, 5, 5mm)
        """
        return asIntOrFloat(mm(self.r).v) # Clip rendered value to min/max and factor to mm
    mm = property(_get_mm) 

    def _get_p(self):
        u"""Answer the rendered value in picas. 

        >>> u = fr(2, base=p(12))
        >>> u, u.p
        (2fr, 6)
        >>> u = units('75%', base=p(72))
        >>> u, u.p, p(u)
        (75%, 54, 4p6)
        """
        return asIntOrFloat(p(self.r).v) # Clip rendered value to min/max and factor to mm
    p = property(_get_p) 

    def _get_inch(self):
        u"""Answer the rendered value in inch. 

        >>> fr(2, base='4"').inch
        2
        >>> fr(2, base=inch(10)).inch
        5
        >>> units('25%', base=inch(10)).inch
        2.5
        """
        return asIntOrFloat(inch(self.r).v) # Clip rendered value to min/max and factor to mm
    inch = property(_get_inch) 

    def _get_base(self):
        u"""Optional base value as reference for relative units. Save as Unit instance.

        >>> u = units('20%', base=pt(200))
        >>> u.base
        200pt
        >>> u.pt # 20% for 200pt
        40
        >>> u = units('5em', base=dict(em=pt(12), perc=pt(50)))
        >>> u.pt # Rendered to base selection pt(12)
        60
        """
        if isinstance(self._base, dict):
            return self._base[self.BASE_KEY]
        return self._base
    def _set_base(self, base):  
        if isinstance(base, dict):
            assert self.BASE_KEY in base
        elif not isinstance(base, dict) and not isUnit(base):
            base = units(base)
        self._base = base
    base = property(_get_base, _set_base)

    def _get_g(self):
        u"""Optional gutter value as reference for relative units. Save as Unit instance.

        >>> u = col(0.25, base=mm(200), g=mm(8))
        >>> u.base
        200mm
        >>> u.mm # (200 + 8)/4 - 8 --> 44 + 8 + 44 + 8 + 44 + 8 + 44 = 200 
        44
        >>> from pagebot.constants import A4
        >>> margin = 15
        >>> u = col(0.5, base=A4[0]-2*margin, g=mm(8))
        >>> u, u.r
        (0.5col, 86mm)
        """
        return self._g
    def _set_g(self, g):  
        if not isUnit(g):
            g = units(g)
        self._g = g
    g = property(_get_g, _set_g)

#   Px

def px(v, *args, **kwargs):
    u = None
    base = kwargs.get('base', Px.BASE)
    g = kwargs.get('g', 0) # Not used by Px
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(px(uv, base=base, g=g, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float, RelativeUnit)):
        u = Px(v, base=base, g=g, min=minV, max=maxV)
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Px.UNIT):
            v = asNumberOrNone(v[:-2])
            if v is not None:
                u = Px(v, base=base, g=g, min=minV, max=maxV)
        else: # Something else, recursively try again
            u = units(v, base=base, g=g, min=minV, max=maxV)
            assert isinstance(u, Px) # Only makes sense for relative if the same.
    return u

class Px(RelativeUnit):
    u"""Answer the px (pixel) instance.

    >>> Px(12) # Direct creation of class instance, only for (int, float, Unit)
    12px
    >>> px(12) # Through creator function
    12px
    >>> px('12px') # Through creator function, strings are interpreted (int, float, Unit, str)
    12px
    >>> u = units('12px')
    >>> u
    12px
    >>> u/2 # Math on Unit create new Unit instance of same type.
    6px
    >>> u-1
    11px
    >>> u.pt # Answer pt value, assuming here an 1:1 conversion
    12
    """
    PT_FACTOR = 1 # This may not always be 1:1 to points.
    UNIT = 'px'

    def _get_px(self):
        return self.v
    px = property(_get_px)

#   Fr

def fr(v, *args, **kwargs):
    u = None
    base = kwargs.get('base', Fr.BASE)
    g = kwargs.get('g', 0) # Not used by Fr
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(fr(uv, base=base, g=g, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float, RelativeUnit)):
        u = Fr(v, base=base, g=g, min=minV, max=maxV)
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Fr.UNIT):
            v = asNumberOrNone(v[:-2])
            if v is not None:
                u = Fr(v, base=base, g=g, min=minV, max=maxV)
        else: # Something else, recursively try again
            u = units(v, base=base, g=g, min=minV, max=maxV)
            assert isinstance(u, Fr) # Only makes sense for relative if the same.
    return u

class Fr(RelativeUnit):
    u"""fractional units, used in CSS-grid.
    https://gridbyexample.com/video/series-the-fr-unit/

    >>> units('5fr')
    5fr
    >>> fr(5)
    5fr
    >>> u = units('4fr', base=100)
    >>> u.isEm, u.isRelative
    (False, True)
    >>> u
    4fr
    >>> u/2
    2fr
    >>> u-0.5
    3.5fr
    >>> u.base = 100
    >>> u, pt(u) # Answer fr value as points, relative to base master value.
    (4fr, 25pt)
    """
    UNIT = 'fr'

    def _get_r(self):
        u"""Answer the rendered clipped value, clipped to the self.min and self.max local values.
        For absolute inits u.v and u.r are identical.
        For relative units u.v answers the clipped value and u.r answers the value rendered by self.base
        self.base can be a unit or a number.

        >>> u = Fr(2)
        >>> u.v
        2
        >>> u.min = 10
        >>> u.max = 20
        >>> u.v
        10
        """
        return self.base / self.v
    r = property(_get_r)

#   Col

def col(v, *args, **kwargs):
    u = None
    base = kwargs.get('base', Col.BASE)
    g = kwargs.get('g', Col.GUTTER)
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(col(uv, base=base, g=g, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float, RelativeUnit)):
        u = Col(v, base=base, g=g, min=minV, max=maxV)
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Col.UNIT):
            v = asNumberOrNone(v[:-3])
            if v is not None:
                u = Col(v, base=base, g=g, min=minV, max=maxV)
        else: # Something else, recursively try again
            u = units(v, base=base, g=g, min=minV, max=maxV)
            assert isinstance(u, Col) # Only makes sense for relative if the same.
    return u

class Col(RelativeUnit):
    u"""Fraction of a width, including gutter calculation. Reverse of Fr.
    Gutter is default Col.GUTTER

    >>> units('0.25col')
    0.25col
    >>> col(1/2)
    0.5col
    >>> u = units('0.5col', base=100, g=8)
    >>> u.isEm, u.isRelative
    (False, True)
    >>> u
    0.5col
    >>> u/2
    0.25col
    >>> u-0.3
    0.2col
    >>> u.base = 500 # With of the column
    >>> u.g = 8
    >>> u, pt(u) # Answer col value as points, relative to base master value and gutter.
    (0.5col, 246pt)
    """
    UNIT = 'col'

    def _get_r(self):
        u"""Answer the rendered clipped value, clipped to the self.min and self.max local values.
        For absolute inits u.v and u.r are identical.
        For relative units u.v answers the clipped value and u.r answers the value rendered by self.base
        self.base can be a unit or a number.
        self.g can be a unit or a number

        >>> u = Col(1/2, base=mm(100), g=mm(4))
        >>> u.v
        0.5
        >>> u.r # (100 + 4)/2 - 4
        48mm
        """
        return (self.base + self.g) * self.v - self.g # Calculate the fraction of base, reduced by gutter
    r = property(_get_r)

#   Em

def em(v, *args, **kwargs):
    u = None
    base = kwargs.get('base', EM_FONT_SIZE)
    g = kwargs.get('g', 0) # Default not used by Em
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v: # Recursively append
            u.append(em(uv, base=base, g=g, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float, RelativeUnit)):
        u = Em(v, base=base, g=g, min=minV, max=maxV)
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Em.UNIT):
            v = asNumberOrNone(v[:-2])
            if v is not None:
                u = Em(v, base=base, g=g, min=minV, max=maxV)
        else: # Something else, recursively try again
            u = units(v, base=base, g=g, min=minV, max=maxV)
            assert isinstance(u, Em) # Only makes sense for relative if the same.
    return u

class Em(RelativeUnit):
    u"""Em size is based on the current setting of the fontSize.
    Used in CSS export.

    >>> units('10em')
    10em
    >>> Em(10)
    10em
    >>> u = units('10em')
    >>> u.isEm and u.isRelative
    True
    >>> u
    10em
    >>> u/2
    5em
    >>> u-8
    2em
    >>> u.base = 12 # Caller can set the base reference value
    >>> pt(u) 
    120pt
    >>> u.base = 24
    >>> pt(u)
    240pt
    >>> em(1, 2, 3, 4)
    (1em, 2em, 3em, 4em)
    """
    isEm = True
    UNIT = 'em'
    BASE_KEY = 'em' # Key in optional base of relative units.

    def _get_pt(self):
        u"""Answer the rendered value in pt. Base value for absolute unit values is ignored.
        self.base can be a unit or a number.

        >>> u = units('10em', base=12)
        >>> u, u.r
        (10em, 120pt)
        >>> u.base = 8 # Alter the base em. 
        >>> u # Full representation
        10em
        >>> u.base # Defined base for the em (often set in pt units)
        8pt
        >>> u.v # Clipped value of u._v
        10
        >>> u.r # Render to Pt instance
        80pt
        >>> u.pt # Render to points number
        80
        """
        return asIntOrFloat((self.base * self.v).v) # Clip to min/max and factor to points
    def _set_pt(self, v):
        self._v = v / self.base
    pt = property(_get_pt, _set_pt) 

#   Perc

def perc(v, *args, **kwargs):
    u"""Convert value v to a Perc instance or list or Perc instances. 

    >>> perc(12)
    12%
    >>> perc(12).base # Base unit value for percentage
    100pt
    >>> perc(12).v
    12
    >>> perc('10%', '11%', '12%', '13%')
    (10%, 11%, 12%, 13%)
    """
    u = None
    base = kwargs.get('base')
    g = kwargs.get('g', 0) # Default not used by Perc
    minV = kwargs.get('min')
    maxV = kwargs.get('max')
    if args: # If there are more arguments, bind them together in a list.
        v = [v]+list(args)
    if isinstance(v, (tuple, list)):
        u = []
        for uv in v:
            u.append(perc(uv, base=base, g=g, min=minV, max=maxV))
        u = tuple(u)
    elif isinstance(v, (int, float, RelativeUnit)):
        u = Perc(v, base=base, g=g, min=minV, max=maxV)
    elif isinstance(v, str):
        v = v.strip().lower()
        if v.endswith(Perc.UNITC): # %-character
            v = asNumberOrNone(v[:-1])
            if v is not None:
                u = Perc(v, base=base, g=g, min=minV, max=maxV)
        elif v.endswith(Perc.UNIT):
            v = asNumberOrNone(v[:-4])
            if v is not None:
                u = Perc(v, base=base, g=g, min=minV, max=maxV)
        else: # Something else, recursively try again
            u = units(v, base=base, g=g, min=minV, max=maxV)
            assert isinstance(u, Perc) # Only makes sense for relative if the same.
    return u

class Perc(RelativeUnit):
    u"""Answer the relative percentage unit, if parsing as percentage (ending with % order "perc").

    >>> units('100%')
    100%
    >>> perc(100)
    100%
    >>> Perc(100)
    100%
    >>> u = perc('100%')
    >>> u, u.r # Default base is 100pt
    (100%, 100pt)
    >>> u/2, (u/2).r # Render to base of 100pt
    (50%, 50pt)
    >>> u/10*2
    20%
    >>> u+21
    121%
    >>> u-30+0.51
    70.51%
    >>> units('66%', base=500).r # Render value towards base unit
    330pt
    >>> units('66%', base=mm(500)).r # Render value towards base unit
    330mm
    >>> Perc(1.2) + 1.2
    2.4%
    """
    BASE = 100 # Default "base reference for relative units."
    UNIT = 'perc'
    UNITC = '%'

    def __repr__(self):
        v = asIntOrFloat(self.v) # Clip to min/max 
        if isinstance(v, int):
            return u'%d%%' % v
        return u'%s%%' % asFormatted(v)


    def _get_pt(self):
        u"""Answer the rendered value in pt. Base value for absolute unit values is ignored.

        >>> u = units('10%', base=120)
        >>> u, pt(u)
        (10%, 12pt)
        >>> u.pt # Render to point int value
        12
        """
        return asIntOrFloat(self.base.v * self.v / self.BASE) # Clip to min/max and factor to points
    def _set_pt(self, v):
        self._v = v / self.base.v * self.BASE
    pt = property(_get_pt) 

UNIT_MAKERS = dict(px=px, pt=pt, mm=mm, inch=inch, p=p, pica=pica, em=em, fr=fr, col=col, perc=perc)
MAKER_UNITS = dict([[maker, unit] for unit, maker in UNIT_MAKERS.items()])
MAKERS = set((pt, px, mm, inch, p, em, fr, col, perc))
CLASS_MAKERS = {Pt:pt, Px:px, Mm:mm, Inch:inch, P:p, Pica:pica, Em:em, Fr:fr, Col:col, Perc:perc}

VALUE_UNIT = re.compile('[ \t]*([0-9.-]*)[ \t]*([a-zA-Z"%]*)[ \t]*')
UNIT_VALUE = re.compile('[ \t]*([a-zA-Z"%]*)[ \t]*([0-9.-]*)[ \t]*')
VALUE_PICA = re.compile('[ \t]*([0-9.-]*)[ \t]*(p[0-9.]*)[ \t]*')

def value2Maker(v):
    u"""Find maker function best matching v. If no unit/maker/class name can be found,
    then assume it is pt() requested. Answer the pair of (value, unitName).
    Otherwise answer None.

    >>> value2Maker('123pt') == pt
    True
    >>> value2Maker('123px') == px
    True
    >>> value2Maker('123') == pt
    True
    >>> value2Maker('123.45fr') == fr
    True
    >>> value2Maker('pt') == pt
    True
    >>> value2Maker(pt) == pt
    True
    >>> value2Maker(Pt) == pt
    True
    >>> value2Maker(Inch) == inch
    True
    >>> value2Maker(Col) == col
    True
    """
    maker = None
    if isinstance(v, (int, float)):
        maker = pt
    elif v in UNIT_MAKERS:
        maker = UNIT_MAKERS[v]
    elif v in CLASS_MAKERS:
        maker = CLASS_MAKERS[v]
    elif v in MAKERS:
        maker = v
    elif isUnit(v):
        maker = UNIT_MAKERS[V.UNIT]
    elif isinstance(v, str):
        v = v.lower()
        if v in UNIT_MAKERS:
            maker = UNIT_MAKERS[v]
        else:
            value, unit = VALUE_UNIT.findall(v)[0]
            if not value:
                unit, value = UNIT_VALUE.findall(v)[0]
            if value:
                if not unit:
                    unit = Pt.UNIT
                elif unit == Inch.UNITC: # '"'
                    unit = Inch.UNIT
                elif unit == Perc.UNITC: # '%'
                    unit = Perc.UNIT
            if unit in UNIT_MAKERS:                                                                                                                          
                maker = UNIT_MAKERS[unit]
    return maker

def units(v, maker=None, base=None, g=None, min=None, max=None):
    u"""If value is a string, then try to guess what type of units value is
    and answer the right instance. Answer None if not valid transformation could be done.

    >>> units('100%')
    100%
    >>> units('   80  perc  ') # Spaced are trimmed.
    80%
    >>> units('12pt')
    12pt
    >>> units('10"')
    10"
    >>> units('10 inch  ')
    10"
    >>> units('140mm')
    140mm
    >>> units('30pt')
    30pt
    >>> units('1.4em')
    1.4em
    >>> units('0.5col')
    0.5col
    >>> units(12) # Default for plain number is pt if no class defined.
    12pt
    >>> units('SomethingElse') is None
    True
    >>> units('12pt', 'mm') # Altering maker units converts.
    4.23mm
    >>> units(mm(12), pt) # Casting to another unit type
    34.02pt
    >>> u1 = units('10pt')
    >>> u1 is units(u1) # Creates copy of u1
    False
    """
    u = None
    makerF = value2Maker(maker)
    assert makerF is None or makerF in MAKERS, ('Cannot find unit maker for "%s"' % maker)

    if isUnit(v):
        if makerF in (None, UNIT_MAKERS[v.UNIT]):
            u = copy(v) # Make sure to copy, avoiding overwriting local values of units.
        else:
            u = makerF(v)
    elif v is not None:
        # Plain values are interpreted as point Units
        if makerF is None:
            makerF = value2Maker(v)        
        # makerF is now supposed to be a maker or real Unit class, use it
        if makerF:
            u = makerF(v, base=base, g=g, min=min, max=max)

    # In case we got a valid unit, then try to set the paremeters if not None.
    if u is not None:
        if base is not None: # Base can be unit or number.
            u.base = base # Recursive force base to be unit instance
        if g is not None: # Optional gutter can be unit or number
            u.g = g # Recursive force gutter to be unit instance.
    
    return u # If possible to create, answer u. Otherwise result is None


if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
