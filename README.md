# d4lf 繁體中文版 (Traditional Chinese Fork)

[d4lfteam/d4lf](https://github.com/d4lfteam/d4lf) 的繁體中文支援分支,讓 Diablo IV 設成繁中也能用 d4lf 自動篩選裝備。

> 原版 README(英文)請看 [README_upstream.md](README_upstream.md)

## 是什麼

d4lf 是 Diablo IV 的自動裝備篩選器——你定義篩選規則(YAML),它在你開箱時用熱鍵把裝備標星 / 標垃圾 / 自動移到倉庫。**不用 OCR**,而是透過遊戲的 TTS 螢幕閱讀器介面取得文字,速度快又準確。

原版只支援英文。本 fork 補上**完整繁中字典**(889 個詞綴 / 488 個傳奇詞綴 / 293 個傳奇裝備 / 332 個封印),資料來自 [D4Companion](https://github.com/josdemmers/Diablo4Companion) 的官方 Blizzard 萃取資料,翻譯與遊戲內顯示**一字不差**。

## 快速開始

### 下載
從 **[Releases](../../releases/latest)** 下載最新的 `d4lf_zhTW_*.zip`,解壓到任意資料夾。

### 安裝
1. 把 `saapi64.dll` 複製到 Diablo IV 安裝目錄
2. PowerShell 跑 `.\sign_dll.ps1`(Season 12 後必要)
3. **D4 客戶端設成繁體中文**
4. 遊戲設定:進階道具資訊 ✓、螢幕閱讀器 ✓、第三方螢幕閱讀器 ✓、邊框視窗模式
5. 跑 `d4lf.exe`

詳細設定見 [INSTALL_zhTW.md](INSTALL_zhTW.md)。

### 寫篩選規則

YAML profile **用英文 key**,所以**跟原版相容**——你在 [Maxroll](https://maxroll.gg)、[Mobalytics](https://mobalytics.gg)、[D4Builds](https://d4builds.gg) 匯入的 build 直接就能用,不用翻譯。

範例 `~/.d4lf/profiles/my_filter.yaml`:
```yaml
Affixes:
  - Sorcerer:
      affixPool:
        - [intelligence, 8]
        - [maximum_life, 800]
        - [movement_speed, 12]
      itemType: [helm, chest, legs]
      minPower: 800
      minGreaterAffixCount: 2
```

執行時 d4lf 會在繁中遊戲畫面看到「智力 +8」「生命值上限 +800」「移動速度 +12」並正確匹配。

## ✨ 自動更新

每天 UTC 03:00 (台北 11:00) GitHub Actions 自動檢查 d4lfteam/d4lf 與 D4Companion 是否有更新,有就重產字典 + 編譯 + 發 release。

d4lf.exe 內建的更新通知會從**本 repo** 拉新版(不是上游英文版),啟動 `autoupdater.bat` 就升級到最新繁中版。

## 字典覆蓋率

| 類型 | 數量 | 來源 |
|---|---|---|
| Affixes 詞綴 | 889 | D4Companion(IdSno 比對) |
| Aspects 傳奇詞綴 | 488 | D4Companion |
| Uniques 傳奇 | 293 | D4Companion |
| Sigils 封印 | 332 | D4Companion |
| Item Types | 33 | 手工對照官方繁中 |
| Tributes 貢品 | 24 | 手工(D4Companion 未收錄) |

## 自己維護一份

從零到有 5 分鐘設定好自動化,完整流程見 [AUTO_UPDATE_SETUP.md](AUTO_UPDATE_SETUP.md)。

## 已知限制

- Tributes 是手工列表,只放主要 24 個。實玩遇到不認得的請開 issue
- D4Companion 的繁中資料偶有 4 個英文佔位符(尚未本地化的新內容),這些自動跳過
- D4 客戶端**必須設成繁中**(不是英文+裝中文 mod)

## 授權與致謝

MIT License,跟上游一致。

- 原版 d4lf:[d4lfteam](https://github.com/d4lfteam/d4lf) ❤️
- 繁中資料:[D4Companion](https://github.com/josdemmers/Diablo4Companion) by josdemmers
- 本 fork:不為盈利,純粹讓繁中玩家也能爽用

## 回報問題

- 繁中匹配 / 字典問題 → 開本 repo 的 [Issues](../../issues)
- d4lf 本身的功能 / bug → 去 [上游](https://github.com/d4lfteam/d4lf/issues)
