import time
import random
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000
spi = board.SPI()

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

height = disp.width
width = disp.height
rotation = 90

# --- Drawing setup ---
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)

# --- Backlight ---
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# --- Buttons ---
button_a = digitalio.DigitalInOut(board.D23)  # Start/Stop stopwatch OR increment counter
button_a.switch_to_input(pull=digitalio.Pull.UP)

button_b = digitalio.DigitalInOut(board.D24)  # Toggle stopwatch/image + reset stopwatch
button_b.switch_to_input(pull=digitalio.Pull.UP)

# --- Stopwatch variables ---
running = False
start_time = 0
elapsed = 0
show_stopwatch = True  # default mode

# --- Counter variable ---
cup_count = 0  # hydration counter

# --- Background images ---
# for stopwatch
bg_stopwatch = Image.open("asset/stopwatch1.png")
bg_stopwatch = bg_stopwatch.resize((width, height))

# for counter
bg_counter = Image.open("asset/counter1.png")
bg_counter = bg_counter.resize((width, height))

# --- color palatte ---
WATER_BLUE = (102, 192, 255)
CONFETTI_COLORS = [(51, 171, 255), (102, 192, 255), (153, 213, 255), (204, 234, 255)]


# ---  Marquee scrolling text ---
def show_marquee(message, stop_callback):
    text_width = font.getlength(message)
    x = width
    while True:
        frame = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(frame)
        draw.text((x, height // 2 - 10), message, font=font, fill=WATER_BLUE)
        disp.image(frame, rotation)
        x -= 5
        if x < -text_width:
            x = width  # loop again
        time.sleep(0.1)
        if stop_callback():  # Button A pressed to stop
            break


# --- Confetti/Bubble effect ---
def show_confetti(duration=4):
    start = time.time()
    while time.time() - start < duration:
        frame = bg_counter.copy()
        draw = ImageDraw.Draw(frame)

        # draw random bubbles
        for _ in range(30):
            x0 = random.randint(0, width)
            y0 = random.randint(0, height)
            r = random.randint(3, 8)
            color = random.choice(CONFETTI_COLORS)
            draw.ellipse((x0, y0, x0 + r, y0 + r), fill=color)

        disp.image(frame, rotation)
        time.sleep(0.1)


# ==============================
#         MAIN LOOP
# ==============================
while True:
    # --- Handle Button A ---
    if not button_a.value:  # pressed
        if show_stopwatch:
            # Stopwatch mode: start/stop
            if not running:
                start_time = time.time() - elapsed  # resume
                running = True
            else:
                running = False
        else:
            # Counter mode: increment water cups
            cup_count += 1
        time.sleep(0.3)  # debounce

    # --- Handle Button B ---
    if not button_b.value:
        press_start = time.time()
        while not button_b.value:
            time.sleep(0.05)
        press_duration = time.time() - press_start

        if press_duration < 1.0:
            # short press → toggle modes
            show_stopwatch = not show_stopwatch
        else:
            # long press
            if show_stopwatch:
                # reset stopwatch
                running = False
                elapsed = 0
            else:
                # increment counter by 1 on long press
                cup_count += 1
        time.sleep(0.3)

    # --- Display logic ---
    if show_stopwatch:
        # Update elapsed if running
        if running:
            elapsed = time.time() - start_time

        # Hydration reminder after 5 minutes
        if elapsed >= 300: 
            def stop_check():
                # Stop marquee if Button A or B is pressed
                return (not button_a.value) or (not button_b.value)
        
            show_marquee("Hydration time!", stop_check)
        
            # Decide which mode to return to
            if not button_a.value:
                show_stopwatch = False  # go to counter mode
            elif not button_b.value:
                show_stopwatch = True   # stay in stopwatch mode
            continue

        elapsed_seconds = int(elapsed)
        mins, secs = divmod(elapsed_seconds, 60)
        hours, mins = divmod(mins, 60)
        text = f"{hours:02d}:{mins:02d}:{secs:02d}"

        # Draw stopwatch bg
        frame = bg_stopwatch.copy()
        draw = ImageDraw.Draw(frame)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (width - text_w) // 2
        y = (height - text_h) // 2

        draw.text((x, y), text, font=font, fill=(0, 0, 0))  # black text
        disp.image(frame, rotation)

    else:
        # Counter mode
        frame = bg_counter.copy()
        draw = ImageDraw.Draw(frame)

        text = f"{cup_count}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = ((width - text_w) // 2) + 20
        y = ((height - text_h) // 2) - 10

        draw.text((x, y), text, font=font, fill=(0, 0, 0))
        disp.image(frame, rotation)

        # Celebration trigger 
        if cup_count % 5 == 0 and cup_count > 0:
            show_confetti(duration=4)

    time.sleep(0.1)
