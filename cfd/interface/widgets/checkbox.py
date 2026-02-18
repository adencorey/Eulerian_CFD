import pygame as pg

from cfd.interface.config import config
from .widget import Widget, NULLWIDGET


class CheckBox(Widget):
    
    def __init__(self, name: str, pos: tuple, text = None, font = config.font["body"], checked=False) -> None:
        super().__init__(name=name, rect=pg.Rect(pos, (0, 0)), text=text, font=font)
        
        self._radius = 0.4 * self._font.get_height()
        self._padding = 1.5 * self._radius
        self.center = (self.rect.left + self._padding, self.rect.centery)
        self.checked = checked
        self._update_text()
        
    #   ==========[ UTILITIES ]==========
    def collide(self, mouse_pos) -> True | False:
        return self._text_rect.collidepoint(mouse_pos) or ((self.center[0] - mouse_pos[0]) ** 2 + (self.center[1] - mouse_pos[1]) ** 2 <= self._radius ** 2)
        
    def _update_text(self) -> None:
        self._text_surf = self._font.render(self.text, True, self._main_clr)
        self._text_rect = self._text_surf.get_rect(left=self.rect.left + 2 * self._padding, centery=self.rect.y)

    def draw(self, screen):
        pg.draw.circle(screen, self._main_clr, self.center, self._radius, int(0.07 * self._font.get_height()))
        if self.checked:
            pg.draw.circle(screen, self._main_clr, self.center, 0.5 * self._radius)
        self._draw_text(screen)