class ProjectileTemplate:
    def __init__(self, radius = 1, bounceOnWall = False, piercing = False, startSpeed = 5, damage = 20, shape = "bullet", diameter = 10, follow = False):
        self.radius = radius
        self.bounceOnWall = bounceOnWall
        self.piercing = piercing
        self.startSpeed = startSpeed
        self.damage = damage
        self.shape = shape
        self.diameter = diameter
        self.follow = follow

projectileConstants = {
    "noAI" : ProjectileTemplate(),
    "large" : ProjectileTemplate(radius = 5, piercing = True),
    "bouncy" : ProjectileTemplate(bounceOnWall = True),
    "explosion" : ProjectileTemplate(startSpeed = 0, piercing = True, damage = 50),
    "homing" : ProjectileTemplate(),
    "scatter" : ProjectileTemplate(piercing = True),
    "missile" : ProjectileTemplate(damage = 0),
    "shockwave" : ProjectileTemplate(startSpeed = 0, piercing =  True, shape = "ring", damage = 10),
    "laser" : ProjectileTemplate(piercing = True, shape = "beam", radius = 10, startSpeed = 10, diameter = 3, damage = 50),
    "energyBeam" : ProjectileTemplate(piercing = True, shape = "beam", radius = 0, startSpeed = 0, diameter = 0, damage = 20, follow = True)
}