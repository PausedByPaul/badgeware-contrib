# Dice Roller for Badgeware Tufty
# Selectable dice value up to 20 set by the menu. Default to 6
# Graeme Richards
# raspberryconnect.com
# Sept 26 V1.01 - GPL-3.0 license
# Badgeware Firmware V3
import time
badge.mode(LORES | VSYNC)
screen.font = font.load("/system/assets/fonts/MonaSans-Medium.af")
screen.antialias = image.X2

DIE_TYPE1=6
DIE_TYPE2=6

THROW1=6 #value of throw 1
THROW2=6 #value of throw 2

SDT=1 #single or double throw

dice_layout=[((40,60),),
             ((20,40),(60,80)),
             ((20,40),(40,60),(60,80)),
             ((20,40),(20,80),(60,40),(60,80)),
             ((20,40),(20,80),(60,40),(60,80),(40,60)),
             ((20,40),(20,60),(20,80),(60,40),(60,60),(60,80)),
             ((20,40),(20,60),(20,80),(60,40),(60,60),(60,80),(40,60)),
             ((20,40),(20,60),(20,80),(60,40),(60,60),(60,80),(40,40),(40,80)),
             ((20,40),(20,60),(20,80),(60,40),(60,60),(60,80),(40,60),(40,40),(40,80))
            ]

def load_config():
    global DIE_TYPE1
    global DIE_TYPE2
    config = {"dice1":DIE_TYPE1,"dice2":DIE_TYPE2}
    if State.load("bw_dicetype",config) == 1:
        DIE_TYPE1 = config["dice1"]
        DIE_TYPE2 = config["dice2"]
    else:
        save_config()

def save_config():
    config = {"dice1":DIE_TYPE1,"dice2":DIE_TYPE2}
    State.save("bw_dicetype",config)

def place_dots(num,pos,dot_col=None):
    sel = num
    sel = clamp(sel,0,9)
    dice = dice_layout[sel-1]
    if dot_col is None:
        if num > 9:
            dot_col = color.blue
        else:
            dot_col = color.white
    screen.pen = dot_col
    for x,y in dice:
        if pos == 2:
            x += 80
        if num > 9:
            dots = shape.squircle(x,y,8)
            screen.shape(dots)
        else:
            dots = shape.circle(x,y,8)
            screen.shape(dots)
    screen.pen = color.white
    if pos == 2:
        screen.text(str(num),115,90,25)
    else:
        screen.text(str(num),35,90,25)

def fade_in(num,pos):
    for i in range(2,10):
        if num > 9:
            dot_col = color.blue.scale(i*10)
        else:
            dot_col = color.white.scale(i*10)
        place_dots(num,pos,dot_col)
        time.sleep(0.05)
        scrn_message()
        if pos == 1:
            place_dots(THROW2,2)
        else:
            place_dots(THROW1,1)
        badge.update()

def roll(self):
    return rnd(1,self)

def change_out(pos):
    offset = 0
    swap = 3 - pos
    throw = THROW1-1
    throw_sw = THROW2
    fin = -15
    if pos == 2:
        throw = THROW2-1
        throw_sw = THROW1
        fin = 175
        offset = 80
    throw = clamp(throw,0,8)
    dots = dice_layout[throw]
    twx = [tween(x + offset,fin,300,tween.QUAD_IN).start() for x,y in dots]
    while not twx[-1].done:
        scrn_message()
        place_dots(throw_sw,swap)
        for tw,dot in zip(twx,dots):
            screen.shape(shape.circle(tw.now,dot[1],8))
        badge.update()

def scrn_message():
    screen.text("Roll A, B or C. UP for config",2,5,14)

def menu():
    global DIE_TYPE1
    global DIE_TYPE2
    option=(4,6,8,10,12,20) #Die Max value selection
    i1=0
    i2=0
    while 1:
        screen.pen = color.white
        screen.text("Change Die type",20,5,16)
        screen.pen = color.orange
        screen.text("A & C to change. B Done",10,24,14)
        screen.text(str(DIE_TYPE1),30,40,40)
        screen.text(str(DIE_TYPE2),100,40,40)
        i1 = option.index(DIE_TYPE1)
        i2 = option.index(DIE_TYPE2)
        if badge.pressed(BUTTON_A):
            i1 = (i1+1) % len(option)
            DIE_TYPE1 = option[i1]
        if badge.pressed(BUTTON_C):
            i2 = (i2+1) % len(option)
            DIE_TYPE2 = option[i2]
        if badge.pressed(BUTTON_B):
            save_config()
            return
        badge.update()

load_config()
screen.pen = color.black
screen.clear()
while True:
    if badge.pressed(BUTTON_A):
        change_out(1)
        THROW1 = roll(DIE_TYPE1)
        fade_in(THROW1,1)
        SDT=1
    if badge.pressed(BUTTON_C):
        change_out(2)
        THROW2 = roll(DIE_TYPE2)
        fade_in(THROW2,2)
        SDT=1
    if badge.pressed(BUTTON_B):
        change_out(1)
        THROW1 = roll(DIE_TYPE1)
        fade_in(THROW1,1)
        change_out(2)
        THROW2 = roll(DIE_TYPE2)
        fade_in(THROW2,2)
        SDT=2
    if badge.pressed(BUTTON_UP):
        menu()
    if SDT == 2:
        screen.text("(" + str(THROW1 + THROW2) + ")",69,100,16) #Total of Double throw
    if THROW1 == THROW2 and SDT == 2:
        screen.text("DOUBLE",62,90,10)
    scrn_message()
    place_dots(THROW1,1)
    place_dots(THROW2,2)
    badge.update()
