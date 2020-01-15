#! /usr/bin/env python3

# program: the super tiny bow game
# This is a mini game where you press the space bar to shoot an arrow at a target
# author: Louison Calbrix
# date: December 2019

import os
import pygame
import random

#----------constants

# screen and display
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 650
LIGHTNESS_SKY_MAX = 90
COLOR_SKY = (80, 80, 200)
COLOR_GRASS = (70, 200, 70)
COLOR_FONT = (0, 255, 40)
COLOR_ROPE = (180, 180, 180)
FONT_NAME = "resources/CloisterBlack.ttf"

# game score
SCORE_TABLE = [3, 2, 1]
# game "physics"
GRAVITY = 3


class GameObject(pygame.sprite.Sprite):
    '''
    Super class for any game element that eventually gets drawn onscreen and
    that may be moved around.
    '''

    def __init__(self, img, topleft, speed):
        '''
        Initialize game object with:
            img being its picture onscreen and 
            rect its position
            speed a list of two integers that makes the game object move
             every frame.
        '''
        super().__init__()
        self._img = img
        self._rect = img.get_rect()
        self._rect.move_ip(topleft)
        self._speed = speed

    def update(self):
        '''
        Empty method. Subclass needs to override this.
        '''
        raise NotImplementedError()

    @property
    def image(self):
        ''' image(self) -> self._img'''
        return self._img

    @property
    def rect(self):
        ''' rect(self) -> self._rect'''
        return self._rect

    @classmethod
    def init(cls):
        '''
        Initialize pictures that were loaded by the subclass to represent said
        class instances onscreen. Subclasses need to load these pictures in a
        class attribute named IMGS that is a list of Surfaces likewise:
            IMGS = [
                pygame.image.load('resources/img1.png'),
                pygame.image.load('resources/img2.png'),
                ...
            ]
        If the subclass requires only one picture then it needs to be done this
        way:
            IMG = pygame.load('resources/img.png')
        Implementation advice: use named indices such as:
            IDDLE = 0
            RUNNING = 1
            ...
        So that later uses of IMGS are explicit:
            cls.IMGS[cls.IDDLE]
        Not to be called before pygame image modulea has been initialized.
        '''
        try:
            IMGS = []
            for surface in cls.IMGS:
                colorkey = surface.get_at((0, 0))
                surface.set_colorkey(colorkey)
                surface = surface.convert()
                IMGS.append(surface)
            cls.IMGS = IMGS
        except AttributeError:
            surface = cls.IMG
            colorkey = surface.get_at((0, 0))
            surface.set_colorkey(colorkey)
            surface = surface.convert()
            cls.IMG = surface


class Bow(GameObject):
    '''
    A bow moving across the screen from top to bottom and back.
    It can shoot arrows.
    '''

    # picture for bow onscreen
    IMG = pygame.image.load('resources/bow2.png')
    # drawing markers
    ROPE_TOP = (54, 20)
    ROPE_BOT = (54, 180)
    # animation
    ROPE_STATES = 10
    # misc constants
    POS_INIT = (20, 0)
    SPEED = [0, 8]
    AMMO_MAX = 5
    FORCE_MIN = 10
    FORCE_MAX = 50
    TIME_FORCE_S = 0.7
    TIME_COOLDOWN_S = 1
    # class attribute keeping track of the only instance of the class
    INSTANCE = pygame.sprite.GroupSingle()

    def __init__(self, context):
        '''
        Create a Bow. A context is needed to eventually be able to keep track
        of the score.
        '''
        super().__init__(Bow.IMG,
                         Bow.POS_INIT,
                         Bow.SPEED.copy())
        self._arrow = Arrow
        self._ammo = Bow.AMMO_MAX
        self._state = NormalBowState(self)
        self._context = context
        Bow.INSTANCE.add(self)

    def update(self, inputs):
        '''
        Update bow's position and uses its state's update method to do other
        state specific updates.
        '''
        self._rect.move_ip(*self._speed)
        # invert speed if going out of screen
        if self._rect.y < 0 or self._rect.y > SCREEN_HEIGHT-self._rect.height:
            self._speed = [-speed_component for speed_component in self._speed]
        self._state.update(inputs)

    def shoot(self):
        '''
        Shoot an arrow with all the force accumulated.
        '''
        topleft = self._rect.topleft
        self._arrow(self._context, topleft, self.force)
        self._ammo -= 1

    def draw(self, step):
        '''
        Redraw a bow's _img, only to be called when the bow's state changes.
        '''
        self._img = Bow.IMG.copy()
        overlay = pygame.Surface(self._img.get_size())
        if step == -1:
            pygame.draw.line(overlay, COLOR_ROPE, Bow.ROPE_TOP, Bow.ROPE_BOT)
        else:
            base_x = Bow.ROPE_TOP[0]
            x = base_x * (1 - step / Bow.ROPE_STATES)
            pygame.draw.line(overlay, COLOR_ROPE, Bow.ROPE_TOP, (x, Bow.ROPE_MIDDLE))
            pygame.draw.line(overlay, COLOR_ROPE, Bow.ROPE_BOT, (x, Bow.ROPE_MIDDLE))
            overlay.blit(Arrow.IMGS[Arrow.SHOT], (x - base_x, 0))
        overlay.set_colorkey(overlay.get_at((0, 0)))
        self._img.blit(overlay, (0, 0))

    @property
    def force(self):
        ''' 
        Return a mapping of _bent_time between Bow.FORCE_MAX and Bow.FORCE_MIN 
        '''
        return ((Bow.FORCE_MAX-Bow.FORCE_MIN) / Bow.TIME_FORCE_FPS) * self._bent_time + Bow.FORCE_MIN

    @classmethod
    def init(cls, fps):
        '''
        Initialize the picture that represents an instance of Bow onscreen. 
        Also initialize class constants related to time depending on fps rate.
        Not to be called before pygame image module has been initialized.
        '''
        super().init()
        cls.TIME_COOLDOWN_FPS = int(cls.TIME_COOLDOWN_S * fps)
        cls.TIME_FORCE_FPS = int(cls.TIME_FORCE_S * fps)
        cls.ROPE_MIDDLE = ((cls.ROPE_BOT[1] - cls.ROPE_TOP[1]) // 2) + cls.ROPE_TOP[1]


class NormalBowState:
    '''
    State for bow instances. Initial Bow state, wait for inputs.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(0)

    def update(self, inputs):
        for an_input in inputs:
            if an_input.type == pygame.KEYDOWN:
                if an_input.key == pygame.K_SPACE:
                    self._master._state = BentBowState(self._master)


class BentBowState:
    '''
    State for bow instances. Master bow amasses force as long as it is in this
    state, that force is released to shoot an arrow when this state is exited.
    '''
    def __init__(self, master):
        self._master = master
        self._master._bent_time = 0

    def update(self, inputs):
        if self._master._bent_time < Bow.TIME_FORCE_FPS:
            self._master._bent_time += 1
            step = self._master._bent_time / (Bow.TIME_FORCE_FPS // Bow.ROPE_STATES)
            if step.is_integer():
                self._master.draw(step)
        for an_input in inputs:
            if an_input.type == pygame.KEYUP:
                if an_input.key == pygame.K_SPACE:
                    self._master.shoot()
                    if self._master._ammo:
                        self._master._state = ReloadBowState(self._master)
                    else:
                        self._master._state = EmptyBowState(self._master)


class ReloadBowState:
    '''
    State for bow instances. Master bow cannot change its state before a
    certain amount of time.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(-1)
        self._master._cooldown = Bow.TIME_COOLDOWN_FPS

    def update(self, inputs):
        self._master._cooldown -= 1
        if self._master._cooldown == 0:
            self._master._state = NormalBowState(self._master)


class EmptyBowState:
    '''
    State for bow instances. Master bow doesn't have any more ammunition, it is
    stopped to make it obvious the game is over.
    '''
    def __init__(self, master):
        self._master = master
        self._master.draw(-1)
        self._master._speed = [0, 0]

    def update(self, inputs):
        pass


class Arrow(GameObject):
    '''
    An arrow that can be shot by a bow. It has an horizontal speed, that makes
    it move across the screen from left to right. It is destroyed if it goes
    beyond the screen's boundaries.
    '''

    IMGS = [
        pygame.image.load('resources/arrow2.png'),
        pygame.image.load('resources/arrow_stopped2.png')
    ]
    SHOT = 0
    STOPPED = 1
    INSTANCES = pygame.sprite.Group()
    HITBOX_OFFSET = (165, 90)
    HITBOX_SIZE = (26, 17)

    def __init__(self, context, topleft, force):
        '''
        Create an arrow shot with force from topleft.
        '''
        super().__init__(Arrow.IMGS[Arrow.SHOT],
                         topleft,
                         [force, 0])
        # hitbox creation
        x, y = self._rect.x, self._rect.y
        self._hitbox = pygame.Rect((x, y), Arrow.HITBOX_SIZE)
        self._hitbox.move_ip(*Arrow.HITBOX_OFFSET)
        self._target = Target.INSTANCE
        self._context = context
        Arrow.INSTANCES.add(self)

    def update(self):
        '''
        Update a moving arrow's position.
        '''
        if self._speed != [0, 0]:
            self._speed[1] += GRAVITY
            self._rect.move_ip(self._speed)
            self._hitbox.move_ip(self._speed)
            if self._rect.x > SCREEN_WIDTH or self._rect.y > SCREEN_HEIGHT:
                super().kill()
            zone = self._hitbox.collidelist(self._target.hitbox)
            if zone != -1:
                self._speed = [0, 0]
                self._img = Arrow.IMGS[Arrow.STOPPED]
                self._context.update_score(zone, self)
                super().kill()

    def __del__(self):
        print('deleted arrow')

    @property
    def score(self):
        ''' score(self) -> self._score '''
        return self._score


class Target:
    '''
    Target that needs to be hit. The class is supposed to be instanciated only
    once for every game so, instead of keeping a reference of that instance, I
    recommend refering to it using the class attribute INSTANCE.
    recommended instanciation:
        Target(background_surface)
    use not intended:
        target = Target(background_surface)
    recommended reference:
        Target.INSTANCE
    '''
    OUTER_I = 2
    MIDDLE_I = 1
    INNER_I = 0
    AREAS = [
        ((79, 127), (26, 153)),
        ((88, 59), (34, 289)),
        ((88, 0), (42, 399))
    ]
    IMG = pygame.image.load('resources/target.png')
    INSTANCE = None

    def __init__(self, background):
        '''
        Create a target. Since the target's sprite is drawn right away and 
        never moved around a surface on which it is going to be drawn is needed:
        that surface is the parameter background.
        '''
        Target.INSTANCE = self
        img = Target.IMG
        x = SCREEN_WIDTH - img.get_width()
        y = SCREEN_HEIGHT - img.get_height()
        iddle_sprite(Target.IMG, (x, y), background)
        inner = Target.AREAS[Target.INNER_I]
        self._inner_hit = pygame.Rect(inner[0], inner[1])
        self._inner_hit.move_ip(x, y)
        middle = Target.AREAS[Target.MIDDLE_I]
        self._middle_hit = pygame.Rect(middle[0], middle[1])
        self._middle_hit.move_ip(x, y)
        outer = Target.AREAS[Target.OUTER_I]
        self._outer_hit = pygame.Rect(outer[0], outer[1])
        self._outer_hit.move_ip(x, y)

    @property
    def image(self):
        ''' image(self) -> self._img '''
        return self._img

    @property
    def rect(self):
        ''' rect(self) -> self._rect '''
        return self._rect

    @property
    def hitbox(self):
        ''' hitbox(self) -> tuple of Rect '''
        return self._inner_hit, self._middle_hit, self._outer_hit

    @classmethod
    def init(cls):
        '''
        Initialize picture that represent an instance of Target onscreen. Not to
        be called before pygame image module has been initialized.
        '''
        cls.IMG = cls.IMG.convert()
        cls.IMG.set_colorkey(cls.IMG.get_at((0, 0)))


class GameContext:
    '''
    The game context contains all the actual game logic. Its attribute are:
        - _screen: the application's display surface on which the game is drawn
        - _background: the background picture bound to change minimally during
                       the whole game.
        - _score: the score
        - _score_font: the font used to write out the score onscreen
    '''
    def __init__(self, screen):
        '''
        Create GameContext object. During initialization, Bow and Target class
        are both instanciated.
        '''
        self._screen =  screen
        self._background = draw_background((200, 240), 8)
        self._score = 0
        self._score_font = pygame.font.Font(FONT_NAME, 55)
        # Bow instanciation
        Bow(self)
        Target(self._background)
        self._drawn = False

    def update(self, inputs):
        if not self._drawn:
            self._screen.blit(self._background, (0, 0))
            self._drawn = True
        # clean up previous position
        for group in Bow.INSTANCE, Arrow.INSTANCES:
            group.clear(self._screen, self._background)
        score_surf_pos = SCREEN_WIDTH//2, 0
        self._screen.blit(self._background, score_surf_pos,
                          pygame.Rect(score_surf_pos, self._score_font.size(str(self._score))))
        # update bow and arrows
        Bow.INSTANCE.sprite.update(inputs)
        Arrow.INSTANCES.update()
        # draw bow and arrows
        for group in Bow.INSTANCE, Arrow.INSTANCES:
            group.draw(self._screen)
        # update score surface
        score_surface = self._score_font.render(str(self._score), False, COLOR_FONT)
        screen.blit(score_surface, score_surf_pos)
        # hand control to another contex
        for an_input in inputs:
            if an_input.type == pygame.KEYDOWN:
                if an_input.key == pygame.K_ESCAPE:
                    self._drawn = False
                    return "Pause"

    def update_score(self, zone, arrow):
        '''
        Update the context's score depending on the zone hit, draw the arrow
        on the background and refresh the screen.
        '''
        self._score += SCORE_TABLE[zone]
        iddle_sprite(arrow.image, arrow.rect, self._background)
        self._screen.blit(self._background, (0, 0))


class PauseContext:
    '''
    The PauseContext is just a layer drawn over the game when it's paused.
    '''
    COLOR_BG = (0, 0, 0, 60)

    def __init__(self, screen):
        self._screen = screen
        self._background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                          flags=pygame.SRCALPHA)
        self._big_font = pygame.font.Font(FONT_NAME, 80)
        self._small_font = pygame.font.Font(FONT_NAME, 55)
        # drawing layer
        self._background.fill(PauseContext.COLOR_BG)
        pause_text = "P . A . U . S . E"
        instruction_text = "press ESCAPE to resume"
        pause_surface = self._big_font.render(pause_text,
                                              False,
                                              COLOR_FONT)
        instruction_surface = self._small_font.render(instruction_text,
                                                      False,
                                                      COLOR_FONT)
        self._background.blit(pause_surface, (40, 40))
        self._background.blit(instruction_surface, (40, 200))
        self._drawn = False

    def update(self, inputs):
        if not self._drawn:
            self._screen.blit(self._background, (0, 0))
            self._drawn = True
        for an_input in inputs:
            if an_input.type == pygame.KEYDOWN:
                if an_input.key == pygame.K_ESCAPE:
                    self._drawn = False
                    return "Game"


class MenuContext:
    '''
    The MenuContext is the central hub for the user to chose options from.
    It redirects the player to a new game, or a list of high scores, ...
    '''

    # TODO:
    #    * class method pos_option(i), pos_cursor(i) 
    #    * créer img_cursor dans GIMP
    #    * charger img_cursor dans la classe
    IMG = pygame.image.load('resources/main_menu.png')
    COLOR_FONT = (0, 0, 0)
    Option = namedtuple('Option', 'string instruction')
    
    def __init__(self, screen):
        self._screen = screen
        self._background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._big_font = pygame.font.Font(None, 80)
        self._small_font = pygame.font.Font(None, 55)
        # options
        option_play = Option('Play', 'Game New')
        option_quit = Option('Quit', 'Quit')
        self._options = option_play, option_quit
        # cursor
        # load img self._cursor_img = ...
        self._cursor_pos = 0
        # drawing layer
        self._background = draw_background((200, 240), 8)
        self._background.blit(MenuContext.IMG, (0, 0))
        # write options 
        for i, option in enumerate(self._options):
            option_surf = self._small_font.render(option.string,
                                                  False,
                                                  MenuContext.COLOR_FONT)
            self._background.blit(option_surf,
                                  MenuContext.pos_option(i))
        self._drawn = False

    def update(self, inputs):
        # draw
        if not self._drawn:
            self._screen.blit(self._background, (0, 0))
        # inputs
        #   up/down: change cursor
        #   enter: select option
        for an_input in inputs:
            if an_input.type == pygame.KEYDOWN:
                if an_input.key == pygame.K_DOWN:
                    self._cursor_pos = (self._cursor_pos + 1) % len(self._options)
                elif an_input.key == pygame.K_UP:
                    self._cursor_pos = (self._cursor_pos - 1) % len(self._options)
                elif an_input.key == pygame.K_ENTER:
                    option = self._options[self._cursor_pos]
                    return option.instruction


def iddle_sprite(img, pos, background):
    '''
    Draw img at pos on the background, thus changing the background.
    '''
    background.blit(img, pos)

def darken_color(base_color, current_color, counter):
    '''
    Randomly return a darken color or the base_color depending on counter,
    the highest counter is the less likely a darker color will be returned.
    '''
    prob = 15 + counter
    rand = random.randint(0, prob)
    if rand >= prob-17:
        # darken
        h, s, l, a = current_color.hsla
        l *= 0.70
        current_color.hsla = h, s, l, a
        return current_color, counter+1
    else:
        return pygame.Color(*base_color), 0

def draw_background(size, sky_stripes=1):
    # background creation
    background = pygame.Surface(size)
    b_width, b_height = size
    # draw sky
    sky_height = b_height / 2
    height_step = sky_height // sky_stripes 
    stripe_color = pygame.Color(*COLOR_SKY)
    h, s, l, a = stripe_color.hsla
    l_step = (LIGHTNESS_SKY_MAX - l) / sky_stripes
    sky_stripe = pygame.Rect(0, 0, b_width, height_step)
    for i in range(sky_stripes):
        pygame.draw.rect(background, stripe_color, sky_stripe)
        sky_stripe.move_ip(0, height_step)
        l += l_step
        stripe_color.hsla = h, s, l, a
    # draw grass
    sky_bottom = int((i+1) * height_step)
    px_array = pygame.PixelArray(background)
    current_color = pygame.Color(*COLOR_GRASS)
    counter = 0
    for i in range(b_width):
        for j in range(sky_bottom, b_height):
            current_color, counter = darken_color(COLOR_GRASS, current_color, counter)
            px_array[i, j] = current_color
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # convert to screen pixel format
    background = background.convert()
    return background


# for test purpose
if __name__ == '__main__':
    
    # pygame init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fps = 30

    # Bow and Arrow init
    Bow.init(fps)
    Arrow.init()
    Target.init()
    # Contexts
    game_context = GameContext(screen)
    pause_context = PauseContext(screen)
    context_dict = {
        "Game": game_context,
        "Pause": pause_context
    }
    active_context = game_context

    while True:

        # dump all previous inputs and grab relevant ones
        inputs = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                inputs.append(event)
            elif event.type == pygame.KEYUP:
                inputs.append(event)
        context_change = active_context.update(inputs)
        if context_change:
            active_context = context_dict[context_change]
        pygame.display.flip()
        clock.tick(fps)


