import time
import board
import json
import busio
import digitalio
from adafruit_featherwing import minitft_featherwing

wing = minitft_featherwing.MiniTFTFeatherWing()

uart = busio.UART(board.TX, board.RX, baudrate=9600)

trg = digitalio.DigitalInOut(board.D13)
trg.direction = digitalio.Direction.OUTPUT
trg.value = False

def scan():
  try:
    uart.reset_input_buffer()
    trg.value = True
    time.sleep(0.5)
    trg.value = False
    time.sleep(0.2)

    data = uart.read()
    if data is not None:
      return ''.join(filter(lambda c: c > ' ', data.decode('latin1')))
    else:
      return None
  finally:
    trg.value = False

with open("prix.json", "r") as lecture_fichier:
    produits = json.load(lecture_fichier)

total=0

while True:
    buttons = wing.buttons

    if buttons.a:
        code_barre = scan()
        if code_barre != None:
            if code_barre in produits:
                total +=  produits[code_barre]
                print(total)
            else:
                # print(code_barre)
                print(total)
                time.sleep(5)
                print("NOUVEAU CLIENT")
                total=0
        # else: pas de code barre, on retourne au début de la boucle
