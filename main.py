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

    def rotate(self, angle):
        return Vector.fromAngle(self.angle() + angle, self.magnitude())

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
        self.buffer = 5
        self.type = projectileType
        self.radius = projectileConstants[projectileType].radius
        self.bounceOnWall = projectileConstants[projectileType].bounceOnWall
        self.piercing = projectileConstants[projectileType].piercing
        self.index = Projectile.currentIndex
        self.maxVel = projectileConstants[projectileType].startSpeed
        self.maxAcc = projectileConstants[projectileType].startSpeed / 5
        self.bounceCount = 0
        self.collisionCount = 0
        Entity.currentIndex += 1

    def conditionalRemove(self):
        self.remove = True

    def collideWithEntity(self):
        if not self.piercing:
            self.remove = True
        self.collisionCount += 1
    
    def findClosest(self, entityType = -1):
        condition = entityType == entity.type if entityType != -1 else True
        closestDistance = sys.maxsize
        closestEntity = -1
        for entity in Entity.entities:
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

    @staticmethod
    def summonByVector(x, y, angle, vel = 0, acc = 0, projectileType = "noAI", owner = -1):
        if vel == 0:
            vel = projectileConstants[projectileType].startSpeed
        Projectile.projectiles.append(Projectile(x, y, vel * math.cos(angle), vel * math.sin(angle), acc * math.cos(angle), vel * math.sin(angle), projectileType, owner))

    def render(self):
        pygame.draw.circle(screen, (0, 255, 255), self.pos.array(), self.radius)
        
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
        self.radius += 1
        if self.tick > 30:
            self.remove = True
    
    def homing(self):
        closestEntity = self.findClosest()
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
        closestEntity = self.findClosest()
        if closestEntity != -1:
            distanceVector = Vector(closestEntity.pos.x - self.pos.x, closestEntity.pos.y - self.pos.y)
            self.homing()
            if distanceVector.magnitude() < 75 and abs(self.vel.angle() - distanceVector.angle()) < math.pi / 36:
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 18, 0, projectileType = "bouncy")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() + math.pi / 36, 0, projectileType = "bouncy")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle(), 0, projectileType = "bouncy")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 36, 0, projectileType = "bouncy")
                Projectile.summonByVector(self.pos.x, self.pos.y, self.vel.angle() - math.pi / 18, 0, projectileType = "bouncy")
                self.remove = True

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
        self.projectileVulnerable = True
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
            if projectile.owner != self and distance(projectile.pos, self.pos) <= projectile.radius + self.radius:
                projectile.collideWithEntity()
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
        
        targets = self.findPositionTargets(200)
        closestWall = self.findClosestWall(10)
        if distance(closestWall, self.pos) < 50:
            targets.append(closestWall)
        closestCorner = self.findClosestCorner(10)
        if distance(closestCorner, self.pos) < 50:
            targets.append(closestCorner)

        mouseVector = Vector.fromArray(pygame.mouse.get_pos())
        if mousehold == 2 and distance(mouseVector, self.pos) <= 50:
            targets.append(mouseVector)

        self.target = self.findClosest("basic")

        if distanceToPlayer < 200:
            targets.append(player.pos)

        if self.target != -1:
            if distance(self.pos, self.target.pos) < 4:
                self.remove = True
            if distanceToPlayer < 5:
                self.remove = True
        
        if len(targets) > 0:
            self.moveAwayMultiple(targets, 200)
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
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "basic"))
        Entity.entities[-1].maxVel = 1 + random.random() * 0.6
        Entity.entities[-1].maxAcc = 0.1

    if e_tick == 1:
        Entity.entities.append(Entity(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], "scared"))

    if mousetick:
        Projectile.summonByVector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], random.randint(0, 360), 0, projectileType = "scatter")
        
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
