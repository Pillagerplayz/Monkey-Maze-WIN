from pygame.locals import *
import pygame
import sys
import os
import random
import tkinter as tk
from tkinter import simpledialog, messagebox

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Player:
    clock = pygame.time.Clock()
    dt = 0
    x = 0
    y = 0
    speed = 200
    original_speed = 200
    speed_boost_end_time = 0
    image = None
    mask = None
    block_size = 0
    window_width = 0
    window_height = 0

    def __init__(self, block_size, window_width, window_height):
        self.block_size = block_size
        self.window_width = window_width
        self.window_height = window_height
        self.frames = [
            pygame.image.load(resource_path("images\\player_frames\\pixil-frame-0.png")).convert_alpha(),
            pygame.image.load(resource_path("images\\player_frames\\pixil-frame-1.png")).convert_alpha(),
            pygame.image.load(resource_path("images\\player_frames\\pixil-frame-2.png")).convert_alpha(),
            pygame.image.load(resource_path("images\\player_frames\\pixil-frame-3.png")).convert_alpha(),
            pygame.image.load(resource_path("images\\player_frames\\pixil-frame-4.png")).convert_alpha(),
        ]
        self.frames = [pygame.transform.scale(frame, (self.block_size - 10, self.block_size - 10)) for frame in self.frames]
        self.image = self.frames[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.x = self.block_size
        self.y = self.block_size

    def moveUp(self):
        self.y -= self.speed * self.dt
        self.image = self.frames[1]

    def moveDown(self):
        self.y += self.speed * self.dt
        self.image = self.frames[2]

    def moveLeft(self):
        self.x -= self.speed * self.dt
        self.image = self.frames[3]

    def moveRight(self):
        self.x += self.speed * self.dt
        self.image = self.frames[4]

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.block_size, self.block_size)
    
    def update_hitbox(self):
        player_width = self.image.get_width()
        player_height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x, self.y, player_width, player_height)

    def update_speed(self, current_time):
        if current_time > self.speed_boost_end_time:
            self.speed = self.original_speed

class Banana:
    def __init__(self, x, y, block_size):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.image = pygame.image.load(resource_path("images\\banana.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (block_size, block_size))
        self.rect = pygame.Rect(self.x, self.y, self.block_size, self.block_size)

    def draw(self, display_surf):
        display_surf.blit(self.image, (self.x, self.y))

class Powerup:
    def __init__(self, x, y, block_size, rarity):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.rarity = rarity
        self.image = pygame.image.load(resource_path(f"images\\powerups\\pixil-frame-{rarity}.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (block_size, block_size))
        self.rect = pygame.Rect(self.x, self.y, self.block_size, self.block_size)

    def draw(self, display_surf):
        display_surf.blit(self.image, (self.x, self.y))

class Exit:
    def __init__(self, x, y, block_size):
        self.x = x
        self.y = y
        self.block_size = block_size
        self.image = pygame.image.load(resource_path("images\\exit.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (block_size, block_size))
        self.rect = pygame.Rect(self.x, self.y, self.block_size, self.block_size)

    def draw(self, display_surf):
        display_surf.blit(self.image, (self.x, self.y))

class Maze:
    def __init__(self, window_width, window_height, difficulty):
        self.block_size = min(window_width // 20, window_height // 15)  # Calculate block size based on window dimensions
        self.M = window_width // self.block_size  # Calculate number of columns
        self.N = window_height // self.block_size  # Calculate number of rows
        self.maze = self.generate_maze(difficulty)
        self.block_image = pygame.image.load(resource_path("images\\block_sprite.png")).convert_alpha()

    def generate_maze(self, difficulty):
        maze = [[1 for _ in range(self.M)] for _ in range(self.N)]
        stack = [(1, 1)]
        while stack:
            x, y = stack[-1]
            maze[y][x] = 0
            neighbors = []
            if x > 1 and maze[y][x - 2] == 1:
                neighbors.append((x - 2, y))
            if x < self.M - 2 and maze[y][x + 2] == 1:
                neighbors.append((x + 2, y))
            if y > 1 and maze[y - 2][x] == 1:
                neighbors.append((x, y - 2))
            if y < self.N - 2 and maze[y + 2][x] == 1:
                neighbors.append((x, y + 2))
            if neighbors:
                nx, ny = random.choice(neighbors)
                stack.append((nx, ny))
                maze[(y + ny) // 2][(x + nx) // 2] = 0
            else:
                stack.pop()
        # Ensure a path to the end
        x, y = 1, 1
        while x < self.M - 1 or y < self.N - 1:
            maze[y][x] = 0
            if x < self.M - 1 and (y == self.N - 1 or random.random() > 0.5):
                x += 1
            elif y < self.N - 1:
                y += 1
        # Add dead ends with paths
        for _ in range(difficulty * 5):
            dx, dy = random.randint(1, self.M - 2), random.randint(1, self.N - 2)
            if maze[dy][dx] == 0:
                maze[dy][dx] = 1
                if random.random() > 0.5:
                    maze[dy][dx - 1] = 0
                else:
                    maze[dy - 1][dx] = 0
        return maze

    def draw(self, display_surf, image_surf):
        for y in range(self.N):
            for x in range(self.M):
                if self.maze[y][x] == 1:
                    image_surf = pygame.transform.scale(image_surf, (self.block_size, self.block_size))
                    display_surf.blit(image_surf, (x * self.block_size, y * self.block_size))
    
    def get_block_hitboxes(self):
        hitboxes = []
        for y in range(self.N):
            for x in range(self.M):
                if self.maze[y][x] == 1:
                    hitbox = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    hitboxes.append(hitbox)
        return hitboxes

class Font:
    def __init__(self, font_path, font_size):
        self.font_path = font_path
        self.font_size = font_size
        self.font = pygame.font.Font(resource_path(font_path), font_size)

    def getRect(self, text):
        return text.get_rect()
    
    def center(self, rect, x, y):
        rect.center = (x, y)
    
    def render(self, text, color):
        return self.font.render(text, True, color)
    
    def resize(self, new_size):
        self.font_size = new_size
        self.font = pygame.font.Font(resource_path(self.font_path), new_size)

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, display_surf):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(display_surf, color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        display_surf.blit(text_surf, text_rect)

    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.hovered and mouse_pressed[0]

class App:
    windowWidth = 800
    windowHeight = 600
    player = 0

    def __init__(self, difficulty):
        self.running = False
        self.level = 1
        self.pts = 0
        self._display_surf = None
        self._block_surf = None
        self._player = None
        self._maze = None
        self._font = None
        self._bananas = []
        self._powerups = []
        self._exit = None
        self._restart_button = None
        self.difficulty = difficulty
        self.HHK = [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_UP, K_RIGHT, K_DOWN, K_LEFT, K_RETURN, K_c]
        self.key_index = 0
        self.last_key_time = 0
        self.key_delay = 200  # 200 milliseconds delay between key presses
        self.pts_image_size = 30  # Initial size for pts_image

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("sounds\\music\\Monkey Maze Theme by Benplayz.mp3"))
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)  # Loop the music indefinitely
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption("Monkey Maze")
        pygame.display.set_icon(pygame.image.load(resource_path("images\\player_frames\\pixil-frame-0.png")))
        self._font = Font("font\\Retro Gaming.ttf", 20)  # Initialize font here
        self.running = True
        self._block_surf = pygame.image.load(resource_path("images\\block_sprite.png")).convert_alpha()
        self._maze = Maze(self.windowWidth, self.windowHeight, self.difficulty)
        self._player = Player(self._maze.block_size, self.windowWidth, self.windowHeight)
        
        # Ensure initial position is not inside a maze block
        self._player.update_hitbox()
        block_hitboxes = self._maze.get_block_hitboxes()
        for block_hitbox in block_hitboxes:
            while self._player.hitbox.colliderect(block_hitbox):
                self._player.x += self._player.block_size  # Move player out of the block

        # Place bananas randomly in the maze
        self._bananas = self.place_items(Banana, 10)

        # Place powerups randomly in the maze
        self._powerups = self.place_items(Powerup, random.randint(0, 3))

        # Place exit at the bottom right corner
        self._exit = Exit((self._maze.M - 1) * self._maze.block_size, (self._maze.N - 1) * self._maze.block_size, self._maze.block_size)

        # Create restart button
        self._restart_button = Button(self.windowWidth - 150, 20, 120, 40, "Restart", self._font.font, (0, 128, 0), (0, 255, 0))

        self.update_pts_image_size()

        return True

    def on_event(self, event):
        if event.type == QUIT:
            self.running = False
        elif event.type == MOUSEBUTTONDOWN:
            if self._restart_button.is_clicked(event.pos, pygame.mouse.get_pressed()):
                self.restart_game()
        elif event.type == KEYDOWN:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_key_time > self.key_delay:
                if event.key == self.HHK[self.key_index]:
                    self.key_index += 1
                    self.last_key_time = current_time
                    if self.key_index == len(self.HHK):
                        self.djkdkf()
                        self.key_index = 0
                else:
                    self.key_index = 0

    def place_items(self, item_class, count):
        items = []
        block_hitboxes = self._maze.get_block_hitboxes()
        for _ in range(count):
            while True:
                x = random.randint(0, self._maze.M - 1) * self._maze.block_size
                y = random.randint(0, self._maze.N - 1) * self._maze.block_size
                if item_class == Powerup:
                    rarity = random.choices([0, 1, 2], weights=[70, 25, 5], k=1)[0]
                    item = item_class(x, y, self._maze.block_size, rarity)
                else:
                    item = item_class(x, y, self._maze.block_size)
                if not any(item.rect.colliderect(block_hitbox) for block_hitbox in block_hitboxes):
                    items.append(item)
                    break
        return items

    def djkdkf(self):
        root = tk.Tk()
        root.withdraw()
        root.focus_force()
        code = simpledialog.askstring("TOP SECRET: Code", "Enter TOP SECRET Code:\t\t\t\t\t")
        root.destroy()
        if code == "Benplayz864YT":
            print("Given player 100,000 bananas!")
            self.pts += 100000
        if code == "PillagerplayzDEV864":
            pz_root = tk.Tk()
            pz_root.withdraw()
            pz_root.focus_force()
            stdcountm = simpledialog.askfloat("Enter Count", "How many bananas?\t\t\t\t\t")
            pz_root.destroy()
            if stdcountm.is_integer():
                self.pts += int(stdcountm)
            else:
                self.pts += float(stdcountm)
        if code == "vm.h.Machine.Kit.runCommand":
            def runExecCommand(self=self):
                hf_input = hf_codebox.get(1.0, tk.END)
                exec(hf_input)
                hf_root.destroy()
            hf_root = tk.Tk()
            hf_root.title("Command Console")

            hf_codebox = tk.Text(hf_root, height=10, width=50)
            hf_codebox.pack(pady=10)
            
            hf_submitBTN = tk.Button(hf_root, text="Run", command=runExecCommand)
            hf_submitBTN.pack(pady=5)
            
            hf_root.focus_force()
            hf_root.mainloop()

    def restart_game(self):
        self._maze = Maze(self.windowWidth, self.windowHeight, self.difficulty)
        self._player = Player(self._maze.block_size, self.windowWidth, self.windowHeight)
        self._bananas = self.place_items(Banana, 10)
        self._powerups = self.place_items(Powerup, random.randint(0, 3))
        self._exit = Exit((self._maze.M - 1) * self._maze.block_size, (self._maze.N - 1) * self._maze.block_size, self._maze.block_size)

    def check_collisions(self):
        self._player.update_hitbox()
        block_hitboxes = self._maze.get_block_hitboxes()
        for block_hitbox in block_hitboxes:
            if self._player.hitbox.colliderect(block_hitbox):
                if self._player.image == self._player.frames[1]:  # Moving up
                    self._player.y = block_hitbox.bottom
                elif self._player.image == self._player.frames[2]:  # Moving down
                    self._player.y = block_hitbox.top - self._player.hitbox.height
                elif self._player.image == self._player.frames[3]:  # Moving left
                    self._player.x = block_hitbox.right
                elif self._player.image == self._player.frames[4]:  # Moving right
                    self._player.x = block_hitbox.left - self._player.hitbox.width

        # Check for banana collisions
        for banana in self._bananas[:]:
            if self._player.hitbox.colliderect(banana.rect):
                self._bananas.remove(banana)
                collect_sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\Banana_pick.wav"))
                collect_sound.play()
                self.pts += 1

        # Check for powerup collisions
        for powerup in self._powerups[:]:
            if self._player.hitbox.colliderect(powerup.rect):
                self._powerups.remove(powerup)
                powerup_sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\Powerup.wav"))
                # Implement powerup effect based on rarity
                if powerup.rarity == 0:  # Common
                    powerup_sound.play()
                    self.pts *= 2
                elif powerup.rarity == 1:  # Rare
                    powerup_sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\Speed.wav"))
                    powerup_sound.play()
                    self._player.speed = self._player.original_speed * 1.5
                    self._player.speed_boost_end_time = pygame.time.get_ticks() + 30000  # 30 seconds
                elif powerup.rarity == 2:  # Epic
                    powerup_sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\X5_powerup.wav"))
                    powerup_sound.play()
                    self.pts *= 5

        # Check for exit collision
        if self._player.hitbox.colliderect(self._exit.rect):
            self.level += 1
            self.difficulty = min(3, self.level)  # Set difficulty based on level
            self._maze = Maze(self.windowWidth, self.windowHeight, self.difficulty)
            self._player = Player(self._maze.block_size, self.windowWidth, self.windowHeight)
            self._bananas = self.place_items(Banana, 10)
            self._powerups = self.place_items(Powerup, random.randint(0, 3))
            self._exit = Exit((self._maze.M - 1) * self._maze.block_size, (self._maze.N - 1) * self._maze.block_size, self._maze.block_size)

    def on_loop(self):
        self._player.dt = self._player.clock.tick(60) / 1000
        self._player.update_speed(pygame.time.get_ticks())
        self.check_collisions()

        player_width = self._player.image.get_width()
        player_height = self._player.image.get_height()

        if self._player.x <= 0:
            self._player.x = 0
        if self._player.x >= self.windowWidth - player_width:
            self._player.x = self.windowWidth - player_width
        if self._player.y <= 0:
            self._player.y = 0
        if self._player.y >= self.windowHeight - player_height:
            self._player.y = self.windowHeight - player_height

    def update_pts_image_size(self):
        self.pts_image_size = 35
        self.pts_image = pygame.image.load(resource_path("images\\banana.png")).convert_alpha()
        self.pts_image = pygame.transform.scale(self.pts_image, (self.pts_image_size + 15, self.pts_image_size + 15))
        self.pts_text = self._font.render(f"x{self.pts}", (255, 255, 255))
        self.pts_text_rect = self._font.getRect(self.pts_text)
        self._font.center(self.pts_text_rect, self.pts_image_size, self.pts_image_size - 30)

    def on_render(self):
        self._display_surf.fill((0, 0, 0))
        self.level_text = self._font.render(f"Level: {self.level}", (255, 255, 255))
        self.level_text_rect = self._font.getRect(self.level_text)
        self._font.center(self.level_text_rect, self.windowWidth // 2, 20)
        self.pts_text = self._font.render(f"x{self.pts}", (255, 255, 255))
        self.pts_text_rect = self._font.getRect(self.pts_text)
        self._font.center(self.pts_text_rect, 50, 20)
        self._maze.draw(self._display_surf, self._block_surf)
        for banana in self._bananas:
            banana.draw(self._display_surf)
        for powerup in self._powerups:
            powerup.draw(self._display_surf)
        self._exit.draw(self._display_surf)
        self._display_surf.blit(self._player.image, (self._player.x, self._player.y))
        self._display_surf.blit(self.level_text, self.level_text_rect)
        self._display_surf.blit(self.pts_text, self.pts_text_rect)
        self._display_surf.blit(self.pts_image, (0, -5))
        self._restart_button.draw(self._display_surf)
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

    def on_execute(self):
        try:
            if not self.on_init():
                self.running = False
            while self.running:
                for event in pygame.event.get():
                    self.on_event(event)
                mouse_pos = pygame.mouse.get_pos()
                self._restart_button.is_hovered(mouse_pos)
                key = pygame.key.get_pressed()
                if key[pygame.K_UP] or key[pygame.K_w]:
                    self._player.moveUp()
                elif key[pygame.K_DOWN] or key[pygame.K_s]:
                    self._player.moveDown()
                elif key[pygame.K_LEFT] or key[pygame.K_a]:
                    self._player.moveLeft()
                elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                    self._player.moveRight()
                elif key[pygame.K_ESCAPE]:
                    self.running = False
                elif (key[pygame.K_LCTRL] or key[pygame.K_RCTRL]) and key[pygame.K_r]:
                    self.restart_game()
                elif key[pygame.K_RETURN] and (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) and key[pygame.K_o]:
                    root = tk.Tk()
                    root.withdraw()
                    root.focus_force()  # Ensure the dialog gets focus
                    self.secCode = simpledialog.askstring("Enter Code", "Enter Code:\t\t\t\t\t")
                    root.destroy()
                    if self.secCode == "Low Taper Fade":
                        print("Imagine if ninja got a low taper fade!")
                        pygame.mixer.music.stop()  # Stop the background music
                        sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\imagine-if-ninja-got-a-low-taper-fade.mp3"))
                        sound.play()
                        while pygame.mixer.get_busy():
                            for event in pygame.event.get():
                                self.on_event(event)
                            mouse_pos = pygame.mouse.get_pos()
                            self._restart_button.is_hovered(mouse_pos)
                            key = pygame.key.get_pressed()
                            if key[pygame.K_UP] or key[pygame.K_w]:
                                self._player.moveUp()
                            elif key[pygame.K_DOWN] or key[pygame.K_s]:
                                self._player.moveDown()
                            elif key[pygame.K_LEFT] or key[pygame.K_a]:
                                self._player.moveLeft()
                            elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                                self._player.moveRight()
                            elif key[pygame.K_ESCAPE]:
                                self.running = False
                            elif (key[pygame.K_LCTRL] or key[pygame.K_RCTRL]) and key[pygame.K_r]:
                                self.restart_game()
                            self.on_loop()
                            self.on_render()
                        pygame.mixer.music.play(-1)  # Loop the music again
                    elif self.secCode == "Packet.Cheat":
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror("Hey you!", "Good try, cheater >:)")
                        root.destroy()
                    elif self.secCode == "(999)":
                        f = open("JUICEWRLD.txt", "w")
                        f.write("Fun Fact: One of the creators of the game, Benplayz864, liked Juice WRLD's songs.")
                        f.close()
                    elif self.secCode == "NINJA":
                        print("I was the knight in shining armor in your movie!")
                        pygame.mixer.music.stop()  # Stop the background music
                        sound = pygame.mixer.Sound(resource_path("sounds\\SFX\\NINJA.mp3"))
                        sound.play()
                        while pygame.mixer.get_busy():
                            for event in pygame.event.get():
                                self.on_event(event)
                            mouse_pos = pygame.mouse.get_pos()
                            self._restart_button.is_hovered(mouse_pos)
                            key = pygame.key.get_pressed()
                            if key[pygame.K_UP] or key[pygame.K_w]:
                                self._player.moveUp()
                            elif key[pygame.K_DOWN] or key[pygame.K_s]:
                                self._player.moveDown()
                            elif key[pygame.K_LEFT] or key[pygame.K_a]:
                                self._player.moveLeft()
                            elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                                self._player.moveRight()
                            elif key[pygame.K_ESCAPE]:
                                self.running = False
                            elif (key[pygame.K_LCTRL] or key[pygame.K_RCTRL]) and key[pygame.K_r]:
                                self.restart_game()
                            self.on_loop()
                            self.on_render()
                        pygame.mixer.music.play(-1)  # Loop the music again
                    elif self.secCode == "MONKEY":
                        class DangerousExecution(Exception):
                            pass
                        pygame.time.wait(3000)
                        pygame.mixer.music.stop()
                        creepyImage = pygame.image.load(resource_path("images\\MONKEY.png"))
                        creepyImage = pygame.transform.scale(creepyImage, (self.windowWidth, self.windowHeight))
                        self._display_surf.blit(creepyImage, (0, 0))
                        pygame.display.flip()
                        jumpscareSound = pygame.mixer.Sound(resource_path("sounds\\SFX\\jumpscare.mp3"))
                        jumpscareSound.play()
                        pygame.time.wait(2000)
                        raise DangerousExecution(" ERROR 666: MONKEY.exe has sent a virus to your files!")
                        self.on_cleanup()
                        while True:
                            for event in pygame.event.get():
                                if event.type == QUIT:
                                    self.running = False
                                    break
                            if not self.running:
                                break
                else:
                    self._player.image = self._player.frames[0]
                self.on_loop()
                self.on_render()
        except KeyboardInterrupt:
            self.on_cleanup()

if __name__ == "__main__":
    difficulty = 1  # Initial difficulty level
    theApp = App(difficulty)
    theApp.on_execute()