from tkinter import *
from tkinter import ttk, messagebox
import requests
import pyttsx3
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# ================================
# Settings
# ================================
API_KEY = "97a9956652ad7410fcbc5233c24ef51e"  # Replace with your API key
CITY_FILE = "last_city.json"

INDIAN_CITIES = [
    "Ahmedabad", "Bengaluru", "Bhopal", "Bhubaneswar", "Chandigarh", "Chennai", "Coimbatore", "Dehradun",
    "Delhi", "Ernakulam", "Faridabad", "Ghaziabad", "Gurgaon", "Guwahati", "Hyderabad", "Indore", "Jaipur",
    "Jammu", "Jamshedpur", "Kanpur", "Kochi", "Kolkata", "Kozhikode", "Lucknow", "Ludhiana", "Madurai",
    "Mangalore", "Mumbai", "Mysuru", "Nagpur", "Nashik", "Noida", "Patna", "Pune", "Raipur", "Rajkot",
    "Ranchi", "Surat", "Thane", "Thiruvananthapuram", "Vadodara", "Varanasi", "Vijayawada", "Visakhapatnam"
]

# ================================
# TTS
# ================================
def speak_weather(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# ================================
# File Save/Load
# ================================
def save_last_city(city):
    with open(CITY_FILE, 'w') as f:
        json.dump({'last_city': city}, f)

def load_last_city():
    if os.path.exists(CITY_FILE):
        with open(CITY_FILE, 'r') as f:
            return json.load(f).get('last_city', 'Chennai')
    return 'Chennai'

# ================================
# Weather Display
# ================================
def display_weather():
    city = city_var.get().strip()
    if not city:
        messagebox.showerror("Error", "Please enter a city")
        return

    save_last_city(city)

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        messagebox.showerror("Error", "City not found!")
        return

    data = response.json()

    # Extract weather info
    weather_desc = data['weather'][0]['description'].lower()
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind = data['wind']['speed']

    emoji = "☀️"
    bg_color = "#fdf6b2"

    if "rain" in weather_desc:
        emoji = "🌧️"
        bg_color = "#d0e5f2"
    elif "cloud" in weather_desc:
        emoji = "⛅"
        bg_color = "#d6dbdf"
    elif "thunder" in weather_desc:
        emoji = "🌩️"
        bg_color = "#8e44ad"
    elif "snow" in weather_desc:
        emoji = "❄️"
        bg_color = "#d6eaf8"
    elif "mist" in weather_desc or "fog" in weather_desc:
        emoji = "🌫️"
        bg_color = "#d5d8dc"
    elif "clear" in weather_desc:
        emoji = "☀️"
        bg_color = "#f9e79f"

    root.config(bg=bg_color)

    # Display result
    result_text = f"{emoji} {weather_desc.title()}\n🌡️ Temp: {temp}°C\n💧 Humidity: {humidity}%\n🌬️ Wind: {wind} m/s"
    weather_output.config(text=result_text)

    # Speak
    speak_weather(f"The weather in {city} is {weather_desc}. The temperature is {temp} degree Celsius.")

    # Forecast graph
    get_forecast(city)

# ================================
# 5-Day Forecast Graph
# ================================
def get_forecast(city):
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(forecast_url)
    data = res.json()

    dates, temps = [], []
    for i in range(0, len(data['list']), 8):  # Every 8 steps = 1 day
        entry = data['list'][i]
        dt = datetime.datetime.fromtimestamp(entry['dt']).strftime('%a')
        temp = entry['main']['temp']
        dates.append(dt)
        temps.append(temp)

    ax.clear()
    ax.plot(dates, temps, marker='o')
    ax.set_title("5-Day Forecast")
    ax.set_ylabel("Temperature (°C)")
    chart.draw()

# ================================
# Tkinter GUI Setup
# ================================
root = Tk()
root.title("🌦️ Indian Weather App")
root.geometry("500x600")
root.resizable(False, False)
root.config(bg="white")

# Dropdown
city_var = StringVar(value=load_last_city())
Label(root, text="Select City:", font=("Arial", 12), bg="white").pack(pady=(20, 5))
city_dropdown = ttk.Combobox(root, textvariable=city_var, values=sorted(INDIAN_CITIES))
city_dropdown.pack(pady=5)

# Search
Button(root, text="Get Weather", font=("Arial", 12), command=display_weather).pack(pady=10)

# Output
weather_output = Label(root, text="", font=("Arial", 14), bg="white", justify=LEFT)
weather_output.pack(pady=20)

# Forecast graph
fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
chart = FigureCanvasTkAgg(fig, master=root)
chart.get_tk_widget().pack()

# Initial Load
display_weather()

root.mainloop()
