import pygame as pg
import sys,time
import numpy as np
from perlin_noise import PerlinNoise
import numba
from pytools import P

TILW:int = 30
TILH:int = 20
MAPW,MAPH = (20,25)
SC_SIZE = SW,SH = ((MAPW+2)*TILW*1.5,(MAPH+2)*TILH*1.3)
Z_TO_Y = 200
WATER_LEVEL = 0.6


def clamp(val,minv,maxv):
    return max(minv, min(val, maxv))

@numba.jit
def waterclamp(val:float,minv:float,maxv:float):
    return max(minv, min(val, maxv))

noise1 = PerlinNoise(octaves=3)
@numba.jit(nopython=True)
def fast(x:int,y:int,z_map):
    if (x+1) == len(z_map[y]):
        xp1:int = x
    else:
        xp1:int = x+1

    if (y+1) == len(z_map):
        yp1:int = y
    else:
        yp1:int = y+1
    
    upleft = (x*TILW,   y*TILH + waterclamp(z_map[y][x],0.001,WATER_LEVEL)*Z_TO_Y )
    upright = (xp1*TILW,   y*TILH + waterclamp(z_map[y][xp1],0.001,WATER_LEVEL)*Z_TO_Y)
    downleft = (x*TILW,   yp1*TILH + waterclamp(z_map[yp1][x],0.001,WATER_LEVEL)*Z_TO_Y )
    downright = (xp1*TILW,   yp1*TILH + waterclamp(z_map[yp1][xp1],0.001,WATER_LEVEL)*Z_TO_Y )

    return upleft,upright,downleft,downright

class MapManager:
    def __init__(self,app) -> None:
        self.app = app
        self.z_map = np.zeros((MAPH,MAPW),dtype=float)
        self.xoffset = 0
        self.yoffset = 0
        self.generate()
        self.surface = pg.surface.Surface(SC_SIZE)

    def update(self,dt):
        #self.xoffset += dt*0.007
        self.surface.fill("black")
        #self.yoffset += dt*0.007
        self.generate()
        self.render_map()

    def generate(self):
        st = time.time()
        xwidth = len(self.z_map[0])
        yheight = len(self.z_map)
        for x in range(xwidth):
            for y in range(yheight):
                self.z_map[y][x] = noise1([(x+self.xoffset)/xwidth, (y+self.yoffset)/yheight])+0.5
        #print("It took {} seconds to make map".format(time.time()-st))

    def render_map(self):
        start_val = 100
        fog = start_val
        y = 0
        for line in self.z_map:
            x = 0
            for tile in line:
                self.Draw_Tile(x,y,fog)
                x += 1
            fog -= start_val/len(self.z_map)
            y += 1
    
    def display_map(self):
        w = (MAPW*TILW) - TILW
        h =  ((MAPH+10)*TILH) - TILH 
        rect = (TILW,
         TILH,
         clamp(w/self.app.zoomlevel,1,self.surface.get_width()-TILW),
         clamp(h/self.app.zoomlevel,1,self.surface.get_height()-TILH) )
        surf = self.surface.subsurface(rect)
        scaled_surf = pg.transform.scale(surf,(surf.get_width()*self.app.zoomlevel,surf.get_height()*self.app.zoomlevel))
        self.app.screen.blit(
            scaled_surf,(SW//2-(scaled_surf.get_width()//2),SH//2-(scaled_surf.get_height()//2) ) )
    
    def Draw_Tile(self,x,y,fog):
        multiplier = 2.2
        color = (clamp(255-fog*multiplier,0,255),clamp(255-fog*multiplier,0,255),clamp(255-fog*multiplier,0,255))
        
        color = (0,clamp(255-fog*2.5,0,255),clamp(fog*0.7,0,255))
        if self.z_map[y][x] > WATER_LEVEL:
            color = (0,0,clamp(160-fog*0.9,0,255))

        upleft,upright,downleft,downright = fast(x,y,self.z_map)

        #pg.draw.polygon(self.surface,color,[upleft,upright,downright,downleft],2)
        #pg.draw.polygon(self.surface,color,[upleft,downright,downleft])

        #pg.draw.polygon(self.surface,color,[upleft,upright,downleft,downright])
        pg.draw.polygon(self.surface,color,[upleft,upright,downright,downleft])

        #pg.draw.polygon(self.surface,(30,30,30),[upleft,upright,downright,downleft],1) #DEBUG LINES

        # if color == "blue":
        #     pg.draw.polygon(self.surface,color,[upleft,upright,downright,downleft],1) #DEBUG LINES
        # else:
        #     pg.draw.polygon(self.surface,color,[upleft,upright,downright,downleft],1) #DEBUG LINES
        #pg.draw.polygon(self.surface,"white",[upleft,downright,downleft],1) #DEBUG LINES

        #pg.draw.line(self.surface,color,upleft,upright,1) #line to the right
        #pg.draw.line(self.surface,color,upleft,downleft,1) #line to the down
        #pg.draw.line(self.surface,color,upleft,downright,3) #line to the down-right

        #pg.draw.circle(self.surface,color,upleft,1) # point
        #pg.draw.circle(self.surface,color,upleft,2) # point
        #pg.draw.line(self.surface,"black",upleft,upright,1) #line to the right
        #pg.draw.line(self.surface,"black",upleft,downleft,1) #line to the down
        #pg.draw.line(self.surface,color,upleft,downright,3) #line to the down-right

class App:
    def __init__(self) -> None:
        self.screen = pg.display.set_mode(SC_SIZE)
        self.clock = pg.time.Clock()
        self.dtcounter = 0
        self.zoomlevel = 1
        self.xoffset = 0
        self.yoffset = 0

    def run(self):
        self.mapmanager = MapManager(self)

        while True:
            self.dt = self.clock.tick(120)
            self.dtcounter += self.dt
            pg.display.set_caption(str(self.clock.get_fps()))

            self.screen.fill("black")

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()

            if pg.mouse.get_pressed()[0]:
                self.zoomlevel += clamp(self.zoomlevel*0.1,0.0075*self.dt,self.zoomlevel*0.6) #0.0075*self.dt
            elif pg.mouse.get_pressed()[2]:
                self.zoomlevel += -clamp(self.zoomlevel*0.1,0.001*self.dt,self.zoomlevel*0.1) #0.0075*self.dt

            keys = pg.key.get_pressed()
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                #self.xoffset += 1*self.dt
                self.mapmanager.xoffset -= 0.01*self.dt
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                #self.xoffset -= 1*self.dt
                self.mapmanager.xoffset += 0.01*self.dt

            if keys[pg.K_w] or keys[pg.K_UP]:
                #self.yoffset += 1*self.dt
                self.mapmanager.yoffset -= 0.01*self.dt
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                #self.yoffset -= 1*self.dt
                self.mapmanager.yoffset += 0.01*self.dt
            
            self.zoomlevel = clamp(self.zoomlevel,0.1,5)

            self.mapmanager.update(self.dt) #maybe wanteddt instead of dt
            
            self.mapmanager.display_map()
            pg.display.update()


if __name__ == '__main__':
    app = App()
    app.run()