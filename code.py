import time
import board
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

for _ in range(2):
  print('3 seconds...')
  time.sleep(3)
  print('scan...')
  print('"{}"'.format(scan()))
  
buttons = wing.buttons

while not buttons.a:
  buttons = wing.buttons
