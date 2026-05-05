#!/usr/bin/env bash
# d4lf 繁體中文版 - 一鍵上線 (Bash 版,WSL/Linux/Mac 用)
#
# 用法(在解壓後的 d4lf-zhTW-fork/ 內):
#   bash setup.sh [repo-name]
#
# 預設 repo 名稱: d4lf-zhTW

set -e

REPO_NAME="${1:-d4lf-zhTW}"
VISIBILITY="${2:-public}"

step() { echo -e "\n→ \033[36m$1\033[0m"; }
ok()   { echo -e "  \033[32m✓\033[0m $1"; }
warn() { echo -e "  \033[33m⚠\033[0m $1"; }
fail() { echo -e "  \033[31m✗\033[0m $1"; exit 1; }

# ── 0. 檢查目錄 ────────────────────────────────────────────
step "檢查當前目錄"
[[ -f src/autoupdater.py && -d assets/lang/zhTW ]] || fail "請在 d4lf-zhTW-fork 根目錄執行"
ok "確認在正確目錄"

# ── 1. 檢查工具 ────────────────────────────────────────────
step "檢查必要工具"
command -v gh  >/dev/null || fail "gh CLI 未安裝。請去 https://cli.github.com/ 安裝"
command -v git >/dev/null || fail "git 未安裝"
ok "gh CLI: $(gh --version | head -1)"

# ── 2. gh 登入 ─────────────────────────────────────────────
step "檢查 GitHub 登入"
if ! gh auth status >/dev/null 2>&1; then
  warn "尚未登入,啟動互動式登入..."
  gh auth login
fi
USER=$(gh api user --jq .login)
ok "已登入為 $USER"

# ── 3. 建立 / 確認 repo ────────────────────────────────────
step "處理 repo $USER/$REPO_NAME"
if gh repo view "$USER/$REPO_NAME" >/dev/null 2>&1; then
  warn "Repo 已存在: https://github.com/$USER/$REPO_NAME"
  read -rp "  繼續使用既有 repo 並 push? (yes/no) " confirm
  [[ "$confirm" =~ ^(yes|y)$ ]] || exit 0
else
  gh repo create "$REPO_NAME" --"$VISIBILITY" \
    --description "d4lf 繁體中文版 - Auto-translated Traditional Chinese fork of d4lfteam/d4lf" \
    >/dev/null
  ok "Repo 建立完成"
fi

# ── 4. git init + push ────────────────────────────────────
step "初始化 git 並推送"
[[ -d .git ]] || { git init -q && git branch -M main; }
git config user.name  >/dev/null 2>&1 || git config user.name  "$USER"
git config user.email >/dev/null 2>&1 || git config user.email "$USER@users.noreply.github.com"

# 替換 README 佔位符
if grep -q "{{REPO}}" README.md 2>/dev/null; then
  sed -i.bak "s|{{REPO}}|$USER/$REPO_NAME|g" README.md && rm -f README.md.bak
  ok "README 連結已更新"
fi

git add .
git diff --cached --quiet || git commit -q -m "Initial zhTW fork from d4lfteam/d4lf with auto-update CI"

REMOTE_URL="https://github.com/$USER/$REPO_NAME.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

git push -u origin main || fail "git push 失敗,可能 repo 已有內容,請手動處理"
ok "推送完成"

# ── 5. 開啟 Actions 寫權限 ────────────────────────────────
step "設定 Actions 寫權限"
echo '{"default_workflow_permissions":"write","can_approve_pull_request_reviews":true}' \
  | gh api -X PUT "/repos/$USER/$REPO_NAME/actions/permissions/workflow" --input - >/dev/null \
  && ok "Actions 已設為 read+write" \
  || warn "失敗,請手動設: https://github.com/$USER/$REPO_NAME/settings/actions"

# ── 6. 觸發第一次 build ───────────────────────────────────
step "觸發第一次 build"
sleep 3
gh workflow run build-and-release.yml --ref main -f force_release=true >/dev/null \
  && ok "Workflow 已觸發" \
  || warn "自動觸發失敗,請手動: https://github.com/$USER/$REPO_NAME/actions"

# ── 7. 完成 ────────────────────────────────────────────────
cat <<EOF

==============================================
  ✓ 全部完成!
==============================================

Repo:      https://github.com/$USER/$REPO_NAME
Releases:  https://github.com/$USER/$REPO_NAME/releases
Actions:   https://github.com/$USER/$REPO_NAME/actions

下一步:
  1. 等 build 跑完 (約 8-12 分鐘,Actions 頁面追蹤)
  2. 從 Releases 下載 d4lf_zhTW_*.zip
  3. 解壓,把 saapi64.dll 複製到 D4 安裝目錄並簽 DLL
  4. D4 設成繁中,跑 d4lf.exe

之後每天 UTC 03:00 (台北 11:00) 自動同步並發 release。
EOF
