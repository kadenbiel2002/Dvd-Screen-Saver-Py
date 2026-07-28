import pygame as p, pygame_widgets as pw, random as r, time as t, sys, tkinter as tk, os, requests, subprocess, pdb
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle
from pygame_widgets.progressbar import ProgressBar
from tkinter import filedialog
from packaging.version import Version

current_version = 'v1.3.1'
latest_version = ''
download_url = 'None'
download = False
devTools = False

def check_for_updates():
    global download_url, latest_version, devTools
    url = "https://api.github.com/repos/kadenbiel2002/Dvd-Screen-Saver-Py/releases/latest"
    print("Checking for updates...")
    try:
        response = requests.get(url).json()
        latest_version = response.get("tag_name", "")
        assets = response.get("assets", [])
        exe = None
        if Version(latest_version) > Version(current_version):
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    print(f"New version {latest_version} available! download at: {download_url}")
                    break
        elif Version(current_version) > Version(latest_version):
            print(f"{current_version} is detected as being in development, dev mode enabled")
            devTools = True
        else:
            print(f"{current_version} is the latest version")
    except Exception as e:
        print(f"Could not check for updates: {e}")

def download_update():
    print(f"Downloading {latest_version}...")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open('./temp.exe', "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    restart_and_replace()
    return

def restart_and_replace():
    running_exe = sys.executable  # Path to the currently running .exe
    new_exe = "./temp.exe"  # The updated executable file
    # 2. Spawn a helper/updater process (detached from the current process)
    # The helper script/bat will wait a second, overwrite running_exe with new_exe, and launch it.
    script_content = f"""
    timeout /t 2 > nul
    del "{running_exe}"
    copy "{new_exe}" "{running_exe}"
    del "{new_exe}"
    start "" "{running_exe}"
    del "%~f0"
    """
            
    # Creates a temporary batch file for the update sequence
    batch_file = "update_helper.bat"
    batch = open(batch_file, "w")
    batch.write(script_content)
    batch.close()

    #if the running exe is python.exe, batch file is not executed so we don't replace python with the dvd screen saver (i've done it, trust me you don't want to try it)
    if not running_exe.endswith('python.exe'):
        subprocess.Popen(batch_file, shell=True)
    else:
        print("dev mode detected, batch file not ran")

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
    saveF = open('./save.dvd', 'w')
    for i in [speed.getValue(), '\n', fpsS.getValue(), '\n', imageX.getValue(), '\n', imageY.getValue(), '\n', imageL.getText(), '\n', keepScale.getValue(), '\n', sfxOn.getValue()]:
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
        saveF = open('./save.dvd', 'r') # if no save file was found, an excepetion will be raised
        for line in saveF:
            saveLines.append(line)
    except Exception as e:
        print(e) # creates save file and passes default values along
        saveF = open('./save.dvd', 'w')
        saveF.write('1.0\n120\n288\n127\n./sprites/DVD_Mask.png\nTrue\nTrue')
        saveLines = ['1.0', '120', '288', '127', './sprites/DVD_Mask.png', 'True', 'True']
    
    saveF.close()
    
    # sets sliders and text box to saved values, updating slider values will automatically update speed and fps variables
    try:
        speed.setValue(float(saveLines[0]))
    except:
        speed.setValue(1.0)
    speedL.setText(speed.getValue())
    try:
        fpsS.setValue(int(saveLines[1]))
    except:
        fpsS.setValue(120)
    fpsL.setText(fpsS.getValue())
    try:
        imageX.setValue(int(saveLines[2]))
    except:
        imageX.setValue(288)
    try:
        imageY.setValue(int(saveLines[3]))
    except:
        imageY.setValue(127)
    try:
        imageL.setText(saveLines[4].replace('\n', ''))
    except:
        imageL.setText('./sprites/DVD_Mask.png')
    try:
        if saveLines[5] == 'False':
            ksBool = False
        else:
            ksBool = True
    except:
        ksBool = True
    try:
        if saveLines[6] == 'False':
            soBool = False
        else:
            soBool = True
    except:
        soBool = True
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
    return altSpeed, ksBool, soBool

def reset():
    """
    Resets settings to default values
    """
    speed.setValue(1.0)
    fpsS.setValue(120)
    imageL.setText('./sprites/DVD_Mask.png')
    if not keepScale.getValue():
        keepScale.toggle()
    
def change_color(mask, color):
    colored_image = p.Surface((p.display.Info().current_w, p.display.Info().current_h))
    colored_image.fill(color)
    
    final_image = mask.copy()
    final_image.blit(colored_image, (0,0), special_flags = p.BLEND_MULT)
    return final_image
    
def change_image(DVD):
    print('Setting Custom Image...')
    try:
        New_DVD = p.image.load(rp(imageL.getText()))
        Img_X, Img_Y = New_DVD.get_size()
        if startProg < 1.0:
            newX = imageX.getValue()
            newY = imageY.getValue()
        else:
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
        imageL.setText('./sprites/DVD_Mask.png')
        return DVD

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a File",
        initialdir=os.getcwd(), # Starts in the current directory
        filetypes=(("PNG", "*.png"), ("JPEG", "*.jpeg"), ("JPG", "*.jpg"), ("BMP", "*.bmp"), ("WEBP", "*.webp"), ("SVG", "*.svg"))
    )

    if file_path:
        imageL.setText(file_path)

startProg = 0.0

def progress():
    global startProg
    startProg += 0.005
    return startProg

p.mixer.init()
sfx1 = p.mixer.Sound(rp('./sprites/sfx1.ogg'))
sfx2 = p.mixer.Sound(rp('./sprites/sfx2.ogg'))
sfx3 = p.mixer.Sound(rp('./sprites/sfx3.ogg'))
sfx4 = p.mixer.Sound(rp('./sprites/sfx4.ogg'))
trumpet = p.mixer.Sound(rp('./sprites/trumpet.ogg'))
root = tk.Tk()
root.withdraw() 
root.attributes('-topmost', True)
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
fpsS = Slider(screen, 100, 180, 800, 20, min=5, max=400, step=1, initial=120, colour=(174, 235, 230))
fpsS.hide()
fpsL = TextBox(screen, 100, 210, 70, 30, fontSize=15, radius=10, onSubmit=submit, onSubmitParams=('f', 5, 400), borderThickness=1, colour=(174, 235, 230))
fpsL.setText('60')
fpsL.hide()
imageL = TextBox(screen, 100, 310, 800, 30, fontSize=15, radius=10, onSubmit=submit, onSubmitParams=('i'), borderThickness=1, colour=(174, 235, 230))
imageL.setText('./sprites/DVD_Mask.png')
imageL.disable()
imageL.hide()
fileB = Button(screen, 100, 310, 150, 30, text='Choose File', onClick=select_file)
fileB.hide()
imageX = Slider(screen, 100, 410, 800, 20, min=25, max=550, step=1, initial=288, colour=(174, 235, 230))
imageX.hide()
imageY = Slider(screen, 100, 510, 800, 20, min=25, max=550, step=1, initial=127, colour=(174, 235, 230))
imageY.hide()
resetB = Button(screen, 100, 650, 50, 30, text='Reset', onClick=reset)
resetB.hide()
altSpeed, ksBool, soBool = openSave() #opens save file, returns string for altSpeed mode
keepScale = Toggle(screen, 100, 610, 20, 20, startOn=ksBool)
keepScale.hide()
sfxOn = Toggle(screen, 100, 610, 20, 20, startOn=soBool)
sfxOn.hide()
startup = ProgressBar(screen, 100, 100, 800, 60, progress, curved=True)
os.environ['SDL_VIDEO_CENTERED'] = '1'
x, y, vel = 0, 0, [speed.getValue()*r.choice([1, -1]), speed.getValue()*r.choice([1, -1])] #Makes coordinates and velocity
showInfo = False #sets bool to show display info
fullscr = False #sets bool to toggle full screen
iter = False #sets iteration bool for fullscreen toggles
catch = False #sets catch bool for fullscreen toggles
showHelp = False #sets the bool to bring up the help menu
settings = False #sets bool to toggle the settings menu
c = 0 #sets counter for corner hits
h = 0 #sets counter for total hits
helpmsg = ["----Help----", "F3: Show live in-game information", "F11: Fullscreen toggle", "R: set the logo to the center of the screen", "H: Toggle this menu", "S: Open settings"] #defines list of lines in the help message
p.display.set_caption('DVD')#Sets executable capton
fps = fpsS.getValue() #sets FPS
clock = p.time.Clock() #sets FPS clock

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
imageText = './sprites/DVD_Mask.png'
submit = False
prevHit = ''
finished = False
sfx = sfx1
playTrumpets = False

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

    return ["Version: "+str(current_version), "DVD X: "+str(curPosX)+" Y: "+str(curPosY), "Screen Width: "+str(curW)+" Height: "+str(curH), "FPS: "+str(fps), hits, corner, color]

def hit_edge(xy, dvd=p.image.load(rp('./sprites/DVD_Mask.png'))):
    """
    Function for when logo hits the edge
        xy: int, expects 1 if horizontal edge is hit and 0 if vertical edge is hit.
    """
    global sfx
    if finished and sfxOn.getValue():
        sfx.stop()
        sfx = r.choice([sfx1, sfx2, sfx3, sfx4])
        sfx.play()
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
    if imageText == './sprites/DVD_Mask.png':
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

bkg = p.Surface((50, 50)) #creates and draws transparent background for menu
bkg.set_alpha(50) #makes the background semi-transparent
bkg.fill((200, 222, 221)) #sets background to grey

startTxt, startRect = renderText('Press H in-game for options menu')
spTxt, spRect = renderText('Speed')
fpTxt, fpRect = renderText('FPS')
imTxt, imRect = renderText('File Name')
imxTxt, imxRect = renderText('Logo Width: 288')
imyTxt, imyRect = renderText('Logo Height: 127')
ksTxt, ksRect = renderText('Keep Scale')
soTxt, soRect = renderText('Sound FX')

oldX, oldY = 0, 0

run = __name__ == '__main__'

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
                if showHelp:
                    showHelp = False
                elif settings:
                    settings = False
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

            #toggles settings
            if event.key == p.K_s:
                if not speedL.selected and not fpsL.selected:
                    settings = not settings

                if settings:
                    speed.show()
                    speedL.show()
                    fpsS.show()
                    fpsL.show()
                    imageL.show()
                    fileB.show()
                    resetB.show()
                    imageX.show()
                    imageY.show()
                    keepScale.show()
                    sfxOn.show()
                    p.mouse.set_visible(True)
                else:
                    speed.hide()
                    speedL.hide()
                    fpsS.hide()
                    fpsL.hide()
                    imageL.hide()
                    fileB.hide()
                    resetB.hide()
                    imageX.hide()
                    imageY.hide()
                    keepScale.hide()
                    sfxOn.hide()
                    if fullscr:
                        p.mouse.set_visible(False)
            if devTools:
                #forces logo to hit corner, only for debugging
                if event.key == p.K_c:
                    if vel[0] > 0:
                        x = width-offsetX-100
                    else:
                        x = offsetX+100
                    if vel[1] > 0:
                        y = height-offsetY-100
                    else:
                        y = offsetY+100

                if event.key == p.K_d:
                    pdb.set_trace()
            

    src = p.display.Info()
    width, height = src.current_w, src.current_h
            
    #Makes new coordinates:
    x += vel[0]
    y += vel[1]

    #Checks if logo hits a wall
    if x > width-offsetX and not edgeX and prevHit != 'right':
        prevHit = 'right'
        DVD, color = hit_edge(0, DVD)
        h += 1 #increases hit counter
        edgeX = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
        
    if x < offsetX and not edgeX and prevHit != 'left':
        prevHit = 'left'
        DVD, color = hit_edge(0, DVD)
        h += 1 #increases hit counter
        edgeX = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
    
    if y > height-offsetY and not edgeY and prevHit != 'bottom':
        prevHit = 'bottom'
        DVD, color = hit_edge(1, DVD)
        if not edgeX:
            h += 1 #increases hit counter
        edgeY = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size

    if y < offsetY and not edgeY and prevHit != 'top':
        prevHit = 'top'
        DVD, color = hit_edge(1, DVD)
        if not edgeX:
            h += 1 #increases hit counter
        edgeY = True
        DVD = p.transform.scale(DVD, (imageX.getValue(), imageY.getValue()))
        DVDRECT = DVD.get_rect()
        dvdW, dvdH = DVDRECT.size
    
    if edgeX and edgeY:
        if sfxOn.getValue():
            sfx.stop()
            trumpet.play()
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
        if devTools:
            info.insert(1, "Dev Tools Enabled")
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

    #displays settings menu
    if settings:
        if bkg.get_size()[0] != width or bkg.get_size()[1] != height:
            """Detects if screen size has changed, scales setting page accordingly"""
            bkg = p.transform.scale(bkg, (width, height))
            spRect.center = (round(width/2), 28)
            fpRect.center = (round(width/2), 158)
            imRect.center = (round(width/2), 288)
            ksRect.center = (round(width/2)-100, 588)
            soRect.center = (round(width/2)+100, 588)
            speed.setWidth(width-200)
            fpsS.setWidth(width-200)
            imageX.setWidth(width-200)
            imageY.setWidth(width-200)
            speedL.setX(int(round(width/2))-int(round(speedL.getWidth()/2)))
            fpsL.setX(int(round(width/2))-int(round(fpsL.getWidth()/2)))
            keepScale.setX(int(round(width/2))-int(round((keepScale.getWidth()+sfxOn.getWidth()+200)/2)))
            sfxOn.setX(keepScale.getX()+keepScale.getWidth()+200)
            resetB.setX(int(round(width/2))-int(round(resetB.getWidth()/2)))

            fileWidth = imageL.getWidth() + fileB.getWidth() + 25
            fileB.setX(round((width/2)-(fileWidth/2)))
            imageL.setX(fileB.getX()+fileB.getWidth()+25)
        imxRect.center = (round(width/2), 388)
        imyRect.center = (round(width/2), 488)
        #Draws text labels:
        screen.blit(bkg, (0,0))
        screen.blit(spTxt, spRect)
        screen.blit(fpTxt, fpRect)
        screen.blit(imTxt, imRect)
        screen.blit(imxTxt, imxRect)
        screen.blit(imyTxt, imyRect)
        screen.blit(ksTxt, ksRect)
        screen.blit(soTxt, soRect)

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
            
        if imageL.getText() != imageText:
            DVD = change_image(DVD)
            dvdW, dvdH = DVD.get_size()
            scalar = dvdW/dvdH
            imageText = imageL.getText()
            if imageText != './sprites/DVD_Mask.png':
                color = 'Custom Image'
            else:
                color = 'Color: White'
            oldX, oldY = 0, 0

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
            
            if color != 'Custom Image':
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
                DVD = p.image.load(imageText) #refreshes image if custom image is being used
            
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

    if startProg < 1.0:
        startup.setWidth(width-100)
        startup.setX(round((width/2)-(startup.getWidth()/2)))
        startup.setY(round(height/2))
        startRect.center = (round(width/2), (startup.getY()-50))
        screen.fill((55, 59, 66))
        screen.blit(startTxt, startRect)
        settings = True
    elif not finished:
        finished = True
        settings = False
        startup.hide()

    if latest_version == '':
        check_for_updates()
        if devTools:
            helpmsg.append("C: Force logo to corner")
            helpmsg.append("D: Open debug console")

    if download_url != 'None' and startProg > 0.37:
        download = tk.messagebox.askyesno(title="Update Available!", message=f"Version {latest_version} is available for download, would you like to update?")
        if download:
            download_update()
            run = False
        else:
            download_url = 'None'

    pw.update(events)
    p.display.update() #updates screen
    clock.tick(fps) #updates fps clock

save()
p.quit()