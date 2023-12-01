class ProjectileTemplate:
    def __init__(self, radius = 1, bounceOnWall = False, piercing = False, startSpeed = 5, damage = 10, shape = "bullet", diameter = 10, follow = False, explosion = False, homing = False):
        self.radius = radius
        self.bounceOnWall = bounceOnWall
        self.piercing = piercing
        self.startSpeed = startSpeed
        self.damage = damage
        self.shape = shape
        self.diameter = diameter
        self.follow = follow
        self.explosion = explosion
        self.homing = homing

projectileConstants = {
    "noAI" : ProjectileTemplate(),
    "bullet" : ProjectileTemplate(),
    "slug" : ProjectileTemplate(damage = 30),
    "piercer" : ProjectileTemplate(startSpeed = 6, piercing = True),
    "missile" : ProjectileTemplate(damage = 0),
    "homingBullet" : ProjectileTemplate(damage = 10),
    "laserPulse" : ProjectileTemplate(piercing = True, shape = "beam", radius = 10, startSpeed = 10, diameter = 3, damage = 50),
    "large" : ProjectileTemplate(radius = 5, piercing = True),
    "bouncy" : ProjectileTemplate(bounceOnWall = True),
    "explosion" : ProjectileTemplate(startSpeed = 0, piercing = True, damage = 50),
    "scatter" : ProjectileTemplate(piercing = True),
    "shockwave" : ProjectileTemplate(startSpeed = 0, piercing =  True, shape = "ring", damage = 10),
    "energyBeam" : ProjectileTemplate(piercing = True, shape = "beam", radius = 0, startSpeed = 0, diameter = 0, damage = 50, follow = True),
    "largeExplosion" : ProjectileTemplate(startSpeed = 0, piercing = True, damage = 10)
}