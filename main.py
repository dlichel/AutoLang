#dmichel

# This demos using modes (aka screens).

from cmu_112_graphics import *
from PIL import ImageTk,Image
import json
import math, os, random
import sentence_translation
import data_cleaner
import dataModify
import random

#write comments idiot

#class for button?

class Button:
    def __init__(self, app, canvas):
        self.app = app
        self.canvas = canvas
        self.tag = None
        
    def __repr__(self):
        return self.tag
        
    def draw(self, x, y, image, hover=False, hoverImg=None, tag=None, scale=1):
        self.tag = tag

##########################
# MENU
##########################

#deprecated function to add a button.
def newButton(app, button, tag):
    if button not in app.buttonDict:
        app.buttonDict[button] = tag

#draws a button based of an image. Makes hover too.
def drawButton(app, canvas, x, y, image, tag=None, hover=False, hoverImg=None, scale=1):
    img = app.scaleImage(image, scale)
    imgWdth = img.size[0]
    imgHght = img.size[1]
    buttonTuple = (abs(x-(imgWdth//2)), abs(x+(imgWdth//2)), abs(y-(imgHght//2)), abs(y+(imgHght//2)))
    newButton(app, buttonTuple, tag)
    if hover == False:
        canvas.create_image(x, y, image=ImageTk.PhotoImage(img))
    else:
        try:
            assert(hoverImg != None)
        except:
            print("Image Not Specified or Found")
            quit()
        newImg = app.scaleImage(hoverImg, scale)
        if (app.mousePos[0] > abs(x-(imgWdth//2)) and
            app.mousePos[0] < abs(x+(imgWdth//2)) and
            app.mousePos[1] > abs(y-(imgHght//2)) and
            app.mousePos[1] < abs(y+(imgHght//2))):
            canvas.create_image(x, y, image=ImageTk.PhotoImage(newImg))
        else:
            canvas.create_image(x, y, image=ImageTk.PhotoImage(img))

#draws the different thing in the menu. Remove unnecessary stuff in final.
def menu_redrawAll(app, canvas):
    drawBackground(app, canvas, app.bgScaled)
    if app.width < 1200 and app.height < 1200:
        canvas.create_rectangle(app.width*(0.25), app.height*(0.12), app.width*(0.75), (app.height * (0.2)),fill='white',width=3)
        scaled = app.boundedScale(app.logo, app.width*0.25,app.height*0.12,app.width*0.75,app.height*0.2)
        canvas.create_image(app.width//2,app.height*0.16,image=ImageTk.PhotoImage(scaled))
        optionCmd= "app.currentScreen = 'options'"
        drawButton(app, canvas, app.width*0.5, app.height*0.5, app.optionButton, tag='options', hover=True, hoverImg=app.optionButtonHover, scale=0.15)
        drawButton(app, canvas, app.width*0.5, app.height*0.3, app.sentenceButton, hover=True, tag='sentence', hoverImg=app.sentenceButtonHover, scale=0.15)
        drawButton(app, canvas, app.width*0.5, app.height*0.7, app.editButton, hover = True, tag='edit', hoverImg = app.editButtonHover, scale=0.15)    
    else:
        canvas.create_rectangle(app.width*(0.3), app.height*(0.12), app.width*(0.7), (app.height * (0.24)),fill='white',width=3)
        scaled = app.boundedScale(app.logo, app.width*0.3,app.height*0.12,app.width*0.7,app.height*0.24)
        canvas.create_image(app.width//2,app.height*0.18,image=ImageTk.PhotoImage(scaled))
        drawButton(app, canvas, app.width*0.5, app.height*0.5, app.optionButton, tag='options', hover=True, hoverImg=app.optionButtonHover, scale=0.15)
        drawButton(app, canvas, app.width*0.5, app.height*0.3, app.sentenceButton, tag='sentence', hover=True, hoverImg=app.sentenceButtonHover, scale=0.15)
        drawButton(app, canvas, app.width*0.5, app.height*0.7, app.editButton, hover = True, tag='edit', hoverImg = app.editButtonHover, scale=0.15)    


#deprecated. Fix later.
def menu_keyPressed(app, event):
    app.mode = 'sentence'

#determines if button click in bounds.
def isValid(pos, bTuple):
    if pos[0] > bTuple[0]:
        if pos[0] < bTuple[1]:
            if pos[1] > bTuple[2]:
                if pos[1] < bTuple[3]:
                    return True
    return False

#determines mouse click commands.
def menu_mousePressed(app, event):
    app.clickPos = (event.x, event.y)
    for i in app.buttonDict:
        if isValid(app.clickPos, i):
            app.mode = app.buttonDict[i]
            if app.mode == 'sentence':
                app.input = ""
                app.timerDelay = 1

#registers position of mouse.
def menu_mouseMoved(app, event):
    app.mousePos = (event.x, event.y)
    #print(app.mousePos)

#makes sure the click isnt held down.
def menu_mouseReleased(app, event):
    app.clickPos = (0,0)
    

#######################
# EDIT
#######################


#draws lines to the canvas
def draw_canvas(app, canvas):
    for i in app.lineList:
        canvas.create_line(i[0], i[1], i[2], i[3], width=5)
        
def fetch_random():
    
    f = open('Data/Databases/OneChar.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    ind = random.randint(0,len(lines))
    f.close()
    #print(lines[ind])
    #print(repr(lines[ind][0]))
    return lines[ind][0]

def edit_redrawAll(app, canvas):
    drawBackground(app, canvas, app.editBackground)
    
    if app.fetched == False:
        app.char = fetch_random()
        app.fetched = True
    
    canvas.create_rectangle(app.width*0.25,app.height*0.1,app.width*0.75,app.height*0.9,fill='white',width=3)
    canvas.create_line(app.width*0.25, app.height*0.5, app.width*0.75, app.height*0.5, width=3)
    canvas.create_text(app.width//2, (app.height*0.25), text=app.char,
                       fill = 'black',
                       font=('Senty Snow Mountain 新蒂雪山体',50,"normal"))
    draw_canvas(app, canvas)

def edit_keyPressed(app, event):
    if event.key == 'Escape':
        app.lineList.clear()
        app.fetched = False
        app.mode = 'menu'
    if event.key == 'Enter':
        app.lineList.clear()
        app.fetched = False

#if I had time I would make this to any bounds, but this will do.
def inBounds(app, x, y):
    if x > app.width*0.25:
        if x < app.width*0.75:
            if y > app.height*0.5:
                if y < app.height*0.9:
                    return True
    return False

def edit_mousePressed(app, event):
    if inBounds(app, event.x, event.y):
        app.lineList.append([event.x, event.y, event.x, event.y])
        app.currentPos = (event.x, event.y)
    #print("pressed at")
    #print(event.x, event.y)
    
    

def edit_mouseDragged(app, event):
    #print(event.x, event.y)
    #app.dragCoords = (event.x, event.y)
    if inBounds(app, event.x, event.y):
        app.lineList.append([app.currentPos[0], app.currentPos[1], event.x, event.y])
        app.currentPos = (event.x, event.y)

def edit_mouseReleased(app, event):
    #print("release")
    app.clickCoords = app.currentPos
    app.dragCoords = app.currentPos
    app.currentPos = app.currentPos


##########################
# SENTENCE
##########################


#draws the text in the middle and top of screen.
def drawSentence(app, canvas):
    canvas.create_rectangle(app.width*0.1,app.height*0.1,app.width*0.9,app.height*0.9,fill='white')
    
    
    canvas.create_text(app.width//2, (app.height//5), text=app.currentSentence,
                       fill = 'black',
                       font=(app.font,math.floor((30/800)*app.width*app.modifyFont),"normal"))

#literally just draws the text in the middle of the screen.
def drawInput(app, canvas):
    canvas.create_text(app.width//2, (app.height//2), text=app.input,
                       fill = 'black',
                       font=("Times New Roman",30,"normal"))

#makes the opposite of JIAN FAN, and vice versa.
def opposite(tizi):
    if tizi == 'JIAN':
        return 'FAN'
    if tizi == 'FAN':
        return 'JIAN'
    if tizi == 'UNKNOWN':
        return 'UNKNOWN'
    else:
        return 'ERROR'

#changes the score based on your accuracy.
def scoreChange(app):
    app.level = app.loader.giveLevel(app.accuracy, app.level)
    app.data['level'] = app.level
    with open('Data/saves/'+app.saveFile, 'w') as json_file:
        json.dump(app.data, json_file, indent=4)
    json_file.close()
    #print(app.level)

#formats and determines the next sentence. Also already determines the solution(s).
#also translates them if need be.
def newSentence(app):
    app.submit = False
    app.currentSentenceDict = app.loader.findSentence(difficulty=app.level, mode=('HSK', 'MODERATE'))
    sentence = app.currentSentenceDict['Phrase']
    finalSentence = list(sentence.values())[0]
    sentence_tizi = app.loader.detect_tizi(finalSentence)
    #print(sentence_tizi)
    if sentence_tizi == opposite(app.tizi):
        #print(finalSentence)
        s = opposite(app.tizi)
        finalSentence = app.loader.switch_tizi(finalSentence,s)
        #print(finalSentence)
    
    if len(finalSentence) > 10:
        finalSentence = finalSentence[:len(finalSentence)//2] + "\n" + finalSentence[len(finalSentence)//2:]
    
    
    app.currentSentence = finalSentence
    sol = list(app.currentSentenceDict['Translation'].values())[0]
    if len(sol) > math.floor(app.width * (40/800)):
        sol = sol[:len(sol)//2] + "\n" + sol[len(sol)//2:]
    app.currentSol = sol
    app.timerDelay = 0
    app.called = True

#loads the sentence screen for the first time.
def sentenceLoader(app, canvas):
    if app.counter < 50:
        app.counter += 1
    else:
        app.input = ""
        app.loader = sentence_translation.Sentence('json here')
        if bool(app.loader) == False:
            app.loader.load()
            app.loader.makeHashes()
            app.sentence_loaded = True

#just draws the solution. In the future, app.currentSol needs to
#be formatted to determine which solution was best.
def drawSol(app, canvas):
    #canvas.create_text(app.width//2, (app.height*0.75), text=app.currentSol,
    #                   fill = 'black',
    #                   font=("Times New Roman",15,"normal"))
    score = 'Sentence Score: ' + str(app.accuracy[0])
    canvas.create_text(app.width//2, (app.height*0.75), text=score,
                       fill = 'black',
                       font=("Times New Roman",15,"normal"))
    translation = 'Answer: ' + str(app.accuracy[1])
    canvas.create_text(app.width//2, (app.height*0.7), text=translation,
                       fill = 'black',
                       font=("Times New Roman",15,"normal"))
    level = 'Level: ' + str((app.level - 1) * 100)
    canvas.create_text(app.width//2, (app.height * 0.8), text=level,
                       fill='black',
                       font=("Times New Roman", 15, "normal"))
    app.solShown = True

#displays the problem and solution screen.
#app.sentence_loaded is the solution screen,
#otherwise its the problem screen. fix the double
#drawBackground. Lock input after sol is shown.
def sentence_redrawAll(app, canvas):
    if app.sentence_loaded == False:
        drawBackground(app, canvas, app.sentenceBackground)
        drawLoadingScreen(app, canvas)
        sentenceLoader(app, canvas)
    else:
        drawBackground(app, canvas, app.sentenceBackground)
        if app.called == False:
            newSentence(app)
        drawSentence(app, canvas)
        drawInput(app, canvas)
        if app.submit:
            drawSol(app, canvas)
        
        
    
#loads the loading screen gif.
def sentence_timerFired(app):
    if app.sentence_loaded == False:
        app.frameCounter = (1+app.frameCounter) % len(app.loadingScreen)
    

#deprecated for now, may use in future. Remove in final if not.
def sentence_mousePressed(app, event):
    pass

#goes into semantic comparison for sentence_translation.
#Right now uses v1, will use v2, fix when v2 is done.
def determineAccuracy(app):
    #print(type(app.input), type(app.currentSol))
    inp = app.input.replace('\n', '')
    #print(f'inp: {app.loader.recieveTranslations(app.currentSol)}')
    #print(app.currentSol)
    newList = app.loader.recieveTranslations(app.currentSol)
    solList = []
    for i in newList:
        solList.append(i[0].strip())
    #print(f'sol: {solList}')
    ans = app.loader.rank_input(inp, solList)
    app.accuracy = ans
    #app.data['level'] = ans[0]
    #print(app.saveFile)
    
    
#keybinds for the sentence practice frame.
#many of these keybinds are debug, but the important ones I will keep
#keep Enter, Backspace, Space, Alphabet
#reroute app.called = False to another key (as a skip key), have "-" decrease font size,
#and "+" increases.
#fix the messed up elif.

def sentence_keyPressed(app, event):
    #print(event.key)
    if event.key == "Escape":
        app.input = ""
        appStarted(app)
        #app.mode = 'menu'
    if event.key == '-':
        app.called = False
    if event.key == "Backspace":
        app.input = app.input[:-1]
    if event.key == "Space":
        app.input += " "
    if event.key == "=":
        app.input = ""
    if event.key == "+":
        app.modifyFont *= 0.9
    if event.key == "*":
        app.modifyFont *= 1.1
    if event.key == "Enter" and app.solShown:
        app.submit = False
        app.input = ""
        app.called = False
        app.solShown = False
    elif event.key == "Enter":
        determineAccuracy(app)
        scoreChange(app)
        app.submit = True
    else:
        if len(app.input) == 35 and event.key != "Backspace":
            app.input += "\n"
        if event.key == "Backspace" or event.key == "Space" or event.key == "=" or event.key == "-" or event.key == "+" or event.key=="*":
            app.input += ""
        else:
            app.input += event.key


####################################
# OPTIONS
####################################
        
#A button that when you click it switches to another text.
def options_newButton(app, button, tag):
    if button not in app.optionsButtonDict:
        app.optionsButtonDict[button] = tag

def switch_button(app, canvas, x, y, size, def_text, switch_text=None, tag = None):
    if tag != None:
        for i in app.options_buttonBounds:
            if tag not in i:
                app.options_buttonBounds.append({tag:(x-((len(def_text)//2)*size),y-size,x+((len(def_text)//2)*size),y+size)})
    canvas.create_rectangle(x-((len(def_text)//2)*size),y-size,x+((len(def_text)//2)*size),y+size,fill='white',width=2)
    if app.switch1:
        canvas.create_text(x, y, text=switch_text, fill='black', font=("Times New Roman",size,"normal"))
    else:
        canvas.create_text(x, y, text=def_text, fill='black', font=("Times New Roman",size,"normal"))        
    buttonTuple = (x-((len(def_text)//2)*size),y-size,x+((len(def_text)//2)*size),y+size)
    options_newButton(app, buttonTuple, tag)
    
#draws the screen. draws the background, a white rectangle in the middle, test text.
#TODO: make switch_button work.
def options_redrawAll(app, canvas):
    drawBackground(app,canvas,app.otherImage)
    canvas.create_rectangle(app.width*0.25,app.height*0.1,app.width*0.75,app.height*0.9,fill='white',width=3)
    canvas.create_text(app.width//2, (app.height*0.1)+30, text='Options',
                       fill = 'black',
                       font=("Comic Sans MS",30,"normal"))
    info1 = 'Current Tizi: ' + app.tizi + ". Press s to switch"
    canvas.create_text(app.width//2, (app.height*0.1)+75, text=info1,
                       fill = 'black',
                       font=("Times New Roman",15,"normal"))
    info2 = 'Pinyin: ' + str(app.pinyin) + ". Press t to switch."
    canvas.create_text(app.width//2, (app.height*0.1)+95, text=info2,
                       fill = 'black',
                       font=("Times New Roman",15,"normal"))
    #switch_button(app, canvas, app.width//2, app.height//2, 15, "Traditional Chinese", switch_text="Simplified Chinese", tag = "print('test')")
    
#just determines the keybinds. Only one, escape to return.
def options_keyPressed(app, event):
    if event.key == "Escape":
        #print(app.data)
        app.mode = 'menu'
    if event.key == "s":
        app.tizi = opposite(app.tizi)
        app.data['options']['tizi'] = app.tizi
        with open('Data/saves/'+app.saveFile, 'w') as json_file:
            json.dump(app.data, json_file, indent=4)
        json_file.close()
    if event.key == 't':
        app.pinyin = not app.pinyin
        app.data['options']['pinyin'] = app.pinyin
        with open('Data/saves/'+app.saveFile, 'w') as json_file:
            json.dump(app.data, json_file, indent=4)
        json_file.close()
        reload_font(app)

#determines mouse click commands.
def options_mousePressed(app, event):
    app.clickPos = (event.x, event.y)
    for i in app.optionsButtonDict:
        if isValid(app.clickPos, i):
            exec(app.optionsButtonDict[i])
        
##############################
# MISC.
##############################
        
#determines font. Need to get a font for simplified, no pinyin, and simplified, zhuyin.
#While tizi and pinyin can be determined in settings, zhuyin must be manually coded.
def font(app, tizi, pinyin=False, zhuyin=False):
    if tizi == 'FAN' and pinyin:
        return app.fontList[0]
    if tizi == 'JIAN' and pinyin:
        return app.fontList[1]
    if tizi == 'FAN' and zhuyin:
        return app.fontList[2]
    if tizi == 'FAN':
        return app.fontList[3]
    if tizi == 'JIAN':
        return app.fontList[4]
    else:
        return app.fontList[3]

#load the data from the saves. Uses stuff from dataModify, but still loads
#data. Will likely make a save() function to write to the file.
def loadSaves(app):
    path = 'Data/saves/'
    if 'saveuse.txt' not in os.listdir(path) or 'save1.json' not in os.listdir(path):
        dat = data_cleaner.Cleaner()
        dat.setup_saves()
    try:
        save_file = []
        with open(path+'saveuse.txt', 'r', encoding='utf-8') as f:
            save_file = f.readlines()
        save_data = dataModify.Data()
        app.saveFile = save_file[0]
        app.data = save_data.loadSaves(save_file[0], filePath=path)
        
    except:
        raise Exception("Failed to load data. Check path.")
    
    app.tizi = app.data['options']['tizi']
    app.pinyin = app.data['options']['pinyin']
    app.level = app.data['level']
    #print(app.level)
    
def reload_font(app):
    app.font = font(app, app.tizi, pinyin=app.pinyin)

#I feel like theres a better way to do this..
#initializes variables and starts code.

def appStarted(app):
    app.saveFile =""
    app.mode = 'menu'
    app.tizi = 'JIAN'
    app.modifyFont = 1
    app.level = 1.0
    app.fontList = ['DFPBiaoKaiW5-HPinIn1NLU','Hanzi-Pinyin-Font','HanWangKaiMediumChuIn','SimSun', 'Source Han Serif SC']
    app.data = {}
    app.fontSelect = 0
    app.pinyin = True
    app.loader = None
    app.input = ""
    app.options_buttonBounds = []
    app.options_clicked = {}
    app.accuracy = 1.1
    app.currentSol = ""
    app.solShown = False
    app.currentSentenceDict = {}
    app.currentSentence = ""
    app.called = False
    app.submit = False
    #if app.mode == 'sentence':
        #print("ok")
    app.backgroundImage = app.loadImage('Data/Assets/backgrounds/bg4.jpg')
    app.sentenceBackground = app.scaleImage(app.loadImage('Data/Assets/backgrounds/sentence_background.jpg'),0.25)
    app.otherImage = app.loadImage('Data/Assets/backgrounds/options_background.png')
    app.bgScaled = app.scaleImage(app.backgroundImage, 0.75)
    app.bgWidth, app.bgHeight = app.backgroundImage.size
    app.logo = app.loadImage('Data/Assets/logos/logoTrad.png')
    app.sentence_loaded = False
    #app.currentScreen = 'menu'
    app.makeAnMVCViolation = False
    app.mousePos = (0,0)
    app.optionButton = app.loadImage('Data/Assets/buttons/options.png')
    app.optionButtonHover = app.loadImage('Data/Assets/buttons/optionsHover.png')
    app.sentenceButton = app.loadImage('Data/Assets/buttons/sentence_translation.png')
    app.sentenceButtonHover = app.loadImage('Data/Assets/buttons/sentence_translationHover.png')
    app.editButton = app.loadImage('Data/Assets/buttons/edit.png')
    app.editButtonHover = app.loadImage('Data/Assets/buttons/editHover.png')
    app.editBackground = app.loadImage('Data/Assets/backgrounds/edit_background.jpg')
    app.loadingScreen = loadAnimatedGif('Data/Assets/loading/loading2.gif')
    app.frameCounter = 0
    app.clickPos = (0,0)
    app.buttonDict = {}
    app.optionsButtonDict = {}
    app.timerDelay = 1
    app.counter = 0
    app.dragCoords = (0,0)
    app.clickCoords = (0,0)
    app.lineList = []
    app.currentPos = (0,0)
    app.fetched = False
    app.char = ""
    app.switch1 = False
    loadSaves(app)
    app.font = font(app, app.tizi,pinyin=app.pinyin)
    
#generates a list of all frames in a gif.
def loadAnimatedGif(path):
    loadingScreen = [ PhotoImage(file=path, format='gif -index 0') ]
    i = 1
    while True:
        try:
            loadingScreen.append(PhotoImage(file=path,
                                                format=f'gif -index {i}'))
            i += 1
        except Exception as e:
            return loadingScreen


#draw Loading screen. draws an image based on what frame is it on.

def drawLoadingScreen(app, canvas):
    img = app.loadingScreen[app.frameCounter]
    canvas.create_image(app.width//2,app.height//2,image=img)
    canvas.create_text(app.width//2,app.height*0.75,text='Loading..', fill='black',font='Arial 26')

#
#draws the background repeatedly on the canvas. I should probably cache the background so that it runs faster
#
def drawBackground(app, canvas, image):
    #canvas.create_image(400,400,image=ImageTk.PhotoImage(image))
    limitWidth = math.ceil(app.width / image.size[0])
    limitHeight = math.ceil(app.height / image.size[1])
    for i in range(limitWidth + 1):
        for j in range(limitHeight + 1):
            canvas.create_image(i*(image.size[0]),j*image.size[1],image=ImageTk.PhotoImage(image))


def gui():
    runApp(width=800, height=800, title='AutoLang')
    
def main():
    gui()


main()


