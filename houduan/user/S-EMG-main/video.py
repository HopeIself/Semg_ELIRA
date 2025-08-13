# video_player.py
import os
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

class VideoPlayer:
    def __init__(self, title="视频播放器"):
        """初始化视频播放器"""
        self.title = title
        self.window = None
        self.canvas = None
        self.video = None
        self.is_playing = False
        self.delay = 15  # ms
        self._play_thread = None
        self._stop_event = threading.Event()
    
    def play(self, video_path, width=None, height=None):
        """
        播放视频
        
        参数:
        video_path: 视频文件路径
        width: 窗口宽度 (可选)
        height: 窗口高度 (可选)
        """
        if not os.path.exists(video_path):
            print(f"错误: 找不到视频文件 '{video_path}'")
            return False
        
        # 停止任何正在播放的视频
        self.stop()
        
        # 创建视频捕获对象
        self.video = cv2.VideoCapture(video_path)
        if not self.video.isOpened():
            print(f"错误: 无法打开视频文件 '{video_path}'")
            return False
        
        # 获取视频尺寸
        video_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 使用指定尺寸或原始视频尺寸
        self.width = width if width else video_width
        self.height = height if height else video_height
        
        # 创建或重置窗口
        self._create_window()
        
        # 在单独的线程中播放视频
        self._stop_event.clear()
        self.is_playing = True
        self._play_thread = threading.Thread(target=self._play_video)
        self._play_thread.daemon = True
        self._play_thread.start()
        
        return True
    
    def stop(self):
        """停止视频播放"""
        if self.is_playing:
            self._stop_event.set()
            if self._play_thread:
                self._play_thread.join(timeout=1.0)
            self.is_playing = False
        
        if self.video is not None:
            self.video.release()
            self.video = None
    
    def close(self):
        """关闭视频播放器"""
        self.stop()
        if self.window:
            self.window.destroy()
            self.window = None
    
    def _create_window(self):
        """创建或重置窗口"""
        if self.window is None:
            self.window = tk.Tk()
            self.window.title(self.title)
            self.window.protocol("WM_DELETE_WINDOW", self.close)
            
            # 创建Canvas来显示视频
            self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
            self.canvas.pack()
            
            # 添加控制按钮
            btn_frame = tk.Frame(self.window)
            btn_frame.pack(fill=tk.X, expand=True)
            
            stop_btn = tk.Button(btn_frame, text="停止", command=self.stop)
            stop_btn.pack(side=tk.LEFT, padx=10, pady=5)
            
            close_btn = tk.Button(btn_frame, text="关闭", command=self.close)
            close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        else:
            # 重置窗口大小
            self.window.title(self.title)
            self.canvas.config(width=self.width, height=self.height)
    
    def _play_video(self):
        """在单独的线程中播放视频"""
        try:
            while self.is_playing and not self._stop_event.is_set():
                ret, frame = self.video.read()
                if not ret:
                    # 视频结束
                    break
                
                # 调整帧大小
                frame = cv2.resize(frame, (self.width, self.height))
                
                # 将BGR转换为RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 转换为PhotoImage
                image = Image.fromarray(rgb_frame)
                photo = ImageTk.PhotoImage(image=image)
                
                # 在主线程中更新UI
                self.window.after(0, self._update_canvas, photo)
                
                # 控制帧率
                time.sleep(self.delay / 1000)
                
            # 播放结束
            if not self._stop_event.is_set():
                self.window.after(0, self._on_video_end)
                
        except Exception as e:
            print(f"播放视频时出错: {str(e)}")
            self.window.after(0, self._show_error, str(e))
    
    def _update_canvas(self, photo):
        """更新画布上的图像"""
        if self.canvas and self.is_playing:
            # 保持引用以防止垃圾回收
            self.photo = photo
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    
    def _on_video_end(self):
        """视频播放结束时调用"""
        self.is_playing = False
        if self.video:
            self.video.release()
            self.video = None
        messagebox.showinfo("播放完成", "视频播放完成")
    
    def _show_error(self, message):
        """显示错误消息"""
        messagebox.showerror("错误", f"播放视频时出错: {message}")
        self.close()


# 简单接口函数 - 可以在main.py中直接调用
def play_video(video_path, width=None, height=None, title="视频播放器"):
    """
    播放视频的简单接口
    
    参数:
    video_path: 视频文件路径
    width: 窗口宽度 (可选)
    height: 窗口高度 (可选)
    title: 窗口标题 (可选)
    
    返回:
    VideoPlayer实例，可以使用stop()和close()方法
    """
    player = VideoPlayer(title)
    success = player.play(video_path, width, height)
    if not success:
        return None
    return player