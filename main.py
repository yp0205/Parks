import os
import random
import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# API 설정
API_KEY = "7c8b7606ae705ee5aeb125202d26e65c"
CITY_NAME = "Seoul"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric&lang=kr"

CLOSET_DIR = r"C:\Parks\my_closet"
IMAGE_WIDTH = 150

# 기본 카테고리
CATEGORY_TAGS = {
    "short_sleeves": ["summer", "short"],
    "long_sleeves": ["spring", "long"],
    "outer": ["rain", "cold", "wind"],
    "shorts": ["summer", "short"],
    "jeans": ["spring", "long"],
    "shoes": ["any"],
}

CATEGORY_GROUP = {
    "겉옷": ["outer"],
    "상의": ["short_sleeves", "long_sleeves"],
    "하의": ["shorts", "jeans"],
    "신발": ["shoes"],
}


# 옷 불러오기
def load_clothes():
    clothes = {}
    for folder in os.listdir(CLOSET_DIR):
        path = os.path.join(CLOSET_DIR, folder)
        if os.path.isdir(path):
            clothes[folder] = [
                os.path.join(path, file)
                for file in os.listdir(path)
                if file.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
    return clothes


# 날씨 불러오기
def get_weather():
    try:
        res = requests.get(WEATHER_URL)
        data = res.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].lower()
        return temp, desc
    except:
        return None, None


# 날씨 기반 코디 추천
def recommend_by_weather(clothes):
    temp, weather = get_weather()
    if temp is None:
        return {}, "날씨 정보를 가져올 수 없습니다."

    reason = f"{weather} / {int(temp)}°C에 적합한 옷을 찾습니다."

    if "rain" in weather or "비" in weather:
        conditions = ["rain"]
    elif temp < 10:
        conditions = ["cold"]
    elif temp < 20:
        conditions = ["spring", "long"]
    elif temp > 25:
        conditions = ["summer", "short"]
    else:
        conditions = ["spring"]

    selected = {}
    for group_name, category_list in CATEGORY_GROUP.items():
        found = False
        for category in category_list:
            if any(
                tag in conditions or tag == "any"
                for tag in CATEGORY_TAGS.get(category, [])
            ):
                available = clothes.get(category, [])
                if available:
                    selected[group_name] = random.choice(available)
                    found = True
                    break
        if not found:
            selected[group_name] = None

    return selected, reason


# 코디 출력
def show_outfit(outfit, reason):
    for widget in weather_frame.winfo_children():
        widget.destroy()

    label = tk.Label(weather_frame, text=reason, font=("Arial", 12))
    label.pack(pady=10)

    for part in ["겉옷", "상의", "하의", "신발"]:
        path = outfit.get(part)
        if path:
            img = Image.open(path)
            ratio = IMAGE_WIDTH / img.width
            new_size = (IMAGE_WIDTH, int(img.height * ratio))
            img = img.resize(new_size)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(weather_frame, image=photo)
            label.image = photo
            label.pack(pady=5)
        else:
            label = tk.Label(
                weather_frame,
                text=f"{part}: 해당 조건의 옷이 없습니다.",
                font=("Arial", 10),
            )
            label.pack(pady=5)


# 옷장 전체 출력
def show_closet():
    for widget in closet_frame.winfo_children():
        widget.destroy()

    for category, paths in clothes.items():
        # 카테고리 제목
        title = tk.Label(
            closet_frame, text=f"📁 {category}", font=("Arial", 11, "bold")
        )
        title.pack(anchor="w", padx=10, pady=(10, 2))

        if not paths:
            label = tk.Label(
                closet_frame, text="(비어있음)", font=("Arial", 10), fg="gray"
            )
            label.pack(anchor="w", padx=20)
        else:
            img_frame = tk.Frame(closet_frame)
            img_frame.pack(anchor="w", padx=20, pady=5)

            for i, path in enumerate(paths):
                img = Image.open(path)
                ratio = IMAGE_WIDTH / img.width
                new_size = (IMAGE_WIDTH, int(img.height * ratio))
                img = img.resize(new_size)
                photo = ImageTk.PhotoImage(img)

                label = tk.Label(img_frame, image=photo)
                label.image = photo
                label.grid(row=0, column=i, padx=5)


def recommend():
    outfit, reason = recommend_by_weather(clothes)
    show_outfit(outfit, reason)


# --- GUI 설정 ---
root = tk.Tk()
root.title("날씨 기반 코디 추천기")
root.geometry("400x700")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# 탭 1: 날씨 기반 코디
weather_tab = tk.Frame(notebook)
notebook.add(weather_tab, text="코디 추천")

weather_frame = tk.Frame(weather_tab)
weather_frame.pack(pady=10)

button = ttk.Button(weather_tab, text="코디 추천 받기", command=recommend)
button.pack(pady=10)

# 탭 2: 옷장 보기
closet_tab = tk.Frame(notebook)
notebook.add(closet_tab, text="내 옷장")

closet_frame = tk.Frame(closet_tab)
closet_frame.pack(pady=10)

clothes = load_clothes()
show_closet()

root.mainloop()
