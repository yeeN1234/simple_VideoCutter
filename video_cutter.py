import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import os
import threading
import ctypes


class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("影片轉圖片工具 (Video to Images)")
        self.root.geometry("600x450")

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.root.columnconfigure(0, weight=1)
        for i in range(5):
            self.root.rowconfigure(i, weight=1)

        # 變數存儲
        self.video_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.name_prefix = tk.StringVar(value="")  # 新增：輸出檔名前綴
        self.mode = tk.StringVar(value="all")
        self.interval_seconds = tk.DoubleVar(value=1.0)
        self.is_processing = False

        self.create_widgets()

    def create_widgets(self):
        # --- 區塊 1: 選擇影片 ---
        frame_input = tk.LabelFrame(self.root, text="步驟 1: 輸入設定")
        frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        frame_input.columnconfigure(1, weight=1)

        tk.Label(frame_input, text="影片路徑:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        tk.Entry(frame_input, textvariable=self.video_path).grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        tk.Button(frame_input, text="瀏覽...", command=self.select_video).grid(row=0, column=2, padx=5, pady=10)

        # --- 區塊 2: 輸出設定 ---
        frame_output = tk.LabelFrame(self.root, text="步驟 2: 輸出設定")
        frame_output.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        frame_output.columnconfigure(1, weight=1)

        tk.Label(frame_output, text="輸出資料夾:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        tk.Entry(frame_output, textvariable=self.output_folder).grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        tk.Button(frame_output, text="瀏覽...", command=self.select_folder).grid(row=0, column=2, padx=5, pady=10)

        # 新增：輸出檔名前綴
        tk.Label(frame_output, text="輸出檔名前綴:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        tk.Entry(frame_output, textvariable=self.name_prefix).grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        tk.Label(frame_output, text="(例如: videoA → videoA_frame_00000.jpg)").grid(row=1, column=2, padx=5, pady=10, sticky="w")

        # --- 區塊 3: 切割選項 ---
        frame_opts = tk.LabelFrame(self.root, text="步驟 3: 切割模式")
        frame_opts.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        tk.Radiobutton(
            frame_opts,
            text="每一幀都輸出 (Frame by Frame)",
            variable=self.mode,
            value="all",
            command=self.toggle_interval_input,
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        sub_frame = tk.Frame(frame_opts)
        sub_frame.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        tk.Radiobutton(sub_frame, text="每隔", variable=self.mode, value="interval", command=self.toggle_interval_input).pack(side="left")
        self.entry_interval = tk.Entry(sub_frame, textvariable=self.interval_seconds, width=5, state="disabled")
        self.entry_interval.pack(side="left", padx=5)
        tk.Label(sub_frame, text="秒輸出一張").pack(side="left")

        # --- 區塊 4: 狀態與進度 ---
        frame_status = tk.Frame(self.root)
        frame_status.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        frame_status.columnconfigure(0, weight=1)

        self.status_label = tk.Label(frame_status, text="準備就緒", fg="blue")
        self.status_label.grid(row=0, column=0, pady=5)

        self.progress = ttk.Progressbar(frame_status, orient="horizontal", mode="determinate")
        self.progress.grid(row=1, column=0, sticky="ew", padx=10)

        # --- 區塊 5: 按鈕 ---
        self.btn_start = tk.Button(self.root, text="開始轉換", bg="#DDDDDD", font=("Arial", 12, "bold"), command=self.start_thread)
        self.btn_start.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

    def toggle_interval_input(self):
        if self.mode.get() == "interval":
            self.entry_interval.config(state="normal")
        else:
            self.entry_interval.config(state="disabled")

    def select_video(self):
        filename = filedialog.askopenfilename(title="選擇影片", filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.ts")])
        if filename:
            self.video_path.set(filename)
            # 可選：自動用影片檔名（不含副檔名）當作前綴
            self.name_prefix.set(os.path.splitext(os.path.basename(filename))[0])

    def select_folder(self):
        folder = filedialog.askdirectory(title="選擇輸出資料夾")
        if folder:
            self.output_folder.set(folder)

    def start_thread(self):
        # 1. 檢查程式是否正在跑
        if self.is_processing:
            return

        # 2. 檢查路徑
        if not os.path.exists(self.video_path.get()):
            messagebox.showerror("路徑錯誤", "找不到影片檔案，請檢查路徑！")
            return
        if not self.output_folder.get():
            messagebox.showerror("路徑錯誤", "請選擇輸出資料夾！")
            return

        # 3. 檢查數字輸入 (Try-Catch 防呆)
        if self.mode.get() == "interval":
            try:
                val = self.interval_seconds.get()
                if val <= 0:
                    messagebox.showwarning("數值錯誤", "間隔秒數必須大於 0！\n請重新輸入。")
                    return
            except tk.TclError:
                messagebox.showerror("輸入錯誤", "您輸入的不是數字！\n請輸入正確的秒數 (例如: 0.5, 1, 5)")
                return
            except Exception as e:
                messagebox.showerror("未知的錯誤", f"發生錯誤：{e}")
                return

        # 4. 驗證通過，開始執行
        self.is_processing = True
        self.btn_start.config(state="disabled", text="處理中...")
        threading.Thread(target=self.process_video, daemon=True).start()

    def process_video(self):
        video_path = self.video_path.get()
        output_folder = self.output_folder.get()
        mode = self.mode.get()
        name_prefix = self.name_prefix.get().strip()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.finish_processing("無法開啟影片", error=True)
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_step = 1
        if mode == "interval":
            seconds = self.interval_seconds.get()
            frame_step = int(fps * seconds)
            if frame_step < 1:
                frame_step = 1

        count = 0
        saved_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if count % frame_step == 0:
                if name_prefix:
                    filename = os.path.join(output_folder, f"{name_prefix}_frame_{saved_count:05d}.jpg")
                else:
                    filename = os.path.join(output_folder, f"frame_{saved_count:05d}.jpg")

                cv2.imwrite(filename, frame)
                saved_count += 1
                if saved_count % 10 == 0:
                    self.update_status(f"已儲存 {saved_count} 張圖片...", (count / total_frames) * 100)

            count += 1

        cap.release()
        self.finish_processing(f"完成！共輸出 {saved_count} 張圖片。")

    def update_status(self, text, progress_val):
        self.status_label.config(text=text)
        self.progress["value"] = progress_val

    def finish_processing(self, message, error=False):
        self.is_processing = False
        self.btn_start.config(state="normal", text="開始轉換")
        self.progress["value"] = 100
        self.status_label.config(text=message, fg="red" if error else "green")
        if error:
            messagebox.showerror("錯誤", message)
        else:
            messagebox.showinfo("成功", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()
