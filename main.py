import machine
import time
from ST7735 import TFT  # Import the TFT class from your library
import sysfont          # Import the font data
from machine import Pin

# Initialize SPI interface for the display
spi = machine.SPI(
    1,
    baudrate=20000000,
    polarity=0,
    phase=0,
    sck=machine.Pin(10),    # GPIO10 (CLK)
    mosi=machine.Pin(11)    # GPIO11 (DIN/MOSI)
    # MISO is not used by the display
)

# Define control pins for the TFT display
dc = machine.Pin(8, machine.Pin.OUT)     # GPIO8 (DC - Data/Command)
reset = machine.Pin(7, machine.Pin.OUT)  # GPIO7 (RST - Reset pin)
cs = machine.Pin(9, machine.Pin.OUT)     # GPIO9 (CS - Chip Select)

# Initialize TFT display
tft = TFT(spi, dc, reset, cs)
tft.initr()      # For red tab displays
tft.rgb(True)
tft.rotation(0)

# Clear the display with black color
tft.fill(tft.BLACK)

# Keypad setup - Zmienione piny dla wierszy
ROWS = [12, 13, 5, 14]  # GPIO pins for rows (zmieniono tylko piny 6 i 7 na 12 i 13)
COLS = [2, 3, 4]        # GPIO pins for columns (bez zmian)

# Map keypad buttons
keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

# Set up row pins as outputs
row_pins = [Pin(pin_num, Pin.OUT) for pin_num in ROWS]
# Set up column pins as inputs with pull-down
col_pins = [Pin(pin_num, Pin.IN, Pin.PULL_DOWN) for pin_num in COLS]

def read_keypad():
    """Reads which key is pressed on the keypad."""
    for row in range(4):
        # Set all rows to low
        for i in range(4):
            row_pins[i].value(0)
        # Set current row to high
        row_pins[row].value(1)
        # Check columns
        for col in range(3):
            if col_pins[col].value() == 1:
                return keys[row][col]
    return None

def display_number(number):
    """Display the given number on the TFT screen."""
    tft.fill(tft.BLACK)  # Clear screen
    tft.text((10, 10), number, tft.WHITE, sysfont.sysfont, 2)

def main():
    """Main function to read keypad and display values."""
    entered_number = ""  # Variable to store the entered number
    tft.fill(tft.BLACK)
    tft.text((10, 10), 'Wpisz liczbe:', tft.WHITE, sysfont.sysfont, 1)

    while True:
        key = read_keypad()
        if key:
            if key == '#':  # If '#' is pressed, show the number
                display_number(entered_number)
            elif key == '*':  # If '*' is pressed, reset the input
                entered_number = ""
                tft.fill(tft.BLACK)
            else:
                entered_number += key  # Append pressed key to the number
                time.sleep(0.3)  # Debounce delay

if __name__ == "__main__":
    main()
