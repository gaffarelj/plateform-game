import pygame
import numpy as np
from math import *
import time
import os
import re   #For Regular Expressions
import random
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import hashlib  #For Sha1 hash
from urllib.request import urlopen  #To connect to the leaderboard

#Define "block" class
class block_s:
    #x and y are the x, y coordinate of its top left corner
    #h is the hight of its bottom (0 is bottom of screen)
    #the type are : 1 = simple block
    #               2 = wood block
    #               3 = coin
    #               4 = spikes
    #               5 = plants
    def __init__(self, x, h, type):
        self.x = int(x) * 32
        self.h = int(h) * 32
        self.y = 736 - int(h) * 32
        self.type = int(type)
        
#Define "player" class
class player_s:
    #x is the coordinate of its left side
    #h is its centrum high (0 is the bottom block line [32 above bottom of screen])
    #vx and vy are its x and y velocity components
    def __init__(self, x, h, vx, vy):
        self.h = int(h)
        self.x = int(x)
        self.y = 736 - int(h)
        self.vx = int(vx)
        self.vy = int(vy)

#Define starting functions
#Screen size
xmax = 1024
ymax = 768
acc = 0
hearthLevel = 5 #Number of lives does the player have
inLevelCoin = 0 #Number of coins in the level
inLevelCoinGotten = 0   #Number of coins the player got in the level
symmetry = False    #If true, the player is going to the left
died = False    #If true, the player died
loading = 0     #0 : level loaded
#Is there a block on the right or left of the player
blockOnLeft = False
blockOnRight = False
godMode = False

#Open a given level
def openLevel(filename):
    global inLevelCoinGotten
    blocks_t = []   #Temporary array containing all blocks
    f = open(filename, "r")
    lines = f.readlines()   #Read the file containing the level data
    f.close()
    j = 0   #Line counter
    text = ""
    coin = 0
    for xi in range(0, 32): #Makes a line of water blocks on the bottom of the screen
        blocks_t.append(block_s(xi, 0, 2))
    for line in lines:  #For each line in the file...
        if j == 0:  #The first line contains the player position
            d = line.split(",") #Split the line because each value is separated by a comma
            pos = [int(d[0]), int(d[1])]
            j += 1
        elif j == 1:    #Second line is the text desplayed before the level begin
            text = line[:-1]    #Remove the last two charachters, these are "\n"
            j += 1
        elif j > 1: #All the others lines contain the blocks informations
            if not(str(line) == "\n"):
                d = line.split(",")
                blocks_t.append(block_s(int(d[0]), int(d[1]), int(d[2])))   #Append the block x, h coordinates and block type to the block list
                if int(d[2]) == 3:  #If the block is a coin, increment the coin variable
                    coin += 1
    inLevelCoinGotten = 0   #Be sure that the player hasn't got any coin before beginning to play
    #Return everything
    return pos, text, blocks_t, coin    

#Check if the player bumped into a block
def checkClash():
    global player
    global acc
    global blocks
    global inLevelCoin
    global inLevelCoinGotten
    global blockOnLeft
    global blockOnRight
    touchBlock = False
    clash = False
    if player.h < 0:    #If the player is under the minimum altitude, kill it
        blockOnLeft = False
        blockOnRight = False
        clash = False
        die()
    else:
        if player.x < 0:    #If the player is more to the left than the screen limit, makes his position x = 0
            player = player_s(0, player.h, player.vx, player.vy)
            clash = True
        elif player.x > xmax - 32:  #Same logic for the right of the screen
            player = player_s(xmax - 32, player.h, player.vx, player.vy)
            clash = True
        index = 0
        blockOnRight = False
        blockOnLeft = False
        time.sleep(0.0015)  #Sleep for 1.5 ms, avoid dt too small (cause mistakes)
        for block in blocks:    #For every block in the level...
            if block.type == 1: #If the block is a solid block...
                if ((player.h - 25 < block.h) and (player.h + 25 > block.h - 32)) and ((player.x < block.x + 32) and (player.x + 32 > block.x)):    #If the player is inside a block (x and h in it)...
                    if player.vy < 0 and player.h + 25 > block.h:   #If the player is going down and he is higher than the surface of the block (avoid passing through block on the top of it)...
                        player = player_s(player.x, block.h + 25, player.vx, 0) #Makes his position right on the top of the block
                        clash = True
                    if player.vy > 0:   #If the player is going up, makes his position right under the block
                        player = player_s(player.x, block.h - 58, player.vx, 0)
                        clash = True
                if (player.h - 17 < block.h and player.h + 50 > block.h):   #If a block is closeby (by altitude)...
                   if (player.x <= block.x + 33 and player.x + 36 > block.x + 32):  #If a block is on the left, makes the player right on its left
                        blockCloseBy = True
                        blockOnLeft = True  #Indicate that there is a block right on its left (to avoid going even more to the left)
                        player = player_s(block.x + 33, player.h, 0, player.vy)
                        time.sleep(0.0075)  #Sleep for 7.5 ms to make dt even bigger (cause more mistakes in this case)
                   if (player.x + 37 >= block.x and player.x < block.x + 32):   #Same logic for the right
                        blockCloseBy = True
                        blockOnRight = True
                        player = player_s(block.x - 36, player.h, 0, player.vy)
                        time.sleep(0.005)
            elif block.type == 3:   #If the block is a coin
                if ((player.h - 25 < block.h) and (player.h + 25 > block.h - 32)) and ((player.x < block.x + 32) and (player.x + 32 > block.x)):    #If the player is in the coin
                    blocks[index] = block_s(-100,-100, 0)   #Makes the coin dissepear from the screen
                    inLevelCoin -= 1    #There is one less coin to get in the game
                    inLevelCoinGotten += 1  #The player got one coin
            elif block.type == 4:   #If the block is spikes
                if ((player.h - 20 < block.h) and (player.h + 20 > block.h - 27)) and ((player.x < block.x + 25) and (player.x + 25 > block.x)):    #If the player is in the spikes (allow some tolerance)
                    clash = False
                    die()   #Kill it
            index += 1
        return clash    #Return if the player bumped on a block or no 

#Handle the player's death
def die():
    global hearthLevel
    global playerPos
    global blocks
    global inLevelCoin
    global inLevelCoinGotten
    global died
    global player
    global loading
    global screen
    global ripImg
    if not (loading < 2): #Be sure that the player do not die if the level is still loading
        screen.blit(ripImg, (player.x, player.y - 25))  #Print the "RIP" image where the player died
        pygame.display.flip()
        hearthLevel -= 1    #Remove one life from the player
        inLevelCoinGotten = 0   #Remove all coins the player might've got
        died = True #Change the dead indicator boolean to True
        #Re-open the correct level
        if levelChoosen == "*":
            playerPos, text, blocks, inLevelCoin = openLevel("assets/dat/level" + str(levelIndex) + ".dat")
        else:
            playerPos, text, blocks, inLevelCoin = openLevel(levelChoosen)
        player = player_s(playerPos[0], playerPos[1], 0, 0) #Put the player to the starting position
        loading = 0 #Indicate that the level just got open
        time.sleep(0.6)   #Wait for one second to let the player see the headstone and realize he died

os.system("mode con cols=100 lines=20") #Makes the console 20 lines high and 100 wide
print("Plateform game created by Jeremie Gaffarel\n")
print("FOR TESTERS (or cheaters) : press TAB to skip a level and SHIFT (left) for infinite lives")
print("Enjoy ! :)")

fs = []
#Check every file in the folder containing all levels
for (dirpath, dirnames, filenames) in os.walk("assets/dat/"):
    fs.extend(filenames)
    break
nLevels = 0

fileNames = []
for name in filenames:
    try:
        m = re.search('level([0-9]+?)\.dat', name)  #Use a RegEx to find the level number for each filename
        nLevels = max(nLevels, int(m.group(1))) #Get the maximum level
    except:
        pass
    fileNames.append(name)  #Stock all levels names in an array'''
choice = 0
#Exectue until the user enter "1" or "2"
while not(choice == 1 or choice == 2):
    try:
        choice = int(input("\nEnter '1' to play all levels or '2' to choose one on your computer : "))
    except:
        pass
    if not(choice == 1 or choice == 2):
        print("Incorrect value.")
choiceLevel = 0
levelChoosen = "*"  #By default, the user will play all levels
if choice == 2:     #But if he choosed option 2
    print()
    w = Tk()
    w.withdraw()    #Hide window
    levelChoosen = askopenfilename(parent = w, initialdir = "assets/dat/",title = "Select a level",filetypes = (("dat files","*.dat"),("all files","*.*")))   #Select a level
    '''THIS PART WAS USED TO SELECT A LEVEL BEFORE USING TKINTER
    #Execute while the user did not enter a valid level number
    while choiceLevel < 1 or choiceLevel > l - 1:
        print("Here are the availables levels :")
        l = 1   #Number of levels
        for name in fileNames:
            print(str(l), ":", name)    #Print each filename and its index
            l += 1
        try:
            choiceLevel = int(input("Enter the id of what you want to play : "))
        except:
            pass
        if choiceLevel < 1 or choiceLevel > l - 1:
            print("\nIncorrect choice !")
    levelChoosen = fileNames[choiceLevel - 1]   #The name of the choosen level'''
os.environ['SDL_VIDEO_CENTERED'] = '1'  #Center the Pygame window
pygame.init()
pygame.display.set_caption("Plateform Game")    #Set window name
screen = pygame.display.set_mode((xmax, ymax))

#Load all images in pygame images
backgroundImg = pygame.image.load("assets/img/background.png").convert()
blockImg = pygame.image.load("assets/img/block.png").convert()
waterImg = pygame.image.load("assets/img/water.png").convert_alpha()
coinImg = pygame.image.load("assets/img/coin.png").convert_alpha()
coinBImg = pygame.image.load("assets/img/coinB.png").convert_alpha()
spikesImg = pygame.image.load("assets/img/spikes.png").convert_alpha()
hearthImg = pygame.image.load("assets/img/hearth.png").convert_alpha()
ripImg = pygame.image.load("assets/img/rip.png").convert_alpha()
#Prepare some text labels for Pygame
infoFont = pygame.font.SysFont("monospace", 30)
bigInfoFont = pygame.font.SysFont("monospace", 50)
infoFont.set_bold(1)
bigInfoFont.set_bold(1)
hearthLabel = infoFont.render("Life : ", 1, (255,0,0))
deadLabel = bigInfoFont.render("GAME OVER", 1, (255,0,0))
deadLabel2 = infoFont.render("Press \"Esc\" to quit.", 1, (0,0,139))
startLabel = infoFont.render("Press ENTER to play", 1, (0,0,139))
continueLabel = infoFont.render("Press ENTER to continue", 1, (0,0,139))
#Set the window icon to a coin
pygame.display.set_icon(coinImg)
screen.fill(pygame.Color(193, 236, 193))

choosePlayerLabel = bigInfoFont.render("Choose a player", 1, (0,0,139))
screen.blit(choosePlayerLabel, ((xmax - choosePlayerLabel.get_rect().width) / 2, 100))

playerIndex = 1
#Print the 8 differents players on 4 rows and 2 columns
for b in range(0,4):        #rows
    for c in range(0,2):    #columns
        playerBImg = pygame.image.load("assets/img/player" + str(playerIndex) + "B.png").convert_alpha()
        screen.blit(playerBImg, (100 + b * 215, 250 + c * 265)) #Place the player on the screen
        playerIndex += 1
pygame.display.flip()

playerChoice = ""
#Execute while no player was choosen
while playerChoice == "":
    mx, my = 0, 0
    event = pygame.event.poll()
    #If mouseclick event : register coordinates
    if event.type == pygame.MOUSEBUTTONDOWN:
        mx = int(event.pos[0])
        my = int(event.pos[1])
    playerIndex = 1
    for b in range(0,4):
        for c in range(0,2):
            #Check if the mouseclick was over a player picture
            if (100 + 215 * b < mx < 250 + 215 * b) and (250 + 265 * c < my < 466 + 265 * c):
                playerChoice = str(playerIndex)#If it was, save the choice
            playerIndex += 1

playerImg = pygame.image.load("assets/img/player" + playerChoice + ".png").convert_alpha()
playerBImg = pygame.image.load("assets/img/player" + playerChoice + "B.png").convert_alpha()
playerBSImg = pygame.image.load("assets/img/player" + playerChoice + "BS.png").convert_alpha()
playerSImg = pygame.image.load("assets/img/player" + playerChoice + "S.png").convert_alpha()

if not(levelChoosen == "*"):    #If the user want to play a specific level and not all of them, the number of levels is 1
    nLevels = 1

t1 = time.time()#Start a clock (useful for speeruners who want to know their time)
#Execute all this for every level
for levelIndex in range(1,nLevels + 1):
    #Stop playing levels if the player don't have any lives
    if hearthLevel == 0:
        break
    #Reinitialize the "level finished" and "block proximity" indicators
    finished = False
    blockOnLeft = False
    blockOnRight = False
    #If the player want to play all levels, open next level in the "levels
    #list" and prepare the level title and finished messages/labels
    if levelChoosen == "*":
        playerPos, text, blocks, inLevelCoin = openLevel("assets/dat/level" + str(levelIndex) + ".dat")
        levelLabel = bigInfoFont.render("LEVEL " + str(levelIndex), 1, (0,0,139))
        ggLabel = infoFont.render("Level " + str(levelIndex) + " completed !", 1, (0,0,139))
    else:
        playerPos, text, blocks, inLevelCoin = openLevel(levelChoosen)
        levelLabel = bigInfoFont.render("Custom level", 1, (0,0,139))
        ggLabel = infoFont.render("Custom level completed !", 1, (0,0,139))
    loading = 0 #Indicate that a level just got open
    player = player_s(playerPos[0], playerPos[1], 0, 0) #Put player at starting position
    backgroundRect = pygame.Rect(200, 325, 624, 225)    #Create a rectangle to have some background to the "Good Game" message
    infoLabel = infoFont.render(text, 1, (0,0,139))     #Prepare the message printed before the level begin
    #Fill the screen with a blue color and print the levels informations
    screen.fill(pygame.Color(193, 236, 193))
    screen.blit(levelLabel, ((xmax - levelLabel.get_rect().width) / 2, (ymax - levelLabel.get_rect().height) / 2 - 75))
    screen.blit(infoLabel, ((xmax - infoLabel.get_rect().width) / 2, (ymax - infoLabel.get_rect().height) / 2))
    screen.blit(startLabel, ((xmax - startLabel.get_rect().width) / 2, (ymax - startLabel.get_rect().height) / 2 + 75))
    pygame.display.flip()
    #Wait for the user to press enter before continuing
    while True:
        event = pygame.event.poll()
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
                break

    t0 = time.time()
    dt = 0
    pushLeft = False
    pushRight = False
    while True: #Compute every frame of the level in a continuous loop
        if inLevelCoin == 0:    #If there is no more coin to get, the level is finished
            finished = True
            #Inform the player that he finished the level
            pygame.draw.rect(screen, (193, 236, 193), backgroundRect)
            screen.blit(ggLabel, ((xmax - ggLabel.get_rect().width) / 2, (ymax - ggLabel.get_rect().height) / 2))
            screen.blit(continueLabel, ((xmax - continueLabel.get_rect().width) / 2, (ymax - continueLabel.get_rect().height) / 2 + 75))
            pygame.display.flip()
            if levelIndex == nLevels:    #If the level was the last level, make the index 11 to avoid letting the script think the player died, and correctly print that he finished 10 levels
                levelIndex = 11
            while True: #Wait for the player to press enter to go to next screen
                event = pygame.event.poll()
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
                        break
            break
        else:   #If there is still some coins to get...
            if not died:    #If the player is still alive
                acc = -9.5  #Put some gravity (more than on earth to make the player fall faster)
                t = time.time() * 30   #find the actual time (*20 is to makes it looks better)
                dt = t - t0 #Get the time step = last time - this time
                t0 = t      #Put the acutal time as the future last time
                if loading > 5: #Avoid letting the player move when the game was just loaded
                    dy = dt * player.vy + acc * dt * dt / 2 #Compute the player vertical displacement
                    player.vy += acc * dt   #Compute the player's new vertical speed
                    dx = 25 * player.vx * dt    #Compute the player horizontal displacement
                    player = player_s(player.x + dx, player.h + dy, player.vx, player.vy)   #Give the player its new position
                else:
                    loading += 1

                screen.fill(pygame.Color("black"))  #Just in case the background was incorrect, be sure to overdraw on every elements from last frame
                screen.blit(backgroundImg, (0, 0))

            if hearthLevel == 0:    #If the player don't have any lives left, print GAME OVER
                screen.fill(pygame.Color(193, 236, 193))
                screen.blit(deadLabel, ((xmax - deadLabel.get_rect().width) / 2, (ymax - deadLabel.get_rect().height) / 2))
                screen.blit(deadLabel2, ((xmax - deadLabel2.get_rect().width) / 2, (ymax - deadLabel2.get_rect().height) / 2 + 75))
            elif died:  #If the player died, put its dead indicator back to False (its death was handled in the "checkClash", this is to avoid making him move while being dead)
                died = False
            else:   #The player is fully alive
                #While the player bumped on a block, check if its new given position is correct by checking if it's not still "in" a block
                clashed = True
                while clashed:
                    clashed = checkClash()
                tElapsed = round(time.time() - t1,2)   #Get the elapsed time since the user began playing
                #Print indications on the top of the screen
                for i in range(hearthLevel):    #Print all lives
                    screen.blit(hearthImg, (150 + i * 40, 15))
                for i in range(inLevelCoin):    #Print coin that the player has to get in black
                    screen.blit(coinBImg, (975 - i * 40, 15))
                for i in range(inLevelCoinGotten):  #Print coin that the player already got
                    screen.blit(coinImg, (975 - (inLevelCoin + i) * 40, 15))
                levelNLabel = infoFont.render("Level " + str(levelIndex) + "/" + str(nLevels) + " - " + str(int(tElapsed)), 1, (0,0,0))
                screen.blit(hearthLabel, (15, 15))
                screen.blit(levelNLabel, (360, 15)) #Print which level the player is playing and the elapsed time since he began playing
                #Print all blocks
                for block in blocks:
                    if block.type == 2: #Print water blocks
                        screen.blit(waterImg, (block.x, block.y))
                    if block.type == 1: #Print solid blocks
                        screen.blit(blockImg, (block.x, block.y))
                    if block.type == 3: #Print coins
                        screen.blit(coinImg, (block.x, block.y))
                    if block.type == 4: #Print spikes
                        screen.blit(spikesImg, (block.x, block.y))
                #If the player is going to the left, print its symmetric image
                if symmetry:
                    screen.blit(playerSImg, (player.x, player.y - 25))
                else :
                    screen.blit(playerImg, (player.x, player.y - 25))

            pygame.display.flip()

            if loading > 5 or hearthLevel == 0: #If the level is fully loaded and the player is alive...
                event = pygame.event.poll()
                if event.type == pygame.QUIT:   #Quit pygame if requested :(
                    pygame.quit()
                    break
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_ESCAPE):  #If the user pressed ESCAPE, kill the player to let him finish
                        hearthLevel = 0
                        break
                    if (event.key == pygame.K_TAB):     #If the user pressed TAB, makes him get all coins to skip the level -> CHEAT
                        inLevelCoinGotten += inLevelCoin
                        inLevelCoin = 0
                        godMode = True  #Cheat is detected and recorded
                    if (event.key == pygame.K_LSHIFT):  #If the user pressed SHIFT (left), activate "God mode" by giving him 100 lives -> CHEAT
                        hearthLevel = 100
                        godMode = True  #Cheat is detected and recorded
                    if (event.key == pygame.K_SPACE) or (event.key == pygame.K_UP):   #If the user pressed SPACE or UP...
                        if player.vy == 0:  #If the vertical speed is 0 (avoid letting him fly away)
                            player.vy = 60  #Makes its vertical speed 60
                    #Detect and record if the user pressed RIGHT or LEFT
                    if (event.key == pygame.K_RIGHT):
                        pushRight = True
                    if (event.key == pygame.K_LEFT):
                        pushLeft = True
                #Detect and record if the user released RIGHT or LEFT (for example, if right is released, don't go right anymore)
                if (event.type == pygame.KEYUP):
                    if (event.key == pygame.K_RIGHT):
                        pushRight = False
                    if (event.key == pygame.K_LEFT):
                        pushLeft = False
                #If the player want to go right (or left) and there is no block in its way, makes his horizontal speed factor +1 (or -1)
                if pushRight and not(blockOnRight):
                    player.vx = 1
                    symmetry = False
                    blockOnLeft = False
                elif pushLeft and not(blockOnLeft):
                    player.vx = -1
                    symmetry = True
                    blockOnRight = False
                else:   #If not right or left, don't move vertically
                    player.vx = 0

if not(levelChoosen == "*"):
    ggText = "You did the level in " + str(tElapsed) + "sec - See you soon"
else:
    ggText = "You did " + str(levelIndex - 1) + "/" + str(nLevels) + " levels in " + str(tElapsed) + "sec - See you soon"
if levelIndex == nLevels and finished:
    ggText = "Good game, you finished in " + str(tElapsed) + "sec !"
ggLabel = infoFont.render(ggText, 1, (0,0,139))
finishLabel = bigInfoFont.render("Press ENTER or ESC to QUIT", 1, (0,0,139))
#Print the user stats, makes the player "dance" and makes coins "raining" (spawn at random places)
symmetry = True
while True:
    screen.fill(pygame.Color(193, 236, 193))
    for i in range(0, 50):
        screen.blit(coinImg, (random.randint(32, 992), random.randint(32, 736)))
    if symmetry:
        screen.blit(playerBSImg, (438, 552))
        symmetry = False
    else:
        screen.blit(playerBImg, (438, 552))
        symmetry = True
    screen.blit(ggLabel, ((xmax - ggLabel.get_rect().width) / 2, (ymax - ggLabel.get_rect().height) / 2 - 75))
    screen.blit(finishLabel, ((xmax - finishLabel.get_rect().width) / 2, (ymax - finishLabel.get_rect().height) / 2))
    pygame.display.flip()
    time.sleep(0.25)
    event = pygame.event.poll() #Then quit pygame when the player press RETURN ENTER ESCAPE or close the window
    if (event.type == pygame.KEYDOWN):
        if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER) or (event.key == pygame.K_ESCAPE):
            break
    if event.type == pygame.QUIT:
        break
pygame.quit()

print("\nGood game !\n")
print("""
      -----  CREDITS  -----

Players sprites :      ScribbleNauts
Coin sprite :          Super Mario
Background and water : Red Runner Open Source
Blocks :               FinalBossBlues
Everything else :      Jeremie Gaffarel\n""")

if levelChoosen == "*": #If the user played all levels, he can save his progress in the leaderboard
    godModeS = ""
    godModeI = "0"
    if godMode: #Specify if the player activated any cheat
        godModeS = "- with cheats (level skip and/or god mode on)"
        godModeI = "1"
    print("You did", str(levelIndex - 1), "levels in", str(tElapsed), "seconds", godModeS)  #Print the user's stats
    input("Press ENTER to save your score (require internet connection)")
    username = input("Write your username (alphanumerics only) : ")

    tohash = username + str(tElapsed) + "it's salty h€re"
    hash = hashlib.sha1(tohash.encode())    #Generate a connection key that will be compared by the api (makes cheating and saving fakes results slightly harder)
    key = hash.hexdigest()
    print("Saving score...")
    #Call the API that save the score (if it was better)
    answer = urlopen("https://renseign.com/private/gameleaderboard/?username=" + username + "&time=" + str(tElapsed) + "&god=" + godModeI + "&levels=" + str(levelIndex - 1) + "&key=" + key).read().decode('utf-8')
    print("\n" + answer)

input("Press ENTER to quit...")
