#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import wacom_logic as model

class WacomApp(tk.Tk):
        def __init__(self):
                super().__init__()
                self.title("Wacom Sync GUI")
                self.geometry("450x480")

                # テーマ設定 (モダンでミニマムな 'clam' を採用)
                style = ttk.Style()
                try:
                    pass
                    #style.theme_use('clam')
                except:
                        pass 

                self.manager = model.WacomManager()
                self.profiles = model.ConfigManager.load_profiles()
                
                self._create_widgets()
                self._load_initial_state()

        def _create_widgets(self):
                # --- 1. Profile Selector (Editable for "Save As") ---
                frame_top = ttk.LabelFrame(self, text="Profile", padding=10)
                frame_top.pack(fill="x", padx=10, pady=5)
                
                # ★変更点: state="normal" にして、手入力で新規作成できるようにしたよ！
                self.combo_profile = ttk.Combobox(frame_top, state="normal")
                self.combo_profile.pack(fill="x")
                self.combo_profile.bind("<<ComboboxSelected>>", self._on_profile_select)

                # --- 2. Device Info ---
                frame_dev = ttk.LabelFrame(self, text="Detected Devices", padding=10)
                frame_dev.pack(fill="x", padx=10, pady=5)
                
                frame_dev_header = ttk.Frame(frame_dev)
                # 前回のバグ修正済み (mb=5 -> pady=(0, 5))
                frame_dev_header.pack(fill="x", pady=(0, 5))
                
                ttk.Label(frame_dev_header, text="Sync Targets:").pack(side="left")
                
                # 🔄 リロードボタン
                btn_refresh = ttk.Button(frame_dev_header, text="↻ Scan", width=8, command=self._refresh_hardware_info)
                btn_refresh.pack(side="right")

                # デバイスリスト
                self.list_devices = tk.Listbox(frame_dev, height=3, bg="white", selectmode="none", activestyle="none", relief="flat", borderwidth=1)
                self.list_devices.pack(fill="x")
                self._update_device_list_ui()

                # --- 3. Settings Area ---
                frame_settings = ttk.LabelFrame(self, text="Settings", padding=10)
                frame_settings.pack(fill="both", expand=True, padx=10, pady=5)

                # Monitor
                ttk.Label(frame_settings, text="Target Monitor:").grid(row=0, column=0, sticky="w", pady=5)
                self.var_target = tk.StringVar()
                self.combo_target = ttk.Combobox(frame_settings, textvariable=self.var_target, state="readonly")
                self.combo_target.grid(row=0, column=1, sticky="ew", padx=5)
                self._update_monitor_list_ui()

                # Mode
                ttk.Label(frame_settings, text="Mode:").grid(row=1, column=0, sticky="w", pady=5)
                frame_mode = ttk.Frame(frame_settings)
                frame_mode.grid(row=1, column=1, sticky="w")
                self.var_mode = tk.StringVar(value="Absolute")
                ttk.Radiobutton(frame_mode, text="Absolute", variable=self.var_mode, value="Absolute").pack(side="left")
                ttk.Radiobutton(frame_mode, text="Relative", variable=self.var_mode, value="Relative").pack(side="left", padx=10)

                # Ratio
                self.var_ratio = tk.BooleanVar()
                ttk.Checkbutton(frame_settings, text="Keep Aspect Ratio", variable=self.var_ratio).grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

                # --- 4. Actions ---
                frame_actions = ttk.Frame(self, padding=10)
                frame_actions.pack(fill="x", side="bottom")
                frame_actions.columnconfigure(0, weight=1)
                frame_actions.columnconfigure(1, weight=1)

                ttk.Button(frame_actions, text="Save Profile", command=self._save_profile).grid(row=0, column=0, sticky="ew", padx=5)
                # ★変更点: ロケットアイコンをチェックマークに変更
                ttk.Button(frame_actions, text="✔ Apply", command=self._apply_settings).grid(row=0, column=1, sticky="ew", padx=5)

        def _load_initial_state(self):
                p_names = list(self.profiles.keys())
                self.combo_profile['values'] = p_names
                if p_names:
                        self.combo_profile.current(0)
                        self._on_profile_select(None)

        def _refresh_hardware_info(self):
                self.manager.refresh_hardware()
                self._update_device_list_ui()
                self._update_monitor_list_ui()
                messagebox.showinfo("Rescan", "Hardware info updated! ✨")

        def _update_device_list_ui(self):
                self.list_devices.delete(0, tk.END)
                if self.manager.devices:
                        for dev in self.manager.devices:
                                self.list_devices.insert(tk.END, f"🖊 {dev}")
                        self.list_devices.config(fg="black")
                else:
                        self.list_devices.insert(tk.END, "❌ No Devices Found")
                        self.list_devices.config(fg="red")

        def _update_monitor_list_ui(self):
                current = self.var_target.get()
                monitors = ["desktop"] + list(self.manager.monitors.keys())
                self.combo_target['values'] = monitors
                if current in monitors:
                        self.combo_target.set(current)
                else:
                        self.combo_target.set("desktop")

        def _on_profile_select(self, event):
                name = self.combo_profile.get()
                if name in self.profiles:
                        data = self.profiles[name]
                        self.var_target.set(data.get("target", "desktop"))
                        self.var_mode.set(data.get("mode", "Absolute"))
                        self.var_ratio.set(data.get("keep_ratio", False))

        def _apply_settings(self):
                current_data = {
                        "target": self.var_target.get(),
                        "mode": self.var_mode.get(),
                        "keep_ratio": self.var_ratio.get()
                }
                logs = self.manager.apply_settings(current_data)
                msg = "\n".join(logs)
                messagebox.showinfo("Result", msg)

        def _save_profile(self):
                # 入力ボックスの文字列を取得（手入力された新しい名前かもしれない）
                name = self.combo_profile.get().strip()
                if not name:
                        messagebox.showwarning("Warning", "Profile name cannot be empty!")
                        return

                data = {
                        "target": self.var_target.get(),
                        "mode": self.var_mode.get(),
                        "keep_ratio": self.var_ratio.get()
                }
                
                # Logic側で保存
                model.ConfigManager.save_profile(name, data)
                
                # リストを再読み込みして、新規追加された名前も含めて更新する
                self.profiles = model.ConfigManager.load_profiles()
                self.combo_profile['values'] = list(self.profiles.keys())
                self.combo_profile.set(name) # 今保存した名前を選択状態にする
                
                messagebox.showinfo("Saved", f"Profile '{name}' saved!")

if __name__ == "__main__":
        app = WacomApp()
        app.mainloop()
