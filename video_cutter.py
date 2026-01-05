import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import os
import threading
import ctypes
import time


class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("影片轉圖片工具 (Video to Images)")
        self.root.geometry("600x500")

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.root.columnconfigure(0, weight=1)
        for i in range(6):
            self.root.rowconfigure(i, weight=1)

        # 變數存儲
        self.video_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.name_prefix = tk.StringVar(value="")  # 新增：輸出檔名前綴
        self.mode = tk.StringVar(value="all")
        self.interval_seconds = tk.DoubleVar(value=1.0)
        self.is_processing = False

        # 執行控制
        self.pause_event = threading.Event()  # set=執行中, clear=暫停
        self.stop_event = threading.Event()
        self.pause_event.set()

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

        self.progress = ttk.Progressbar(frame_status, orient="horizontal", mode="determinate", maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", padx=10)

        # --- 區塊 5: 按鈕 ---
        self.btn_start = tk.Button(self.root, text="開始轉換", bg="#DDDDDD", font=("Arial", 12, "bold"), command=self.start_thread)
        self.btn_start.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # --- 區塊 6: 暫停 / 終止 ---
        frame_controls = tk.Frame(self.root)
        frame_controls.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
        frame_controls.columnconfigure(0, weight=1)
        frame_controls.columnconfigure(1, weight=1)

        self.btn_pause = tk.Button(frame_controls, text="暫停轉換", state="disabled", command=self.toggle_pause)
        self.btn_pause.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.btn_stop = tk.Button(frame_controls, text="終止轉換", state="disabled", command=self.stop_processing)
        self.btn_stop.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def toggle_pause(self):
        if not self.is_processing:
            return

        if self.pause_event.is_set():
            self.pause_event.clear()
            self.root.after(0, lambda: self.btn_pause.config(text="繼續轉換"))
            # 進度值保持不變，只更新文字
            current = float(self.progress["value"])
            self.update_status("已暫停（按『繼續轉換』繼續）", current)
        else:
            self.pause_event.set()
            self.root.after(0, lambda: self.btn_pause.config(text="暫停轉換"))
            current = float(self.progress["value"])
            self.update_status("繼續處理中...", current)

    def stop_processing(self):
        if not self.is_processing:
            return

        self.stop_event.set()
        self.pause_event.set()  # 若目前暫停中，解除暫停讓執行緒能結束
        self.root.after(0, lambda: self.btn_pause.config(state="disabled"))
        self.root.after(0, lambda: self.btn_stop.config(state="disabled"))
        current = float(self.progress["value"])
        self.update_status("正在終止...", current)

    def _wait_if_paused_or_stopped(self) -> bool:
        # 回傳 False 表示應該終止
        while not self.pause_event.is_set():
            if self.stop_event.is_set():
                return False
            time.sleep(0.05)
        return not self.stop_event.is_set()

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
        self.stop_event.clear()
        self.pause_event.set()
        self.update_status("開始處理...", 0)
        self.btn_start.config(state="disabled", text="處理中...")
        self.btn_pause.config(state="normal", text="暫停轉換")
        self.btn_stop.config(state="normal")
        threading.Thread(target=self.process_video, daemon=True).start()

    def process_video(self):
        video_path = self.video_path.get()
        output_folder = self.output_folder.get()
        mode = self.mode.get()
        name_prefix = self.name_prefix.get().strip()

        # 先嘗試用 metadata 取得總幀數；MKV/變動幀率影片常拿不到
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.finish_processing("無法開啟影片", error=True)
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            self.update_status("正在估算影片總幀數（MKV 常需要這一步）...", 0)
            total_frames = self.estimate_total_frames(video_path)
            if self.stop_event.is_set():
                self.finish_processing("已終止轉換。", final_progress=float(self.progress["value"]))
                return

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.finish_processing("無法開啟影片", error=True)
                return

            fps = cap.get(cv2.CAP_PROP_FPS)

        frame_step = 1
        if mode == "interval":
            seconds = self.interval_seconds.get()
            frame_step = int(fps * seconds)
            if frame_step < 1:
                frame_step = 1

        count = 0
        saved_count = 0

        # 進度更新節流：每 0.2 秒更新一次 UI（避免很久才跳一次）
        last_ui_update = 0.0

        while True:
            if not self._wait_if_paused_or_stopped():
                break

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

            count += 1

            now = time.time()
            if now - last_ui_update >= 0.2:
                progress_val = min(100.0, (count / total_frames) * 100.0) if total_frames else 0.0
                self.update_status(f"已儲存 {saved_count} 張圖片...", progress_val)
                last_ui_update = now

        cap.release()
        if self.stop_event.is_set():
            final_progress = min(100.0, (count / total_frames) * 100.0) if total_frames else float(self.progress["value"])
            self.finish_processing("已終止轉換。", final_progress=final_progress)
        else:
            self.finish_processing(f"完成！共輸出 {saved_count} 張圖片。")

    def estimate_total_frames(self, video_path: str):
        # 用 grab() 只前進不解碼，通常比 read() 快，適合拿不到 FRAME_COUNT 的格式
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        scanned = 0
        last_status = 0.0
        while True:
            if not self._wait_if_paused_or_stopped():
                break

            ok = cap.grab()
            if not ok:
                break

            scanned += 1
            now = time.time()
            if now - last_status >= 0.5:
                self.update_status(f"正在估算總幀數... 已掃描 {scanned} 幀", 0)
                last_status = now

        cap.release()
        return scanned if scanned > 0 else None

    def update_status(self, text, progress_val):
        # 將 UI 更新排回主執行緒，避免在背景執行緒觸控 Tk widget
        self.root.after(0, self._apply_status, text, progress_val)

    def _apply_status(self, text, progress_val):
        self.status_label.config(text=text)
        self.progress["value"] = progress_val

    def finish_processing(self, message, error=False, final_progress=100):
        # 同樣用 after 讓收尾 UI 更新在主執行緒進行
        self.root.after(0, self._apply_finish, message, error, final_progress)

    def _apply_finish(self, message, error=False, final_progress=100):
        self.is_processing = False
        self.btn_start.config(state="normal", text="開始轉換")
        self.btn_pause.config(state="disabled", text="暫停轉換")
        self.btn_stop.config(state="disabled")
        self.progress["value"] = final_progress
        self.status_label.config(text=message, fg="red" if error else "green")
        if error:
            messagebox.showerror("錯誤", message)
        else:
            messagebox.showinfo("成功", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()
