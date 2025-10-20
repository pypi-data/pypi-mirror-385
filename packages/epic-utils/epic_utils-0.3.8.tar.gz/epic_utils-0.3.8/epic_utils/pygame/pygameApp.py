from ..core import Vector2Int, Vector2, Color
from .config import PygameConfig
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg

class Application:
    def __init__(self, size : Vector2Int, title : str, updateFunction = None, fps_limit = 60, update_on_pause = False, eventHandler  = None):
        pg.init()
        self.info = pg.display.Info()
        self.size : Vector2Int = size
        self.title : str = title
        self.paused = False
        self.running = True
        self.clock = pg.time.Clock()
        self.fps = fps_limit
        self.display = pg.display.set_mode(self.size.toTuple())
        self.updateFunction = updateFunction
        self.update_on_pause = update_on_pause
        self.eventHandler = eventHandler
        pg.display.set_caption(self.title)
        self.debug = False
        
        #background init
        self.backgroundColor = Color(0,0,0)

    def setFPS(self, fps : int):
        """Set the FPS limit"""
        self.fps = fps
    
    def setDebug(self, debug : bool):
        """Set the debug mode"""
        self.debug = debug
        
    #Screen functions

    def setBGColor(self, color : Color):
        """Set the background color"""
        self.backgroundColor = color
    
    def clearScreen(self):
        """Clear the screen"""
        self.display.fill(self.backgroundColor.toTuple())    
        
        if self.debug:
            text = PygameConfig.DEBUGFONT.render(f"{int(self.clock.get_fps())}", True, PygameConfig.DEBUGFONTCOLOR.toTuple())  
            self.display.blit(text, (0,0))
            
    def fillScreen(self, color: Color, pos: Vector2Int, size: Vector2Int):
        self.display.fill(color.toTuple(), (pos.x, pos.y, size.x, size.y))
     
    def toggleFullScreen(self):
        """Toggle fullscreen"""
        pg.display.toggle_fullscreen()
        
    def setResizable(self, resizable : bool):
        """Set the window to be resizable"""
        flags = pg.RESIZABLE if resizable else 0
        self.display = pg.display.set_mode(self.size.toTuple(), flags)

    def setSize(self, size : Vector2Int):
        """Set the size of the window"""
        self.size = size
        self.display = pg.display.set_mode(self.size.toTuple())
        self.info = pg.display.Info()
    
    #Application functions
        
    def setPaused(self, paused : bool):
        """Pause the application"""
        self.paused = paused

    def stop(self):
        """Quit the application"""
        self.running = False

    def run(self):
        while self.running:
            pg.event.pump()
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.running = False
                    break
                #call event handler
            if self.eventHandler != None:
                self.eventHandler(events)
                    
            #if paused do not run the update function unless update_on_pause is set to True
            if self.paused:
                if self.update_on_pause and self.updateFunction != None:
                    self.updateFunction()    
                self.clock.tick(self.fps)
                continue
            #call update function
            if self.updateFunction != None:
                self.updateFunction()
            pg.display.update()
            self.clock.tick(self.fps)
        pg.quit()
        