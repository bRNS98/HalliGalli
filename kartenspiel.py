import tkinter
from tkinter import *
import random
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk
from collections import Counter
import usb.core
import usb.util
import array
import threading

##Initialisieren der GUI

root = Tk()
root.title('HalliGalli')
root.geometry("1920x1080")
root.configure(background="lightblue")
my_frame = Frame(root, bg="lightblue")
my_frame.pack(pady=20)

#Create Frames For Cards
player1_frame = LabelFrame(my_frame, text="Spieler1", bd=0)
player1_frame.grid(row=0, column=0, padx=50, ipadx=20)

player2_frame = LabelFrame(my_frame, text="Spieler2", bd=0)
player2_frame.grid(row=0, column=1, padx=50,ipadx=20)

player3_frame = LabelFrame(my_frame, text="Spieler3", bd=0)
player3_frame.grid(row=0, column=2,padx=50, ipadx=30)

player4_frame = LabelFrame(my_frame, text="Spieler4", bd=0)
player4_frame.grid(row=0, column=3, padx=50,ipadx=10)

#Label erstellen(Bilderrahmen)
player1_label = Label(player1_frame, text='')
player1_label.pack(pady=20)

player2_label = Label(player2_frame, text='')
player2_label.pack(pady=20)

player3_label = Label(player3_frame, text='')
player3_label.pack(pady=20)

player4_label = Label(player4_frame, text='')
player4_label.pack(pady=20)


#Initialisieren von sonstigen Instanzen
pygame.mixer.init()
global dev
dev = usb.core.find(idVendor=0x054c, idProduct=0x1000)
if dev is None:
    raise ValueError('Device is not found')
global useableInput





#Resize Cards
def resize_cards(card):
    global playcard
    #open image
    card_image = Image.open(card)
    #Resize
    card_image_R= card_image.resize((150, 218))
    playcard = ImageTk.PhotoImage(card_image_R)
    return playcard


#Neues Deck erstellen
def createdeck():
    suits=["Banane", "Pflaume", "Erdbeere","Limone"]
    values = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5]
    global deck
    deck = []
    for suit in suits:
        for value in values:
            deck.append(f'{value}_of_{suit}')
    global deck2
    tr = f"tabula_rasa.png"
    deck2 = [tr, tr, tr, tr]


#Spieler erstellen
def createplayers():
    #Create our players
    global player1, player2, player3, player4
    player1 = []
    player2 = []
    player3 = []
    player4 = []
    #Rückseite als Standardbild nehmen
    global player1_image, player2_image, player3_image, player4_image
    player1_image = resize_cards(f"karten/tabula_rasa.png")
    player1_label.config(image=player1_image)

    player2_image = resize_cards(f"karten/tabula_rasa.png")
    player2_label.config(image=player2_image)

    player3_image = resize_cards(f"karten/tabula_rasa.png")
    player3_label.config(image=player3_image)

    player4_image = resize_cards(f"karten/tabula_rasa.png")
    player4_label.config(image=player4_image)
    #Zu verteilende Karten im Titel ändern
    root.title(f'HalliGalli- {len(deck)} Cards remaining')



def deal_cards(playerId):


    try:
        if playerId == 1:
            card = random.choice(deck)
            deck.remove(card)
            player1.append(card)
            global player1_image
            player1_image = resize_cards(f"karten/{card}.png")
            player1_label.config(image=player1_image)
        if playerId == 2:
            card = random.choice(deck)
            deck.remove(card)
            player2.append(card)
            global player2_image
            player2_image = resize_cards(f"karten/{card}.png")
            player2_label.config(image=player2_image)
        if playerId == 3:
            card = random.choice(deck)
            deck.remove(card)
            player3.append(card)
            global player3_image
            player3_image = resize_cards(f"karten/{card}.png")
            player3_label.config(image=player3_image)
        if playerId == 4:
            card = random.choice(deck)
            deck.remove(card)
            player4.append(card)
            global player4_image
            player4_image = resize_cards(f"karten/{card}.png")
            player4_label.config(image=player4_image)
        root.title(f'HalliGalli- {len(deck)} Cards remaining')
        checkInput()
    except:
        root.title(f'No Cards in Deck!')
        announceWinner()

# Öffnen des InputStreams der Controller. Diese werden nach aussen hin als EIN Controller angesehen
# Dieser Input gibt einen unsigniertes('B') Array vom Typ int wieder.
# die read Funktion hat als Parameter den Inputstream, Byteanzahl, optional: Zeit wielange es horchen soll.
# Wenn kein Input kommt, wird eine Fehlermeldung ausgeworfen, welche hier die Schleife wieder startet
#Eine While True: Schleife führte paradoxerweiser bei mir zu Fehlern, weswegen ich hier diese unschöne Schleife verwendet habe
def checkInput():
        money = 0
        time = 50
        while money < time:
            try:
                rawInput = dev.read(0x81, 1024)
                data = array.array('B', rawInput)
                money += 1
                if data is not None:
                    interpretInput(data)
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out'):
                    checkInput()

def interpretInput(useableInput):

    if useableInput[2] in[1, 2, 4, 8, 16]:
        if useableInput[2] == 1:
            ping(1)
        else:
            deal_cards(1)
    if useableInput[2] in[32, 64, 128] or useableInput[3] in [1, 2]:
        if useableInput[2] == 32:
            ping(2)
        else:
            deal_cards(2)
    if useableInput[3] in[4, 8, 16, 32, 64]:
        if useableInput[3] == 4:
            ping(3)
        else:
            deal_cards(3)
    if useableInput[3] == 128 or useableInput[4] > 240:
        if useableInput[3] == 128:
            ping(4)
        else:
            deal_cards(4)



def ping(playerId):
    global label
    pygame.mixer.music.load('Sound/bell.mp3')
    pygame.mixer.music.play()
    if isfiveofakind() == 5:
        print("Winner!")
        points = (len(player1)+len(player2)+len(player3)+len(player4))
        playerpoints[playerId-1] += points
        label = tkinter.Label(root, text=""+str(points)+" Punkte für Spieler "+str(playerId), bg="lightblue", font=("Helvetica", 50))
        label.pack(pady=20)
        createplayers()
    else:
        print("Wrong!")
        negativepoints[playerId-1] += 4
        label = tkinter.Label(root, text="4 Punkte Abzug für Spieler "+str(playerId), bg="lightblue", font=("Helvetica", 50))
        label.pack(pady=20)
    root.after(1000, label.destroy)
    checkInput()

def announceWinner():
    player1Points = playerpoints[0] - negativepoints[0]
    player2Points = playerpoints[1] - negativepoints[1]
    player3Points = playerpoints[2] - negativepoints[2]
    player4Points = playerpoints[3] - negativepoints[3]
    result=[player1Points, player2Points, player3Points, player4Points]
    messagebox.showinfo("Endpunktestand", "Spieler 1: "+str(result[0])+"\n"+"Spieler 2: "+str(result[1])+"\n"+"Spieler 3: "+str(result[2])+"\n"+"Spieler 4: "+str(result[3])+"\n")

def isfiveofakind():
    valueCount =  0
    valueCount2 = 0
    valueCount3 = 0
    ##Im folgenden wird die Gewinnfunktion bei 1-3 aufgedeckten Karten geprüft
    if len(player1) < 1:
        return -1
    if len(player1) == 1 and len(player2) == 0 and len(player3) == 0 and len(player4) == 0:
        cardPlayer1= str(player1[len(player1)-1])
        if int(cardPlayer1[0:1]) == 5:
            return 5
        else:
            return -1
    if len(player1) == 1 and len(player2) == 1 and len(player3) == 0 and len(player4) == 0:

        cardPlayer1 = str(player1[len(player1)-1])
        cardPlayer2= str(player2[len(player2)-1])
        cardType1 = cardPlayer1[1:]
        cardValue1 = int(cardPlayer1[0:1])
        cardValue2 = int(cardPlayer2[0:1])
        cardType2 = cardPlayer2[1:]
        if cardType1 == cardType2:
            return cardValue1+cardValue2
        elif cardValue2 == 5:
            return 5
        else:
            return -1
    if len(player1) == 1 and len(player2) == 1 and len(player3) == 1 and len(player4) == 0:
        cardPlayer3= str(player3[len(player3)-1])
        cardPlayer1 = str(player1[len(player1)-1])
        cardPlayer2= str(player2[len(player2)-1])
        cardType1 = cardPlayer1[1:]
        cardValue1 = int(cardPlayer1[0:1])
        cardValue2 = int(cardPlayer2[0:1])
        cardType2 = cardPlayer2[1:]
        cardValue3 = int(cardPlayer3[0:1])
        cardType3 = cardPlayer3[1:]
        if cardType1 == cardType3 and cardType3 == cardType2:
            return cardValue2 + cardValue3 + cardValue1
        elif cardType1 == cardType3 and cardType3 != cardType2:
            return cardValue3 + cardValue1
        elif cardType1 == cardType2 and cardType3 != cardType1:
            return cardValue2 + cardValue1
        elif cardType3 == cardType2:
            return cardValue2 + cardValue3
        elif cardType3 != cardType1 and cardType3 != cardType2:
            return cardValue3


    cardPlayer1= str(player1[len(player1)-1])
    cardPlayer2 = str(player2[len(player2)-1])
    cardPlayer3 = str(player3[len(player3)-1])
    cardPlayer4 = str(player4[len(player4)-1])

    cardValue1 = int(cardPlayer1[0:1])
    cardValue2 = int(cardPlayer2[0:1])
    cardValue3 = int(cardPlayer3[0:1])
    cardValue4 = int(cardPlayer4[0:1])

    cardType1 = cardPlayer1[1:]
    cardType2 = cardPlayer2[1:]
    cardType3 = cardPlayer3[1:]
    cardType4 = cardPlayer4[1:]

    #Schauen, wieviele unique Elemente es in der Liste gibt
    typeList = [cardType1, cardType2, cardType3, cardType4]
    typecounter = Counter(typeList).values()

#1 Element: Alle 4 Karten sind vom gleichen Typ
    if len(typecounter) == 1:
        valueCount=cardValue1+cardValue2+cardValue3+cardValue4
        return valueCount
#2 Elemente: Verteielung der Elemente ist 1-3 oder 2-2
    if len(typecounter) == 2:
        if cardType1 == cardType2:
            valueCount += cardValue1 + cardValue2
            if cardType1 == cardType3:
                valueCount += cardValue3
            elif cardType3 == cardType4:
                valueCount2 =cardValue3 + cardValue4
            else:
                valueCount2 = cardValue3
                valueCount += cardValue4
        if cardType1 == cardType3:
            valueCount += cardValue1 + cardValue3
            if cardType1 == cardType4:
                valueCount += cardValue4
            elif cardType2 == cardType3:
                valueCount2 = cardValue2 + cardValue3
            else:
                valueCount2 = cardValue2
        if cardType2 == cardType3:
            valueCount+= cardValue2+cardValue3
            if cardType2 == cardType4:
                valueCount += cardValue4
            elif cardType4 == cardType1:
                valueCount2 = cardValue1 + cardValue4
            else:
                valueCount2 = cardValue1
        if cardType2 == cardType4:
            valueCount += cardValue2 + cardValue4
    #3 Elemente: Verteilung ist 1-2 1 1
    if len(typecounter) == 3:
        if cardType1 == cardType2:
            valueCount = cardValue1+cardValue2
            valueCount2 = cardValue3
            valueCount3 = cardValue4
        if cardType1 == cardType3:
            valueCount = cardValue1+cardValue3
            valueCount2 = cardValue2
            valueCount3 = cardValue4
        if cardType1 == cardType4:
            valueCount = cardValue1+cardValue4
            valueCount2 = cardValue2
            valueCount3 = cardValue3
        if cardType2 == cardType3:
            valueCount = cardValue2+cardValue3
            valueCount2 = cardValue1
            valueCount3 = cardValue4
        if cardType2 == cardType4:
            valueCount = cardValue2+cardValue4
            valueCount2 = cardValue1
            valueCount3 = cardValue3
        if cardType3 == cardType4:
            valueCount = cardValue3 + cardValue4
            valueCount2 = cardValue1
            valueCount3 = cardValue2
    #4 Elemente: Es wird geprüft, ob eines der Elemente 5 ist
    if len(typecounter) == 4:
        if cardValue1 == 5 or cardValue2 == 5 or cardValue3 == 5 or cardValue4 == 5:
            return 5
    if valueCount == 5 or valueCount2 == 5 or valueCount3 == 5:
        return 5
    else:
        return -1


def gamesetup():
    createdeck()
    createplayers()
    global playerpoints
    playerpoints = [0, 0, 0, 0]
    global negativepoints
    negativepoints = [0, 0, 0, 0]






gamesetup()
thread=threading.Thread(target=checkInput, daemon= True)
thread.start()
#do-while loop, die das Spiel darstellt
#Muss ein daemon sein, damit das Spiel beim schließen auch beendet wird

#mainloop ist die do-while Schleife, die auf Updates prüft und muss deshalb immer als letztes stehen
root.mainloop()




