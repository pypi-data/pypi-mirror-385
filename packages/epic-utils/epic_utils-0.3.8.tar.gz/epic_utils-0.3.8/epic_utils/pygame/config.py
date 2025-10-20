from ..core import Color

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
pg.font.init()


class PygameConfig:
    DEBUGFONT = pg.font.SysFont("Arial", 20)
    DEBUGFONTCOLOR = Color(255,255,255)