import board
import busio
import adafruit_mpr121

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create MPR121 object
mpr121 = adafruit_mpr121.MPR121(i2c)

print("Touch sensor test! Press Ctrl+C to quit.")

while True:
    for i in range(12):  # MPR121 has 12 electrodes
        if mpr121[i].value:
            print(f"Electrode {i} touched!")

