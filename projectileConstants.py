class ProjectileTemplate:
    def __init__(self, radius = 1, bounceOnWall = False, piercing = False, startSpeed = 5):
        self.radius = radius
        self.bounceOnWall = bounceOnWall
        self.piercing = piercing
        self.startSpeed = startSpeed

projectileConstants = {
    "noAI" : ProjectileTemplate(),
    "large" : ProjectileTemplate(radius = 5, piercing = True),
    "bouncy" : ProjectileTemplate(bounceOnWall = True),
    "explosion" : ProjectileTemplate(startSpeed = 0),
    "homing" : ProjectileTemplate(piercing = True),
    "scatter" : ProjectileTemplate()
}