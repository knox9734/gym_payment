import serial
import time

# Establish the connection to the Arduino
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)  # Replace 'COM3' with your port

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)  # Give some delay for Arduino to respond
    data = arduino.readline().decode('utf-8').rstrip()  # Read the response
    return data

while True:
    num = input("Enter a character: ")  # Taking input from user
    if num == 'exit':  # Exit condition
        break
    value = write_read(num)
    print(f"Arduino Response: {value}")
