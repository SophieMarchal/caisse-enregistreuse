import time
import board
import json
import busio
import displayio
import digitalio
import terminalio
from adafruit_display_text import label
from adafruit_ssd1351      import SSD1351
from adafruit_st7735r      import ST7735R
from adafruit_bitmap_font  import bitmap_font
from adafruit_featherwing  import minitft_featherwing

en = digitalio.DigitalInOut(board.A4)
en.direction = digitalio.Direction.OUTPUT
en.value = True
time.sleep(1)

# Setup SPI bus using hardware SPI:
spi = board.SPI()

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=board.A3, chip_select=board.A5, reset=board.A2,baudrate=4800)
display = SSD1351(display_bus, width=128, height=128)
group = displayio.Group(x=16, y=32)
with open("/photos/au_revoir.bmp", "rb") as file:
  blinka = displayio.OnDiskBitmap(file)
  face = displayio.TileGrid(blinka, pixel_shader=displayio.ColorConverter())
  group.append(face)
  display.show(group)
  # Wait for the image to load.
  display.refresh(target_frames_per_second=24)

wing = minitft_featherwing.MiniTFTFeatherWing()

uart = busio.UART(board.TX, board.RX, baudrate=9600)

trg = digitalio.DigitalInOut(board.D13)
trg.direction = digitalio.Direction.OUTPUT

noto18 = bitmap_font.load_font('/fonts/Noto-18.bdf')
noto18.load_glyphs('1234567890: '.encode('utf-8'))

def affiche_photo(code_barre):
  displayio.release_displays()
  display_bus = displayio.FourWire(spi, command=board.A3, chip_select=board.A5, reset=board.A2,baudrate=38400)
  display = SSD1351(display_bus, width=128, height=128)
  ### ici le code pour afficher la photo
  # group = displayio.Group(x=16, y=32)
  fichier="/photos/{}.bmp".format(code_barre)
  try:
    with open(fichier, "rb") as file:
      blinka = displayio.OnDiskBitmap(file)
      face = displayio.TileGrid(blinka, pixel_shader=displayio.ColorConverter())
      group = displayio.Group(x=16, y=32)
      group.append(face)
      display.show(group)
      display.refresh(target_frames_per_second=24)
  except OSError:
    with open("/blinka.bmp", "rb") as file:
      blinka = displayio.OnDiskBitmap(file)
      face = displayio.TileGrid(blinka, pixel_shader=displayio.ColorConverter())
      group = displayio.Group(x=16, y=32)
      group.append(face)
      display.show(group)
      # Wait for the image to load.
      display.refresh(target_frames_per_second=24)

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
        affiche_photo("inconnu")
    else:
        mabel=label.Label(terminalio.FONT, text='prix= {}'.format(prix), x=20, y=20)
        affiche_photo(code_barre)
    groupe.append(mabel)
    if nouveau_client:
        tabel=label.Label(terminalio.FONT,text= 'AU REVOIR', color= 0xff0000, x=70, y=70)
        groupe.append(tabel)
        affiche_photo("au_revoir")
    displayio.release_displays()
    display_bus = displayio.FourWire(board.SPI(), command=board.D6, chip_select=board.D5)
    display = ST7735R(display_bus, width=160, height=80, colstart=24, rotation=270, bgr=True)
    display.show(groupe)

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
                print ('code-barre non connu: {}'.format(code_barre))
                ecriture(total,None,False, code_barre)
        else:
            ecriture(total,None, False, code_barre)
    time.sleep(0.2)