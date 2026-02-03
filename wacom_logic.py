#!/usr/bin/env python3
import subprocess
import json
import os

CONFIG_FILE = os.path.expanduser("~/.wacom_profiles.json")

class WacomManager:
        def __init__(self):
                self.refresh_hardware()

        def refresh_hardware(self):
                """
                デバイスとモニター情報を再取得してプロパティを更新する
                """
                self.devices = self._get_devices()
                self.monitors = self._get_monitors()
                return self.devices, self.monitors

        def _get_devices(self):
                try:
                        res = subprocess.check_output(["xsetwacom", "--list", "devices"]).decode("utf-8")
                        devices = []
                        for line in res.strip().split('\n'):
                                if "STYLUS" in line.upper() or "ERASER" in line.upper():
                                        dev_name = line.split('\t')[0].strip()
                                        devices.append(dev_name)
                        return devices
                except Exception:
                        return []

        def _get_monitors(self):
                monitors = {}
                try:
                        res = subprocess.check_output(["xrandr", "--listmonitors"]).decode("utf-8")
                        for line in res.splitlines():
                                if line.startswith("Monitors:"): continue
                                parts = line.split()
                                name = parts[-1]
                                res_str = parts[-2].split('+')[0]
                                w = int(res_str.split('x')[0].split('/')[0])
                                h = int(res_str.split('x')[1].split('/')[0])
                                monitors[name] = {'w': w, 'h': h}
                except Exception:
                        pass
                return monitors

        def apply_settings(self, profile):
                # (前回と同じなので省略。変更なし！)
                target = profile.get("target", "desktop")
                mode = profile.get("mode", "Absolute")
                keep_ratio = profile.get("keep_ratio", False)
                
                logs = []
                logs.append(f"🎯 Target: {target} | Mode: {mode} | Ratio: {keep_ratio}")

                for dev in self.devices:
                        try:
                                subprocess.run(["xsetwacom", "set", dev, "Mode", mode], check=True)
                                map_target = "desktop" if target == "desktop" else target
                                subprocess.run(["xsetwacom", "set", dev, "MapToOutput", map_target], check=True)
                                
                                if keep_ratio and target != "desktop" and target in self.monitors:
                                        self._apply_aspect_ratio(dev, target)
                                        logs.append(f"✅ {dev} (Ratio Fixed)")
                                elif not keep_ratio:
                                        subprocess.run(["xsetwacom", "set", dev, "ResetArea"])
                                        logs.append(f"✅ {dev} (Standard)")
                                else:
                                        logs.append(f"✅ {dev}")
                        except Exception as e:
                                logs.append(f"❌ {dev} Error: {e}")
                return logs

        def _apply_aspect_ratio(self, dev, target_monitor):
                # (前回と同じなので省略)
                area_out = subprocess.check_output(["xsetwacom", "get", dev, "Area"]).decode("utf-8").split()
                max_x = int(area_out[2])
                max_y = int(area_out[3])
                mon_w = self.monitors[target_monitor]['w']
                mon_h = self.monitors[target_monitor]['h']
                
                mon_ratio = mon_w / mon_h
                tab_ratio = max_x / max_y
                
                new_x, new_y = max_x, max_y
                if mon_ratio > tab_ratio:
                        new_y = int(max_x / mon_ratio)
                else:
                        new_x = int(max_y * mon_ratio)
                
                subprocess.run(["xsetwacom", "set", dev, "Area", "0", "0", str(new_x), str(new_y)])

class ConfigManager:
        # (前回と同じなので省略)
        @staticmethod
        def load_profiles():
                if not os.path.exists(CONFIG_FILE): return {}
                with open(CONFIG_FILE, 'r') as f: return json.load(f)

        @staticmethod
        def save_profile(name, data):
                profiles = ConfigManager.load_profiles()
                profiles[name] = data
                with open(CONFIG_FILE, 'w') as f: json.dump(profiles, f, indent=4)

# --- wacom_logic.py の末尾に追記してね ---

def main_cli():
    print("========================================")
    print("   Wacom Profile Manager (CLI Mode)     ")
    print("========================================")

    manager = WacomManager()
    if not manager.devices:
        print("❌ No Wacom devices found.")
        return

    print("🖊 Detected Devices:")
    for d in manager.devices:
        print(f"  - {d}")
    print("----------------------------------------")

    profiles = ConfigManager.load_profiles()
    
    # プロファイル選択
    if profiles:
        print("📂 Saved Profiles:")
        p_names = list(profiles.keys())
        for i, name in enumerate(p_names):
            print(f"  [{i+1}] {name}")
    else:
        print("📂 No saved profiles found.")
        p_names = []

    print("  [N] New Configuration / Quick Setup")
    
    choice = input("\n👉 Select option: ").strip()

    target_profile = {}

    # 既存プロファイルの選択
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(p_names):
            target_profile = profiles[p_names[idx]]
            print(f"\n🚀 Loading profile: {p_names[idx]}")
        else:
            print("❌ Invalid selection.")
            return
    # 新規設定
    else:
        print("\n🛠  Manual Setup")
        mon_list = list(manager.monitors.keys())
        print(f"Monitors: {mon_list}")
        t = input("Target (Enter for desktop): ").strip()
        target = t if t else "desktop"
        
        mode_in = input("Mode (A=Absolute/R=Relative): ").strip().lower()
        mode = "Relative" if mode_in == "r" else "Absolute"
        
        ratio_in = input("Keep Aspect Ratio? (y/n): ").strip().lower()
        keep_ratio = (ratio_in == "y")
        
        target_profile = {
            "target": target,
            "mode": mode,
            "keep_ratio": keep_ratio
        }

    # 適用処理
    print("\nApplying settings...")
    logs = manager.apply_settings(target_profile)
    for log in logs:
        print(log)
    
    # 新規の場合のみ保存を聞く
    if not choice.isdigit():
        save_q = input("\n💾 Save this configuration? (name/n): ").strip()
        if save_q and save_q.lower() != 'n':
            ConfigManager.save_profile(save_q, target_profile)
            print(f"Saved as '{save_q}'!")

    print("\n✨ Done!")

if __name__ == "__main__":
    main_cli()
