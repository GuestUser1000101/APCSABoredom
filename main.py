import pygame
pygame.init()
from pygame.locals import *
import sys
import random
import math
import numpy as np

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

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def array(self):
        return (self.x, self.y)

    def add(self, vec):
        self.x += vec.x
        self.y += vec.y

    def difference(self, vec):
        return Vector(vec.x - self.x, vec.y - self.y)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self, magnitude):
        distance = math.sqrt(self.x ** 2 + self.y ** 2)
        if distance != 0:
            self.x *= magnitude / distance
            self.y *= magnitude / distance

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
        pygame.draw.circle(screen, (255, 255, 255), self.array(), 5)

    @staticmethod
    def fromAngle(angle, magnitude = 1):
        return Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @staticmethod
    def fromArray(array):
        return Vector(array[0], array[1])

class Projectile:
    projectiles = []
    currentIndex = 0
    def __init__(self, x = 0, y = 0, vx = 0, vy = 0, ax = 0, ay = 0, projectileType = "noAI", owner = -1):
        self.pos = Vector(x, y)
        self.vel = Vector(vx, vy)
        self.acc = Vector(0, 0)
        self.tick = 0
        self.owner = owner
        self.remove = False
        self.radius = 1
        self.buffer = 5
        Entity.currentIndex += 1

    def conditionalRemove(self):
        self.remove = True

    @staticmethod
    def summonByVector(x, y, angle, vel, acc = 0, projectileType = "noAI", owner = -1):
        Projectile.projectiles.append(x, y, vel * math.cos(angle), vel * math.sin(angle), acc * math.cos(angle), vel * math.sin(angle), projectileType, owner)

    def render(self):
        pygame.draw.circle(screen, (0, 255, 255), self.pos.array(), self.radius)
        
    def update(self):
        exec(f'''self.{self.type}()''')
        
        self.tick += 1

        self.vel.add(self.acc)
        self.pos.add(self.vel)

        if self.pos.x > width or self.pos.x < 0:
            self.pos.x -= self.vel.x
            self.vel.x = -self.vel.x
        if self.pos.y > height or self.pos.y < 0:
            self.pos.y -= self.vel.y
            self.vel.y = -self.vel.y

    def noAI(self):
        pass

class Entity:
    entities = []
    currentIndex = 0
    def __init__(self, x = 0, y = 0, entityType = "noAI"):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        self.maxAcc = 0.4
        self.maxVel = random.random() * 2
        self.tick = 0
        self.remove = False
        self.target = 0
        self.type = entityType
        self.invulnerabilityTick = 0
        self.color = (255, 0, 0) if self.type == "basic" else (0, 255, 0)
        self.index = Entity.currentIndex
        self.radius = 2
        Entity.currentIndex += 1

    def moveTowards(self, vector):
        self.acc.x = vector.x - self.pos.x
        self.acc.y = vector.y - self.pos.y
        self.acc.normalize(self.maxAcc)

    def moveAwayMultiple(self, vectors):
        if len(vectors) != 0:
            differenceVectors = []
            for vector in vectors:
                differenceVectors.append(self.pos.difference(vector))
            largestThreatMultiplier = 0
            largestAngle = 0
            for angle in range(0, 360, 45):
                threatMultiplier = 1
                for vector in differenceVectors:
                    threatMultiplier = smallestAngleDifference(vector.angle(), toRadians(angle)) * 180 / math.pi * threatMultiplier
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
                

    def findTargets(self, radius):
        targets = []
        for entity in Entity.entities:
            if self.index != entity.index and distance(entity.pos, self.pos) < radius and entity.type == "basic":
                targets.append(entity)
        return targets

    def findPositionTargets(self, radius):
        targets = []
        for entity in Entity.entities:
            if self.index != entity.index and distance(entity.pos, self.pos) < radius and entity.type == "basic":
                targets.append(entity.pos)
        return targets

    def findClosestWall(self, radius = -1):
        wallX = width if self.pos.x > width / 2 else 0
        wallY = height if self.pos.y > height / 2 else 0

        if abs(self.pos.x - wallX) < abs(self.pos.y - wallY):
            return Vector(wallX, self.pos.y)
        else:
            return Vector(self.pos.x, wallY)

    def checkProjectileCollision(self):
        for projectile in Projectile:
            if projectile.owner != self and distance(projectile.pos, self.pos) <= projectile.radius + self.radius:
                projectile.conditionalRemove()
                return True
        return False
    
    def render(self):
        pygame.draw.circle(screen, self.color, self.pos.array(), self.radius)
        
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
                self.remove = True
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


    def scared(self):
        targets = self.findPositionTargets(150)
        closestWall = self.findClosestWall()
        if distance(closestWall, self.pos) < 50:
            targets.append(closestWall)

        mouseVector = Vector.fromArray(pygame.mouse.get_pos())
        if mousehold == 2 and distance(mouseVector, self.pos) <= 50:
            targets.append(mouseVector)

        self.target = self.findClosest("basic")

        if self.target != -1:

            if distance(self.pos, self.target.pos) < 4:
                self.remove = True
        
        if len(targets) > 0:
            self.moveAwayMultiple(targets)
        else:
            self.stop()

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

    if q_key:
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "basic"))
        Entity.entities[-1].maxVel = 1 + random.random() * 0.6
        Entity.entities[-1].maxAcc = 0.1

    if e_key:
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "scared"))
        
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
        entity.vel.render(entity.pos, 15)
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

    draw()
    mousetick = 0
    pygame.display.update()
    clock.tick(FPS)