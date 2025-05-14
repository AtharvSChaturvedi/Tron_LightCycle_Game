import pygame as py

class Player:
    def __init__(self, x, y, color, direction="UP"):
        self.x=x
        self.y=y
        self.color=color
        self.direction=direction
        self.trail=[(x, y)]
        self.alive=True

    def handle_input(self, keys):
        if keys.get("up") and self.direction!="DOWN":
            self.direction="UP"
        elif keys.get("down") and self.direction!="UP":
            self.direction="DOWN"
        elif keys.get("left") and self.direction!="RIGHT":
            self.direction="LEFT"
        elif keys.get("right") and self.direction!="LEFT":
            self.direction="RIGHT"

    def move(self):
        if self.direction=="UP":
            self.y-=1
        elif self.direction=="DOWN":
            self.y+=1
        elif self.direction=="LEFT":
            self.x-=1
        elif self.direction=="RIGHT":
            self.x+=1
        self.trail.append((self.x, self.y))

    def check_collision(self,cols,rows,all_trails):
        if (self.x,self.y) in all_trails or not (0<=self.x<cols and 0<=self.y<rows):
            self.alive=False

    def draw(self,screen,tile_size):
        for tx, ty in self.trail:
            rect=py.Rect(tx*tile_size,ty*tile_size,tile_size,tile_size)
            py.draw.rect(screen,self.color,rect)
