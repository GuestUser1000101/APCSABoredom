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
        (100, 60), (200, 60), (300, 60),
        (70, 100), (130, 100), (180, 100), (220, 100), (280, 100), (330, 100),
        (60, 140), (80, 140), (120, 140), (140, 140), (180, 140), (220, 140), (280, 140), (320, 140), (340, 140),
        (60, 180), (80, 180), (120, 180), (140, 180), (180, 180), (220, 180), (280, 180), (320, 180), (340, 180),
    ])
}
