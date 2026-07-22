import pygame as p, pygame_widgets as pw, random as r, time as t, sys, tkinter as tk, os
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle

def rp(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def checkIn(txt, min, max):
    """
    txt: str, user input.
    min: float, minimum value
    max: float, maximum value
    Checks if the txt input is within bounds specified, returns true if input was within bounds false if not.
    """
    try:
        txt = float(txt) #if input was not a number, an excepetion will be raised and printed in the log
        if txt > max or txt < min:
            raise Exception("input out of bounds") #raise exception if the user input was outside the bounds of the slider
    except Exception as e:
        print(e)
        return False
    return True

def submit(id, min=0, max=0):
    if id == 's':
        if checkIn(speedL.getText(), min, max):
            speed.setValue(float(speedL.getText()))
        else:
            if str(speedL.getText()).lower() == 'fast':
                speed.max = 120
                speed.setValue(120)
            elif str(speedL.getText()).lower() == 'slow':
                speed.min = .01
                speed.setValue(.01)
            else:
                speedL.setText(speed.getValue())
    elif id == 'f':
        if checkIn(fpsL.getText(), min, max):
            fpsS.setValue(float(fpsL.getText()))
        else:
            fpsL.setText(fpsS.getValue())  
    elif id == 'i':
        return True

def save():
    """
    Writes settings to save file, each setting value is stored on one line of the save file.
    """
    saveF = open(rp('./save.dvd'), 'w')
    for i in [speed.getValue(), '\n', fpsS.getValue()]:
        saveF.write(str(i))
    saveF.close()
    print('saved')

def openSave():
    """
    Opens the save file and sets setting values to saved values, returns string for altSpeed mode
    """
    print('opening...')
    saveLines = [] # list for containing saved values
    try:
        saveF = open(rp('./save.dvd'), 'r') # if no save file was found, an excepetion will be raised
        for line in saveF:
            saveLines.append(line)
    except Exception as e:
        print(e) # creates save file and passes default values along
        saveF = open(rp('./save.dvd'), 'w')
        saveF.write('1.0\n60')
        saveLines = ['1.0', '60']
    
    saveF.close()
    
    # sets sliders and text box to saved values, updating slider values will automatically update speed and fps variables
    speed.setValue(float(saveLines[0]))
    speedL.setText(speed.getValue())
    fpsS.setValue(float(saveLines[1]))
    fpsL.setText(fpsS.getValue())
    altSpeed = 'n' # set to 's' for slow mode, 'f' for fast mode and 'n' for normal

    if not checkIn(float(saveLines[0]), .5, 30):
        # if the value is outside bounds, altSpeed will be enabled
        if float(saveLines[0]) > 30:
            altSpeed = 'f'
            speed.max = 120
            speedL.setText('fast')
        else:
            altSpeed = 's'
            speed.min = .01
            speedL.setText('slow')
    return altSpeed

def reset():
    """
    Resets settings to default values
    """
    speed.setValue(1.0)
    fpsS.setValue(60)
    
def change_color(mask, color):
    colored_image = p.Surface((p.display.Info().current_w, p.display.Info().current_h))
    colored_image.fill(color)
    
    final_image = mask.copy()
    final_image.blit(colored_image, (0,0), special_flags = p.BLEND_MULT)
    return final_image
    
def change_image(DVD):
    print('Setting Custom Image...')
    try:
        New_DVD = p.image.load(rp('./sprites/'+imageL.getText()+'.png'))
        Img_X, Img_Y = New_DVD.get_size()
        newY = round((288/Img_X)*Img_Y)
        newX = 288
        if newY > 550:
            newY = 550
            newX = round((550/Img_Y)*Img_X)
        New_DVD = p.transform.scale(New_DVD, (newX, newY))
        Img_X, Img_Y = New_DVD.get_size()
        imageX.setValue(Img_X)
        imageY.setValue(Img_Y)
        icn = p.transform.scale(New_DVD, (100,100))
        p.display.set_icon(icn)
        return New_DVD
    except Exception as e:
        print(e)
        imageL.setText('DVD_Mask')
        return DVD

p.init() #Initialize Pygame
Font = p.font.Font(rp('dvdFont.ttf'), 25) #initializes font
bigFont = p.font.Font(rp('dvdFont.ttf'), 35)
width, height = 1500, 750 #Initial screen width & height
screen = p.display.set_mode((width, height), p.RESIZABLE) #Sets screen to resizable mode
speed = Slider(screen, 100, 50, 800, 20, min=.5, max=30, step=.25, initial=1, colour=(174, 235, 230)) #Initialize speed slider
speed.hide()
speedL = TextBox(screen, 100, 80, 70, 30, fontSize=15, radius=10, onSubmit=submit, onSubmitParams=('s', .5, 30), borderThickness=1, colour=(174, 235, 230)) #Initialize speed text box
speedL.setText('1.0')
speedL.hide()
fpsS = Slider(screen, 100, 180, 800, 20, min=5, max=400, step=1, initial=60, colour=(174, 235, 230))
fpsS.hide()
fpsL = TextBox(screen, 100, 210, 70, 30, fontSize=15, radius=10, onSubmit=submit, onSubmitParams=('f', 5, 400), borderThickness=1, colour=(174, 235, 230))
fpsL.setText('60')
fpsL.hide()
imageL = TextBox(screen, 100, 310, 300, 30, fontSize=15, radius=10, onSubmit=submit, onSubmitParams=('i'), borderThickness=1, colour=(174, 235, 230))
imageL.setText('DVD_Mask')
imageL.hide()
imageX = Slider(screen, 100, 410, 800, 20, min=25, max=550, step=1, initial=288, colour=(174, 235, 230))
imageX.hide()
imageY = Slider(screen, 100, 510, 800, 20, min=25, max=550, step=1, initial=127, colour=(174, 235, 230))
imageY.hide()
keepScale = Toggle(screen, 100, 610, 20, 20, startOn=True)
keepScale.hide()
resetB = Button(screen, 100, 650, 50, 30, text='Reset', onClick=reset)
resetB.hide()
altSpeed = openSave() #opens save file, returns string for altSpeed mode
os.environ['SDL_VIDEO_CENTERED'] = '1'
x, y, vel = 0, 0, [speed.getValue()*r.choice([1, -1]), speed.getValue()*r.choice([1, -1])] #Makes coordinates and velocity
showInfo = False #sets bool to show display info
fullscr = False #sets bool to toggle full screen
iter = False #sets iteration bool for fullscreen toggles
catch = False #sets catch bool for fullscreen toggles
showHelp = False #sets the bool to bring up the help menu
settings = False #sets bool to toggle the settings menu
showMenuHelp = True #sets the bool to toggle the --Press H for help--
c = 0 #sets counter for corner hits
h = 0 #sets counter for total hits
helpmsg = ["----Help----", "F3: Show live in-game information", "F11: Fullscreen toggle", "R: set the logo to the center of the screen", "H: Toggle this menu", "S: Open settings"] #defines list of lines in the help message
p.display.set_caption('DVD')#Sets executable capton
fps = fpsS.getValue() #sets FPS
clock = p.time.Clock() #sets FPS clock
more = Font.render("--Press H for help--", True, (255, 255, 255)) #makes default on boot helper
morerect = more.get_rect() #makes surface for default on boot helper
run = True
x, y = screen.get_rect().center #sets the start location
counter = 0
edgeX = False #edge detection to prevent logo from locking up outside of bounds
edgeY = False

#Loads in sprites
wht = p.Color(0)
wht.hsla = (0, 0, 100, 100)
grn = p.Color(0)
grn.hsla = (122, 100, 40, 100)
blu = p.Color(0)
blu.hsla = (244, 100, 40, 100)
red = p.Color(0)
red.hsla = (0, 100, 50, 30)
org = p.Color(0)
org.hsla = (35, 100, 50, 0)
colors = [wht, grn, blu, red, org]
mask = p.image.load(rp('./sprites/DVD_Mask.png')).convert_alpha()
hue = 0
imageText = 'DVD_Mask'
submit = False

def get_info(color):
    """
    Function for getting in game live information
    """
    info = p.display.Info() #creates object to get information


    curPosX, curPosY = DVDRECT.center[0], DVDRECT.center[1] #gets current position of logo
    curW, curH = info.current_w, info.current_h #gets current width and height of window
    fps = round(clock.get_fps())#gets current fps (in interger)


    hits = "Total hits: "+str(h) #gets total hits
    corner = "Corner hits: "+str(c) #gets corner hits

    return ["DVD X: "+str(curPosX)+" Y: "+str(curPosY), "Screen Width: "+str(curW)+" Height: "+str(curH), "FPS: "+str(fps), hits, corner, color]

def hit_edge(xy, dvd=p.image.load(rp('./sprites/DVD_Mask.png'))):
    """
    Function for when logo hits the edge
        xy: int, expects 1 if horizontal edge is hit and 0 if vertical edge is hit.
    """
    vel[xy] = -vel[xy] #"Bounces" logo of the edge
    new_color = r.choice(colors)
    if new_color == wht:
        color = "Color: White"
    elif new_color == grn:
        color = "Color: Green"
    elif new_color == blu:
        color = "Color: Blue"
    elif new_color == red:
        color = "Color: Red"
    elif new_color == org:
        color = "Color: Orange"
    if imageText == 'DVD_Mask':
        dvd = change_color(mask, new_color) #sets logo to new random color
        icn = p.transform.scale(dvd, (100,100))
        p.display.set_icon(icn) #sets window icon to cureent logo color
    else:
        color = "Custom Image"
    return dvd, color

def textHollow(font, message, fontcolor):
    notcolor = [c^0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = p.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img

def textOutline(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = p.Surface(outline.get_size(), 16)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(0)
    return img
    
def logoInBounds(x, y, w, h):
    if 30 < x < w-30 and 20 < y < h-20:
        return True
    else:
        return False

def renderText(txt):
    newTxt = bigFont.render(txt, True, (255,255,255))
    newTxtRect = newTxt.get_rect()
    return newTxt, newTxtRect

DVD, color = hit_edge(0) #initializes DVD color
DVDRECT = DVD.get_rect() #Makes object for the sprites to be loaded onto
p.display.set_icon(DVD)
offsetX = mask.get_size()[0]/2
offsetY = mask.get_size()[1]/2

dvdW, dvdH = DVDRECT.size
scalar = dvdW/dvdH

bkg = p.Surface((width, height)) #creates and draws transparent background for menu
bkg.set_alpha(50) #makes the background semi-transparent
bkg.fill((200, 222, 221)) #sets background to grey

spTxt, spRect = renderText('Speed')
fpTxt, fpRect = renderText('FPS')
imTxt, imRect = renderText('File Name')
imxTxt, imxRect = renderText('Logo Width: 288')
imyTxt, imyRect = renderText('Logo Height: 127')
ksTxt, ksRect = renderText('Keep Scale')

oldX, oldY = 288, 127

while run:
    events = p.event.get()
    for event in events:
        #Exits if user closes window
        if event.type == p.QUIT:
            print("exiting")
            run = False

        if event.type == p.KEYUP:
            #toggles info menu

            if event.key == p.K_ESCAPE:
                if showMenuHelp:
                    showMenuHelp = False
                elif showHelp:
                    showHelp = False
                else:
                    print("exiting")
                    run = False

            if event.key == p.K_F3:
                showInfo = not showInfo

            #toggles fullscreen
            if event.key == p.K_F11:
                if not fullscr:
                    fullscr = True
                    screen = p.display.set_mode((0, 0), p.FULLSCREEN)
                    p.mouse.set_visible(False)
                else:
                    fullscr = False
                    screen = p.display.set_mode((width-20, height-80), p.RESIZABLE)
                    p.mouse.set_visible(True)

            #resets the logo to the center of the window
            if event.key == p.K_r and not imageL.selected:
                info = p.display.Info()
                x, y = round(info.current_w/2), round(info.current_h/2)

            #toggles help menu
            if event.key == p.K_h and not imageL.selected:
                showHelp = not showHelp
                showMenuHelp = False

            #toggles settings
            if event.key == p.K_s:
                if not imageL.selected and not speedL.selected and not fpsL.selected:
                    settings = not settings

                if settings:
                    speed.show()
                    speedL.show()
                    fpsS.show()
                    fpsL.show()
                    imageL.show()
                    resetB.show()
                    imageX.show()
                    imageY.show()
                    keepScale.show()
                    p.mouse.set_visible(True)
                else:
                    speed.hide()
                    speedL.hide()
                    fpsS.hide()
                    fpsL.hide()
                    imageL.hide()
                    resetB.hide()
                    imageX.hide()
                    imageY.hide()
                    keepScale.hide()
                    if fullscr:
                        p.mouse.set_visible(False)

    src = p.display.Info()
    width, height = src.current_w, src.current_h
            
    #Makes new coordinates:
    x += vel[0]
    y += vel[1]

    #Checks if logo hits a wall
    if x > width-offsetX and not edgeX:
        print("right")
        DVD, color = hit_edge(0, DVD)
        h += 1 #increases hit counter
        edgeX = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
        
    if x < offsetX and not edgeX:
        print("left")
        DVD, color = hit_edge(0, DVD)
        h += 1 #increases hit counter
        edgeX = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
        
    if y > height-offsetY and not edgeY:
        print("bottom")
        DVD, color = hit_edge(1, DVD)
        if not edgeX:
            h += 1 #increases hit counter
        edgeY = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size

    if y < offsetY and not edgeY:
        print("top")
        DVD, color = hit_edge(1, DVD)
        if not edgeX:
            h += 1 #increases hit counter
        edgeY = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
        
    if edgeX and edgeY:
        print("corner")
        c += 1 #increase corner counter
       
    if edgeX and logoInBounds(x, y, width, height):
        edgeX = False
        
    if edgeY and logoInBounds(x, y, width, height):
        edgeY = False
    
    screen.fill((0, 0, 0)) #redraws black background
    Iy = 9 #sets text starting Y coordinate
    offsetX, offsetY = dvdW/2, dvdH/2
    DVDRECT.center = (x, y) #moves the logo
    screen.blit(DVD, DVDRECT)

    #shows live info menu
    if showInfo:
        info = get_info(color)
        for i in info:
            curIn = Font.render(i, True, (255,255,255))
            curInRect = curIn.get_rect()
            curInRect.center = (round(curInRect.w/2), Iy)
            screen.blit(curIn, curInRect)
            Iy += 18

    #shows help menu
    if showHelp:
        for i in helpmsg:
            help = Font.render(i, True, (255, 255, 255))
            helprect = help.get_rect()
            helprect.center = (round(helprect.w/2), Iy)
            screen.blit(help, helprect)
            Iy += 18
    else:
        #shows default on boot helper
        if showMenuHelp:
            morerect.center = (round(morerect.w/2), Iy)
            screen.blit(more, morerect)
            counter += 1

    #displays settings menu
    if settings:
        if bkg.get_size()[0] != width or bkg.get_size()[1] != height:
            bkg = p.transform.scale(bkg, (width, height))
        screen.blit(bkg, (0,0))

        spRect.center = (round(width/2), 28)
        screen.blit(spTxt, spRect)

        fpRect.center = (round(width/2), 158)
        screen.blit(fpTxt, fpRect)
        
        imRect.center = (round(width/2), 288)
        screen.blit(imTxt, imRect)
        
        imxRect.center = (round(width/2), 388)
        screen.blit(imxTxt, imxRect)
        
        imyRect.center = (round(width/2), 488)
        screen.blit(imyTxt, imyRect)
        
        ksRect.center = (round(width/2), 588)
        screen.blit(ksTxt, ksRect)

        if speed.getWidth() != width-200:
            speed.setWidth(width-200)
        if fpsS.getWidth() != width-200:
            fpsS.setWidth(width-200)
        if imageX.getWidth() != width-200:
            imageX.setWidth(width-200)
        if imageY.getWidth() != width-200:
            imageY.setWidth(width-200)
        speedL.setX(int(round(width/2))-int(round(speedL.getWidth()/2)))
        fpsL.setX(int(round(width/2))-int(round(fpsL.getWidth()/2)))
        imageL.setX(int(round(width/2))-int(round(imageL.getWidth()/2)))
        keepScale.setX(int(round(width/2))-int(round(keepScale.getWidth()/2)))
        resetB.setX(int(round(width/2))-int(round(resetB.getWidth()/2)))

        if abs(vel[0]) != speed.getValue():
            if speed.getValue() > 30 and altSpeed != 'f':
                altSpeed = 'f'
                speedL.setText('fast')
            elif speed.getValue() > 30 and altSpeed == 'f':
                speed.setValue(30)
                speed.max = 30
                altSpeed = 'n'
            elif speed.getValue() < .5 and altSpeed != 's':
                altSpeed = 's'
                speedL.setText('slow')
            elif speed.getValue() < .5 and altSpeed == 's':
                speed.setValue(.5)
                speed.min = .5
                altSpeed = 'n'
            else:
                altSpeed = 'n'
                speed.min = .5
                speed.max = 30
                speedL.setText(speed.getValue())
        
        if fps != fpsS.getValue():
            fpsL.setText(fpsS.getValue())
            fps = fpsS.getValue()

        if vel[0] < 0:
            vel[0] = -(speed.getValue())
        else:
            vel[0] = speed.getValue()

        if vel[1] < 0:
            vel[1] = -(speed.getValue())
        else:
            vel[1] = speed.getValue()
            
        if imageL.getText() != imageText and not imageL.selected:
            DVD = change_image(DVD)
            dvdW, dvdH = DVD.get_size()
            scalar = dvdW/dvdH
            imageText = imageL.getText()

        if oldX != imageX.getValue() or oldY != imageY.getValue():
            if keepScale.getValue() and oldX != imageX.getValue():
                newY = round(imageX.getValue()/scalar)
                if newY > 550:
                    print('Too Tall')
                    imageX.setValue(round(550*scalar))
                    imageY.setValue(550)
                else:
                    imageY.setValue(newY)
            if keepScale.getValue() and oldY != imageY.getValue():
                newX = round(imageY.getValue()*scalar)
                if newX > 550:
                    print('Too Wide')
                    imageY.setValue(round(imageX.getValue()/scalar))
                    imageX.setValue(550)
                else:
                    imageX.setValue(newX)
            
            imxTxt, imxRect = renderText('Logo Width: '+str(imageX.getValue()))
            imyTxt, imyRect = renderText('Logo Height: '+str(imageY.getValue()))
            
            if imageText == 'DVD_Mask':
                if color == "Color: White":
                    new_color = wht
                if color == "Color: Green":
                    new_color = grn
                if color == "Color: Blue":
                    new_color = blu
                if color == "Color: Red":
                    new_color = red
                if color == "Color: Orange":
                    new_color = org
                DVD = change_color(mask, new_color) #refreshes logo before transform, image gets weird if this is not done
            else:
                DVD = p.image.load('./sprites/'+imageText+'.png') #refreshes image if custom image is being used
            
            DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
            DVDRECT = DVD.get_rect()
            dvdW, dvdH = DVDRECT.size
            
            oldX, oldY = imageX.getValue(), imageY.getValue()
          
        if dvdW/dvdH != scalar and keepScale.getValue():
            newY = round(imageX.getValue()/scalar)
            if newY > 550:
                newX = round(imageY.getValue()*scalar)
                imageX.setValue(newX)
            else:
                imageY.setValue(newY)

    if counter >= fps*5:
        showMenuHelp = False
        counter = 0
    
    pw.update(events)
    p.display.update() #updates screen
    clock.tick(fps) #updates fps clock

save()
p.quit()
quit()