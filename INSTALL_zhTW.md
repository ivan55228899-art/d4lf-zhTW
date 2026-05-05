# 在 Windows 上建置繁中版 d4lf.exe

## 前置需求

1. **Python 3.14** (d4lf 要求)
   - 從 https://www.python.org/downloads/ 下載安裝
   - 安裝時勾選「Add Python to PATH」

2. **Visual Studio Build Tools 2022**(編譯部分相依套件需要)
   - 從 https://visualstudio.microsoft.com/visual-cpp-build-tools/ 下載
   - 安裝時勾選:
     - 「使用 C++ 的桌面開發」
     - 「Windows 11 SDK」(或 10,看你的系統)

3. **uv** (Python 套件管理器,d4lf 用這個)
   ```powershell
   winget install --id=astral-sh.uv -e
   ```

## 建置步驟

### 1. 解壓本 zip 到一個資料夾,例如 `C:\code\d4lf-zhTW`

### 2. 開啟 PowerShell,進入該資料夾
```powershell
cd C:\code\d4lf-zhTW
```

### 3. 安裝相依套件
```powershell
uv sync
```
這會建立虛擬環境並安裝所有相依套件,大約需要 1-3 分鐘。

### 4. 跑測試確認沒壞東西(可選但建議)
```powershell
uv run pytest tests/ -x
```

### 5. 建置可執行檔
```powershell
uv run python build.py
```
完成後會產生一個 `d4lf/` 資料夾,裡面有 `d4lf.exe` 和所有需要的資產檔。

### 6. 安裝到 Diablo IV

按原版 README 的步驟做:
1. 把 `d4lf/saapi64.dll` 複製到 Diablo IV 安裝目錄
2. 用 `sign_dll.ps1` 在本機簽署 DLL(Season 12 後必要)
3. 進入 D4,確認所有遊戲設定都正確(語言改繁中、進階道具資訊開啟、螢幕閱讀器開啟)

### 7. 啟動 d4lf 並設定繁中

第一次跑 `d4lf.exe` 時,GUI 會建立預設的 `params.ini`。關閉 d4lf,編輯這個檔:

```
位置: C:\Users\<你>\.d4lf\params.ini
```

在 `[general]` 區段加上(或修改):
```ini
[general]
language = zhTW
profiles = my_profile
...其他設定...
```

重新啟動 d4lf.exe,正常使用熱鍵(預設 F11)篩選。

## 疑難排解

### 「No module named 'XXX'」
通常是 `uv sync` 沒跑完整。重跑一次,確認虛擬環境啟用。

### 建置時 PyInstaller 報錯
通常是 Visual Studio Build Tools 沒裝齊。確認「使用 C++ 的桌面開發」工作負載已勾選。

### d4lf.exe 啟動就崩潰
- 看 `C:\Users\<你>\.d4lf\logs\` 底下的最新 log
- 若是 `language not supported`,代表 params.ini 改錯位置,確認在 `[general]` 區段下
- 若是其他 Python 錯誤,可能是某個 zhTW 字典格式有問題,開 issue 附上 log

### TTS 抓到的詞綴匹配不到
- 把 d4lf 的 log level 改成 `debug`
- 看 log 裡出現的原始 TTS 字串
- 在 `assets/lang/zhTW/affixes.json` 確認該詞綴的 value 是不是跟 TTS 字串一致
- 不一致就改 value 並回報 issue,我會修正

### 想驗證繁中字典正確性(測試指令)
```powershell
uv run python -c "
import json
d = json.load(open('assets/lang/zhTW/affixes.json'))
print('總詞綴數:', len(d))
for k in ['attack_speed','maximum_life','movement_speed','damage_reduction']:
    print(f'  {k} -> {d.get(k)}')"
```
應看到中文 value(攻擊速度、生命值上限、移動速度、傷害減免)。

## 未來更新

當 D4 發新賽季加新詞綴/裝備時:

```powershell
cd <D4Companion 路徑>
git pull

cd C:\code\d4lf-zhTW
uv run python -m src.tools.gen_data_zhTW <D4Companion 路徑>
uv run python build.py
```

字典會自動重新產生,exe 重新打包。
