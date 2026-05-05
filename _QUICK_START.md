# 給 Ivan 的快速啟動指南

整個 fork 已經做完且自動化完成,你只需要做**一件事**讓它上線:

## 一句話版本

```powershell
cd d4lf-zhTW-fork
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

跑這一行,腳本會自動幫你做:

1. ✓ 檢查並安裝 GitHub CLI(`gh`)
2. ✓ 登入 GitHub
3. ✓ 在你的帳號下建立 `d4lf-zhTW` repo
4. ✓ git init / commit / push 全部代碼
5. ✓ 自動開啟 Actions 寫權限
6. ✓ 觸發第一次 build(force release)
7. ✓ 開啟 Actions 頁面追蹤進度
8. ✓ Build 完成後開啟 Releases 頁面

預計總時長 **10-15 分鐘**(其中 8-12 分鐘是 GitHub 在 Windows runner 上跑 PyInstaller)。

## 跑完之後

你會有:

- **`https://github.com/<你>/d4lf-zhTW`** — 你自己的 fork
- **`Releases`** 第一筆 `v8.4.2-zh.1` 含 `d4lf_zhTW_v8.4.2-zh.1.zip`
- **每天 UTC 03:00** 自動同步上游 + D4Companion + 發新 release
- **d4lf.exe 內建更新檢查** 會從你的 fork 拉新版

## 從 Release 安裝到電腦上

腳本跑完後:

1. 從你的 Releases 頁面下載 `d4lf_zhTW_*.zip`
2. 解壓到 `C:\d4lf` 之類的地方
3. 把 `saapi64.dll` 複製到 `<D4 安裝目錄>`(通常是 `C:\Program Files (x86)\Diablo IV`)
4. 在 PowerShell 跑 `cd <D4 安裝目錄>; .\sign_dll.ps1`(需要管理員)
5. 開 D4 → 設定 → 語言 → 繁體中文
6. D4 設定 → 進階道具資訊 ✓、螢幕閱讀器 ✓、第三方螢幕閱讀器 ✓、邊框視窗 ✓
7. 跑 `d4lf.exe`,F11 切換篩選

## 之後完全不用碰

新賽季加詞綴?自動更新。
上游 d4lf 改架構?自動 merge(衝突時跳過繼續發版)。
D4Companion 補翻譯?自動同步。

唯一要你介入的情況:**上游做了會破壞 zhTW 字典的大改動**(罕見)。屆時去 `Actions` 頁面看 log,通常修一下 `gen_data_zhTW.py` 就好。

## 不想用 PowerShell?

WSL / Git Bash / Mac:
```bash
cd d4lf-zhTW-fork
bash setup.sh
```

## 手動模式(不想用腳本)

照 [`AUTO_UPDATE_SETUP.md`](AUTO_UPDATE_SETUP.md) 的步驟做。約 5 分鐘手動完成。

## 我建議的命名

如果你想讓其他繁中玩家也能用,repo 命名 `d4lf-zhTW` 最直觀。
若想低調自用,可以改成 `d4lf-fork` 之類的:
```powershell
PowerShell -ExecutionPolicy Bypass -File setup.ps1 -RepoName "d4lf-fork" -Visibility "private"
```

---

剩下的事情就是等 D4 開新賽季,然後享受不用記英文詞綴的爽感。
