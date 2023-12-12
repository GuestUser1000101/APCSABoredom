class ProjectileTemplate:
    def __init__(
        self,
        radius=1,
        bounceOnWall=False,
        piercing=False,
        startSpeed=5,
        damage=10,
        shape="bullet",
        diameter=10,
        follow=False,
        explosionType="none",
        homing=False,
        invincibilityFrames=15,
        explodeAtEntity=False,
        seeking=False,
        collisionDamage=True,
        mass=1,
        gravity=False
    ):
        self.radius = radius
        self.bounceOnWall = bounceOnWall
        self.piercing = piercing
        self.startSpeed = startSpeed
        self.damage = damage
        self.shape = shape
        self.diameter = diameter
        self.follow = follow
        self.explosionType = explosionType
        self.homing = homing
        self.invincibilityFrames = invincibilityFrames
        self.explodeAtEntity = explodeAtEntity
        self.seeking = seeking
        self.collisionDamage = collisionDamage
        self.mass=mass
        self.gravity=gravity


projectileConstants = {
    "noAI": ProjectileTemplate(),
    "bullet": ProjectileTemplate(),
    "bouncer": ProjectileTemplate(damage=15, bounceOnWall=True),
    "slug": ProjectileTemplate(damage=20, radius=2),
    "piercer": ProjectileTemplate(damage=15, startSpeed=6, piercing=True),
    "rebounder": ProjectileTemplate(damage=20, bounceOnWall=True),
    "bomb": ProjectileTemplate(
        damage=40, bounceOnWall=True, piercing=True, startSpeed=3, collisionDamage=False, invincibilityFrames=0
    ),
    "homingBullet": ProjectileTemplate(damage=20, homing=True),
    "missile": ProjectileTemplate(
        damage=25, startSpeed=3, explosionType="smallExplosion", radius=2
    ),
    "laserPulse": ProjectileTemplate(
        piercing=True,
        shape="beam",
        radius=8,
        startSpeed=10,
        diameter=2,
        damage=25,
        invincibilityFrames=5,
    ),
    "seeker": ProjectileTemplate(
        damage=20, startSpeed=6, seeking=True, bounceOnWall=True, radius=2
    ),
    "bounceSplitter": ProjectileTemplate(damage=0, bounceOnWall=True, invincibilityFrames=0),
    "grenade": ProjectileTemplate(
        damage=70,
        bounceOnWall=True,
        piercing=True,
        startSpeed=3,
        radius=4,
        collisionDamage=False,
    ),
    "vibrator": ProjectileTemplate(
        damage=30,
        bounceOnWall=True,
        piercing=True,
        startSpeed=5,
        radius=3,
        collisionDamage=False,
    ),
    "splitter": ProjectileTemplate(damage=0, radius=2, invincibilityFrames=0),
    "shell": ProjectileTemplate(damage=35, explosionType="mediumExplosion", radius=3),
    "homingMissile": ProjectileTemplate(
        damage=25, startSpeed=3, explosionType="smallExplosion", homing=True, radius=2
    ),
    "laserBeam": ProjectileTemplate(
        piercing=True,
        shape="beam",
        radius=0,
        startSpeed=0,
        diameter=0,
        damage=2,
        follow=True,
        invincibilityFrames=2,
    ),
    "laserSplitter": ProjectileTemplate(
        damage=40, shape="beam", radius=12, diameter=3, piercing=True, startSpeed=12
    ),
    "pursuer": ProjectileTemplate(
        damage=40,
        radius=5,
        startSpeed=8,
        seeking=True,
        bounceOnWall=True,
        piercing=True,
    ),
    "grenadeSplitter": ProjectileTemplate(damage=0, bounceOnWall=True),
    "plasmaGrenade": ProjectileTemplate(
        damage=100,
        bounceOnWall=True,
        piercing=True,
        startSpeed=5,
        radius=6,
        collisionDamage=False,
        invincibilityFrames=0
    ),
    "pulser": ProjectileTemplate(
        damage=50,
        bounceOnWall=True,
        piercing=True,
        startSpeed=8,
        radius=6,
        collisionDamage=False,
    ),
    "multiSplitter": ProjectileTemplate(damage=0, radius=3),
    "homingSplitter": ProjectileTemplate(
        damage=0, radius=3, piercing=True, startSpeed=3
    ),
    "rocket": ProjectileTemplate(
        damage=50,
        startSpeed=7,
        explosionType="largeExplosion",
        shape="beam",
        radius=6,
        diameter=2,
    ),
    "homingShell": ProjectileTemplate(
        damage=40, explosionType="mediumExplosion", homing=True, radius=3
    ),
    "laserCannon": ProjectileTemplate(
        piercing=True,
        shape="beam",
        radius=0,
        startSpeed=0,
        diameter=0,
        damage=4,
        follow=True,
        invincibilityFrames=2,
        explodeAtEntity=True,
    ),
    "laserField": ProjectileTemplate(damage=40, radius=4, piercing=True, startSpeed=6),
    "bouncy": ProjectileTemplate(bounceOnWall=True),
    "largeExplosion": ProjectileTemplate(
        startSpeed=0, piercing=True, damage=60, invincibilityFrames=60
    ),
    "mediumExplosion": ProjectileTemplate(
        startSpeed=0, piercing=True, damage=40, invincibilityFrames=45
    ),
    "smallExplosion": ProjectileTemplate(startSpeed=0, piercing=True, damage=20),
    "scatter": ProjectileTemplate(piercing=True),
    "smallShockwave": ProjectileTemplate(
        startSpeed=0,
        piercing=True,
        shape="ring",
        damage=10,
        diameter=5,
    ),
    "largeShockwave": ProjectileTemplate(
        startSpeed=0, piercing=True, shape="ring", damage=20
    ),
    "blackhole" : ProjectileTemplate(
        startSpeed=0, damage=100, piercing=True, radius = 10, mass=10, gravity=True
    )
}
