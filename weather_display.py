import tkinter as tk
from tkinter import ttk
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import random
import math

class WeatherDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shanghai Weather Display")
        self.root.geometry("800x700")
        self.root.configure(bg='lightblue')
        
        # 读取CSV数据
        self.weather_data = self.load_weather_data()
        self.current_index = 0
        
        # 特效相关变量
        self.effects_canvas = None
        self.rain_drops = []
        self.snow_flakes = []
        self.sun_rays = []
        self.current_weather_type = ""
        self.effects_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 启动自动更新
        self.start_auto_update()
        
    def load_weather_data(self):
        """加载天气数据"""
        try:
            # 读取CSV文件，指定编码为utf-8
            df = pd.read_csv('weather.csv', encoding='utf-8')
            return df
        except UnicodeDecodeError:
            # 如果utf-8失败，尝试gbk编码
            try:
                df = pd.read_csv('weather.csv', encoding='gbk')
                return df
            except:
                # 如果都失败，尝试其他编码
                df = pd.read_csv('weather.csv', encoding='gb2312')
                return df
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建特效画布（全屏覆盖）
        self.effects_canvas = tk.Canvas(self.root, bg='lightblue', highlightthickness=0)
        self.effects_canvas.pack(fill='both', expand=True)
        
        # 日期和温度显示区域（左上角）
        self.info_frame = tk.Frame(self.effects_canvas, bg='lightblue')
        self.effects_canvas.create_window(20, 20, anchor='nw', window=self.info_frame)
        
        self.date_label = tk.Label(self.info_frame, 
                                 font=('Arial', 16, 'bold'),
                                 bg='lightblue',
                                 fg='darkblue')
        self.date_label.pack(anchor='w')
        
        self.temp_label = tk.Label(self.info_frame,
                                 font=('Arial', 14),
                                 bg='lightblue',
                                 fg='darkred')
        self.temp_label.pack(anchor='w')
        
        # 天气图标显示区域（中间）
        self.weather_frame = tk.Frame(self.effects_canvas, bg='lightblue')
        self.effects_canvas.create_window(500, 300, anchor='center', window=self.weather_frame)
        
        self.weather_icon = tk.Label(self.weather_frame,
                                   font=('Arial', 100),
                                   bg='lightblue',
                                   fg='orange')
        self.weather_icon.pack(expand=True)
        
        # 天气描述
        self.weather_desc = tk.Label(self.weather_frame,
                                   font=('Arial', 18),
                                   bg='lightblue',
                                   fg='darkgreen')
        self.weather_desc.pack()
        
        # 控制按钮
        self.control_frame = tk.Frame(self.effects_canvas, bg='lightblue')
        self.effects_canvas.create_window(400, 650, anchor='center', window=self.control_frame)
        
        self.prev_btn = tk.Button(self.control_frame, 
                                text="Former Day",
                                command=self.prev_day,
                                font=('Arial', 12))
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = tk.Button(self.control_frame,
                                text="Next Day", 
                                command=self.next_day,
                                font=('Arial', 12))
        self.next_btn.pack(side='left', padx=5)
        
        # 自动更新开关
        self.auto_update_var = tk.BooleanVar(value=True)
        self.auto_check = tk.Checkbutton(self.control_frame,
                                       text="Auto Update",
                                       variable=self.auto_update_var,
                                       font=('Arial', 12),
                                       bg='lightblue')
        self.auto_check.pack(side='left', padx=10)
        
        # 初始化显示
        self.update_display()
    
    def get_weather_icon(self, weather_text):
        """根据天气情况返回对应的图标"""
        weather_text = str(weather_text).lower()
        
        if '晴' in weather_text:
            return '☀️'  # 太阳
        elif '雨' in weather_text or '雨' in weather_text:
            return '🌧️'  # 下雨
        elif '云' in weather_text or '阴' in weather_text:
            return '☁️'  # 多云/阴天
        elif '雪' in weather_text:
            return '❄️'  # 雪
        else:
            return '🌤️'  # 默认图标
    
    def get_weather_type(self, weather_text):
        """获取天气类型用于特效"""
        weather_text = str(weather_text).lower()
        
        if '晴' in weather_text:
            return 'sunny'
        elif '雨' in weather_text:
            return 'rainy'
        elif '雪' in weather_text:
            return 'snowy'
        elif '云' in weather_text or '阴' in weather_text:
            return 'cloudy'
        else:
            return 'default'
    
    def translate_weather_to_english(self, weather_text):
        """将中文天气描述翻译成英文"""
        weather_text = str(weather_text)
        
        # 常见天气词汇翻译
        translations = {
            '晴': 'Sunny',
            '多云': 'Cloudy',
            '阴': 'Overcast',
            '雨': 'Rainy',
            '小雨': 'Light Rain',
            '中雨': 'Moderate Rain',
            '大雨': 'Heavy Rain',
            '小': 'Light',
            '中': 'Moderate',
            '大': 'Heavy',
            '雷雨': 'Thunderstorm',
            '雪': 'Snowy',
            '雾': 'Foggy',
            '霾': 'Hazy',
            '沙尘': 'Dusty',
            '~': ' to ',
            '转': ' to '
        }
        
        # 替换中文词汇
        english_text = weather_text
        for chinese, english in translations.items():
            english_text = english_text.replace(chinese, english)
        
        return english_text
    
    def clear_effects(self):
        """清除所有特效"""
        self.effects_canvas.delete("rain", "snow", "sun_ray", "fog")
        self.rain_drops.clear()
        self.snow_flakes.clear()
        self.sun_rays.clear()
        self.effects_running = False
    
    def create_sun_rays(self):
        """创建太阳光照特效"""
        center_x, center_y = 400, 300
        for i in range(12):
            angle = i * 30
            ray_length = 150
            end_x = center_x + ray_length * math.cos(math.radians(angle))
            end_y = center_y + ray_length * math.sin(math.radians(angle))
            
            ray = self.effects_canvas.create_line(
                center_x, center_y, end_x, end_y,
                fill='yellow', width=3, tags="sun_ray"
            )
            self.sun_rays.append(ray)
    
    def animate_sun_rays(self):
        """太阳光照动画"""
        if not self.effects_running or self.current_weather_type != 'sunny':
            return
        
        for ray in self.sun_rays:
            # 让光线闪烁
            current_color = self.effects_canvas.itemcget(ray, 'fill')
            new_color = 'orange' if current_color == 'yellow' else 'yellow'
            self.effects_canvas.itemconfig(ray, fill=new_color)
        
        self.root.after(500, self.animate_sun_rays)
    
    def create_rain_effect(self):
        """创建雨滴特效"""
        for _ in range(50):
            x = random.randint(0, 800)
            y = random.randint(-100, 0)
            length = random.randint(10, 20)
            speed = random.randint(3, 8)
            
            drop = {
                'x': x,
                'y': y,
                'length': length,
                'speed': speed,
                'id': self.effects_canvas.create_line(
                    x, y, x, y + length,
                    fill='#4682B4', width=2, tags="rain"  # 钢蓝色
                )
            }
            self.rain_drops.append(drop)
    
    def animate_rain(self):
        """雨滴动画"""
        if not self.effects_running or self.current_weather_type != 'rainy':
            return
        
        for drop in self.rain_drops[:]:
            # 移动雨滴
            drop['y'] += drop['speed']
            
            # 更新雨滴位置
            self.effects_canvas.coords(
                drop['id'],
                drop['x'], drop['y'],
                drop['x'], drop['y'] + drop['length']
            )
            
            # 如果雨滴超出屏幕，重新生成
            if drop['y'] > 700:
                self.effects_canvas.delete(drop['id'])
                self.rain_drops.remove(drop)
                
                # 创建新的雨滴
                x = random.randint(0, 800)
                y = random.randint(-100, -50)
                length = random.randint(10, 20)
                speed = random.randint(3, 8)
                
                new_drop = {
                    'x': x,
                    'y': y,
                    'length': length,
                    'speed': speed,
                    'id': self.effects_canvas.create_line(
                        x, y, x, y + length,
                        fill='#4682B4', width=2, tags="rain"  # 钢蓝色
                    )
                }
                self.rain_drops.append(new_drop)
        
        self.root.after(50, self.animate_rain)
    
    def create_snow_effect(self):
        """创建雪花特效"""
        for _ in range(30):
            x = random.randint(0, 800)
            y = random.randint(-50, 0)
            size = random.randint(3, 8)
            speed = random.randint(1, 3)
            drift = random.uniform(-1, 1)
            
            flake = {
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'drift': drift,
                'id': self.effects_canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill='white', outline='white', tags="snow"
                )
            }
            self.snow_flakes.append(flake)
    
    def animate_snow(self):
        """雪花动画"""
        if not self.effects_running or self.current_weather_type != 'snowy':
            return
        
        for flake in self.snow_flakes[:]:
            # 移动雪花
            flake['y'] += flake['speed']
            flake['x'] += flake['drift']
            
            # 更新雪花位置
            self.effects_canvas.coords(
                flake['id'],
                flake['x'] - flake['size'], flake['y'] - flake['size'],
                flake['x'] + flake['size'], flake['y'] + flake['size']
            )
            
            # 如果雪花超出屏幕，重新生成
            if flake['y'] > 700 or flake['x'] < -10 or flake['x'] > 810:
                self.effects_canvas.delete(flake['id'])
                self.snow_flakes.remove(flake)
                
                # 创建新的雪花
                x = random.randint(0, 800)
                y = random.randint(-50, -10)
                size = random.randint(3, 8)
                speed = random.randint(1, 3)
                drift = random.uniform(-1, 1)
                
                new_flake = {
                    'x': x,
                    'y': y,
                    'size': size,
                    'speed': speed,
                    'drift': drift,
                    'id': self.effects_canvas.create_oval(
                        x - size, y - size, x + size, y + size,
                        fill='white', outline='white', tags="snow"
                    )
                }
                self.snow_flakes.append(new_flake)
        
        self.root.after(100, self.animate_snow)
    
    def create_fog_effect(self):
        """创建雾霾效果"""
        # 创建半透明覆盖层
        self.effects_canvas.create_rectangle(
            0, 0, 800, 700,
            fill='lightgray', stipple='gray50', tags="fog"
        )
        
        # 添加一些浮动的雾团
        for _ in range(5):
            x = random.randint(0, 800)
            y = random.randint(0, 700)
            size = random.randint(50, 100)
            self.effects_canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill='lightgray', stipple='gray25', tags="fog"
            )
    
    def change_background_color(self, weather_type):
        """根据天气类型改变背景颜色"""
        color_map = {
            'sunny': '#87CEEB',      # 天蓝色
            'rainy': '#708090',      # 石板灰
            'snowy': '#F0F8FF',      # 爱丽丝蓝
            'cloudy': '#D3D3D3',     # 浅灰色
            'default': '#87CEEB'     # 默认天蓝色
        }
        
        new_color = color_map.get(weather_type, '#87CEEB')
        self.root.configure(bg=new_color)
        self.effects_canvas.configure(bg=new_color)
        
        # 更新所有组件的背景色
        for widget in [self.info_frame, self.weather_frame, self.control_frame]:
            widget.configure(bg=new_color)
        
        for widget in [self.date_label, self.temp_label, self.weather_icon, self.weather_desc, self.auto_check]:
            widget.configure(bg=new_color)
    
    def start_weather_effects(self, weather_type):
        """启动天气特效"""
        self.clear_effects()
        self.current_weather_type = weather_type
        self.effects_running = True
        
        # 改变背景颜色
        self.change_background_color(weather_type)
        
        if weather_type == 'sunny':
            self.create_sun_rays()
            self.animate_sun_rays()
        elif weather_type == 'rainy':
            self.create_rain_effect()
            self.animate_rain()
        elif weather_type == 'snowy':
            self.create_snow_effect()
            self.animate_snow()
        elif weather_type == 'cloudy':
            self.create_fog_effect()
    
    def update_display(self):
        """更新显示内容"""
        if self.current_index < len(self.weather_data):
            row = self.weather_data.iloc[self.current_index]
            
            # 更新日期
            date_str = str(row['date'])
            self.date_label.config(text=f"Date: {date_str}")
            
            # 更新温度
            high_temp = row['high']
            low_temp = row['low']
            self.temp_label.config(text=f"Highest Temperature: {high_temp}°C  Lowest Temperature: {low_temp}°C")
            
            # 更新天气图标和描述
            weather_text = str(row['weather'])
            icon = self.get_weather_icon(weather_text)
            english_weather = self.translate_weather_to_english(weather_text)
            self.weather_icon.config(text=icon)
            self.weather_desc.config(text=english_weather)
            
            # 启动对应的天气特效
            weather_type = self.get_weather_type(weather_text)
            self.start_weather_effects(weather_type)
    
    def next_day(self):
        """显示下一天"""
        if self.current_index < len(self.weather_data) - 1:
            self.current_index += 1
            self.update_display()
    
    def prev_day(self):
        """显示前一天"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
    
    def auto_update(self):
        """自动更新到下一日"""
        if self.auto_update_var.get():
            self.next_day()
            # 如果到达最后一天，重新开始
            if self.current_index >= len(self.weather_data) - 1:
                self.current_index = 0
    
    def start_auto_update(self):
        """启动自动更新线程"""
        def update_loop():
            while True:
                time.sleep(3)  # 每3秒更新一次
                if self.auto_update_var.get():
                    self.root.after(0, self.auto_update)
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WeatherDisplay()
    app.run()
