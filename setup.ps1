# d4lf 繁體中文版 - 一鍵上線腳本
#
# 這個腳本會自動完成所有 GitHub 設定:
#   1. 檢查並安裝 gh CLI(如果沒裝)
#   2. 用 gh 登入 GitHub
#   3. 建立 repo (預設 d4lf-zhTW)
#   4. git init + commit + push
#   5. 開啟 Actions write 權限
#   6. 觸發第一次 build
#   7. 等待完成並開啟 release 頁面
#
# 用法(在解壓後的 d4lf-zhTW-fork/ 資料夾內):
#   PowerShell -ExecutionPolicy Bypass -File setup.ps1
#
# 或者帶自訂 repo 名稱:
#   PowerShell -ExecutionPolicy Bypass -File setup.ps1 -RepoName "my-d4lf"

param(
    [string]$RepoName = "d4lf-zhTW",
    [string]$Visibility = "public",  # 或 "private"
    [switch]$SkipBuild  # 略過第一次手動 build (僅 push,等排程)
)

$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n→ $msg" -ForegroundColor Cyan }
function Write-OK { param($msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "  ✗ $msg" -ForegroundColor Red }

# ── 0. 檢查在正確目錄 ──────────────────────────────────────────
Write-Step "檢查當前目錄"
if (-not (Test-Path "src/autoupdater.py") -or -not (Test-Path "assets/lang/zhTW")) {
    Write-Fail "這個腳本必須在 d4lf-zhTW-fork 解壓後的根目錄執行"
    Write-Host "  目前位置: $(Get-Location)"
    exit 1
}
Write-OK "確認在 d4lf-zhTW-fork 根目錄"

# ── 1. 檢查/安裝 gh CLI ───────────────────────────────────────
Write-Step "檢查 GitHub CLI"
$ghPath = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghPath) {
    Write-Warn "gh CLI 未安裝,嘗試用 winget 安裝..."
    try {
        winget install --id GitHub.cli -e --silent --accept-source-agreements --accept-package-agreements
        # winget 裝完當前 session 沒拿到 PATH,提示重開
        Write-Fail "gh 已安裝但本 session 無法直接呼叫"
        Write-Host "請關閉 PowerShell,重開一個新視窗後再次執行本腳本"
        exit 1
    } catch {
        Write-Fail "winget 安裝失敗: $_"
        Write-Host "請手動安裝 gh CLI: https://cli.github.com/"
        exit 1
    }
}
Write-OK "gh CLI 已安裝 ($((gh --version | Select-Object -First 1)))"

# ── 2. 檢查/安裝 git ──────────────────────────────────────────
Write-Step "檢查 Git"
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Warn "git 未安裝,嘗試用 winget 安裝..."
    winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements
    Write-Fail "請關閉 PowerShell 重開後再執行"
    exit 1
}
Write-OK "git 已安裝"

# ── 3. gh 登入 ────────────────────────────────────────────────
Write-Step "檢查 GitHub 登入狀態"
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warn "尚未登入 GitHub,啟動互動式登入..."
    Write-Host "  跟著畫面提示完成 (建議選 HTTPS + Login with web browser)"
    gh auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "GitHub 登入失敗"
        exit 1
    }
}
$user = (gh api user | ConvertFrom-Json).login
Write-OK "已登入為 $user"

# ── 4. 檢查 repo 是否已存在 ──────────────────────────────────
Write-Step "檢查 repo $user/$RepoName 是否已存在"
gh repo view "$user/$RepoName" 2>&1 | Out-Null
$repoExists = $LASTEXITCODE -eq 0
if ($repoExists) {
    Write-Warn "Repo 已存在: https://github.com/$user/$RepoName"
    $confirm = Read-Host "  要繼續使用既有 repo 並 push 上去嗎? (yes/no)"
    if ($confirm -notin @("yes","y")) {
        Write-Host "取消"
        exit 0
    }
} else {
    Write-Step "建立新 repo $user/$RepoName ($Visibility)"
    $description = "d4lf 繁體中文版 - Auto-translated Traditional Chinese fork of d4lfteam/d4lf"
    gh repo create $RepoName --$Visibility --description $description --confirm 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "建立 repo 失敗"
        exit 1
    }
    Write-OK "Repo 建立完成"
}

# ── 5. git init + commit + push ──────────────────────────────
Write-Step "初始化 git repo"
if (Test-Path ".git") {
    Write-Warn ".git 已存在,跳過 git init"
} else {
    git init -q
    git branch -M main
    Write-OK "git 初始化完成"
}

# 設身分(若沒設過)
$gitName = git config user.name
$gitEmail = git config user.email
if (-not $gitName -or -not $gitEmail) {
    git config user.name "$user"
    git config user.email "$user@users.noreply.github.com"
    Write-OK "設定 git 身分為 $user"
}

# 替換 README 的 {{REPO}} 佔位符(如果有)
$readme = Get-Content README.md -Raw
if ($readme -match "\{\{REPO\}\}") {
    $readme = $readme -replace "\{\{REPO\}\}", "$user/$RepoName"
    Set-Content README.md $readme -NoNewline
    Write-OK "更新 README 中的 repo 連結"
}

git add .
$status = git status --porcelain
if ($status) {
    git commit -m "Initial zhTW fork from d4lfteam/d4lf with auto-update CI" -q
    Write-OK "commit 完成"
} else {
    Write-Warn "沒有要 commit 的變更"
}

# 設 remote 並 push
$remoteUrl = "https://github.com/$user/$RepoName.git"
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    if ($existingRemote -ne $remoteUrl) {
        git remote set-url origin $remoteUrl
        Write-OK "更新 remote 到 $remoteUrl"
    }
} else {
    git remote add origin $remoteUrl
    Write-OK "加上 remote: $remoteUrl"
}

Write-Step "推送到 GitHub"
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Fail "git push 失敗。可能原因:repo 已有內容、或網路問題"
    Write-Host "  手動處理: git pull --rebase origin main; git push -u origin main"
    exit 1
}
Write-OK "推送完成"

# ── 6. 開啟 Actions 寫權限 ──────────────────────────────────
Write-Step "設定 Actions 寫權限"
# GitHub API: 設定 workflow 權限
$apiPath = "/repos/$user/$RepoName/actions/permissions/workflow"
$body = '{"default_workflow_permissions":"write","can_approve_pull_request_reviews":true}'
$body | gh api -X PUT $apiPath --input - 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-OK "Actions 已設為 read+write"
} else {
    Write-Warn "Actions 權限設定失敗,請手動設定:"
    Write-Host "  https://github.com/$user/$RepoName/settings/actions"
    Write-Host "  Workflow permissions → Read and write permissions"
}

# ── 7. 觸發第一次 build ──────────────────────────────────────
if (-not $SkipBuild) {
    Write-Step "觸發第一次 build (force_release=true)"
    Start-Sleep -Seconds 3  # 給 GitHub 一秒消化新 push 的 workflow 檔
    gh workflow run build-and-release.yml --ref main -f force_release=true 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Workflow 已觸發"
    } else {
        Write-Warn "自動觸發失敗,請手動觸發:"
        Write-Host "  https://github.com/$user/$RepoName/actions"
        Write-Host "  → Build & Release zhTW → Run workflow"
    }

    Write-Step "等待 build 完成 (約 8-12 分鐘)"
    Write-Host "  正在開啟 Actions 頁面追蹤進度..."
    Start-Process "https://github.com/$user/$RepoName/actions"

    # 輪詢狀態
    Write-Host "  本腳本會持續檢查狀態,按 Ctrl+C 可中止追蹤(workflow 會繼續跑)"
    $startTime = Get-Date
    $maxWait = New-TimeSpan -Minutes 20
    while (((Get-Date) - $startTime) -lt $maxWait) {
        Start-Sleep -Seconds 30
        $runs = gh run list --workflow=build-and-release.yml --limit 1 --json status,conclusion,databaseId | ConvertFrom-Json
        if ($runs.Count -eq 0) { continue }
        $run = $runs[0]
        $elapsed = [int]((Get-Date) - $startTime).TotalSeconds
        if ($run.status -eq "completed") {
            if ($run.conclusion -eq "success") {
                Write-OK "Build 成功! (耗時 ${elapsed}s)"
                break
            } else {
                Write-Fail "Build 失敗 (conclusion: $($run.conclusion))"
                Write-Host "  log: gh run view $($run.databaseId) --log"
                exit 1
            }
        }
        Write-Host "  ... $($run.status) (已等 ${elapsed}s)" -ForegroundColor DarkGray
    }
}

# ── 8. 完成 ─────────────────────────────────────────────────
Write-Host "`n==============================================" -ForegroundColor Green
Write-Host "  ✓ 全部完成!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repo:      https://github.com/$user/$RepoName"
Write-Host "Releases:  https://github.com/$user/$RepoName/releases"
Write-Host "Actions:   https://github.com/$user/$RepoName/actions"
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "  1. 等 release 跑完 (Actions 頁面看)"
Write-Host "  2. 從 Releases 下載 d4lf_zhTW_*.zip"
Write-Host "  3. 解壓,把 saapi64.dll 複製到 D4 安裝目錄並簽 DLL"
Write-Host "  4. D4 設成繁中,跑 d4lf.exe"
Write-Host ""
Write-Host "之後每天 UTC 03:00 (台北 11:00) 自動同步,有更新會發 release。" -ForegroundColor DarkGray
Write-Host ""

if (-not $SkipBuild) {
    $openReleases = Read-Host "現在開啟 Releases 頁面? (yes/no, 預設 yes)"
    if ($openReleases -ne "no" -and $openReleases -ne "n") {
        Start-Process "https://github.com/$user/$RepoName/releases"
    }
}
