class Theme:
    
    def __init__(self, light_bg, dark_bg, main, highlight, hover):
        
        self.light_bg = light_bg
        self.dark_bg = dark_bg
        self.main = main
        self.highlight = highlight
        self.hover = hover
    
THEME = {
    
    "light": Theme(
        light_bg=(255, 255, 255),
        dark_bg=(230, 230, 230),
        main=(60, 60, 60),
        highlight=(0, 0, 0),
        hover=(200, 200, 200)
    ),
    "dark": Theme(
        light_bg=(50, 50, 50),
        dark_bg=(25, 25, 25),
        main=(200, 200, 200),
        highlight=(255, 255, 255),
        hover=(100, 100, 100)
    )
}