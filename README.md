# Gallery-DL GUI

これは `gallery-dl` を簡単に利用するためのGUIツールです。
URLを入力してダウンロードしたり、ブラウザからエクスポートしたCookieを簡単に変換して利用したりできます。
モダンなダークテーマと使いやすいインターフェースを採用しています。

## フォルダ構成

```text
c:\software\Gallery-DL\
  ├── gallery_dl_gui.py      (メインのGUIツール)
  ├── convert_cookies.bat    (Cookie変換用バッチ)
  ├── cookies\               (変換後のCookieファイル置き場)
  └── json_input\            (JSON形式のCookieを入れる場所)
```

## 使い方

### 1. 落とすだけの場合

1. `gallery_dl_gui.py` を実行します（Python環境が必要です）。
2. URL欄にギャラリーのURLを入力します。
3. "Start Download" を押すとダウンロードが始まります。

### 2. Cookie を使う場合

1. **Cookieの準備**:
    - ブラウザの拡張機能（EditThisCookieなど）でCookieを **JSON形式** でエクスポートします。
    - その `.json` ファイルを `json_input` フォルダに入れます。
2. **変換**:
    - **GUIから**: `gallery_dl_gui.py` を起動し、"Convert" ボタンを押します。
    - **バッチから**: `convert_cookies.bat` をダブルクリックします。
    - **注意**: ファイル名が `cookies.json` の場合、新しい名前を入力する画面が出ます。
    - 変換が成功すると、`json_input` のファイルは消え、`cookies` フォルダに `.txt` ファイルが作成されます。
3. **ダウンロード**:
    - GUIで "Use Cookie" にチェックを入れます。
    - ドロップダウンリストから使いたいCookieファイルを選択します。
    - **Reloadボタン**: アプリ起動中に新しいCookieファイルを追加した場合、"Reload" ボタンを押すとリストが更新されます。
    - "Start Download" を押すと、`DownloadData` フォルダにダウンロードが始まります。
    - ファイルは `DownloadData/サイト名/詳細/ファイル名` の形式で保存されます。
    - **Stopボタン**: ダウンロードを途中で停止したい場合は "Stop" ボタンを押してください。

## 動作環境

- Windows

## ライセンス（サードパーティコンポーネント）

- 本ソフトウェアは以下のオープンソースソフトウェアを含んでいます。
- 各ライセンスの全文は同梱の LICENSE ファイルを参照してください。

### 1. Gallery-DL
- プロジェクト: Gallery-DL
- ライセンス: GNU GPL v3
- 公式リポジトリ: https://github.com/mikf/gallery-dl
- 本配布物には未改変のバイナリを含みます。
- ソースコードは上記公式リポジトリより入手可能です。

### 2. Python
- プロジェクト: Python
- ライセンス: Python Software Foundation License

### 3. OpenSSL
- プロジェクト: OpenSSL
- ライセンス: Apache License 2.0

- OpenSSLはApache License 2.0に基づいてライセンスされています。
- ライセンスのコピーは
- https://www.apache.org/licenses/LICENSE-2.0
- から入手できます。

### 4. zlib
- プロジェクト: zlib
- ライセンス: zlib License
- SQLiteはパブリックドメインです。https://www.sqlite.org/copyright.htmlをご覧ください。

### 5. Tcl/Tk
- プロジェクト: Tcl/Tk
- ライセンス: BSD-style License

### 6. SQLite
- プロジェクト: SQLite
- ライセンス: Public Domain

### 7. libffi
- プロジェクト: libffi
- ライセンス: MIT License

### 8. Zstandard (zstd)
- プロジェクト: Zstandard
- ライセンス: BSD 2-Clause License

### 9. certifi
- プロジェクト: certifi
- ライセンス: Mozilla Public License 2.0

### 10. charset-normalizer
- プロジェクト: charset-normalizer
- ライセンス: MIT License

### 11. setuptools
- プロジェクト: setuptools
- ライセンス: MIT License

---

- 本GUI部分のコードは MIT License の下で提供されています。

---

### GPLに関する注意

- このプログラムには、GNU General Public License v3に基づいてライセンスされたgallery-dlが含まれています。
- この配布物にはGPLv3ライセンスのコピーが含まれています。
- 対応する完全なソースコードは、公式リポジトリ
- （https://github.com/mikf/gallery-dl）
- から入手できます。

---

# Gallery-DL GUI (English)

This is a GUI tool for easy use of `gallery-dl`.
You can download content by entering a URL and easily convert cookies exported from your browser for use.
It features a modern dark theme and a user-friendly interface.

## Folder Structure

```text
c:\software\Gallery-DL\
  ├── gallery_dl_gui.py      (Main GUI tool)
  ├── convert_cookies.bat    (Batch file for cookie conversion)
  ├── cookies\               (Storage for converted cookie files)
  └── json_input\            (Location for JSON format cookies)
```

## Usage

### 1. Simple Download

1. Run `gallery_dl_gui.py` (requires Python environment).
2. Enter the gallery URL in the URL field.
3. Click "Start Download" to begin downloading.

### 2. Using Cookies

1. **Preparing Cookies**:
    - Export cookies in **JSON format** using a browser extension (e.g., EditThisCookie).
    - Place the `.json` file in the `json_input` folder.
2. **Conversion**:
    - **Via GUI**: Launch `gallery_dl_gui.py` and click the "Convert" button.
    - **Via Batch**: Double-click `convert_cookies.bat`.
    - **Note**: If the file is named `cookies.json`, a prompt will appear to enter a new name.
    - Upon successful conversion, the file in `json_input` will be removed, and a `.txt` file will be created in the `cookies` folder.
3. **Downloading**:
    - Check "Use Cookie" in the GUI.
    - Select the desired cookie file from the dropdown list.
    - **Reload Button**: If you add new cookie files while the app is running, click "Reload" to update the list.
    - Click "Start Download" to begin downloading to the `DownloadData` folder.
    - Files are saved in the format `DownloadData/site-name/details/filename`.
    - **Stop Button**: Click "Stop" to halt the download process.

## Requirements

- Windows

## Licenses (Third-party Components)

This software includes the following open-source software.
Please refer to the included LICENSE file for the full text of each license.

### 1. Gallery-DL
- Project: Gallery-DL
- License: GNU GPL v3
- Official repository: https://github.com/mikf/gallery-dl
- This distribution includes the unmodified binary.
- The source code is available from the official repository above.

### 2. Python
- Project: Python
- License: Python Software Foundation License

### 3. OpenSSL
- Project: OpenSSL
- License: Apache License 2.0

OpenSSL is licensed under the Apache License 2.0.
You may obtain a copy of the License at:
https://www.apache.org/licenses/LICENSE-2.0

### 4. zlib
- Project: zlib
- License: zlib License
- SQLite is in the public domain. See https://www.sqlite.org/copyright.html

### 5. Tcl/Tk
- Project: Tcl/Tk
- License: BSD-style License

### 6. SQLite
- Project: SQLite
- License: Public Domain

### 7. libffi
- Project: libffi
- License: MIT License

### 8. Zstandard (zstd)
- Project: Zstandard
- License: BSD 2-Clause License

### 9. certifi
- Project: certifi
- License: Mozilla Public License 2.0

### 10. charset-normalizer
- Project: charset-normalizer
- License: MIT License

### 11. setuptools
- Project: setuptools
- License: MIT License

---

- The code for the GUI portion is provided under the MIT License.

---

### GPL Notice

- This program includes gallery-dl, which is licensed under the GNU General Public License v3.
- A copy of the GPLv3 license is included in this distribution.
- The complete corresponding source code is available from the official repository:
- https://github.com/mikf/gallery-dl
