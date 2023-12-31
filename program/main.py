import pygame

pygame.init()
from pygame.locals import *
import sys
import random
import math
from data.projectileConstants import *
from data.guiConstants import *

clock = pygame.time.Clock()
FPS = 60
pygame.display.set_caption("test")

width, height = 960, 540
gravityConstant = 1000
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
running = True
mousetick = 0
mousehold = 0
mouseX = 0
mouseY = 0

velocityTime = [(0, 0)] * 400

weaponSelection = 0
weapons = [
    "bullet",
    "bouncer",
    "slug",
    "piercer",
    "rebounder",
    "bomb",
    "splitter",
    "missile",
    "homingBullet",
    "laserPulse",
    "seeker",
    "bounceSplitter",
    "grenade",
    "vibrator",
    "multiSplitter",
    "shell",
    "homingMissile",
    "laserBeam",
    "laserSplitter",
    "pursuer",
    "grenadeSplitter",
    "plasmaGrenade",
    "pulser",
    "homingSplitter",
    "rocket",
    "homingShell",
    "laserCannon",
    "laserField",
    "blackhole",
]

alphabet = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]
for letter in alphabet:
    exec(f"{letter}_tick = 0")


def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0


def boolToSign(bool):
    return 1 if bool else -1


def graphVelocity():
    for v, t in velocityTime:
        pygame.draw.circle(screen, (255, 255, 255), (t * 2, height + (-v * 20)), 1)


def distance(vector1, vector2):
    return ((vector1.x - vector2.x) ** 2 + (vector1.y - vector2.y) ** 2) ** 0.5


def cloneList(l):
    cloned = []
    for item in l:
        cloned.append(item)
    return cloned


def displacement(acc, vel, targetVel=0):
    return (targetVel**2 - vel**2) / 2 / acc


def smallestAngleDifference(angle1, angle2):
    angleDiff = abs(angle1 - angle2)
    if angleDiff > math.pi:
        return 2 * math.pi - angleDiff
    else:
        return angleDiff


def positiveAngleEquivalent(angle):
    if angle < 0:
        return positiveAngleEquivalent(angle + 2 * math.pi)
    elif angle >= 2 * math.pi:
        return positiveAngleEquivalent(angle - 2 * math.pi)
    else:
        return angle


def crossZero(angle1, angle2):
    angle1 = positiveAngleEquivalent(angle1)
    angle2 = positiveAngleEquivalent(angle2)

    return abs(angle1 - angle2) > math.pi


def toDegrees(angle):
    return angle / math.pi * 180


def toRadians(angle):
    return angle / 180 * math.pi


def colorCheck(color):
    if type(color) == list or type(color) == tuple:
        red = colorCheck(color[0])
        green = colorCheck(color[1])
        blue = colorCheck(color[2])
        return (red, green, blue)
    else:
        if color > 255:
            return 255
        elif color < 0:
            return 0
        else:
            return color


def gradient(color1, color2, percentage, brightnessPercentage=1):
    redDiff = color2[0] - color1[0]
    greenDiff = color2[1] - color1[1]
    blueDiff = color2[2] - color1[2]
    return colorCheck(
        (
            color1[0] * brightnessPercentage + redDiff * percentage,
            color1[1] * brightnessPercentage + greenDiff * percentage,
            color1[2] * brightnessPercentage + blueDiff * percentage,
        )
    )


def inBetween(p1, p2, pointer):
    return (pointer >= p1 and pointer <= p2) or (pointer <= p1 and pointer >= p2)


def inBetweenOrdered(PMin, PMax, pointer):
    return PMin <= pointer and PMax >= pointer


def approachAngle(currentAngle, targetAngle, percentage):
    currentAngle = positiveAngleEquivalent(currentAngle)
    targetAngle = positiveAngleEquivalent(targetAngle)

    smallestAngle = smallestAngleDifference(currentAngle, targetAngle)
    direction = boolToSign(crossZero(currentAngle, targetAngle)) * sign(
        targetAngle - currentAngle
    )

    return currentAngle - smallestAngle * direction * percentage


def getImage(file):
    return pygame.image.load(file).convert_alpha()


def withSolidColor(image, color):
    newImage = image.copy()
    for y in range(newImage.get_height()):
        for x in range(newImage.get_width()):
            pixel = newImage.get_at((x, y))
            if len(pixel) >= 4 and pixel[3] > 0:
                newImage.set_at((x, y), (color + tuple([pixel[3]])))

    return newImage


def renderImage(image, x, y, scale=1, color = "none"):
    image = withSolidColor(image, color) if color != "none" else image
    screen.blit(
        pygame.transform.scale(
            image,
            (image.get_width() * scale, image.get_height() * scale),
        ),
        (x, y),
    )


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))

    def array(self):
        return (self.x, self.y)

    def add(self, vec):
        self.x += vec.x
        self.y += vec.y

    def added(self, vec):
        return Vector(self.x + vec.x, self.y + vec.y)

    def difference(self, vec):
        return Vector(vec.x - self.x, vec.y - self.y)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self, magnitude):
        distance = math.sqrt(self.x**2 + self.y**2)
        if distance != 0:
            self.x *= magnitude / distance
            self.y *= magnitude / distance
            return Vector(self.x, self.y)
        return Vector(0, 0)

    def normalized(self, magnitude):
        distance = math.sqrt(self.x**2 + self.y**2)
        return (
            Vector(self.x * magnitude / distance, self.y * magnitude / distance)
            if distance != 0
            else Vector(0, 0)
        )

    def shuffledVector(self, uncertainty):
        return Vector(
            self.x + (random.random() - 0.5) * uncertainty,
            self.y + (random.random() - 0.5) * uncertainty,
        )

    def zero(self):
        self.x = 0
        self.y = 0

    def angle(self):
        return math.atan2(self.y, self.x)

    def render(self, pos, multiplier=1):
        pygame.draw.line(
            screen,
            (255, 255, 255),
            pos.array(),
            (pos.x + self.x * multiplier, pos.y + self.y * multiplier),
        )

    def renderPoint(self):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 2)

    def renderPoint(self):
        pygame.draw.circle(screen, (255, 255, 255), self.array(), 5)

    def rotate(self, angle):
        return Vector.fromAngle(self.angle() + angle, self.magnitude())

    @staticmethod
    def fromAngle(angle, magnitude=1):
        return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @staticmethod
    def fromArray(array):
        return Vector(array[0], array[1])

    @staticmethod
    def fromVector(vector):
        return Vector(vector.x, vector.y)

    def isOutOfBounds(self):
        return self.x < 0 or self.x > width or self.y < 0 or self.y > width

    def boundPoint(self):
        if self.x < 0:
            self.x = -self.x
        elif self.x > width:
            self.x = 2 * width - self.x
        if self.y < 0:
            self.y = -self.y
        elif self.y > height:
            self.y = 2 * height - self.y

    def getBoundedPoint(self):
        if self.x < 0:
            x = -self.x
        elif self.x > width:
            x = 2 * width - self.x
        else:
            x = self.x

        if self.y < 0:
            y = -self.y
        elif self.y > height:
            y = 2 * height - self.y
        else:
            y = self.y

        return Vector(x, y)


class Line:
    def __init__(self, p1, p2, diameter=1):
        self.p1 = p1
        self.p2 = p2
        self.diameter = diameter

    def getSlope(self):
        if self.p1.x - self.p2.x == 0:
            return float("inf")
        else:
            return (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)

    def getAngle(self):
        return math.atan2(self.p2.y - self.p1.y, self.p2.x - self.p1.x)

    def getYIntercept(self):
        return self.p1.y - self.getSlope() * self.p1.x

    def getY(self, x):
        return self.getSlope() * x + self.getYIntercept()

    def getX(self, y):
        return (y - self.getYIntercept()) / self.getSlope()

    def getIntercection(self, line, b="null"):
        if b == "null":
            if type(line) != Line:
                raise Exception("Expected line object")
            m = line.getSlope()
            b = line.getYIntercept()
            return self.getIntercection(m, b)
        else:
            m = line
            thisSlope = self.getSlope()
            if thisSlope == m:
                return Vector(0, 0)
            thisYIntercept = self.getYIntercept()
            x = (b - thisYIntercept) / (thisSlope - m)
            y = thisSlope * x + thisYIntercept
            return Vector(x, y)

    def getPerpendicularIntersection(self, point):
        thisSlope = self.getSlope()
        if thisSlope == float("inf"):
            perpendicularSlope = 0
        elif thisSlope == 0:
            perpendicularSlope = float("inf")
        else:
            perpendicularSlope = -1 / thisSlope

        perpendicularYIntercept = point.y - point.x * perpendicularSlope

        return self.getIntercection(perpendicularSlope, perpendicularYIntercept)

    def interceptCircle(self, center, radius):
        closestPoint = self.getPerpendicularIntersection(center)
        if self.p1.x > self.p2.x:
            farthestXPoint = self.p1
            closestXPoint = self.p2
        else:
            farthestXPoint = self.p2
            closestXPoint = self.p1

        if closestPoint.x > farthestXPoint.x:
            closestPoint = farthestXPoint
        elif closestPoint.x < closestXPoint.x:
            closestPoint = closestXPoint

        return distance(center, closestPoint) < radius + self.diameter / 2

    def getBoundedLinesX(self):
        lines = self.getBoundedLinesY()
        if self.p1.x < 0:
            lines += Line(
                Vector(0, self.getY(0)), Vector(-self.p1.x, self.p1.y)
            ).getBoundedLinesY()
        elif self.p1.x > width:
            lines += Line(
                Vector(width, self.getY(width)),
                Vector(2 * width - self.p1.x, self.p1.y),
            ).getBoundedLinesY()

        if self.p2.x < 0:
            lines += Line(
                Vector(0, self.getY(0)), Vector(-self.p2.x, self.p2.y)
            ).getBoundedLinesY()
        elif self.p2.x > width:
            lines += Line(
                Vector(width, self.getY(width)),
                Vector(2 * width - self.p2.x, self.p2.y),
            ).getBoundedLinesY()

        return lines

    def getBoundedLinesY(self):
        lines = [self]
        if self.p1.y < 0:
            lines += Line(
                Vector(self.getX(0), 0), Vector(self.p1.x, -self.p1.y)
            ).getBoundedLinesX()
        elif self.p1.y > height:
            lines += Line(
                Vector(self.getX(height), height),
                Vector(self.p1.x, 2 * height - self.p1.y),
            ).getBoundedLinesX()

        if self.p2.y < 0:
            lines += Line(
                Vector(self.getX(0), 0), Vector(self.p2.x, -self.p2.y)
            ).getBoundedLinesX()
        elif self.p2.y > height:
            lines += Line(
                Vector(self.getX(height), height),
                Vector(self.p2.x, 2 * height - self.p2.y),
            ).getBoundedLinesX()

        return lines

    def renderBoundedLines(self):
        for line in self.getBoundedLinesX():
            line.render((255, 0, 255))

    def lengthen(self, direction, multiplier):
        if direction == 1:
            self.p1.x += (self.p1.x - self.p2.x) * (multiplier - 1)
            self.p1.y += (self.p1.y - self.p2.y) * (multiplier - 1)
        elif direction == 2:
            self.p2.x += (self.p2.x - self.p1.x) * (multiplier - 1)
            self.p2.y += (self.p2.y - self.p1.y) * (multiplier - 1)

    def setLength(self, direction, length):
        thisLength = distance(self.p1, self.p2)
        if thisLength != 0:
            if direction == 1:
                self.p1.x = self.p2.x + (self.p1.x - self.p2.x) / thisLength * length
                self.p1.y = self.p2.y + (self.p1.y - self.p2.y) / thisLength * length
            elif direction == 2:
                self.p2.x = self.p1.x + (self.p2.x - self.p1.x) / thisLength * length
                self.p2.y = self.p1.y + (self.p2.y - self.p1.y) / thisLength * length

    def render(self, color):
        vectorDiff = self.p1.difference(self.p2)
        points = (
            self.p1.added(
                vectorDiff.rotate(math.pi / 2).normalized(self.diameter / 2)
            ).array(),
            self.p1.added(
                vectorDiff.rotate(-math.pi / 2).normalized(self.diameter / 2)
            ).array(),
            self.p2.added(
                vectorDiff.rotate(-math.pi / 2).normalized(self.diameter / 2)
            ).array(),
            self.p2.added(
                vectorDiff.rotate(math.pi / 2).normalized(self.diameter / 2)
            ).array(),
        )
        pygame.draw.polygon(screen, color, points)
        pygame.draw.circle(screen, color, self.p1.array(), self.diameter / 2)
        pygame.draw.circle(screen, color, self.p2.array(), self.diameter / 2)


class Projectile:
    projectiles = []
    currentIndex = 0

    def __init__(
        self,
        x=0,
        y=0,
        vx=0,
        vy=0,
        ax=0,
        ay=0,
        projectileType="noAI",
        owner=-1,
        targetType=-1,
        angle=0,
    ):
        self.pos = Vector(x, y)
        self.startPos = Vector(x, y)
        self.vel = Vector(vx, vy)
        self.acc = Vector(0, 0)
        self.tick = 0
        self.owner = owner
        self.remove = False
        self.buffer = 5
        self.type = projectileType
        self.angle = angle
        self.radius = projectileConstants[projectileType].radius
        self.bounceOnWall = projectileConstants[projectileType].bounceOnWall
        self.piercing = projectileConstants[projectileType].piercing
        self.index = Projectile.currentIndex
        self.maxVel = projectileConstants[projectileType].startSpeed
        self.maxAcc = projectileConstants[projectileType].startSpeed / 5
        self.bounceCount = 0
        self.collisionCount = 0
        self.targetType = targetType
        self.damage = projectileConstants[projectileType].damage
        self.shape = projectileConstants[projectileType].shape
        self.diameter = projectileConstants[projectileType].diameter
        self.follow = projectileConstants[projectileType].follow
        self.homing = projectileConstants[projectileType].homing
        self.explosionType = projectileConstants[projectileType].explosionType
        self.invincibilityFrames = projectileConstants[
            projectileType
        ].invincibilityFrames
        self.initialTickSave = 0
        self.alreadySplit = False
        self.explodeAtEntity = projectileConstants[projectileType].explodeAtEntity
        self.seeking = projectileConstants[projectileType].seeking
        self.collisionDamage = projectileConstants[projectileType].collisionDamage
        self.shootCooldown = 0
        self.mass = projectileConstants[projectileType].mass
        self.gravity = projectileConstants[projectileType].gravity
        self.cooldown = projectileConstants[projectileType].cooldown
        self.line = (
            Line(
                self.pos,
                Vector(
                    self.pos.x + self.radius * math.cos(self.angle),
                    self.pos.y + self.radius * math.sin(self.angle),
                ),
                self.diameter,
            )
            if self.shape == "beam"
            else Line(self.pos, self.pos, self.radius * 2)
        )
        Projectile.currentIndex += 1

    def __str__(self):
        return "Projectile #" + self.index + " of type " + self.type

    def conditionalRemove(self):
        self.remove = True

    def collideWithEntity(self, target):
        if not self.piercing:
            self.remove = True
        if self.explosionType != "none":
            if self.explodeAtEntity:
                self.explode(self.explosionType, target.pos)
            else:
                self.explode(self.explosionType)
        if self.seeking:
            closest = self.findClosest(exceptions=[self.owner, target])
            if closest != -1:
                self.pointAtEntity(closest)
        self.collisionCount += 1

    def findClosest(self, radius=-1, entityType=-1, exceptions=[]):
        closestDistance = sys.maxsize
        closestEntity = -1
        for entity in Entity.entities:
            typeCondition = entityType == entity.type if entityType != -1 else True
            radiusCondition = (
                distance(self.pos, entity.pos) <= radius if radius != -1 else True
            )
            exceptionCondition = (
                not entity in exceptions if len(exceptions) > 0 else True
            )

            if (
                typeCondition
                and radiusCondition
                and exceptionCondition
                and distance(self.pos, entity.pos) < closestDistance
            ):
                closestDistance = distance(self.pos, entity.pos)
                closestEntity = entity
        return closestEntity

    def pointAtEntity(self, entity):
        entityVector = Vector(entity.pos.x - self.pos.x, entity.pos.y - self.pos.y)
        self.vel = self.vel.rotate(entityVector.angle() - self.vel.angle())

    def stop(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopX(self):
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopY(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc

    def slow(self, coefficient):
        self.acc.y = coefficient * self.maxVel * -math.sin(self.vel.angle())
        self.acc.x = coefficient * self.maxVel * -math.cos(self.vel.angle())

    def setSpeed(self, speed):
        self.vel.normalize(speed)

    def findTargets(self, radius, entityType=-1):
        targets = []
        for entity in Entity.entities:
            condition = entity.type == entityType if entityType != -1 else True
            if distance(entity.pos, self.pos) < radius and condition:
                targets.append(entity)
        return targets

    @staticmethod
    def summonByVector(
        x, y, angle, vel=0, acc=0, projectileType="noAI", owner=-1, targetType=-1
    ):
        if vel == 0:
            vel = projectileConstants[projectileType].startSpeed
        Projectile.projectiles.append(
            Projectile(
                x,
                y,
                vel * math.cos(angle),
                vel * math.sin(angle),
                acc * math.cos(angle),
                vel * math.sin(angle),
                projectileType,
                owner,
                targetType,
                angle=angle,
            )
        )

    def render(self):
        if self.shape == "ring":
            pygame.draw.circle(
                screen, (0, 255, 255), self.pos.array(), self.radius, self.diameter
            )
        elif self.shape == "bullet":
            pygame.draw.circle(screen, (0, 255, 255), self.pos.array(), self.radius)
        elif self.shape == "beam":
            self.line.render((0, 255, 255))

    def home(self, target):
        if target != -1:
            distanceToClosest = distance(self.pos, target.pos)
            distanceVector = Vector(
                target.pos.x - self.pos.x, target.pos.y - self.pos.y
            )
            distanceVector.normalize(self.maxAcc)
            distanceX = abs(self.pos.x - target.pos.x)
            distanceY = abs(self.pos.y - target.pos.y)
            if distanceToClosest < 400:
                self.acc = distanceVector
                if abs(distanceX) < abs(
                    displacement(self.maxAcc, self.vel.x, target.vel.x)
                ):
                    self.stopX()
                if abs(distanceY) < abs(
                    displacement(self.maxAcc, self.vel.y, target.vel.y)
                ):
                    self.stopY()

    def update(self):
        if self.homing:
            self.home(self.findClosest(exceptions=[self.owner]))

        self.tick += 1
        if self.shootCooldown > 0:
            self.shootCooldown -= 1

        if self.acc.magnitude() > self.maxAcc:
            self.acc.normalize(self.maxAcc)

        self.vel.add(self.acc)

        if self.vel.magnitude() > self.maxVel:
            self.vel.normalize(self.maxVel)
        elif round(self.vel.magnitude(), 5) < self.maxAcc:
            self.vel.zero()

        self.pos.add(self.vel)

        if self.follow and self.owner != -1:
            self.pos = self.owner.pos

        if self.shape == "beam":
            if self.vel.magnitude() != 0:
                self.angle = self.vel.angle()
            self.line.p1 = Vector.fromVector(self.pos)
            self.line.p2 = self.pos.added(Vector.fromAngle(self.angle, self.radius))
            self.line.diameter = self.diameter

        if self.bounceOnWall:
            if self.pos.x >= width or self.pos.x <= 0:
                closest = self.findClosest(exceptions=[self])
                if self.seeking and closest != -1:
                    self.pointAtEntity(closest)
                else:
                    self.pos.x -= self.vel.x
                    self.vel.x = -self.vel.x
                self.bounceCount += 1
            if self.pos.y >= height or self.pos.y <= 0:
                closest = self.findClosest(exceptions=[self])
                if self.seeking and closest != -1:
                    self.pointAtEntity(self.findClosest())
                else:
                    self.pos.y -= self.vel.y
                    self.vel.y = -self.vel.y
                self.bounceCount += 1
        else:
            if (
                self.pos.x > width
                or self.pos.x < 0
                or self.pos.y > height
                or self.pos.y < 0
            ):
                self.remove = True

        self.gravitateEntities()

        exec(f"""self.{self.type}()""")

    def alignedToClosest(self, maxDistance, minAngleDiff, minDistance):
        closestEntity = self.findClosest(entityType=self.targetType)
        if closestEntity != -1 and closestEntity != self.owner:
            distanceVector = Vector(
                closestEntity.pos.x - self.pos.x, closestEntity.pos.y - self.pos.y
            )
            if (
                distanceVector.magnitude() < maxDistance
                and abs(self.vel.angle() - distanceVector.angle()) < minAngleDiff
            ) or distanceVector.magnitude() < minDistance:
                return True
        return False

    def split(self, amount, projectileType, angleDiff):
        for i in range(amount):
            Projectile.summonByVector(
                self.pos.x,
                self.pos.y,
                self.vel.angle() + angleDiff * (i - amount / 2 + 0.5),
                0,
                projectileType=projectileType,
            )

    def explode(self, explosionType="explosion", pos=-1):
        if pos == -1:
            pos = self.pos

        Projectile.summonByVector(pos.x, pos.y, 0, 0, projectileType=explosionType)
        Projectile.projectiles[-1].damage = self.damage

    def gravitateEntities(self):
        if self.gravity and self.mass > 0:
            for entity in Entity.entities:
                distanceToEntity = distance(self.pos, entity.pos)
                if distanceToEntity > 0:
                    entity.vel.add(
                        Vector(
                            self.pos.x - entity.pos.x, self.pos.y - entity.pos.y
                        ).normalize(gravityConstant * self.mass / distanceToEntity**2)
                    )

    def smallExplosion(self):
        if self.tick < 2:
            self.radius += 12
        elif self.tick < 10:
            self.radius -= 3
        else:
            self.remove = True

    def mediumExplosion(self):
        if self.tick < 2:
            self.radius += 20
        elif self.tick < 20:
            self.radius -= 2
        else:
            self.remove = True

    def largeExplosion(self):
        if self.tick < 8:
            self.radius += 5
        elif self.tick < 40:
            self.radius += (random.random() - 0.5) * 6
            self.radius += 0.5
        elif self.tick < 100:
            self.radius += (random.random() - 0.5) * 6
            self.radius -= 1
        elif self.tick < 120:
            if self.radius > 0:
                self.radius -= 2
            else:
                self.remove = True
        else:
            self.remove = True

    def massiveExplosion(self):
        if self.tick < 4:
            self.radius += 80
        elif self.tick < 40:
            self.radius += (random.random() - 0.5) * 12
            self.radius += 0.5
        elif self.tick < 100:
            self.radius += (random.random() - 0.5) * 12
            self.radius -= 0.5
        elif self.tick < 120:
            if self.radius > 0:
                self.radius -= 20
            else:
                self.remove = True
        else:
            self.remove = True

    def noAI(self):
        pass

    def bullet(self):
        pass

    def bouncer(self):
        if self.bounceCount > 3:
            self.remove = True

    def slug(self):
        pass

    def piercer(self):
        pass

    def rebounder(self):
        self.damage = 20 + self.bounceCount * 10
        self.radius = 1 + self.bounceCount * 0.5
        if self.bounceCount > 5:
            self.remove = True

    def bomb(self):
        if self.tick >= 90:
            self.explode("smallExplosion")
            self.remove = True

    def missile(self):
        pass

    def homingBullet(self):
        pass

    def laserPulse(self):
        pass

    def seeker(self):
        self.damage = 20 + self.bounceCount * 5
        self.radius = 2 + self.bounceCount * 0.5
        self.maxVel = 6 + self.bounceCount * 0.5
        self.setSpeed(6 + self.bounceCount * 0.5)
        if self.bounceCount > 5:
            self.remove = True

    def bounceSplitter(self):
        if self.bounceCount >= 1:
            self.split(3, "rebounder", math.pi / 36)
            self.remove = True

    def grenade(self):
        if self.tick < 120:
            self.radius -= 1 / 50
        elif self.tick < 150:
            self.radius -= 1 / 50
            if self.alignedToClosest(0, math.pi / 36, 10):
                self.explode("mediumExplosion")
                self.remove = True
        else:
            self.explode("mediumExplosion")
            self.remove = True

    def vibrator(self):
        if self.vel.magnitude() > 0.2:
            self.slow(0.005)
        else:
            if self.initialTickSave == 0:
                self.initialTickSave = self.tick
                self.explode("smallShockwave")
            elif self.tick == self.initialTickSave + 20:
                self.explode("smallShockwave")
            elif self.tick >= self.initialTickSave + 40:
                self.explode("smallShockwave")
                self.remove = True

    def splitter(self):
        if self.alignedToClosest(200, math.pi / 18, 50):
            self.split(3, "bullet", math.pi / 36)
            self.remove = True

    def shell(self):
        pass

    def homingMissile(self):
        pass

    def laserBeam(self):
        self.angle = approachAngle(self.angle, self.owner.angle, 0.3)

        if self.tick < 20:
            self.radius += (self.tick // 2) ** 4
            self.diameter += 0.2
        elif self.tick < 80:
            if self.diameter < 6:
                if self.diameter > 2:
                    self.diameter += (random.random() - 0.5) * 2
                else:
                    self.diameter += 2
            else:
                self.diameter -= 2
        elif self.tick == 80:
            self.diameter = 4
        elif self.tick < 88:
            self.diameter -= 0.5
        else:
            self.remove = True

    def laserSplitter(self):
        if not self.alreadySplit and self.alignedToClosest(100, math.pi / 36, 20):
            self.split(2, "laserPulse", math.pi / 18)
            self.alreadySplit = True

    def pursuer(self):
        if self.bounceCount + self.collisionCount > 10:
            self.remove = True

    def grenadeSplitter(self):
        if self.bounceCount >= 1:
            self.split(3, "grenade", math.pi / 36)
            self.remove = True

    def plasmaGrenade(self):
        if self.tick < 150:
            self.radius -= 1 / 100
        elif self.tick < 300:
            if self.tick % 60 > 30:
                self.radius += 1 / 5
            else:
                self.radius -= 1 / 5
            if self.alignedToClosest(0, math.pi / 36, 25):
                self.explode("largeExplosion")
                self.remove = True
        else:
            self.explode("largeExplosion")
            self.remove = True

    def pulser(self):
        if self.vel.magnitude() > 0.2:
            self.slow(0.005)
        else:
            if self.tick < self.initialTickSave + 305:
                if (self.tick - self.initialTickSave) % 60 == 5:
                    self.explode("largeShockwave")
                    self.radius = 1
                elif (self.tick - self.initialTickSave) % 60 < 5:
                    self.radius -= 2
                else:
                    self.radius += 0.1
            elif self.tick >= self.initialTickSave + 240:
                self.explode("largeShockwave")
                self.remove = True

    def multiSplitter(self):
        if self.alignedToClosest(200, math.pi / 18, 50):
            self.split(5, "slug", math.pi / 36)
            self.remove = True

    def homingSplitter(self):
        if not self.alreadySplit and self.alignedToClosest(0, math.pi / 18, 500):
            self.initialTickSave = self.tick
            self.alreadySplit = True
        if self.alreadySplit:
            if (
                self.tick == self.initialTickSave
                or self.tick == self.initialTickSave + 20
                or self.tick == self.initialTickSave + 40
                or self.tick == self.initialTickSave + 60
                or self.tick == self.initialTickSave + 80
                or self.tick == self.initialTickSave + 100
                or self.tick == self.initialTickSave + 120
                or self.tick == self.initialTickSave + 140
                or self.tick == self.initialTickSave + 160
            ):
                Projectile.summonByVector(
                    self.pos.x,
                    self.pos.y,
                    0,
                    projectileType="homingBullet",
                    owner=self.owner,
                )
                self.radius -= 0.2
            elif self.tick > self.initialTickSave + 160:
                self.remove = True

    def rocket(self):
        pass

    def homingShell(self):
        pass

    def laserCannon(self):
        self.angle = approachAngle(self.angle, self.owner.angle, 0.3)

        if self.tick < 50:
            self.radius += (self.tick // 10) ** 4
            self.diameter += 0.2
        elif self.tick < 90:
            if self.diameter < 20:
                if self.diameter > 5:
                    self.diameter += (random.random() - 0.5) * 8
                else:
                    self.diameter += 4
            else:
                self.diameter -= 4
        elif self.tick == 90:
            self.diameter = 10
        elif self.tick < 100:
            self.diameter -= 1
        else:
            self.remove = True

    def laserField(self):
        closestEntity = self.findClosest()
        if closestEntity != -1 and self.shootCooldown <= 0:
            vectorToClosest = Vector(
                closestEntity.pos.x - self.pos.x, closestEntity.pos.y - self.pos.y
            )
            Projectile.summonByVector(
                self.pos.x,
                self.pos.y,
                vectorToClosest.angle(),
                projectileType="laserPulse",
                owner=self.owner,
            )
            self.shootCooldown = 20

        self.radius = 2 * math.sin(self.tick / 10) + 5

    def blackhole(self):
        if self.tick > 300:
            self.remove = True

    def smallShockwave(self):
        if self.tick < 20:
            self.radius += 2
        elif self.tick < 24:
            self.diameter -= 1
            self.radius += 2
        else:
            self.remove = True

    def largeShockwave(self):
        if self.tick < 30:
            self.radius += 3
        elif self.tick < 39:
            self.diameter -= 1
            self.radius += 3
        else:
            self.remove = True


class Entity:
    entities = []
    currentIndex = 0

    def __init__(self, x=0, y=0, entityType="noAI"):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        self.movementAcc = Vector(0, 0)
        self.movementVel = Vector(0, 0)
        self.maxMovementAcc = 0.4
        self.maxMovementVel = 2
        self.tick = 0
        self.remove = False
        self.target = 0
        self.type = entityType
        self.invulnerabilityTick = 0
        self.color = (
            (255, 0, 0)
            if self.type == "basic" or self.type == "shooter"
            else (0, 255, 0)
        )
        self.index = Entity.currentIndex
        self.radius = 2
        self.projectileVulnerable = True
        self.shootTick = 0
        self.shootCooldown = 60
        self.damageTick = 0
        self.damageCooldown = 5
        self.health = 100
        self.maxHealth = 100
        self.angle = 0
        self.mass = 1
        Entity.currentIndex += 1

    def __str__(self):
        return "Entity #" + str(self.index) + " of type " + self.type

    def moveTowards(self, vector):
        self.movementAcc.x = vector.x - self.pos.x
        self.movementAcc.y = vector.y - self.pos.y
        self.movementAcc.normalize(self.maxMovementAcc)

    def moveAwayMultiple(self, vectors, radius=-1):
        if len(vectors) != 0:
            differenceVectors = []
            distances = []
            for vector in vectors:
                differenceVectors.append(self.pos.difference(vector))
                distances.append(distance(self.pos, vector))
            largestThreatMultiplier = 0
            largestAngle = 0
            for angle in range(0, 360, 45):
                threatMultiplier = 1
                for i in range(len(vectors)):
                    distanceMultiplier = (
                        math.floor((radius + 1) / (distances[i] + 1))
                        if radius != -1
                        else 1
                    )
                    threatMultiplier = (
                        smallestAngleDifference(
                            differenceVectors[i].angle(), toRadians(angle)
                        )
                        * 180
                        / math.pi
                        * threatMultiplier
                    )
                if threatMultiplier > largestThreatMultiplier:
                    largestThreatMultiplier = threatMultiplier
                    largestAngle = angle
            self.acc = Vector.fromAngle(toRadians(largestAngle), self.maxAcc)

    def moveAway(self, vector):
        self.movementAcc.x = self.pos.x - vector.x
        self.movementAcc.y = self.pos.y - vector.y
        self.movementAcc.normalize(self.maxMovementAcc)

    def stop(self):
        self.movementAcc.y = (
            -sign(self.vel.x + self.movementVel.y) * self.maxMovementAcc
        )
        self.movementAcc.x = (
            -sign(self.vel.x + self.movementVel.x) * self.maxMovementAcc
        )

    def stopX(self):
        self.movementAcc.x = (
            -sign(self.vel.x + self.movementVel.x) * self.maxMovementAcc
        )

    def stopY(self):
        self.movementAcc.y = (
            -sign(self.vel.x + self.movementVel.y) * self.maxMovementAcc
        )

    def setTarget(self, target):
        self.target = target

    def findClosest(self, entityType):
        closestDistance = sys.maxsize
        closestEntity = -1
        for entity in Entity.entities:
            if (
                self.index != entity.index
                and entityType == entity.type
                and distance(self.pos, entity.pos) < closestDistance
            ):
                closestDistance = distance(self.pos, entity.pos)
                closestEntity = entity
        return closestEntity

    def findTargets(self, radius, entityType=-1):
        targets = []
        for entity in Entity.entities:
            condition = entityType == entity.type if entityType != -1 else True
            if (
                self.index != entity.index
                and distance(entity.pos, self.pos) < radius
                and condition
            ):
                targets.append(entity)
        return targets

    def findPositionTargets(self, radius, entityType=-1):
        targets = []
        for entity in Entity.entities:
            condition = entityType == entity.type if entityType != -1 else True
            if (
                self.index != entity.index
                and distance(entity.pos, self.pos) < radius
                and condition
            ):
                targets.append(entity.pos)
        return targets

    def findClosestWall(self, buffer=0):
        wallX = width + buffer if self.pos.x > width / 2 else -buffer
        wallY = height + buffer if self.pos.y > height / 2 else -buffer

        if abs(self.pos.x - wallX) < abs(self.pos.y - wallY):
            return Vector(wallX, self.pos.y)
        else:
            return Vector(self.pos.x, wallY)

    def findClosestCorner(self, buffer=0):
        cornerX = width + buffer if self.pos.x > width / 2 else -buffer
        cornerY = height + buffer if self.pos.y > height / 2 else -buffer

        return Vector(cornerX, cornerY)

    def checkProjectileCollision(self):
        for projectile in Projectile.projectiles:
            if projectile.shape == "ring":
                collisionCondition = (
                    distance(projectile.pos, self.pos)
                    <= projectile.radius + self.radius + projectile.diameter / 2
                    and distance(projectile.pos, self.pos)
                    >= projectile.radius - self.radius - projectile.diameter / 2
                )
            elif projectile.shape == "bullet":
                collisionCondition = (
                    distance(projectile.pos, self.pos)
                    <= projectile.radius + self.radius
                )
            elif projectile.shape == "beam":
                collisionCondition = projectile.line.interceptCircle(
                    self.pos, self.radius
                )
            if projectile.owner != self and collisionCondition:
                projectile.collideWithEntity(self)
                if projectile.collisionDamage and projectile.explosionType == "none":
                    self.damageRequest(
                        projectile.damage, projectile.invincibilityFrames
                    )
                return True
        return False

    def damageRequest(self, damage, invincibilityFrames=30):
        if self.damageTick <= 0:
            self.health -= damage
            self.damageTick = invincibilityFrames

    def render(self):
        pygame.draw.circle(screen, self.color, self.pos.array(), self.radius)

    def renderHealth(self):
        pygame.draw.rect(screen, (50, 50, 50), (self.pos.x - 4, self.pos.y + 4, 8, 2))
        pygame.draw.rect(
            screen,
            gradient((255, 0, 0), (0, 255, 0), self.health / self.maxHealth, 1.3),
            (self.pos.x - 4, self.pos.y + 4, 7 * self.health / self.maxHealth + 1, 2),
        )

    def update(self):
        exec(f"""self.{self.type}()""")

        if self.target != -1 and not self.target.remove:
            self.angle = math.atan2(
                self.target.pos.y - self.pos.y, self.target.pos.x - self.pos.x
            )

        if self.health <= 0:
            self.remove = True

        if self.damageTick > 0:
            self.damageTick -= 1

        self.tick += 1

        if self.shootTick > 0:
            self.shootTick -= 1

        if self.movementAcc.magnitude() > self.maxMovementAcc:
            self.movementAcc.normalize(self.maxMovementAcc)

        self.movementVel.add(self.movementAcc)

        self.vel.add(self.acc)

        if self.movementVel.magnitude() > self.maxMovementVel:
            self.movementVel.normalize(self.maxMovementVel)
        elif round(self.movementVel.magnitude(), 5) < self.maxMovementAcc:
            self.movementVel.zero()

        if round(self.vel.magnitude(), 5) < 0.1:
            self.vel.zero()

        self.pos.add(self.vel)
        self.pos.add(self.movementVel)

        if self.pos.x > width or self.pos.x < 0:
            self.pos.x -= self.vel.x
        if self.pos.y > height or self.pos.y < 0:
            self.pos.y -= self.vel.y

    def basic(self):
        self.target = self.findClosest("scared")

        if self.target != -1:
            distanceToTarget = distance(self.pos, self.target.pos)
            distanceToPlayer = distance(self.pos, player.pos)
            distanceX = self.target.pos.x - self.pos.x
            distanceY = self.target.pos.y - self.pos.y

            if distanceToPlayer < 4:
                pass
                # self.remove = True
            elif distanceToTarget < 200:
                self.moveTowards(self.target.pos.shuffledVector(10))
                if abs(distanceX) < abs(
                    displacement(self.maxAcc, self.vel.x, self.target.vel.x)
                ):
                    self.stopX()
                if abs(distanceY) < abs(
                    displacement(self.maxAcc, self.vel.y, self.target.vel.y)
                ):
                    self.stopY()
            else:
                self.stop()
        else:
            self.stop()

        if self.projectileVulnerable:
            if self.checkProjectileCollision():
                self.remove = True

    def scared(self):
        distanceToPlayer = distance(self.pos, player.pos)

        targets = self.findPositionTargets(200, "shooter")
        closestWall = self.findClosestWall(10)
        if distance(closestWall, self.pos) < 50:
            targets.append(closestWall)
        closestCorner = self.findClosestCorner(10)
        if distance(closestCorner, self.pos) < 50:
            targets.append(closestCorner)

        mouseVector = Vector.fromArray(pygame.mouse.get_pos())
        if mousehold == 2 and distance(mouseVector, self.pos) <= 50:
            targets.append(mouseVector)

        self.target = self.findClosest("shooter")

        if distanceToPlayer < 200:
            targets.append(player.pos)

        if self.target != -1:
            if distance(self.pos, self.target.pos) < 4:
                self.remove = True
            if distanceToPlayer < 5:
                self.remove = True

        if len(targets) > 0:
            self.moveAwayMultiple(targets, 300)
        else:
            self.stop()

        if self.projectileVulnerable:
            self.checkProjectileCollision()

    def shooter(self):
        self.target = self.findClosest("sniper")

        if self.target != -1:
            distanceVector = Vector(
                self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y
            )
            distanceToTarget = distanceVector.magnitude()

            if distanceToTarget < 200:
                if self.shootTick <= 0:
                    projectileType = Gui.unlockedWeapons[weaponSelection]
                    Projectile.summonByVector(
                        self.pos.x,
                        self.pos.y,
                        distanceVector.angle(),
                        0,
                        0,
                        projectileType,
                        self,
                        "sniper",
                    )
                    self.shootTick = projectileConstants[Gui.unlockedWeapons[weaponSelection]].cooldown

            if distanceToTarget < 1000 and distanceToTarget > 150:
                self.moveTowards(self.target.pos.shuffledVector(10))
            else:
                self.stop()
        else:
            self.stop()

        if self.projectileVulnerable:
            self.checkProjectileCollision()

    def sniper(self):
        self.target = self.findClosest("shooter")

        if self.target != -1:
            distanceVector = Vector(
                self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y
            )
            distanceToTarget = distanceVector.magnitude()

            if distanceToTarget < 200:
                if self.shootTick <= 0:
                    projectileType = Gui.unlockedWeapons[weaponSelection]
                    Projectile.summonByVector(
                        self.pos.x,
                        self.pos.y,
                        distanceVector.angle(),
                        0,
                        0,
                        projectileType,
                        self,
                        "shooter",
                    )
                    self.shootTick = projectileConstants[Gui.unlockedWeapons[weaponSelection]].cooldown

            if distanceToTarget < 1000 and distanceToTarget > 150:
                self.moveTowards(self.target.pos.shuffledVector(10))
            else:
                self.stop()
        else:
            self.stop()

        if self.projectileVulnerable:
            self.checkProjectileCollision()

    def noAI(self):
        pass


class Controller:
    def __init__(self):
        self.pos = Vector(0, 0)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        self.maxAcc = 0.2
        self.maxVel = 5
        self.tick = 0
        self.angle = 0
        self.weaponIndex = 0
        self.mouseLine = Line(Vector(mouseX, mouseY), self.pos)
        self.cooldown = 0

    def __str__(self):
        return "The Player"

    def findClosestWall(self):
        wallX = width if self.pos.x > width / 2 else 0
        wallY = height if self.pos.y > height / 2 else 0

        if abs(self.pos.x - wallX) < abs(self.pos.y - wallY):
            return Vector(wallX, self.pos.y)
        else:
            return Vector(self.pos.x, wallY)

    def findClosestCorner(self):
        cornerX = width if self.pos.x > width / 2 else 0
        cornerY = height if self.pos.y > height / 2 else 0

        return Vector(cornerX, cornerY)

    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.pos.array(), 5)

    def update(self):
        self.tick += 1
        self.mouseLine.p1.x = mouseX
        self.mouseLine.p1.y = mouseY
        self.mouseLine.p2 = self.pos

        if self.cooldown > 0:
            self.cooldown -= 1

        self.mouseLine.setLength(1, 3000)

        if self.tick % (FPS / FPS) == 0:
            velocityTime[self.tick % len(velocityTime)] = (
                self.vel.magnitude(),
                self.tick % len(velocityTime),
            )

        if self.acc.magnitude() > self.maxAcc:
            self.acc.normalize(self.maxAcc)

        self.vel.add(self.acc)

        if self.vel.magnitude() > self.maxVel:
            self.vel.normalize(self.maxVel)
        elif round(self.vel.magnitude(), 5) < self.maxAcc:
            self.vel.zero()

        self.pos.add(self.vel)

        self.angle = math.atan2(mouseY - self.pos.y, mouseX - self.pos.x)

        if self.pos.x > width or self.pos.x < 0:
            self.pos.x -= self.vel.x
        if self.pos.y > height or self.pos.y < 0:
            self.pos.y -= self.vel.y

    def controller(self):
        if w_key and s_key:
            self.acc.y = -sign(self.vel.y) * self.maxAcc
        elif w_key:
            self.acc.y = -self.maxAcc
        elif s_key:
            self.acc.y = self.maxAcc
        else:
            self.acc.y = -sign(self.vel.y) * self.maxAcc

        if a_key and d_key:
            self.acc.x = -sign(self.vel.x) * self.maxAcc
        elif a_key:
            self.acc.x = -self.maxAcc
        elif d_key:
            self.acc.x = self.maxAcc
        else:
            self.acc.x = -sign(self.vel.x) * self.maxAcc
        
        if self.cooldown <= 0 and mousehold:
            closestPos = -1
            closestDistance = 50
            for entity in Entity.entities:
                distanceToEntity = distance(entity.pos, Vector(mouseX, mouseY))
                if distanceToEntity < closestDistance:
                    closestDistance = distanceToEntity
                    closestPos = entity.pos

            shootAngle = math.atan2(closestPos.y - self.pos.y, closestPos.x - self.pos.x) if closestPos != -1 else self.angle

            Projectile.summonByVector(
                self.pos.x,
                self.pos.y,
                shootAngle,
                0,
                0,
                Gui.unlockedWeapons[weaponSelection],
                self,
            )

            self.cooldown = projectileConstants[Gui.unlockedWeapons[weaponSelection]].cooldown


class Widgit:
    def __init__(
        self, parentPos, x, y, width, height, widgitType="none", index=0, image="none"
    ):
        self.parentPos = parentPos
        self.relativePos = Vector(x, y)
        self.width, self.height = width, height
        self.widgitType = widgitType
        self.clickStatus = False
        self.holdStatus = False
        self.hoverStatus = False
        self.selectedStatus = False
        self.lockStatus = False
        self.hidden = False
        self.rect = Rect(
            self.relativePos.x + self.parentPos.x,
            self.relativePos.y + self.parentPos.x,
            self.width,
            self.height,
        )
        self.index = index
        self.image = image

    def update(self):
        self.rect.x = self.relativePos.x + self.parentPos.x
        self.rect.y = self.relativePos.y + self.parentPos.y
        self.rect.width = self.width
        self.rect.height = self.height

        self.hoverStatus = self.rect.collidepoint(mouseX, mouseY)
        self.holdStatus = mousehold and self.hoverStatus
        self.clickStatus = mousetick and self.hoverStatus
        if self.clickStatus:
            self.selectedStatus = not self.selectedStatus

        if self.lockStatus:
            self.selectedStatus = False

        exec(f"self.{self.widgitType}()")

    def render(self):
        borderColor = (
            (175, 175, 175)
            if self.selectedStatus and not self.lockStatus
            else (120, 120, 120)
        )
        imageColor = (
            (75, 75, 75)
            if self.selectedStatus and not self.lockStatus
            else (50, 50, 50)
        )
        if self.lockStatus:
            fillColor = (120, 120, 120)
        elif self.hoverStatus:
            fillColor = (160, 160, 160)
        elif self.selectedStatus:
            fillColor = (130, 130, 130)
        else:
            fillColor = (100, 100, 100)

        pygame.draw.rect(screen, fillColor, self.rect)
        pygame.draw.rect(screen, borderColor, self.rect, 2)

        if self.image != "none":
            renderImage(
                self.image,
                self.relativePos.x + self.parentPos.x + (self.width - self.image.get_width()) / 2,
                self.relativePos.y + self.parentPos.y + (self.height - self.image.get_height()) / 2,
                1,
                imageColor
            )

    def none(self):
        pass

    @staticmethod
    def fromArray(array, pos, widgitType):
        widgitWidth = 20
        widgitHeight = 20
        widgits = []
        indexCounter = 0
        for position in array:
            widgits.append(
                Widgit(
                    pos,
                    position[0] - widgitWidth / 2,
                    position[1] - widgitHeight / 2,
                    widgitWidth,
                    widgitHeight,
                    widgitType,
                    indexCounter,
                )
            )
            indexCounter += 1

        return widgits


class Gui:
    guis = []
    unlockedWeapons = []

    def __init__(self, x, y, width, height, guiType="none", widgits=[]):
        self.pos = Vector(x, y)
        self.width, self.height = width, height
        self.hidden = False
        self.widgits = widgits
        self.guiType = guiType

    def render(self):
        pygame.draw.rect(
            screen, (50, 50, 50), Rect(self.pos.x, self.pos.y, self.width, self.height)
        )
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            Rect(self.pos.x, self.pos.y, self.width, self.height),
            5,
        )
        for widgit in self.widgits:
            widgit.update()
            widgit.render()

        exec(f"self.{self.guiType}()")

    def setWidgitRequirements(self, dependentWidgitIndex, independentWidgitIndex):
        self.widgits[dependentWidgitIndex].lockStatus = (
            not self.widgits[independentWidgitIndex].selectedStatus
            or self.widgits[independentWidgitIndex].lockStatus
        )

    @staticmethod
    def guiFromTemplate(x, y, guiType):
        guiTemplate = guiConstants[guiType]
        return Gui(
            x,
            y,
            guiTemplate.width,
            guiTemplate.height,
            guiType,
            Widgit.fromArray(guiTemplate.widgits, Vector(x, y), "none"),
        )

    def weaponSelect(self):
        for i in range(1, 4):
            self.setWidgitRequirements(i, 0)
        for i in range(6):
            self.setWidgitRequirements(4 + i, i // 2 + 1)
        for i in range(10, 14):
            self.setWidgitRequirements(i, i // 2 - 1)
        self.setWidgitRequirements(14, 6)
        self.setWidgitRequirements(15, 7)
        self.setWidgitRequirements(16, 8)
        self.setWidgitRequirements(17, 9)
        self.setWidgitRequirements(18, 9)
        for i in range(19, 28):
            self.setWidgitRequirements(i, i - 9)

        for widgit in self.widgits:
            widgit.image = getImage(f"assets/weapons/{weapons[widgit.index]}.png")

        Gui.unlockedWeapons = []

        for i in range(len(self.widgits)):
            if self.widgits[i].selectedStatus:
                Gui.unlockedWeapons.append(weapons[i])


player = Controller()

testGui = Gui.guiFromTemplate(100, 100, "weaponSelect")
testGui.widgits[0].selectedStatus = True


def draw():
    global weaponSelection

    screen.fill((0, 0, 0))

    if q_tick == 1 or o_key:
        Entity.entities.append(
            Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "shooter")
        )

    if e_tick == 1 or p_key:
        Entity.entities.append(
            Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "sniper")
        )

    if l_tick == 1:
        weaponSelection += 1

    if k_tick == 1:
        weaponSelection -= 1

    if weaponSelection >= len(Gui.unlockedWeapons):
        weaponSelection = 0
    elif weaponSelection < 0:
        weaponSelection = len(Gui.unlockedWeapons) - 1

    if z_tick == 1:
        print(Gui.unlockedWeapons[weaponSelection])

    player.controller()
    player.update()
    player.render()
    # player.findClosestWall().renderPoint()

    # graphVelocity()
    # player.vel.render(player.pos, 15)

    projectilesCopy = []
    projectilesRemoved = 0
    for projectile in Projectile.projectiles:
        projectile.update()
        projectile.render()
        if not projectile.remove:
            projectilesCopy.append(projectile)
        else:
            projectilesRemoved += 1
    Projectile.currentIndex -= projectilesRemoved
    Projectile.projectiles = cloneList(projectilesCopy)

    entitiesCopy = []
    entitiesRemoved = 0
    for entity in Entity.entities:
        entity.update()
        entity.render()
        entity.renderHealth()
        # entity.vel.render(entity.pos, 15)
        if not entity.remove:
            entitiesCopy.append(entity)
        else:
            entitiesRemoved += 1
    Entity.currentIndex -= entitiesRemoved
    Entity.entities = cloneList(entitiesCopy)

    testGui.render()

    #player.mouseLine.renderBoundedLines()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousetick = 1
                mousehold = 1
            elif event.button == 2:
                mousetick = 2
                mousehold = 2
            elif event.button == 3:
                mousetick = 3
                mousehold = 3
        elif event.type == pygame.MOUSEBUTTONUP:
            mousehold = 0

    keys = pygame.key.get_pressed()

    for letter in alphabet:
        exec(f"{letter}_key = True if keys[pygame.K_{letter}] else False")
        if eval(f"{letter}_key"):
            exec(f"{letter}_tick = 1 if {letter}_tick == 0 else {letter}_tick")
        else:
            exec(f"{letter}_tick = 0 if {letter}_tick == -1 else {letter}_tick")

    draw()

    for letter in alphabet:
        exec(f"{letter}_tick = -1 if {letter}_tick == 1 else {letter}_tick")

    mousetick = 0
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    pygame.display.update()
    clock.tick(FPS)
