import tkinter as tk
from tkinter import simpledialog
import json
import os
import glob

# パス - カレントディレクトリからの相対パス
base_dir = "."
json_input_dir = "json_input"
output_dir = "cookies"

# 出力ディレクトリが存在しない場合は作成する
os.makedirs(output_dir, exist_ok=True)

# 入力ディレクトリ内のすべてのJSONファイルを探す
json_files = glob.glob(os.path.join(json_input_dir, "*.json"))

if not json_files:
    print(f"No JSON files found in: {json_input_dir}")
else:
    print(f"Found {len(json_files)} JSON files. Starting conversion...")

for json_path in json_files:
    try:
        filename = os.path.basename(json_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        # cookies.jsonに特別な処理が必要かチェックする
        if filename.lower() == "cookies.json":
            print("Found cookies.json. Requesting new filename...")
            root = tk.Tk()
            root.withdraw() # メインウィンドウを非表示にする
            
            # ダイアログを最前面に表示する（ハック的だがしばしば必要）
            root.attributes("-topmost", True)
            
            new_name = simpledialog.askstring("Rename Cookie", "Enter a name for this cookie file (without .txt):", parent=root)
            root.destroy()
            
            if not new_name:
                print(" -> Skipped: No name entered.")
                continue
                
            name_without_ext = new_name
            # ファイル名をサニタイズする（基本的）
            name_without_ext = "".join(c for c in name_without_ext if c.isalnum() or c in (' ', '.', '_', '-')).strip()
            if not name_without_ext:
                 print(" -> Skipped: Invalid name.")
                 continue

        txt_path = os.path.join(output_dir, f"{name_without_ext}.txt")

        print(f"Processing: {filename}")

        with open(json_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# Converted from JSON for gallery-dl\n\n")

            for c in cookies:
                domain = c.get("domain", "")
                # hostOnly: False -> TRUE, True -> FALSE
                flag = "FALSE" if c.get("hostOnly", False) else "TRUE"
                path = c.get("path", "/")
                secure = "TRUE" if c.get("secure", False) else "FALSE"
                # expiry or expirationDate, default 0
                expiration = str(int(c.get("expiry") or c.get("expirationDate") or 0))
                name = c.get("name", "")
                value = c.get("value", "")
                
                # Netscape形式で書き込む（7列、タブ区切り）
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")

        print(f" -> Converted to: {txt_path}")
        
        # 元のJSONファイルを削除する
        os.remove(json_path)
        print(f" -> Deleted: {json_path}")

    except Exception as e:
        print(f"Error processing {json_path}: {e}")

print("\nAll operations completed.")
