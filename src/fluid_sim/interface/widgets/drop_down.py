import pygame as pg
import numpy as np

import logging

from fluid_sim.settings.manager import settings
from fluid_sim.interface.config import config, Widget

logger = logging.getLogger(__name__)

class DropDown(Widget):
    
    def __init__(self, name:str, rect:pg.Rect, text:list[str], setting) -> None:
        
        super().__init__(name=name, rect=rect, text=text)
        
        self.get_index(setting)
        self.show = False
        self.hovering = None
        
        #   initialise other rects
        self.arrow_rect = pg.Rect(self.rect.topright, (int(0.8 * self.rect.height), self.rect.height))
        self.sub_rect: list[pg.Rect] = []
        for i in range(1, len(text) + 1):
            self.sub_rect.append(rect.copy().move(0, i * rect.height))
            
    def get_index(self, setting) -> None:
        
        for i, txt in enumerate(self.text):
            #   if option in drop down matches setting
            if txt.lower() == str(setting):
                self.index = i
                break
        try:
            self.index  #   check if variable exists
        except NameError as e:
            logger.warning(f"Unable to find the index with the correct setting, {e}")
            self.index = 0

        
    def get_selected(self) -> str:
        return self.text[self.index]
    
    
    #   ==========[ UPDATE ]==========
    def update(self, hovering:str) -> None:
        
        super().update(hovering)
        for text in self.text:
            if hovering == f"{self.name}.{text.lower()}":
                self.hovering = text
                return
        self.hovering = None


    #   ==========[ DRAW ]==========
    def _draw_arrow(self, screen:pg.Surface) -> None:
        
        center = np.array(self.arrow_rect.center, dtype=np.float16)
        
        #   rect
        pg.draw.rect(screen, self.bg_clr, self.arrow_rect)
        pg.draw.rect(screen, self.main_clr, self.arrow_rect, self.border)
        
        #   arrow
        len = int(0.25 * self.arrow_rect.height)
        sign = -1 if self.show else 1
        points = []
        for i in range(3):
            rad = np.deg2rad(i * 120)
            coord = center + len * np.array((np.sin(rad), sign * np.cos(rad)), dtype=np.float16)
            points.append(coord.astype(np.int16))
            
        pg.draw.polygon(screen, self.main_clr, points)
        
    def _draw_block(self, screen:pg.Surface, rect:pg.Rect, text:str, main_clr=None, bg_clr=None) -> None:
        
        if not main_clr: main_clr = self.main_clr
        if not bg_clr: bg_clr = self.bg_clr
        
        #   draw rect
        pg.draw.rect(screen, bg_clr, rect)
        pg.draw.rect(screen, main_clr, rect, self.border)
        
        #   draw text
        text_surf = config.font["body"].render(text, True, main_clr)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
            
    
    def draw(self, screen:pg.Surface) -> None:
        
        self._draw_arrow(screen)
        self._draw_block(screen, self.rect, self.get_selected())
        
        if self.show:
            for i, rect in enumerate(self.sub_rect):
                if self.hovering == self.text[i]:
                    main_clr, bg_clr = config.hl_clr, config.hvr_clr
                else:
                    main_clr, bg_clr = config.main_clr, config.bg_clr
                self._draw_block(screen, rect, self.text[i], main_clr, bg_clr)