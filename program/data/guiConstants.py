class GuiTemplate:
    def __init__(
        self,
        width=100,
        height=100,
        widgits = [],
    ):
        self.width=width
        self.height=height
        self.widgits = widgits

guiConstants = {
    "weaponSelect" : GuiTemplate(width=400, height=200, widgits=[
        (200, 20),
        (80, 60), (200, 60), (320, 60),
        (40, 100), (120, 100), (180, 100), (220, 100), (280, 100), (360, 100),
        (20, 140), (60, 140), (100, 140), (140, 140), (180, 140), (220, 140), (280, 140), (340, 140), (380, 140),
        (20, 180), (60, 180), (100, 180), (140, 180), (180, 180), (220, 180), (280, 180), (340, 180), (380, 180),
    ])
}
