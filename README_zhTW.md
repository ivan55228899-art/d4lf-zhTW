# d4lf 繁體中文版 (zhTW Fork)

這是 [d4lfteam/d4lf](https://github.com/d4lfteam/d4lf) 的繁體中文支援分支。原版 d4lf 只支援英文,本分支讓你**遊戲與工具都用繁中**就能正常使用篩選器。

## 為什麼這樣做有效?

d4lf **不是用 OCR 讀畫面**——它透過 Diablo IV 的 TTS(螢幕閱讀器)介面 `saapi64.dll` 取得遊戲文字。資料字典在 `assets/lang/{語言}/*.json`,程式碼本來就有完整多語言架構,只是 validator 鎖在 `enUS`。

本分支做的事:
1. 解開 validator 限制,允許 `zhTW`
2. 從 [D4Companion](https://github.com/josdemmers/Diablo4Companion) 的官方繁中資料(Blizzard 萃取)產生完整的 `assets/lang/zhTW/` 字典
3. 修正 `closest_match` 讓 build planner 匯入(Maxroll/Mobalytics/D4Builds 都是英文)在繁中模式下也能用
4. **YAML profile 維持英文 key**(`attack_speed`、`maximum_life`),所以你的篩選檔可以跨語言移植

## 安裝步驟

### 1. 把 Diablo IV 設成繁體中文
Battle.net → Diablo IV → 齒輪 → 遊戲設定 → 語言 → **繁體中文**。

### 2. 設定遊戲內選項(同原版)
- **進階道具資訊**:選項 → 玩法 → **啟用**(這個沒開篩選器會壞掉)
- **使用螢幕閱讀器**:選項 → 輔助使用 → **啟用**
- **第三方螢幕閱讀器**:選項 → 輔助使用 → **啟用**
- 字型大小:小或中
- 關 HDR
- 邊框視窗模式(不要用獨佔全螢幕,否則 paragon overlay 失效)

### 3. 安裝 d4lf 本體
按原版 README 的「Installation and quick start guide」做完前置(下載 release、把 `saapi64.dll` 複製到 D4 目錄、用 `sign_dll.ps1` 簽 DLL)。

### 4. 套用繁中分支

**方案 A:直接用本分支的 release**(最簡單)
從本 fork 的 Releases 下載打包好的 zip,解壓蓋掉原版即可。

**方案 B:手動覆蓋資產檔**(用原版 d4lf release + 手動加繁中)
1. 把本 repo 的 `assets/lang/zhTW/` 整個資料夾複製到原版 d4lf 安裝目錄的 `assets/lang/` 底下
2. 編輯 `C:/Users/<你>/.d4lf/params.ini`,在 `[general]` 區段加上:
   ```ini
   language = zhTW
   ```
   原版 d4lf release 的 validator 會擋掉(`language not supported`),這時要改用本分支重新編譯,或是直接用方案 A。

### 5. 啟動 d4lf
跑 `d4lf.exe`,正常用熱鍵(預設 F11)篩選裝備。

## 字典來源與覆蓋率

| 檔案 | 來源 | 條目數 | 涵蓋率 |
|---|---|---|---|
| `affixes.json` | D4Companion zhTW(IdSno 比對) | 889 | 882 直譯 + 7 英文 fallback |
| `aspects.json` | D4Companion zhTW Name | 488 | ~99%(4 個未本地化的英文佔位符已濾掉) |
| `item_types.json` | 手工對照官方繁中用詞 | 33 | 100% |
| `sigils.json` | D4Companion zhTW Name | 332(地下城+詞綴) | 99%+ |
| `uniques.json` | D4Companion zhTW Name | 293 | ~98%(4 個英文佔位符濾掉) |
| `tributes.json` | 手工(D4Companion 沒收錄) | 24 | 主要的都有,**請實際遊玩驗證** |
| `tooltips.json` | 「物品力量」 | 1 | 待驗證 |
| `corrections.json` | 空模板 | - | TTS 怪異字串遇到再補 |

字典 **key 都是英文 snake_case**(例:`attack_speed`、`maximum_life`),所以 YAML profile 跨語言可用——把 enUS 寫好的 profile 直接拿來繁中也能跑,反之亦然。

## 已驗證可用的功能

- ✅ TTS 道具匹配 → 詞綴篩選(核心功能,889 個詞綴)
- ✅ 手寫 YAML profile(用英文 key)
- ✅ Build planner 匯入(Maxroll、Mobalytics、D4Builds)——透過 `closest_match` 的 key 直通機制
- ✅ Aspect / Unique / Sigil 篩選
- ✅ 自動標記垃圾、收藏、移動道具

## 已知限制(誠實標註)

1. **物品類型(item_types.json)是手工翻譯**——若 D4 繁中客戶端的 TTS 讀法跟我這份對不上,可能某個類型(如「雙手鐮刀」是不是叫「巨鐮」?)會失敗。第一次跑請看 log,有問題開 issue,改 `assets/lang/zhTW/item_types.json` 對應 value 就好。
2. **Tributes 是手工列表**——只放了主要 24 個,在地獄狂潮使用時若有不認得的貢品種類,補進 `tributes.json`。
3. **Tooltips「物品力量」未實機驗證**——若 TTS 讀的是別的詞(如「物品威力」),改 `tooltips.json` 的 value。
4. **Aspect / Unique 中 4 個英文佔位符**——D4Companion 的 zhTW 資料裡這幾個還沒本地化(例:`Gloves Unique Druid 98`),這些被自動跳過,意味著這些新內容暫時無法用 unique-name 精確篩選,但通用 filter(`mythic: true`、`minPower`、`minGreaterAffixCount`)仍有效。
5. **新版 D4 加詞綴/裝備時要重產字典**——D4Companion 通常會更新,跑 `python -m src.tools.gen_data_zhTW <D4Companion 路徑>` 即可重新產生字典。

## 重新產生字典(維護用)

```bash
git clone https://github.com/josdemmers/Diablo4Companion
cd d4lf-zhTW-fork
python -m src.tools.gen_data_zhTW ../Diablo4Companion
```

## 改動清單(技術細節)

| 檔案 | 變動 |
|---|---|
| `src/config/models.py` | `language` 欄位 description 更新;validator 加 `zhTW` |
| `src/item/descr/text.py` | `closest_match` 加 key 直通與 fallback,使 importer 跨語言可用 |
| `src/tools/gen_data_zhTW.py` | **新增**:從 D4Companion 產生 zhTW 字典(獨立於 gen_data.py) |
| `assets/lang/zhTW/*.json` | **新增**:完整繁中字典(8 檔) |

源碼總共改動約 30 行;其餘是新增檔案。

## 授權

跟原版相同 MIT License。原版作者: [d4lfteam](https://github.com/d4lfteam/d4lf)。

## 回報問題

繁中相關問題開在本 fork 的 issue;原版 d4lf 行為問題請去 [上游](https://github.com/d4lfteam/d4lf/issues)。
