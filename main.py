import pygame, sys, math, random
pygame.init()

screen = pygame.display.set_mode([1440, 810])
clock = pygame.time.Clock()
elapsed_time = clock.tick(60)
best_score = 0

def getFont(fontSize):
    return pygame.font.Font("assets/early_gameboy.ttf", fontSize)
    
class MainWindow():
    def __init__(self):
        pygame.display.set_caption("Sorting Monster")

        self.initialize()
        while True:
            self.main_loop()

    def initialize(self):
        self.stages = {"start": StartScreen(self),
                       "level": LevelScreen(self)}
        self.current_stage = "start"
        pass

    def main_loop(self):
        global elapsed_time
        screen.fill((0,0,0))
        self.event_loop()
        self.render_loop()
        elapsed_time = clock.tick(60)
        pygame.display.flip()

    def render_loop(self):
         self.stages[self.current_stage].render()

    def event_loop(self):
        for event in pygame.event.get():
            self.stages[self.current_stage].event(event)
            if event.type == pygame.QUIT:
                self.quit()

    def set_stage(self,stage):
        self.current_stage = stage
    
    def quit(self):
        pygame.quit()
        sys.exit()

class LevelScreen():
    def __init__(self, MainWindow: MainWindow):
        self.main_window = MainWindow
        self.assets()
        self.game_end = False
        self.score = 0
        self.timer = 4*60 # 60 game fps
        self.level_background = pygame.transform.scale(self.assets["level_background"],(1440,810))
        self.monster = Monster()
        self.keybinding = {"d":"Recyclable",
                           "j":"Biodegradeable",
                           "k":"Non-biodegradeable"}
        self.main_menu =self.start_button = Button(570,520,385*0.9,126*0.9,self.assets["main_menu"],self.assets["main_menu_pressed"],True, self.reset_game)
        self.trashes = []
        self.trash_animation = []
        self.correction_animation = []
        self.generate_trash()
    
    def game_over(self):
        global best_score

        self.game_end = True
        if best_score < self.score: best_score =  self.score

    def reset_game(self):
        self.monster = Monster()
        self.trashes = []
        self.correction_animation = []
        self.trash_animation = []
        self.generate_trash()
        self.game_end = False
        self.score = 0
        self.timer = 4*60
        self.main_window.set_stage("start")

    def assets(self):
        self.assets = {
            "level_background": pygame.image.load("assets/level_background.png"),
            "game_over": pygame.transform.scale(pygame.image.load("assets/game_over.png"),(880,640)),
            "key_d": pygame.transform.scale(pygame.image.load("assets/key_d.png"),(75,75)),
            "key_j": pygame.transform.scale(pygame.image.load("assets/key_j.png"),(75,75)),
            "key_k": pygame.transform.scale(pygame.image.load("assets/key_k.png"),(75,75)),
            "heart": pygame.transform.scale(pygame.image.load("assets/heart.png"),(60,60)),
            "timer": pygame.transform.scale(pygame.image.load("assets/timer.png"),(76,600)),
            "main_menu": pygame.image.load("assets/main_menu.png"),
            "main_menu_pressed": pygame.image.load("assets/main_menu_pressed.png")
        }
        self.trash = [
            Trash("Bottle","assets/trash/plastic_bottle.png","Recyclable"),
            Trash("Metal","assets/trash/cog.png","Recyclable"),
            Trash("Aluminum Foil","assets/trash/foil.png","Recyclable"),
            Trash("Newspaper","assets/trash/newspaper.png","Recyclable"),
            Trash("Banana","assets/trash/banana.png","Biodegradeable"),
            Trash("Apple","assets/trash/apple.png","Biodegradeable"),
            Trash("Bone","assets/trash/bone.png","Biodegradeable"),
            Trash("Styrofoam Cup","assets/trash/styrofoam.png","Non-biodegradeable"),
            Trash("Plastic Bag","assets/trash/plastic_bag.png","Non-biodegradeable"),
            Trash("Mask","assets/trash/mask.png","Non-biodegradeable")
        ]
    def render(self):
        screen.blit(self.level_background,(0,0))
        screen.blit(getFont(15).render("recyclable",False,(50,34,0)),(470,470))
        screen.blit(getFont(15).render("biodegradeable",False,(12,70,0)),(650,450))
        screen.blit(getFont(15).render("non-biodegradeable",False,(0,72,114)),(830,470))
        screen.blit(self.assets["key_d"],(505,(700+(math.sin(pygame.time.get_ticks()/500)*2))))
        screen.blit(self.assets["key_j"],(725,(700+(math.sin(pygame.time.get_ticks()/500)*2))))
        screen.blit(self.assets["key_k"],(930,(700+(math.sin(pygame.time.get_ticks()/500)*2))))
        self.render_trash()
        self.render_heart()
        self.monster.render()
        screen.blit(self.assets["timer"],(1320,150))
        timer_bar = pygame.Rect(1340,170,36,560*(self.timer/(4*60)))
        timer_bar.bottomleft = (1340,730)
        screen.blit(getFont(20).render("SCORE: "+str(self.score),False,(44,14,31)),(20,750))
        pygame.draw.rect(screen,(252,82,46),timer_bar)
        if self.game_end:
            screen.blit(self.assets["game_over"],(300,70))
            self.main_menu.draw()
            screen.blit(getFont(30).render(str(self.score),False,(44,14,31)),(740,372))
            screen.blit(getFont(30).render(str(best_score),False,(44,14,31)),(740,425))
        else:
            self.timer -= 1
            if self.timer == 0:
                self.take_heart()
                self.timer = 4*60

    def render_heart(self):
        for i in range(self.monster.lives):
            screen.blit(self.assets["heart"],(1360-(i*70),20))

    def render_trash(self):
        delta_time = elapsed_time/1000
        for i in reversed(range(len(self.trash_animation.copy()))):
            if not self.trash_animation[i].next_frame(delta_time):
                self.trash_animation.pop(i)

        for i in reversed(range(len(self.correction_animation.copy()))):
            if not self.correction_animation[i].next_frame(delta_time):
                self.correction_animation.pop(i)

        for i in range(len(self.trashes)):
            trash = pygame.transform.scale(self.trashes[i].get_image(),(90,90))
            if i == 0:
                screen.blit(trash,(190,80))
                name =getFont(15).render(self.trashes[i].get_name(),False,(0,0,0) )
                name_rect = name.get_rect()
                name_rect.topleft = (330,70)
                screen.blit(name,name_rect)
            else:
                screen.blit(trash,(45,80+((i-1)*105)))

    def generate_trash(self):
        self.trashes.extend(random.sample(set(self.trash)-set(self.trashes),6-len(self.trashes)))

    def take_heart(self):
        self.monster.add_tentacle()
        if self.monster.get_lives() <= 0:
            self.game_over()
            return

    def process_input(self, key):
        self.timer = 4*60
        if self.game_end: return
        if self.trashes[0].get_category() == self.keybinding[key]:
            self.score += 1
        else:
            text = getFont(10).render(self.trashes[0].get_name()+" is a "+self.trashes[0].get_category(),False,(100,0,0))
            self.correction_animation.append(KeyFrame(text,[(170,800),(170,500)],5))
            self.take_heart()
        if key == "d": self.trash_animation.append(KeyFrame(pygame.transform.scale(self.trashes[0].get_image(),(60,60)),[(190,80),(510,500)],0.5))
        elif key == "j": self.trash_animation.append(KeyFrame(pygame.transform.scale(self.trashes[0].get_image(),(60,60)),[(190,80),(720,500)],0.5))
        elif key == "k": self.trash_animation.append(KeyFrame(pygame.transform.scale(self.trashes[0].get_image(),(60,60)),[(190,80),(940,500)],0.5))
        self.trashes.pop(0)
        self.generate_trash()
    def event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            key= pygame.key.name(event.key)
            if key in ['d','j','k']:
                self.process_input(key)
        if self.game_end:
            self.main_menu.handle_event(event)

        
class Trash():
    def __init__(self, name, imageSrc, category):
        self.name = name
        self.image = pygame.image.load(imageSrc)
        self.category = category

    def get_category(self):
        return self.category
    
    def get_image(self):
        return self.image
    
    def get_name(self):
        return self.name
    
class StartScreen():
    def __init__(self, MainWindow: MainWindow):
        self.assets()
        self.main_window = MainWindow
        self.start_button = Button(screen.get_rect().center[0]-(385*0.9/2),450,385*0.9,126*0.9,self.assets["start_button"],self.assets["start_pressed_button"],True, self.move_stage)
        self.quit_button = Button(screen.get_rect().center[0]-(385*0.9/2),580,385*0.9,126*0.9,self.assets["quit_button"],self.assets["quit_pressed_button"],True, self.main_window.quit)
        self.title = pygame.transform.scale(self.assets["title"],(825*1.5,300*1.5))
        self.animation = None
        pass
    def assets(self):
        self.assets = {
            "start_button": pygame.image.load("assets/start.png"),
            "start_pressed_button": pygame.image.load("assets/start_pressed.png"),
            "quit_button": pygame.image.load("assets/quit.png"),
            "quit_pressed_button": pygame.image.load("assets/quit_pressed.png"),
            "title": pygame.image.load("assets/title.png"),
        }

    def move_stage(self):
        self.main_window.set_stage("level")

    def render(self):
        screen.fill((100,66,64))
        self.start_button.draw()
        self.quit_button.draw()
        screen.blit(self.title,(screen.get_rect().center[0]-((825*1.5)/2),30))

    def event(self,event):
        self.start_button.handle_event(event)
        self.quit_button.handle_event(event)

class Monster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.assets()
        self.blinking_time = 0
        self.lives = 3
        self.animation_state = 0

        self.tentacle_animation = []
        self.tentacle_reversed_animation = []

    def get_lives(self):
        return (self.lives-len(self.tentacle_animation))
    def blinking(self):
        blinking_reset = [100,200,300,400]
        if self.blinking_time <= 99:
            self.monster_animation["open"].next_frame((580,200),(0,8),delay=2)
        elif self.blinking_time == 500:
            self.monster_animation["open"].reset_frame()
            self.monster_animation["open"].next_frame((580,200),(0,8),delay=10, reverse=True)
        elif self.blinking_time >= 500:
            self.monster_animation["open"].next_frame((580,200),(0,8),delay=10, reverse=True)
        elif self.blinking_time in blinking_reset:
            self.monster_animation["open"].reset_frame()
            self.monster_animation["open"].next_frame((580,200),(6,8),delay=10, reverse=True)
        elif self.blinking_time % 100 < 50:
            self.monster_animation["open"].next_frame((580,200),(6,8),delay=10, reverse=True)
        elif self.blinking_time % 100 == 50:
            self.monster_animation["open"].reset_frame()
            self.monster_animation["open"].next_frame((580,200),(6,8),delay=10)
        elif self.blinking_time % 100 > 50:
            self.monster_animation["open"].next_frame((580,200),(6,8),delay=10)
        flipped_eye = pygame.transform.flip(self.monster_animation["open"].get_frame(),True,False)
        flipped_eye.set_colorkey((0,0,0))
        screen.blit(flipped_eye,(780,200))

        if self.blinking_time >= 550:
            self.blinking_time = 0
        else:
            self.blinking_time += 1

    def add_tentacle(self):
        if self.lives == 1:
            self.tentacle_animation.append(self.monster_animation["tentacle_1"])
        elif self.lives == 2:
            self.tentacle_animation.append(self.monster_animation["tentacle_2"])
        elif self.lives == 3:
            self.tentacle_animation.append(self.monster_animation["tentacle_3"])
        self.blinking_time = 0
        self.animation_state = 1

    def attacking(self):
        self.monster_animation["open"].next_frame((580,200),(9,19),delay=2)
        flipped_eye = pygame.transform.flip(self.monster_animation["open"].get_frame(),True,False)
        flipped_eye.set_colorkey((0,0,0))
        screen.blit(flipped_eye,(780,200))
        if len(self.tentacle_animation) == 0 and len(self.tentacle_reversed_animation) == 0: 
            self.animation_state = 0
            return
        for tentacle in self.tentacle_reversed_animation.copy():
            if not tentacle.next_frame((950,-60),(0,5),delay=3,reverse=True):
                self.tentacle_reversed_animation.remove(tentacle)
        for tentacle in self.tentacle_animation.copy():
            if not tentacle.next_frame((950,-60),(0,5),delay=3):
                self.lives -= 1
                self.tentacle_animation.remove(tentacle)
                self.tentacle_reversed_animation.append(tentacle)
                tentacle.reset_frame()
    def render(self):
        if self.animation_state == 0:
            self.blinking()
        elif self.animation_state == 1:
            self.attacking()

    def assets(self):
        self.assets = {
            "monster_sheet":pygame.image.load("assets/monster_eye.png"),
        }
        self.monster_animation = {
            "open": SpriteAnimation(self.assets["monster_sheet"],200,(160,160),(0,0,0)),
            "tentacle_1": SpriteAnimation(pygame.image.load("assets/tentacle_1st.png"),500,(500,500),(255,255,255)),
            "tentacle_2": SpriteAnimation(pygame.image.load("assets/tentacle_2nd.png"),500,(500,500),(255,255,255)),
            "tentacle_3": SpriteAnimation(pygame.image.load("assets/tentacle_3rd.png"),500,(500,500),(255,255,255))
        }

class Button():
    def __init__(self, x, y, width, height, button_img, pressed_img, is_strict=False, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.button_img = pygame.transform.scale(button_img,(width,height))
        self.pressed_img = pygame.transform.scale(pressed_img,(width,height))
        self.is_strict = is_strict
        self.state = 0
        pass

    def is_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False
        
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hover():
            self.state = 1
            if not self.is_strict:
                self.action()
        elif event.type == pygame.MOUSEBUTTONUP and self.is_hover():
            self.state = 0
            if self.is_strict:
                self.action()
        else:
            self.state = 0

    def draw(self):
        if self.state == 0: screen.blit(self.button_img,(self.rect.x, self.rect.y))
        else: screen.blit(self.pressed_img,(self.rect.x, self.rect.y))

class SpriteAnimation():
    def __init__(self, sprite_sheet: pygame.Surface, width: int, scale: tuple, color_key = None):
        self.width = width
        self.scale = scale
        self.sprite_sheet = sprite_sheet.convert_alpha()
        self.color_key = color_key
        self.current_frame = 0
        self.current_time = 0 
        self.generate_sheet()
    
    def reset_frame(self):
        self.current_frame = 0
        self.current_time = 0

    def generate_sheet(self):
        self.sheet = []
        for i in range(self.sprite_sheet.get_width()//self.width):
            frame = self.get_image(self.sprite_sheet,i,self.width,self.scale).convert_alpha()
            frame.set_colorkey(self.color_key)
            self.sheet.append(frame)
        self.min_max = (0, len(self.sheet)-1)

    def get_image(self, sheet, frame, width, scale):
        image = pygame.Surface((width, self.sprite_sheet.get_height())).convert_alpha()
        image.blit(sheet,(0, 0),((frame*width), 0, width, self.sprite_sheet.get_height()))
        image = pygame.transform.scale(image, scale)
        return image
    
    def get_frame(self):
        return self.current_surface
    
    def next_frame(self, coords, min_max: tuple, delay = 0, loop = False, reverse = False):
        if min_max != self.min_max:
            self.min_max = min_max
            self.current_frame = 0
            self.current_time = 0

        if self.current_frame >= (self.min_max[1]-self.min_max[0]) and loop: self.current_frame = 0
        elif self.current_time <= delay: 
            self.current_time+=1
        else:
            if not (self.current_frame >= (self.min_max[1]-self.min_max[0])):
                self.current_frame+=1
                self.current_time = 0
        if reverse == True:
            self.current_surface = self.sheet[min_max[1]-self.current_frame]
        else:
            self.current_surface = self.sheet[min_max[0]+self.current_frame]
        screen.blit(self.current_surface, coords)
        if self.current_frame >= self.min_max[1]:
            return False
        else:
            return True

class KeyFrame:
    def __init__(self, surface, keyframes, duration):
        self.surface = surface
        self.keyframes = keyframes
        self.duration = duration
        self.current_frame_time = 0 
        self.time_per_frame = self.duration / (len(self.keyframes) - 1)
        self.surface_rect = self.surface.get_rect()

    def lerp(self, start, end, t):
        return (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)

    def next_frame(self, delta_time):
        self.current_frame_time += delta_time
        current_frame = int(self.current_frame_time // self.time_per_frame)
        t = (self.current_frame_time % self.time_per_frame) / self.time_per_frame
        if current_frame < len(self.keyframes) - 1:
            current_pos = self.lerp(self.keyframes[current_frame], self.keyframes[current_frame + 1], t)
        else:
            current_pos = self.keyframes[-1]

        self.surface_rect.topleft = current_pos
        screen.blit(self.surface, self.surface_rect)

        if self.current_frame_time >= self.duration:
            return False
        else:
            return True


MainWindow()