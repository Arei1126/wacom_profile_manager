# Wacom Profile Manager

Linux環境におけるWacomタブレットの設定（マッピング、動作モード、アスペクト比維持）を管理・同期するためのツールです。
スタイラスペンと消しゴムの両方を自動検出し、一括で設定を適用します。

GUIとCUIの両方に対応しており、好みの環境で使用可能です。

## 特徴 (Features)

* **デバイス同期**: ペン先 (Stylus) と消しゴム (Eraser) を自動検出し、設定を一括適用。
* **プロファイル管理**: よく使う設定（例: 「お絵描き用」「ブラウジング用」）を名前を付けて保存・切り替え可能。
* **アスペクト比維持**: モニターとタブレットの比率を計算し、描画エリアを自動調整。
* **デュアルI/F**: 
    * **GUI**: Tkinterを使用したシンプルでミニマムな操作画面。
    * **CUI**: ターミナルから素早く設定可能なCLIモード。

## 必要要件 (Requirements)

* Python 3.x
* `xsetwacom` (Wacomドライバ)
* `xrandr` (ディスプレイ情報取得用)
* `tkinter` (GUIを使用する場合 / 通常はPythonに含まれています)

## インストール (Installation)

リポジトリをクローンするか、ファイルを任意のディレクトリに配置してください。

```bash
# 実行権限の付与
chmod +x wacom_gui.py wacom_logic.py

## 使い方 (Usage)

1. GUIモード (推奨)
視覚的に設定を確認しながら操作できます。


実行コマンド:
./wacom_gui.py
または
python3 wacom_gui.py

主な機能:
- Profile: 保存済みの設定を選択、または直接入力して新規作成。
- Detected Devices: 認識されているデバイスと接続状況を表示。
- Settings: モニター選択、モード（絶対/相対）、アスペクト比維持を設定。
- Save Profile: 現在の設定をプロファイル名（コンボボックスの値）で保存。
- Apply: 設定を即時適用。

2. CUIモード
GUI環境がない場合や、ターミナルからサクッと設定したい場合に使用します。

実行コマンド:
./wacom_logic.py
または
python3 wacom_logic.py

対話形式のウィザードに従って設定を行うか、保存済みのプロファイル番号を選択してください。

ファイル構成 (File Structure)

- wacom_gui.py: GUIアプリケーションのエントリーポイント。
- wacom_logic.py: 設定適用、デバイス検出、ファイル保存などのロジック部分（兼CLIツール）。
- ~/.wacom_profiles.json: プロファイルデータが保存されるファイル（自動生成）。

License

MIT License
