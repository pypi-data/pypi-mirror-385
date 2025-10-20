from ..core import Vector2, Color, Vector2Int
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from time import sleep

class Border:
    def __init__(self, width : int, color : Color):
        self.width = width
        self.color = color


class UIObject:
    def __init__(self, parent, position : Vector2, size : Vector2, border = Border(0, Color.Black), backgroundColor : Color = Color.White, anchorPoint : Vector2 = Vector2.zero):
        if position.x > 1:
            position.x = position.x / parent.size.x
        if position.y > 1:
            position.y = position.y / parent.size.y
        if size.x > 1:
            size.x = size.x / parent.size.x
        if size.y > 1:
            size.y = size.y / parent.size.y
        self.position = position
        self.size = size
        
        self.absoluteSize : Vector2 = Vector2(size.x * parent.size.x, size.y * parent.size.y)
        self.absolutePosition : Vector2 = Vector2(position.x * parent.size.x + anchorPoint.x*self.absoluteSize.x, position.y * parent.size.y + anchorPoint.y*self.absoluteSize.y)
        self.anchorPoint : Vector2 = anchorPoint
        self.backgroundColor : Color = backgroundColor
        self.border = border
        self.children = []
        self.parent = parent
        self.parent.addChild(self)
    def get_Rect(self):
        self.absolutePosition : Vector2 = Vector2(self.position.x * self.parent.size.x + self.anchorPoint.x*self.absoluteSize.x, self.position.y * self.parent.size.y + self.anchorPoint.y*self.absoluteSize.y)
        self.absoluteSize : Vector2 = Vector2(self.size.x * self.parent.size.x, self.size.y * self.parent.size.y)
        return pg.Rect(self.absolutePosition.x, self.absolutePosition.y, self.absoluteSize.x, self.absoluteSize.y)
        
    def draw(self, screen : pg.Surface):
        screen.fill(self.backgroundColor.toTuple(), self.get_Rect())
        if self.border.width > 0:
            pg.draw.rect(screen, self.border.color.toTuple(), self.get_Rect(), self.border.width)
    def addChild(self, child):
        self.children.append(child)
    def removeChild(self, child):
        self.children.remove(child)
        
    def delete(self):
        self.parent.removeChild(self)
        del self


class TextLabel(UIObject):
    def __init__(self, parent, position : Vector2, size : Vector2, text : str, font : pg.font.Font, textColor : Color, border = Border(0, Color.Black), backgroundColor : Color = Color.White, anchorPoint : Vector2 = Vector2(0, 0), textCenter : Vector2 = Vector2(0.5, 0.5)):
        super().__init__(parent, position, size, border=border, backgroundColor=backgroundColor, anchorPoint=anchorPoint)
        self.text : str = text
        self.font = font
        self.textColor : Color = textColor
        self.text_center = textCenter
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
    def changeText(self, text : str):
        self.text = text
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
    def draw(self, screen : pg.Surface):
        super().draw(screen)
        screen.blit(self.renderedText, (self.absolutePosition.x + (self.absoluteSize.x - self.renderedText.get_width()) * self.text_center.x, self.absolutePosition.y + (self.absoluteSize.y - self.renderedText.get_height()) * self.text_center.y))

class Dropdown(UIObject):
    Dropdowns = []
    def __init__(self, parent, position : Vector2, size : Vector2, options : list, font : pg.font.Font, textColor : Color, border = Border(0, Color.Black), backgroundColor : Color = Color.White, dropdownColor : Color = Color(50, 50, 50), anchorPoint : Vector2 = Vector2(0, 0), textCenter : Vector2 = Vector2(0.5, 0.5)):
        super().__init__(parent, position, size, border=border, backgroundColor=backgroundColor, anchorPoint=anchorPoint)
        self.options = options
        self.font = font
        self.dropdownColor = dropdownColor
        self.textColor = textColor
        self.text_center = textCenter
        self.renderedOptions = []
        self.dropdown_options = []
        self.opened = False
        for option in self.options:
            self.renderedOptions.append(self.font.render(option, True, self.textColor.toTuple()))
        self.selectedOption = 0 if len(self.options) > 0 else -1
        Dropdown.Dropdowns.append(self)
    def draw(self, screen : pg.Surface):
        super().draw(screen)
        #show selected option
        #render selected option but center it according to the textcentered property so a value of 0.5 and 0.5 centers the text vertically and horizontally
        if self.selectedOption != -1:
            screen.blit(self.renderedOptions[self.selectedOption], (self.absolutePosition.x + (self.absoluteSize.x - self.renderedOptions[self.selectedOption].get_width()) * self.text_center.x, self.absolutePosition.y + (self.absoluteSize.y - self.renderedOptions[self.selectedOption].get_height()) * self.text_center.y))
    def drawOptions(self, screen : pg.Surface):
        for i in range(len(self.options)):
                screen.fill(self.dropdownColor.toTuple(), pg.Rect(self.absolutePosition.x, self.absolutePosition.y + (i+1) * self.absoluteSize.y, self.absoluteSize.x, self.absoluteSize.y))
                screen.blit(self.renderedOptions[i], (self.absolutePosition.x + (self.absoluteSize.x - self.renderedOptions[i].get_width()) * self.text_center.x, self.absolutePosition.y + (i+1) * self.absoluteSize.y + (self.absoluteSize.y - self.renderedOptions[i].get_height()) * self.text_center.y))
                pg.draw.rect(screen, self.border.color.toTuple(), pg.Rect(self.absolutePosition.x, self.absolutePosition.y + (i+1) * self.absoluteSize.y, self.absoluteSize.x, self.absoluteSize.y), self.border.width)
            
    def setOptions(self, options : list):
        self.options = options
        self.renderedOptions = []
        for option in self.options:
            self.renderedOptions.append(self.font.render(option, True, self.textColor.toTuple()))
    def handleMouseEvent(self, pos=None):
        if pos == None:
            pos = pg.mouse.get_pos()
        has_opened = False
        if self.get_Rect().collidepoint(pos):
            self.opened = not self.opened
            has_opened = True
        if self.opened:
            for i in range(len(self.options)):#
                if pg.Rect(self.absolutePosition.x, self.absolutePosition.y + (i+1) * self.absoluteSize.y, self.absoluteSize.x, self.absoluteSize.y).collidepoint(pg.mouse.get_pos()):
                    self.changeSelectedOption(i)
                    self.opened = False
        if self.opened and not has_opened:
            self.opened = False
    def getSelected(self):
        return self.options[self.selectedOption]
    def getSelectedIndex(self):
        return self.selectedOption
    def changeSelectedOption(self, option : int):
        self.selectedOption = option
    def delete(self):
        Dropdown.Dropdowns.remove(self)
        super().delete()

class TextButton(UIObject):
    TextButtons = []
    def __init__(self, parent, position : Vector2, size : Vector2, text : str, font : pg.font.Font, textColor : Color, border = Border(0, Color.Black), backgroundColor : Color = Color.White, anchorPoint : Vector2 = Vector2(0, 0), textCenter : Vector2 = Vector2(0.5, 0.5), activaton_function = None, activation_args = []):      
        super().__init__(parent, position, size, border=border, backgroundColor=backgroundColor, anchorPoint=anchorPoint)
        self.text : str = text
        self.font = font
        self.textColor : Color = textColor
        self.text_center = textCenter
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
        self.activation_function = activaton_function
        self.activation_args = activation_args
        TextButton.TextButtons.append(self)
        
    def changeText(self, text : str):
        self.text = text
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
    def draw(self, screen : pg.Surface):
        super().draw(screen)
        screen.blit(self.renderedText, (self.absolutePosition.x + (self.absoluteSize.x - self.renderedText.get_width()) * self.text_center.x, self.absolutePosition.y + (self.absoluteSize.y - self.renderedText.get_height()) * self.text_center.y))
    def handleMouseEvent(self, pos=None):
        if pos == None:
            pos = pg.mouse.get_pos()
        if self.get_Rect().collidepoint(pos):
            if self.activation_function != None:
                self.activation_function(*self.activation_args)
    def delete(self):
        TextButton.TextButtons.remove(self)
        super().delete()
        
class Application:
    def __init__(self, size : Vector2Int, title : str, updateFunction = None, fps_limit = 60, update_on_pause = False):
        pg.init()
        info = pg.display.Info()
        self.size : Vector2Int = size
        self.title : str = title
        self.paused = False
        self.running = True
        self.clock = pg.time.Clock()
        self.fps = fps_limit
        self.display = pg.display.set_mode(self.size.toTuple())
        self.updateFunction = updateFunction
        self.update_on_pause = update_on_pause
        self.children = []
        pg.display.set_caption(self.title)
        
        
        #Init Pygame
        
    def setFPS(self, fps : int):
        self.fps = fps
    def addChild(self, child : UIObject):
        self.children.append(child)
    def clearScreen(self):
        self.display.fill(Color.Black.toTuple())
    def drawChildren(self, obj : UIObject):
        for child in obj.children:
            child.draw(self.display)
            if (len(child.children) > 0):
                self.drawChildren(child)
    def setSize(self, size : Vector2Int):
        self.size = size
        self.display = pg.display.set_mode(self.size.toTuple())
    def setPaused(self, paused : bool):
        self.paused = paused
        
    def stop(self):
        self.running = False
    def draw(self):
        self.clearScreen()
        self.drawChildren(self)
    def drawPopup(self):
        for dropdown in Dropdown.Dropdowns:
            if dropdown.opened:
                dropdown.drawOptions(self.display)
    def run(self):
        while self.running:
            pg.event.pump()
            events = pg.event.get()
            if self.paused:
                if self.display != None:
                    self.display = None
                    
                if self.update_on_pause and self.updateFunction != None:
                    self.updateFunction([])    
                self.clock.tick(self.fps)
                continue
            if self.display == None:
                self.display = pg.display.set_mode(self.size.toTuple())
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    for dropdown in Dropdown.Dropdowns:
                        dropdown.handleMouseEvent(pos=pos)
                    for button in TextButton.TextButtons:
                        button.handleMouseEvent(pos=pos)
                elif event.type == pg.QUIT:
                    self.running = False
            self.draw()
            self.drawPopup()
            pg.display.update()
            if self.updateFunction != None:
                self.updateFunction(events)
            self.clock.tick(self.fps)
        pg.quit()
        
    