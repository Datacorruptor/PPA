import cv2
from PIL import ImageGrab
import numpy as np
import easyocr

reader = easyocr.Reader(['en'],gpu=True)
PLAYERS = 9

def detect_suits(frame):
    suits ={
        (129, 136, 139) : "Spades",
        (65, 94, 254) :"Hearts",
        (120, 168, 0) :"Clubs",
        (203, 150, 119) :"Diamonds"
    }
    try:
        #print(suits[tuple(frame[35][100])] ,"+",suits[tuple(frame[35][220])])

        return suits[tuple(frame[35][100])], suits[tuple(frame[35][220])]
    except Exception:
        print("Unable to detect a suit")
        return -1

def upscale_image(frame):
    scale_percent = 220
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

def black_white(frame):
    for i in range(len(frame)):
        for j in range(len(frame[0])):
            if sum(list(frame[i][j])) > 180*3:
                frame[i][j]=[0,0,0]
            else:
                frame[i][j] = [255, 255, 255]
    return frame
def detect_ranks(frame):

    frame = black_white(frame)
    result = reader.readtext(frame)
    #print(result)
    combination = " ".join(i[1] for i in result).lower().replace('o','0').replace('i','1').replace('l','1')
    #print(combination)

    suits = combination.split()

    if len(suits)==2:
        if suits[0] == '0':
            suits[0] = 'q'
        if suits[1] == '0':
            suits[1] = 'q'
        return suits
    else:
        print("Unable to detect a rank")
        return -1



def combine_to_hand(ranks,suits):

    hand = ranks[0].replace("10","T").upper()
    hand+= ranks[1].replace("10","T").upper()

    if RANKS[hand[0]]<RANKS[hand[1]]:
        hand = hand[1]+hand[0]

    if suits[0]==suits[1]:
        hand+='s'
    else:
        hand+='o'

    return hand

def from_string_to_range(range_str):
    hand_range = set()

    range_parts = range_str.split(',')

    for i in range(RANKS[range_parts[0][0]],13):
        hand_range.add(list(RANKS)[i]+list(RANKS)[i]+'o')

    for k in range(1,len(range_parts)):
        if len(range_parts[k])==4:
            for i in range(RANKS[range_parts[k][1]], RANKS[range_parts[k][0]]):
                hand_range.add(range_parts[k][0] + list(RANKS)[i] + range_parts[k][2])
        else:
            hand_range.add(range_parts[k])

    #print(hand_range)
    return hand_range


def detect_pos():
    img_table= np.array(ImageGrab.grab(bbox=(1000, 100, 1920, 600)))
    table = cv2.cvtColor(img_table, cv2.COLOR_BGR2RGB)
    cv2.imshow("full table", table)

    if PLAYERS == 6:
        positions = [(337,360),(304,669),(146,716),(93,483),(152,175),(236,158)]
        position_names = ["BU","SB","BB","UTG","MP","CO"]
    if PLAYERS == 9:
        positions = [(337,360),(303,614),(254,714),(131,695),(97,556),(85,297),(157,175),(170,161),(317,273)]
        position_names = ["BU","SB","BB","UTG","UTG+1","MP1","MP2","MP3","CO"]

    pos_index=0
    max=0
    for i in range(len(positions)):
        brightness = sum(table[positions[i][0]][positions[i][1]])
        if brightness > max:
            max=brightness
            pos_index = i
    #print(position_names[pos_index])
    return pos_index,position_names[pos_index]

def check_in_range(hand,position_index):
    if hand in RANGES[position_index]:
        return True
    else:
        return False


RANKS = {
    "2":0,
    "3":1,
    "4":2,
    "5":3,
    "6":4,
    "7":5,
    "8":6,
    "9":7,
    "T":8,
    "J":9,
    "Q":10,
    "K":11,
    "A":12,
}

range_strings=[]
if PLAYERS == 6:
    range_strings = [
        "22+,A2s+,K7s+,Q7s+,J7s+,T8s+,97s+,87s,76s,65s,54s,A2o+,K8o+,Q8o+,J8o+,T8o+,97o+,87o,76o,65o,54o", #BU
        "22+,A6s+,K9s+,Q9s+,J8s+,T9s,98s,87s,76s,ATo+,K9o+,Q9o+,J9o+", #SB
        "22+,A6s+,K9s+,Q9s+,J8s+,T9s,98s,87s,76s,ATo+,K9o+,Q9o+,J9o+", #BB
        "22+,ATs+,KQs,AJo+,KQo", #UTG
        "22+,ATs+,KJs+,ATo+,KJo+", #MP
        "22+,A6s+,K9s+,Q9s+,J9s+,T8s+,98s,87s,76s,65s,A9o+,K9o+,Q9o+,J9o+,T9o,98o,87o"  #CO
    ]
elif PLAYERS == 9:
    range_strings=[
        "22+,A2s+,K9s+,Q9s+,J8s+,T8s+,97s+,86s+,75s+,65s,54s,A2o+,KTo+,QTo+,J9o+,T8o+,98o,87o,76o,65o",  # BU
        "22+,A2s+,K9s+,Q9s+,J9s+,T9s,98s,87s,76s,65s,54s,ATo+,KTo+,QTo+,JTo",  # SB
        "22+,A2s+,K9s+,Q9s+,J9s+,T9s,98s,87s,76s,65s,54s,ATo+,KTo+,QTo+,JTo",  # BB
        "77+,AQs+,AKo", #UTG
        "77+,AQs+,AKo", #UTG+1
        "77+,AQs+,AQo+", #UTG+2
        "77+,AJs+,KQs,QJs,JTs,T9s,98s,AQo+", #MP1
        "66+,AJs+,KQs,QJs,JTs,T9s,98s,87s,AJo+,KQo", #MP2
        "55+,ATs+,KJs+,QJs,JTs,T9s,98s,87s,76s,ATo+,KQo", #MP3
        "22+,A7s+,K9s+,Q9s+,J9s+,T8s+,97s+,87s,76s,65s,54s,A9o+,KTo+,QTo+,JTo,T9o,98o,87o" #CO
    ]

RANGES = []
for range_str in range_strings:
    RANGES.append(from_string_to_range(range_str))



while True:
    img_np = np.array(ImageGrab.grab(bbox=(1380,430,1500,470)))
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    frame = upscale_image(frame)
    suits = detect_suits(frame)
    frame[35][100] = [0, 0, 0]
    frame[35][220] = [0, 0, 0]
    cv2.imshow("cut", frame)
    ranks = detect_ranks(frame)
    cv2.imshow("edited", frame)
    pos_index,pos_name = detect_pos()
    if ranks!=-1 and suits!=-1:
        hand = combine_to_hand(ranks,suits)

        print("[",hand,pos_name,"] ==> ",end='')
        if check_in_range(hand,pos_index):
            print("Raise")
        else:
            print("Fold")

    cv2.waitKey(1)


cv2.destroyAllWindows()