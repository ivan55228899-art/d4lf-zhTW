# 自動更新設定指引

本 fork 內建 GitHub Actions 工作流,設定好之後**完全不用人工介入**:

- 每天 UTC 03:00 (台北 11:00) 自動檢查上游 d4lf 與 D4Companion 是否有更新
- 有更新就自動同步原始碼 + 重產繁中字典
- 自動編譯 Windows exe + 發 GitHub Release
- 你的 d4lf.exe 內建的「檢查更新」會從**你自己的 fork** 拉新版

整個流程從 push 到 GitHub 那一刻起就跑起來,你只要做一次 5 分鐘的設定。

## 一次性設定(約 5 分鐘)

### 步驟 1:把這份 fork 推到你的 GitHub

```bash
# 在解壓的 d4lf-zhTW-fork 資料夾內
cd d4lf-zhTW-fork

git init
git add .
git commit -m "Initial zhTW fork from d4lfteam/d4lf"
git branch -M main

# 改成你自己的 GitHub repo URL
git remote add origin https://github.com/<你的 GitHub 帳號>/d4lf-zhTW.git
git push -u origin main
```

> 如果你還沒在 GitHub 開 repo,先去 https://github.com/new 建一個 (建議命名 `d4lf-zhTW`,**留空,不要勾 README/LICENSE**),建完才推上去。

### 步驟 2:給 Actions 寫入 release 的權限

GitHub repo 預設禁止 Actions 建 release 跟自動 commit。要去開啟:

1. 進入你的 repo → **Settings** → **Actions** → **General**
2. 捲到最下面 **Workflow permissions** 區段
3. 選 **Read and write permissions**
4. 勾選 **Allow GitHub Actions to create and approve pull requests**
5. 按 Save

### 步驟 3:啟用工作流

1. Repo 頁面 → **Actions** 分頁
2. 第一次進去會看到提示 "Workflows aren't being run on this forked repository" → 點 **I understand my workflows, go ahead and enable them**
3. 看到 **Build & Release zhTW** workflow → 點進去 → 右上 **Run workflow** 按鈕 → main 分支 → 勾 "Force a release even if no changes detected"(第一次需要)→ Run

工作流會跑大約 8-12 分鐘:
- 同步上游(若有變更)
- 拉 D4Companion 資料
- 重產字典
- 編譯 exe
- 發 release

跑完去 **Releases** 看,會有 `v8.4.2-zh.1` 之類的 tag 跟 `d4lf_zhTW_v8.4.2-zh.1.zip`。

### 步驟 4:下載並安裝

1. 去 Releases 頁下載最新的 zip
2. 解壓到任意資料夾
3. 把 `saapi64.dll` 複製到 Diablo IV 安裝目錄
4. 用 PowerShell 跑 `.\sign_dll.ps1`(Season 12 後必要)
5. D4 設成繁中
6. 跑 `d4lf.exe`

之後每次有更新,d4lf.exe 啟動時會跳通知,你執行 `autoupdater.bat` 就自動下載新版。

## 驗證自動更新指向你的 fork(可選但建議)

下載 release zip,解壓後用記事本打開 `d4lf.exe`(對,就是 binary 直接搜字串),搜尋 `repos/`。

正確的話應該看到:
```
api.github.com/repos/<你的帳號>/d4lf-zhTW/releases/latest
```

而不是上游的 `d4lfteam/d4lf`。如果還是上游,代表 CI 的 sed 替換沒跑成功——回去看 Actions log。

## 排程時間調整

預設每天 UTC 03:00 跑(台灣 11:00)。要改的話編輯 `.github/workflows/build-and-release.yml`:

```yaml
on:
  schedule:
    - cron: "0 3 * * *"   # 改這行
```

cron 語法:`分 時 日 月 星期`。範例:
- `"0 18 * * *"` — 每天 UTC 18:00 = 台北凌晨 02:00
- `"0 */6 * * *"` — 每 6 小時跑一次
- `"0 3 * * 1"` — 每週一 UTC 03:00

## 手動觸發(不想等排程)

Actions 分頁 → Build & Release zhTW → Run workflow 按鈕。

## 處理上游合併衝突

若 d4lf 上游做了大改動,自動 merge 可能有衝突。工作流會自動 abort merge 並繼續(只重產字典),不會擋住 release。

要徹底解決衝突就在本機:
```bash
git remote add upstream https://github.com/d4lfteam/d4lf.git
git fetch upstream
git merge upstream/main
# 解衝突後
git push
```

## 停用自動更新

不要 schedule 跑 → 把 `.github/workflows/build-and-release.yml` 裡的 `schedule:` 那兩行刪掉或註解掉。

完全停用 Actions → 在 GitHub repo 的 Settings → Actions → Disable。

## 維護成本盤點

- **儲存空間**:每個 release zip 約 30-50 MB。CI 自動只保留最近 10 個 release,所以不會無限長大(約 500 MB 上限)
- **CI 額度**:Public repo 免費無限額;Private repo 每月 2000 分鐘免費,本工作流每次跑 ~12 分鐘,每天跑一次 = 月 360 分鐘,綽綽有餘
- **人工介入**:正常情況下零。除非上游 repo 結構大改、D4Companion 改 API、或你想加新功能

## 相關檔案

| 檔案 | 作用 |
|---|---|
| `.github/workflows/build-and-release.yml` | 自動化主流程 |
| `src/autoupdater.py` | d4lf 內建更新器(被 CI 改寫成指向你的 fork) |
| `src/tools/gen_data_zhTW.py` | 字典產生器 |
| `assets/lang/zhTW/*.json` | CI 自動重產的繁中字典 |
