import pygame
pygame.init()
from pygame.locals import *
import sys
import random
import math
from data.projectileConstants import *

clock = pygame.time.Clock()
FPS = 60
pygame.display.set_caption("test")

width, height = 960, 540
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
running = True
mousetick = 0
mousehold = 0

velocityTime = [(0, 0)] * 400

alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
for letter in alphabet:
    exec(f"{letter}_tick = 0")

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

def graphVelocity():
    for (v, t) in velocityTime:
        pygame.draw.circle(screen, (255, 255, 255), (t * 2, height + (-v * 20)), 1)

def distance(vector1, vector2):
    return ((vector1.x - vector2.x)**2 + (vector1.y - vector2.y)**2)**0.5

def cloneList(l):
    cloned = []
    for item in l:
        cloned.append(item)
    return cloned

def displacement(acc, vel, targetVel = 0):
    return (targetVel**2 - vel**2) / 2 / acc

def smallestAngleDifference(angle1, angle2):
    angleDiff = abs(angle1 - angle2)
    if angleDiff > math.pi:
        return 2 * math.pi - angleDiff
    else:
        return angleDiff

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

def gradient(color1, color2, percentage, brightnessPercentage = 1):
    redDiff = color2[0] - color1[0]
    greenDiff = color2[1] - color1[1]
    blueDiff = color2[2] - color1[2]
    return colorCheck((color1[0] * brightnessPercentage + redDiff * percentage,
                      color1[1] * brightnessPercentage + greenDiff * percentage,
                      color1[2] * brightnessPercentage + blueDiff * percentage
    ))

def inBetween(p1, p2, pointer):
    return (pointer >= p1 and pointer <= p2) or (pointer <= p1 and pointer >= p2)

def inBetweenOrdered(PMin, PMax, pointer):
    return (PMin <= pointer and PMax >= pointer)

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
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self, magnitude):
        distance = math.sqrt(self.x ** 2 + self.y ** 2)
        if distance != 0:
            self.x *= magnitude / distance
            self.y *= magnitude / distance
            return Vector(self.x, self.y)
        return Vector(0, 0)
    
    def normalized(self, magnitude):
        distance = math.sqrt(self.x ** 2 + self.y ** 2)
        return Vector(self.x * magnitude / distance, self.y * magnitude / distance) if distance != 0 else Vector(0, 0)

    def shuffledVector(self, uncertainty):
        return Vector(self.x + (random.random() - 0.5) * uncertainty, self.y + (random.random() - 0.5) * uncertainty)

    def zero(self):
        self.x = 0
        self.y = 0

    def angle(self):
        return math.atan2(self.y, self.x)

    def render(self, pos, multiplier = 1):
        pygame.draw.line(screen, (255, 255, 255), pos.array(), (pos.x + self.x * multiplier, pos.y + self.y * multiplier))

    def renderPoint(self):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 2)

    def renderPoint(self):
        pygame.draw.circle(screen, (255, 255, 255), self.array(), 5)

    def rotate(self, angle):
        return Vector.fromAngle(self.angle() + angle, self.magnitude())

    @staticmethod
    def fromAngle(angle, magnitude = 1):
        return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @staticmethod
    def fromArray(array):
        return Vector(array[0], array[1])
    
    @staticmethod
    def fromVector(vector):
        return Vector(vector.x, vector.y)
    
class Line:
    def __init__(self, p1, p2, diameter = 1):
        self.p1 = p1
        self.p2 = p2
        self.diameter = diameter
    
    def getSlope(self):
        if self.p1.x - self.p2.x == 0:
            return float('inf')
        else:
            return (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)
        
    
    def getAngle(self):
        return math.atan2(self.p2.y - self.p1.y, self.p2.x - self.p1.x)
        
    def getYIntercept(self):
        return self.p1.y - self.getSlope() * self.p1.x
    
    def getIntercection(self, line, b = "null"):
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
        if thisSlope == float('inf'):
            perpendicularSlope = 0
        elif thisSlope == 0:
            perpendicularSlope = float('inf')
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
    
    def render(self, color):
        vectorDiff = self.p1.difference(self.p2)
        points = (self.p1.added(vectorDiff.rotate(math.pi / 2).normalized(self.diameter / 2)).array(),
                  self.p1.added(vectorDiff.rotate(-math.pi / 2).normalized(self.diameter / 2)).array(),
                  self.p2.added(vectorDiff.rotate(-math.pi / 2).normalized(self.diameter / 2)).array(),
                  self.p2.added(vectorDiff.rotate(math.pi / 2).normalized(self.diameter / 2)).array()
                  )
        pygame.draw.polygon(screen, color, points)
        pygame.draw.circle(screen, color, self.p1.array(), self.diameter / 2)
        pygame.draw.circle(screen, color, self.p2.array(), self.diameter / 2)


        #pygame.draw.line(screen, color, self.p1.array(), self.p2.array(), self.diameter)
    
class Projectile:
    projectiles = []
    currentIndex = 0
    def __init__(self, x = 0, y = 0, vx = 0, vy = 0, ax = 0, ay = 0, projectileType = "noAI", owner = -1, targetType = -1, angle = 0):
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
        self.line = Line(self.pos, Vector(self.pos.x + self.radius * math.cos(self.angle), self.pos.y + self.radius * math.sin(self.angle)), self.diameter) if self.shape == "beam" else Line(self.pos, self.pos, self.radius * 2)
        Entity.currentIndex += 1

    def conditionalRemove(self):
        self.remove = True

    def collideWithEntity(self):
        if not self.piercing:
            self.remove = True
        self.collisionCount += 1
    
    def findClosest(self, entityType = -1):
        closestDistance = sys.maxsize
        closestEntity = -1
        for entity in Entity.entities:
            condition = entityType == entity.type if entityType != -1 else True
            if condition and distance(self.pos, entity.pos) < closestDistance:
                closestDistance = distance(self.pos, entity.pos)
                closestEntity = entity
        return closestEntity
    
    def stop(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopX(self):
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopY(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc

    def findTargets(self, radius, entityType = -1):
        targets = []
        for entity in Entity.entities:
            condition = entity.type == entityType if entityType != -1 else True
            if distance(entity.pos, self.pos) < radius and condition:
                targets.append(entity)
        return targets

    @staticmethod
    def summonByVector(x, y, angle, vel = 0, acc = 0, projectileType = "noAI", owner = -1, targetType = -1):
        if vel == 0:
            vel = projectileConstants[projectileType].startSpeed
        Projectile.projectiles.append(Projectile(x, y, vel * math.cos(angle), vel * math.sin(angle), acc * math.cos(angle), vel * math.sin(angle), projectileType, owner, targetType, angle = angle))

    def render(self):
        if self.shape == "ring":
            pygame.draw.circle(screen, (0, 255, 255), self.pos.array(), self.radius, self.diameter)
        elif self.shape == "bullet":
            pygame.draw.circle(screen, (0, 255, 255), self.pos.array(), self.radius)
        elif self.shape == "beam":
            self.line.render((0, 255, 255))

    def update(self):
        exec(f'''self.{self.type}()''')
        
        self.tick += 1

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
            if self.pos.x > width or self.pos.x < 0:
                self.pos.x -= self.vel.x
                self.vel.x = -self.vel.x
                self.bounceCount += 1
            if self.pos.y > height or self.pos.y < 0:
                self.pos.y -= self.vel.y
                self.vel.y = -self.vel.y
                self.bounceCount += 1
        else:
            if self.pos.x > width or self.pos.x < 0 or self.pos.y > height or self.pos.y < 0:
                self.remove = True

    def noAI(self):
        pass

    def bouncy(self):
        if self.bounceCount > 3:
            self.remove = True

    def large(self):
        self.radius += 0.1

    def explosion(self):
        if self.tick < 2:
            self.radius += 12
        elif self.tick < 10:
            self.radius -= 3
        else:
            self.remove = True
    
    def homing(self):
        closestEntity = self.findClosest(self.targetType)
        if closestEntity != -1:
            distanceToClosest = distance(self.pos, closestEntity.pos)
            distanceVector = Vector(closestEntity.pos.x - self.pos.x, closestEntity.pos.y - self.pos.y)
            distanceVector.normalize(self.maxAcc)
            distanceX = abs(self.pos.x - closestEntity.pos.x)
            distanceY = abs(self.pos.y - closestEntity.pos.y)
            if distanceToClosest < 200:
                self.acc = distanceVector
                if abs(distanceX) < abs(displacement(self.maxAcc, self.vel.x, closestEntity.vel.x)):
                    self.stopX()
                if abs(distanceY) < abs(displacement(self.maxAcc, self.vel.y, closestEntity.vel.y)):
                    self.stopY()

    def scatter(self):
        closestEntity = self.findClosest(self.targetType)
        if closestEntity != -1 and closestEntity != self.owner:
            distanceVector = Vector(closestEntity.pos.x - self.pos.x, closestEntity.pos.y - self.pos.y)
            self.homing()
            if distanceVector.magnitude() < 100 and abs(self.vel.angle() - distanceVector.angle()) < math.pi / 36:
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 9, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 12, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 18, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 36, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle(), 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 36, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 18, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 12, 0, projectileType = "missile")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 9, 0, projectileType = "missile")
                self.remove = True

    def missile(self):
        #self.homing()
        if self.remove:
            Projectile.summonByVector(self.pos.x, self.pos.y, 0, 0, projectileType = "shockwave")
            Projectile.summonByVector(self.pos.x, self.pos.y, 0, 0, projectileType = "explosion")

    def shockwave(self):
        if self.tick < 30:
            self.radius += 5
        elif self.tick < 35:
            self.diameter -= 1
            self.radius += 5
        else:
            self.remove = True
        
    def laser(self):
        pass

    def energyBeam(self):
        self.angle += (self.owner.angle - self.angle) / 5
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

class Entity:
    entities = []
    currentIndex = 0
    def __init__(self, x = 0, y = 0, entityType = "noAI"):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        self.maxAcc = 0.4
        self.maxVel = 2
        self.tick = 0
        self.remove = False
        self.target = 0
        self.type = entityType
        self.invulnerabilityTick = 0
        self.color = (255, 0, 0) if self.type == "basic" or self.type == "shooter" else (0, 255, 0)
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
        Entity.currentIndex += 1

    def moveTowards(self, vector):
        self.acc.x = vector.x - self.pos.x
        self.acc.y = vector.y - self.pos.y
        self.acc.normalize(self.maxAcc)

    def moveAwayMultiple(self, vectors, radius = -1):
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
                    distanceMultiplier = math.floor((radius + 1) / (distances[i] + 1)) if radius != -1 else 1
                    threatMultiplier = smallestAngleDifference(differenceVectors[i].angle(), toRadians(angle)) * 180 / math.pi * threatMultiplier
                if threatMultiplier > largestThreatMultiplier:
                    largestThreatMultiplier = threatMultiplier
                    largestAngle = angle
            self.acc = Vector.fromAngle(toRadians(largestAngle), self.maxAcc)

    def moveAway(self, vector):
        self.acc.x = self.pos.x - vector.x
        self.acc.y = self.pos.y - vector.y
        self.acc.normalize(self.maxAcc)
        
    def stop(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopX(self):
        self.acc.x = -sign(self.vel.x) * self.maxAcc

    def stopY(self):
        self.acc.y = -sign(self.vel.y) * self.maxAcc

    def setTarget(self, target):
        self.target = target

    def findClosest(self, entityType):
        closestDistance = sys.maxsize
        closestEntity = -1
        for entity in Entity.entities:
            if self.index != entity.index and entityType == entity.type and distance(self.pos, entity.pos) < closestDistance:
                closestDistance = distance(self.pos, entity.pos)
                closestEntity = entity
        return closestEntity   

    def findTargets(self, radius, entityType = -1):
        targets = []
        for entity in Entity.entities:
            condition = entityType == entity.type if entityType != -1 else True
            if self.index != entity.index and distance(entity.pos, self.pos) < radius and condition:
                targets.append(entity)
        return targets

    def findPositionTargets(self, radius, entityType = -1):
        targets = []
        for entity in Entity.entities:
            condition = entityType == entity.type if entityType != -1 else True
            if self.index != entity.index and distance(entity.pos, self.pos) < radius and condition:
                targets.append(entity.pos)
        return targets

    def findClosestWall(self, buffer = 0):
        wallX = width + buffer if self.pos.x > width / 2 else -buffer
        wallY = height + buffer if self.pos.y > height / 2 else -buffer

        if abs(self.pos.x - wallX) < abs(self.pos.y - wallY):
            return Vector(wallX, self.pos.y)
        else:
            return Vector(self.pos.x, wallY)

    def findClosestCorner(self, buffer = 0):
        cornerX = width + buffer if self.pos.x > width / 2 else -buffer
        cornerY = height + buffer if self.pos.y > height / 2 else -buffer

        return Vector(cornerX, cornerY)

    def checkProjectileCollision(self):
        for projectile in Projectile.projectiles:
            if projectile.shape == "ring":
                collisionCondition = distance(projectile.pos, self.pos) <= projectile.radius + self.radius + projectile.diameter / 2 and distance(projectile.pos, self.pos) >= projectile.radius - self.radius - projectile.diameter / 2
            elif projectile.shape == "bullet":
                collisionCondition = distance(projectile.pos, self.pos) <= projectile.radius + self.radius
            elif projectile.shape == "beam":
                collisionCondition = projectile.line.interceptCircle(self.pos, self.radius)
            if projectile.owner != self and collisionCondition:
                projectile.collideWithEntity()
                self.damageRequest(projectile.damage)
                return True
        return False
    
    def damageRequest(self, damage):
        if self.damageTick <= 0:
            self.health -= damage
            self.damageTick = self.damageCooldown
    
    def render(self):
        pygame.draw.circle(screen, self.color, self.pos.array(), self.radius)

    def renderHealth(self):
        pygame.draw.rect(screen, (50, 50, 50), (self.pos.x - 4, self.pos.y + 4, 8, 2))
        pygame.draw.rect(screen, gradient((255, 0, 0), (0, 255, 0), self.health / self.maxHealth, 1.3), (self.pos.x - 4, self.pos.y + 4, 7 * self.health / self.maxHealth + 1, 2))
        
    def update(self):
        exec(f'''self.{self.type}()''')

        if self.target != -1 and not self.target.remove:
            self.angle = math.atan2(self.target.pos.y - self.pos.y, self.target.pos.x - self.pos.x)

        if self.health <= 0:
            self.remove = True
        
        if self.damageTick > 0:
            self.damageTick -= 1
        
        self.tick += 1

        if self.shootTick > 0:
            self.shootTick -= 1

        if self.acc.magnitude() > self.maxAcc:
            self.acc.normalize(self.maxAcc)

        self.vel.add(self.acc)

        if self.vel.magnitude() > self.maxVel:
            self.vel.normalize(self.maxVel)
        elif round(self.vel.magnitude(), 5) < self.maxAcc:
            self.vel.zero()

        self.pos.add(self.vel)

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
                #self.remove = True
            elif distanceToTarget < 200:
                self.moveTowards(self.target.pos.shuffledVector(10))
                if abs(distanceX) < abs(displacement(self.maxAcc, self.vel.x, self.target.vel.x)):
                    self.stopX()
                if abs(distanceY) < abs(displacement(self.maxAcc, self.vel.y, self.target.vel.y)):
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
            distanceVector = Vector(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
            distanceToTarget = distanceVector.magnitude()

            if distanceToTarget < 500:
                if self.shootTick <= 0:
                    projectileType = "energyBeam" if random.randint(1, 100) < 80 else "energyBeam"
                    Projectile.summonByVector(self.pos.x, self.pos.y, distanceVector.angle(), 0, 0, projectileType, self, "sniper")
                    self.shootTick = 120

            if distanceToTarget < 1000 and distanceToTarget > 50:
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
            distanceVector = Vector(self.target.pos.x - self.pos.x, self.target.pos.y - self.pos.y)
            distanceToTarget = distanceVector.magnitude()

            if distanceToTarget < 400:
                if self.shootTick <= 0:
                    projectileType = "noAI" if random.randint(1, 100) < 90 else "noAI"
                    Projectile.summonByVector(self.pos.x, self.pos.y, distanceVector.angle(), 0, 0, projectileType, self, "shooter")
                    self.shootTick = 1000

            if distanceToTarget < 600 and distanceToTarget > 500:
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
        if self.tick % (FPS / FPS) == 0:
            velocityTime[self.tick % len(velocityTime)] = (self.vel.magnitude(), self.tick % len(velocityTime))

        if self.acc.magnitude() > self.maxAcc:
            self.acc.normalize(self.maxAcc)

        self.vel.add(self.acc)

        if self.vel.magnitude() > self.maxVel:
            self.vel.normalize(self.maxVel)
        elif round(self.vel.magnitude(), 5) < self.maxAcc:
            self.vel.zero()

        self.pos.add(self.vel)

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

player = Controller()
#exampleEntity = Entity()
#exampleEntity.pos.x = 200
#exampleEntity.pos.y = 200
#Entity.entities.append(exampleEntity)

#for i in range(50):
#    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "scared"))
#    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "scared"))
#    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "basic"))
#    Entity.entities[-1].target = Entity.entities[-2]
#    Entity.entities[-2].target = Entity.entities[-1]
#    Entity.entities[-3].target = Entity.entities[-1]
#
#    Entity.entities[-1].maxVel = 0.4
#    Entity.entities[-1].maxAcc = 0.04

def draw():
    global prey
    
    screen.fill((0, 0, 0))
    
    #if random.randint(0, 100) > 98:
    #    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "scared"))
    #    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "scared"))
    #    Entity.entities.append(Entity(random.randint(0, width), random.randint(0, height), "basic"))
    #    Entity.entities[-1].target = Entity.entities[-2]
    #    Entity.entities[-2].target = Entity.entities[-1]
    #    Entity.entities[-3].target = Entity.entities[-1]
    #
    #    Entity.entities[-1].maxVel = 0.4
    #    Entity.entities[-1].maxAcc = 0.04

    if q_tick == 1:
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "shooter"))

    if e_tick == 1 or r_tick == 1 or t_tick == 1 or y_tick == 1:
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "sniper"))

    if mousetick:
        Projectile.summonByVector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], random.randint(0, 360), 0, projectileType = "laser")

    player.controller()
    player.update()
    player.render()
    player.findClosestWall().renderPoint()
    
    graphVelocity()
    player.vel.render(player.pos, 15)

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
        #entity.vel.render(entity.pos, 15)
        if not entity.remove:
            entitiesCopy.append(entity)
        else:
            entitiesRemoved += 1
    Entity.currentIndex -= entitiesRemoved
    Entity.entities = cloneList(entitiesCopy)
    
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
            else:
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
    pygame.display.update()
    clock.tick(FPS)
