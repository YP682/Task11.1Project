import tkinter as tk
from tkinter import ttk, messagebox  # Import messagebox module
import paho.mqtt.client as mqtt

# MQTT settings
broker = "broker.emqx.io"
temperature_topic = "home/temperature"
humidity_topic = "home/humidity"
light_topic = "home/light"

# Global variables to store sensor data
temperature = None
humidity = None
light_intensity = None

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(temperature_topic)
    client.subscribe(humidity_topic)
    client.subscribe(light_topic)

def on_message(client, userdata, msg):
    global temperature, humidity, light_intensity
    if msg.topic == temperature_topic:
        temperature = float(msg.payload.decode())
        temperature_label.config(text=f"Temperature: {temperature} °C")
        # Check temperature
        if temperature > 28:
            messagebox.showwarning("Temperature Alert", "It is too hot. Bring the pet inside!")
        elif temperature < 7:
            messagebox.showwarning("Temperature Alert", "It is too cold. Bring the pet inside!")
    elif msg.topic == humidity_topic:
        humidity = float(msg.payload.decode())
        humidity_label.config(text=f"Humidity: {humidity} %")
        # Check humidity
        if humidity > 70:
            messagebox.showwarning("Humidity Alert", "Humidity is too high. Bring the pet inside!")
        elif humidity < 30:
            messagebox.showwarning("Humidity Alert", "Humidity is too low. Bring the pet inside!")
    elif msg.topic == light_topic:
        light_intensity = float(msg.payload.decode())
        light_label.config(text=f"Light Intensity: {light_intensity} lux")
        # Check light intensity
        if light_intensity < 10.00:
            messagebox.showwarning("Alert", "It is too dark outside. Bring the pet inside!")

# GUI setup
root = tk.Tk()
root.title("Sensor Data")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

temperature_label = ttk.Label(mainframe, text="Temperature: -- °C")
temperature_label.grid(row=0, column=0, padx=5, pady=5)

humidity_label = ttk.Label(mainframe, text="Humidity: -- %")
humidity_label.grid(row=1, column=0, padx=5, pady=5)

light_label = ttk.Label(mainframe, text="Light Intensity: -- lux")
light_label.grid(row=2, column=0, padx=5, pady=5)

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883, 60)
client.loop_start()

# Start the Tkinter event loop
root.mainloop()
