import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH=500
WIN_HEIGHT=800

GEN=0
#loading all images
BIRD_IMGS=[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))

BASE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))

BG_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

#fonts for score
STAT_FONT=pygame.font.SysFont("comicsans", 50)
#3 oblects bird base and pipe and class for each
class Bird:#creating the bird
    IMGS=BIRD_IMGS
    MAX_ROTATION=25#how uch bird will tilt
    ROT_VEL=20#how fast bird will tilt
    ANIMATION_TIME=5#time for each animation
     
    def __init__(self,x,y):#initialising the bird
        self.x=x #starting position
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0#to see which img is being shown
        self.img=self.IMGS[0]#to initialize first img
        
         
    def jump(self):#on jumping
        self.vel=-10.5#since 0,0 is top left so negative to go up
        self.tick_count=0#keeps track of last jump
        self.height=self.y#keeps track where bird jumped from
    
    def move(self):#called to move bird
        self.tick_count+=1#frame went by
        d=self.vel*self.tick_count+1.5*self.tick_count**2#displacement
       
        if d>=16:
            d=16#to avoid rapid fall
        if d<0:
            d-=2#to make jump better
        
        self.y=self.y + d#changing y pos
        
        #less rotation when rising and more when falling
        #tilting bird upwards or downwards
        if d<0 or self.y<self.height + 50:#keeping track of where we are jumping from 
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
        else:#keeping track of where we are falling from
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
        
    def draw(self,win):#to display the different bird images
       self.img_count += 1
       #displaying what bird image to show
       #makes bird flap up and down
       if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
       elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
       elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
       elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
       elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
    
       if self.tilt<=-80:#bird shouldnt be flapping when falling
           self.img=self.IMGS[1]
           self.img_count=self.ANIMATION_TIME*2
       #to rotate bird     
       rotated_image=pygame.transform.rotate(self.img, self.tilt)
       new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center) 
       win.blit(rotated_image,new_rect.topleft)
      
    def get_mask(self):#for collision
         return pygame.mask.from_surface(self.img)

class Pipe:
    GAP=200
    VEL=5#bird stays in place pipe and bg move
    
    def __init__(self,x):
        self.x=x
        self.height=0
        self.top=0
        self.bottom=0
        
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False,True)#upper pipe is inverted
        self.PIPE_BOTTOM=PIPE_IMG
        
        self.passed=False
        self.set_height()
        
    def set_height(self):#sets a random height for top and bottom pipes
        self.height=random.randrange(50,450)
        self.top=self.height-self.PIPE_TOP.get_height()
        self.bottom=self.height+self.GAP
            
    def move(self):#moving pipe based on velocity
        self.x -=self.VEL
    
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
            
    def collide(self,bird):#pixel perfect collision using mask(list of pixels of an object)
        bird_mask=bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)                      
            
        top_offset=(self.x-bird.x,self.top-round(bird.y))#distance from bird and top mask and round because no decimal
        bottom_offset=(self.x-bird.x,self.bottom-round(bird.y))#distance from bird and bottom mask
            
        b_point=bird_mask.overlap(bottom_mask,bottom_offset)#collision pt between bird mask and bottom pipe returns none if no collision
        t_point=bird_mask.overlap(top_mask,top_offset)#collision pt between bird mask and top pipe
            
        if b_point or t_point :
            return True
        return False
            
class Base:
    VEL=5
    WIDTH=BASE_IMG.get_width()
    IMG=BASE_IMG
    
    def __init__(self,y):
        self.y=y
        self.x1=0#start of base
        self.x2=self.WIDTH#end of base
        
    def move(self):#repeating base img once its over
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        #checking if img is over
        if self.x1+self.WIDTH<0:
            self.x1=self.x2+self.WIDTH
        
        if self.x2+self.WIDTH<0:
            self.x2=self.x1+self.WIDTH
            
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))
                
def draw_window(win,birds,pipes,base,score,gen):
    win.blit(BG_IMG,(0,0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    text=STAT_FONT.render("Score: "+str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))
    
    text=STAT_FONT.render("Gen: "+str(gen),1,(255,255,255))
    win.blit(text,(10,10))
    
    base.draw(win)    
    for bird in birds:
        bird.draw(win)
    
    pygame.display.update()
    
def main(genomes,config):#genomes and config as main is the fitness function
    global GEN
    GEN+=1
    
    nets=[]#keeping track of neural networks
    ge=[]#keeping track of genomes
    birds= []
    
    for _,g in genomes:#since genome has id and object
        net=neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)#setting neural network for genome
        birds.append(Bird(230, 350))
        g.fitness=0#setting initial fitness
        ge.append(g)#append genome to list
    
    base=Base(730)
    pipes=[Pipe(600)]
    win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock=pygame.time.Clock()
    score=0
    
    run=True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                quit()
        
        #moving bird pipe and base        
        
        pipe_ind=0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind=1
        else:#if no birds left then end
            run=False
            break
        for x,bird in enumerate(birds):#moving bird
            bird.move()
            ge[x].fitness += 0.1#every second bird stays alive it gets 1 fitness
            
            output=nets[x].activate((bird.y,abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))
            #calling activation fn
            if output[0]>0.5:
                bird.jump()
        
        add_pipe=False
        rem=[]
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):#for collision
                       ge[x].fitness -= 1#to decrease fitness on collision
                       birds.pop(x)#removing bird
                       nets.pop(x)
                       ge.pop(x)
                if not pipe.passed and pipe.x<bird.x:#checking if pipe is passed
                    pipe.passed=True 
                    add_pipe=True#add pipe if bird passes a pipe
            if pipe.x+pipe.PIPE_TOP.get_width()<0:#if pipe is off the screen
                rem.append(pipe)#removing the pipe
            pipe.move()
        
        if add_pipe:
            score+=1
            for g in ge:
                g.fitness += 5#increasing fitness
            pipes.append(Pipe(600))
        
        for r in rem:
            pipes.remove(r)
        
        for x,bird in enumerate(birds):
            if bird.y+bird.img.get_height()>730 or bird.y<0:#if bird hits floor
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        if score>50:#ending game if score reaches 50
            break
        
        base.move()
        draw_window(win, birds,pipes,base,score,GEN)
        
    
    
#ai part      
def run(config_path):#setting up neat
    config=neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p=neat.Population(config)#to initialize population
    p.add_reporter(neat.StdOutReporter(True))
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)
    winner=p.run(main,50)#running main 50 times as the fitness function
    #using main as the fitness fn since we increase fitness by how far the bird goes
    
    
if __name__ == "__main__":#to load config file
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,"config.txt")
    run(config_path)
    
    
    
    
    
    

                