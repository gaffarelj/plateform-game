import pygame
import re
import os

os.system("mode con cols=100 lines=20")
print("Game creator --- (by Jeremie Gaffarel)\n")

text = ""
text = input("What is the message printed before the level begin ? (press ENTER to let empty) :\n")

print("\nInstructions :")
print("Click on the screen where you want to add an element")
print("Follow the instructions that are on the top left")
input("\nPress ENTER to begin...")

xmax = 1024
ymax = 768
os.environ['SDL_VIDEO_CENTERED'] = '1'  #Center the Pygame window
pygame.init()
screen = pygame.display.set_mode((xmax, ymax))
#Load all images and prepare labels
playerImg = pygame.image.load("assets/img/player1.png").convert_alpha()
backgroundImg = pygame.image.load("assets/img/background.png").convert()
blockImg = pygame.image.load("assets/img/block.png").convert()
coinImg = pygame.image.load("assets/img/coin.png").convert_alpha()
spikesImg = pygame.image.load("assets/img/spikes.png").convert_alpha()
infoFont = pygame.font.SysFont("monospace", 22)
infoFont.set_bold(1)

screen.blit(backgroundImg, (0, 0))
pygame.display.flip()

#Define blocks arrays
solidBlocks = []
coins = []
spikes = []
player = [200,250]
instructionTxt = " - SPACE to remove last one - ENTER when done"

infoLabel = infoFont.render("Add solid blocks" + instructionTxt, 1, (0,0,0))
while True: #Keep going until the user press ENTER to go to the next step
    screen.blit(backgroundImg, (0, 0))
    screen.blit(infoLabel, (15, 15))
    event = pygame.event.poll()
    if (event.type == pygame.KEYDOWN):  #If ENTER was pressed, break loop to go to the next step
        if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
            break
        if (event.key == pygame.K_SPACE):   #If SPACE was pressed, remove the last element in the current block list
            solidBlocks = solidBlocks[:-1]
    if event.type == pygame.MOUSEBUTTONDOWN:    #DETECT mouse click
        x = int(event.pos[0] / 32)      #Get the click coordinated (by step of 32 because there can only be one block every 32 pixels)
        y = int(event.pos[1] / 32)
        if [x, y] not in solidBlocks:
            solidBlocks.append([x, y])  #Add a block in the list where the click was registred
    for block in solidBlocks:   #Print all blocks
        screen.blit(blockImg, (block[0] * 32, block[1] * 32))
    pygame.display.flip()

#THE SAME LOGIC IS USED FOR THE THREE NEXT WHILE LOOPS

infoLabel = infoFont.render("Add coins (min 1)", 1, (0,0,0))
while True:
    screen.blit(backgroundImg, (0, 0))
    screen.blit(infoLabel, (15, 15))
    event = pygame.event.poll()
    if (event.type == pygame.KEYDOWN):
        if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
            if len(coins) > 0:
                break
        if (event.key == pygame.K_SPACE):
            coins = coins[:-1]
    if event.type == pygame.MOUSEBUTTONDOWN:
        x = int(event.pos[0] / 32)
        y = int(event.pos[1] / 32)
        if [x, y] not in coins:
            coins.append([x, y])
    for block in solidBlocks:
        screen.blit(blockImg, (block[0] * 32, block[1] * 32))
    for coin in coins:
        screen.blit(coinImg, (coin[0] * 32, coin[1] * 32))
    pygame.display.flip()

infoLabel = infoFont.render("Add spikes", 1, (0,0,0))
while True:
    screen.blit(backgroundImg, (0, 0))
    screen.blit(infoLabel, (15, 15))
    event = pygame.event.poll()
    if (event.type == pygame.KEYDOWN):
        if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
            break
        if (event.key == pygame.K_SPACE):
            spikes = spikes[:-1]
    if event.type == pygame.MOUSEBUTTONDOWN:
        x = int(event.pos[0] / 32)
        y = int(event.pos[1] / 32)
        if [x, y] not in spikes:
            spikes.append([x, y])
    for block in solidBlocks:
        screen.blit(blockImg, (block[0] * 32, block[1] * 32))
    for coin in coins:
        screen.blit(coinImg, (coin[0] * 32, coin[1] * 32))
    for spike in spikes:
        screen.blit(spikesImg, (spike[0] * 32, spike[1] * 32))
    pygame.display.flip()

infoLabel = infoFont.render("Place player", 1, (0,0,0))
while True:
    screen.blit(backgroundImg, (0, 0))
    screen.blit(infoLabel, (15, 15))
    event = pygame.event.poll()
    if (event.type == pygame.KEYDOWN):
        if (event.key == pygame.K_RETURN) or (event.key == pygame.K_KP_ENTER):
            break
    if event.type == pygame.MOUSEBUTTONDOWN:
        x = int(event.pos[0])
        y = 768 - int(event.pos[1])
        player = [x, y]
    for block in solidBlocks:
        screen.blit(blockImg, (block[0] * 32, block[1] * 32))
    for coin in coins:
        screen.blit(coinImg, (coin[0] * 32, coin[1] * 32))
    for spike in spikes:
        screen.blit(spikesImg, (spike[0] * 32, spike[1] * 32))
    screen.blit(playerImg, (player[0] - 17, 768 - player[1] - 25))
    pygame.display.flip()

pygame.quit()
print("\nLevel created. Saving...")

#Put every block and the player position in one string variable (one info per line)
file = ""
file += str(player[0]) + "," + str(player[1]) + "\n"
file += text + "\n"
for solidBlock in solidBlocks:
    file += str(solidBlock[0]) + "," + str(23-solidBlock[1]) + ",1\n"
for coin in coins:
    file += str(coin[0]) + "," + str(23-coin[1]) + ",3\n"
for spike in spikes:
    file += str(spike[0]) + "," + str(23-spike[1]) + ",4\n"

#Get all filenames in the folder containing all levels
fs = []
for (dirpath, dirnames, filenames) in os.walk("assets/dat/"):
    fs.extend(filenames)
    break
maxLevel = 0
for name in filenames:
    try:
        m = re.search('level([0-9]+?)\.dat', name)  #Find the last level number
        maxLevel = max(maxLevel, int(m.group(1)))
    except:
        pass

#While the user hasn't specified "1" or "2", keep asking/printing error message
choice = 0
while not(choice == 1 or choice == 2):
    try:
        choice = int(input("Enter '1' to save as next level (level" + str(maxLevel + 1) + ".dat) or '2' to save it on your computer : "))
    except:
        pass
    if not(choice == 1 or choice == 2):
        print("Incorrect value.")

if choice == 1: #If the user's choice was "1", save the file as the next level
    f = open("assets/dat/level" + str(maxLevel + 1) + ".dat","w")
    f.writelines(file)
    f.close()
elif choice == 2:   #If the user's choice was "2"...
    fileExist = True
    while fileExist:    #Keep asking for a file name while the specified one already exist
        filenameT = str(input("Enter a filename : "))
        if os.path.isfile("assets/dat/" + filenameT + ".dat"):
            print("That file already exists !")
        else:
            fileExist = False
    f = open("assets/dat/" + filenameT + ".dat","w")  #Then save the file
    f.writelines(file)
    f.close()

print("\nFile saved.")
input("Press ENTER to play the game, otherwise close the console")
os.system("play.py")    #Open "play.py" to play the game
