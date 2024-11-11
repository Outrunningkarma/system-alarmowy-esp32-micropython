import machine
import time
from ST7735 import TFT
import sysfont
from machine import Pin

# Initialize SPI interface for the display
spi = machine.SPI(
    1,
    baudrate=20000000,
    polarity=0,
    phase=0,
    sck=machine.Pin(10),
    mosi=machine.Pin(11)
)

# Define control pins for the TFT display
dc = machine.Pin(8, machine.Pin.OUT)
reset = machine.Pin(7, machine.Pin.OUT)
cs = machine.Pin(9, machine.Pin.OUT)

# Initialize TFT display
tft = TFT(spi, dc, reset, cs)
tft.initr()
tft.rgb(True)
tft.rotation(1)

tft.fill(tft.BLACK)

ROWS = [12, 13, 5, 18]  # GPIO pins for rows
COLS = [2, 3, 4]        # GPIO pins for columns

keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

row_pins = [Pin(pin_num, Pin.OUT) for pin_num in ROWS]
col_pins = [Pin(pin_num, Pin.IN, Pin.PULL_DOWN) for pin_num in COLS]

current_screen = 1
entered_code = ""
last_entered_code = ""
input_active = False  # Controls if input is active for code entry

def read_keypad():
    for row in range(4):
        for i in range(4):
            row_pins[i].value(0)
        row_pins[row].value(1)
        for col in range(3):
            if col_pins[col].value() == 1:
                return keys[row][col]
    return None

def display_screen_number():
    tft.text((90, 60), f"Screen {current_screen}", tft.WHITE, sysfont.sysfont, 1)

def clear_screen():
    tft.fill(tft.BLACK)
    display_screen_number()

def update_time():
    now = time.localtime()
    current_time = "{:02}:{:02}".format(now[3], now[4])
    tft.text((100, 10), current_time, tft.WHITE, sysfont.sysfont, 1)

def main_screen():
    clear_screen()
    tft.text((10, 30), 'Wpisz kod:', tft.WHITE, sysfont.sysfont, 1)

def thank_you_screen():
    clear_screen()
    tft.text((10, 30), 'Dziekuje za wpisanie kodu', tft.WHITE, sysfont.sysfont, 1)

def last_code_screen():
    clear_screen()
    tft.text((10, 30), "Ostatni kod:", tft.WHITE, sysfont.sysfont, 1)
    tft.text((10, 50), f"{last_entered_code}", tft.WHITE, sysfont.sysfont, 1)

def time_screen():
    clear_screen()
    display_screen_number()  # Show "Screen 3" by default

def show_back_option():
    tft.text((90, 60), "* - wroc", tft.WHITE, sysfont.sysfont, 1)

def main():
    global current_screen, entered_code, last_entered_code, input_active

    last_screen_change_time = time.time()  # Time of last screen change
    debounce_time = 0.15  # Shorter debounce time for quick response on press without hold

    while True:
        clear_screen()
        if current_screen == 1:
            main_screen()
        elif current_screen == 2:
            last_code_screen()
        elif current_screen == 3:
            time_screen()

        input_active = False  # Reset input activity state on each screen entry

        while True:
            key = read_keypad()
            if key:
                current_time = time.time()
                if key == '4' and (current_time - last_screen_change_time) > debounce_time:
                    current_screen = (current_screen - 1) if current_screen > 1 else 3
                    last_screen_change_time = current_time  # Update time for next press
                    break
                elif key == '6' and (current_time - last_screen_change_time) > debounce_time:
                    current_screen = (current_screen + 1) if current_screen < 3 else 1
                    last_screen_change_time = current_time  # Update time for next press
                    break
                elif key == '#':  # Confirm screen selection
                    if current_screen == 1 and not input_active:
                        input_active = True
                        entered_code = ""
                        tft.fill(tft.BLACK)  # Clear screen once input is active
                    elif current_screen == 2:
                        last_code_screen()
                        show_back_option()
                        while True:
                            exit_key = read_keypad()
                            if exit_key == '*':  # Exit to previous screen
                                clear_screen()  # Reset to default screen
                                break
                    elif current_screen == 3:
                        time_screen()
                        update_time()  # Show time after confirmation
                        show_back_option()
                        while True:
                            exit_key = read_keypad()
                            if exit_key == '*':  # Exit to previous screen
                                clear_screen()  # Reset to default screen
                                break
                elif input_active and current_screen == 1:  # Only accept input if input is active
                    if key == '*':  # Exit input mode and return to screen with "Screen 1" text
                        input_active = False
                        main_screen()
                        break
                    elif key == '0':  # Confirm code
                        last_entered_code = entered_code
                        thank_you_screen()
                        time.sleep(1)
                        input_active = False
                        main_screen()
                        break
                    else:
                        entered_code += key
                        tft.text((10, 40), entered_code, tft.WHITE, sysfont.sysfont, 2)
                        time.sleep(0.1)  # Shorter delay for quicker response
                time.sleep(0.1)  # Reduced general delay for improved responsiveness

if __name__ == "__main__":
    main()

