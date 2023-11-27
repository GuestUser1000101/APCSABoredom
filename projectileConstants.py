class ProjectileTemplate:
    def __init__(self, radius = 1, bounceOnWall = False, piercing = False, startSpeed = 5, damage = 10):
        self.radius = radius
        self.bounceOnWall = bounceOnWall
        self.piercing = piercing
        self.startSpeed = startSpeed
        self.damage = damage

projectileConstants = {
    "noAI" : ProjectileTemplate(),
    "large" : ProjectileTemplate(radius = 5, piercing = True),
    "bouncy" : ProjectileTemplate(bounceOnWall = True),
    "explosion" : ProjectileTemplate(startSpeed = 0, piercing = True),
    "homing" : ProjectileTemplate(),
    "scatter" : ProjectileTemplate(piercing = True),
    "missile" : ProjectileTemplate(damage = 20),
    "spiral" : ProjectileTemplate(piercing = True)
}