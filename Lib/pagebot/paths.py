#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#     www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#
#     Supporting DrawBot, www.drawbot.com
#     Supporting Flat, xxyxyz.org/flat
# -----------------------------------------------------------------------------
#
#     paths.py
#
#
#    NOTE: should stay at root level, else derived path won't be correct.

ROOT_PATH = '/'.join(__file__.split('/')[:-1])
RESOURCES_PATH = ROOT_PATH + '/resources'
DEFAULT_FONT_PATH = RESOURCES_PATH + '/testfonts/google/roboto/Roboto-Regular.ttf'
