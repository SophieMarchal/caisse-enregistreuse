import time
import board
import json
import busio
import displayio
import digitalio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font  import bitmap_font
from adafruit_featherwing import minitft_featherwing

wing = minitft_featherwing.MiniTFTFeatherWing()

uart = busio.UART(board.TX, board.RX, baudrate=9600)

trg = digitalio.DigitalInOut(board.D13)
trg.direction = digitalio.Direction.OUTPUT

noto18 = bitmap_font.load_font('/fonts/Noto-18.bdf')
noto18.load_glyphs('1234567890: '.encode('utf-8'))

def scan():
  try:
    uart.reset_input_buffer()
    trg.value = True
    time.sleep(0.5)
    trg.value = False
    time.sleep(0.2)

    data = uart.readline()
    if data is not None:
      return ''.join(filter(lambda c: c > ' ', data.decode('latin1')))
    else:
      return None
  finally:
    trg.value = False

def ecriture(total,prix,nouveau_client, code_barre):
    groupe= displayio.Group()
    yabel=label.Label(noto18,text='total: {}'.format(total), x=20, y=40)
    groupe.append(yabel)
    if prix == None:
        mabel=label.Label(terminalio.FONT, text=str(code_barre), x=20, y=20)
    else:
        mabel=label.Label(terminalio.FONT, text='prix= {}'.format(prix), x=20, y=20)
    groupe.append(mabel)
    if nouveau_client:
        tabel=label.Label(terminalio.FONT,text= 'AU REVOIR', color= 0xff0000, x=70, y=70)
        groupe.append(tabel)
    wing.display.show(groupe)

with open("prix.json", "r") as lecture_fichier:
    produits = json.load(lecture_fichier)

with open("carte.json","r") as lecture_fichier:
    carte = json.load(lecture_fichier)

total=0

while True:
    buttons = wing.buttons

    if buttons.a:
        code_barre = scan()
        if code_barre != None:
            if code_barre in produits:
                prix= produits[code_barre]
                total +=  prix
                ecriture(total, prix, False, code_barre)
            elif code_barre in carte:
                ecriture(total,None,True, code_barre)
                total=0
            else:
                print ("code-barre non connu")
                ecriture(total,None,False, code_barre)
        else:
            ecriture(total,None, False, code_barre)
    time.sleep(0.2)