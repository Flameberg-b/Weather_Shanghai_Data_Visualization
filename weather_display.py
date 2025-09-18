import tkinter as tk
from tkinter import ttk
import pandas as pd
from datetime import datetime, timedelta
import threading
import time

class WeatherDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shanghai Weather Display")
        self.root.geometry("600x600")
        self.root.configure(bg='lightblue')
        
        # 读取CSV数据
        self.weather_data = self.load_weather_data()
        self.current_index = 0
        
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
        # 日期和温度显示区域（左上角）
        self.info_frame = tk.Frame(self.root, bg='lightblue')
        self.info_frame.pack(anchor='nw', padx=20, pady=20)
        
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
        self.weather_frame = tk.Frame(self.root, bg='lightblue')
        self.weather_frame.pack(expand=True, fill='both')
        
        self.weather_icon = tk.Label(self.weather_frame,
                                   font=('Arial', 80),
                                   bg='lightblue',
                                   fg='orange')
        self.weather_icon.pack(expand=True)
        
        # 天气描述
        self.weather_desc = tk.Label(self.weather_frame,
                                   font=('Arial', 16),
                                   bg='lightblue',
                                   fg='darkgreen')
        self.weather_desc.pack()
        
        # 控制按钮
        self.control_frame = tk.Frame(self.root, bg='lightblue')
        self.control_frame.pack(pady=10)
        
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
        else:
            return '🌤️'  # 默认图标
    
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
