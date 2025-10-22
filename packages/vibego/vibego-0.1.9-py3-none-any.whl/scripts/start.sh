#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$ROOT_DIR/state/master_restart.lock"
START_LOG="$ROOT_DIR/logs/start.log"
CODEX_STAMP_FILE="$ROOT_DIR/state/npm_codex_install.stamp"
CODEX_INSTALL_TTL="${CODEX_INSTALL_TTL:-86400}"

log_line() {
  local ts
  ts=$(date '+%Y-%m-%d %H:%M:%S%z')
  printf '[%s] %s\n' "$ts" "$*"
}

log_info() {
  log_line "$@"
}

log_error() {
  log_line "$@" >&2
}

cleanup() {
  rm -f "$LOCK_FILE"
}

trap cleanup EXIT

cd "$ROOT_DIR"

mkdir -p "$(dirname "$LOCK_FILE")"
mkdir -p "$(dirname "$START_LOG")"

exec > >(tee -a "$START_LOG")
exec 2> >(tee -a "$START_LOG" >&2)

log_info "start.sh 启动，pid=$$"

if [[ -f "$LOCK_FILE" ]]; then
  log_error "已有 start.sh 在执行，跳过本次启动。"
  exit 1
fi

printf '%d\n' $$ > "$LOCK_FILE"

log_info "锁文件已创建：$LOCK_FILE"

ensure_codex_installed() {
  local need_install=1
  local now
  local codex_bin
  if ! command -v npm >/dev/null 2>&1; then
    log_error "未检测到 npm，可执行文件缺失，跳过 @openai/codex 全局安装"
    return
  fi

  log_info "检测到 npm 版本：$(npm --version)"

  if [[ ! "$CODEX_INSTALL_TTL" =~ ^[0-9]+$ ]]; then
    log_error "CODEX_INSTALL_TTL 非法值：$CODEX_INSTALL_TTL，回退为 86400 秒"
    CODEX_INSTALL_TTL=86400
  fi

  if (( need_install )); then
    codex_bin=$(command -v codex 2>/dev/null || true)
    if [[ -n "$codex_bin" ]]; then
      log_info "Detected existing codex binary at ${codex_bin}; skipping install (upgrade manually if needed)"
      need_install=0
    elif [[ -x "/opt/homebrew/bin/codex" ]]; then
      log_info "Detected existing codex binary at /opt/homebrew/bin/codex; skipping install (upgrade manually if needed)"
      need_install=0
    fi
  fi

  if (( need_install )) && [[ -f "$CODEX_STAMP_FILE" ]]; then
    local last_ts
    last_ts=$(cat "$CODEX_STAMP_FILE" 2>/dev/null || printf '0')
    if [[ "$last_ts" =~ ^[0-9]+$ ]]; then
      now=$(date +%s)
      local elapsed=$(( now - last_ts ))
      if (( elapsed < CODEX_INSTALL_TTL )); then
        local remaining=$(( CODEX_INSTALL_TTL - elapsed ))
        log_info "Previous install happened ${elapsed}s ago (cooldown ${CODEX_INSTALL_TTL}s); skipping install with ${remaining}s remaining"
        need_install=0
      fi
    fi
  fi

  if (( need_install )); then
    log_info "开始执行 npm install -g @openai/codex@latest"
    if npm install -g @openai/codex@latest; then
      now=$(date +%s)
      printf '%s\n' "$now" > "$CODEX_STAMP_FILE"
      log_info "npm install -g @openai/codex@latest 成功"
    else
      local status=$?
      log_error "npm install -g @openai/codex@latest failed (exit code ${status}); continuing startup"
    fi
  fi
}

ensure_codex_installed

if pgrep -f "python.*master.py" >/dev/null 2>&1; then
  log_info "检测到历史 master 实例，正在终止..."
  pkill -f "python.*master.py" || true
  sleep 1
  if pgrep -f "python.*master.py" >/dev/null 2>&1; then
    log_info "残留 master 进程仍在，执行强制结束"
    pkill -9 -f "python.*master.py" || true
    sleep 1
  fi
  if pgrep -f "python.*master.py" >/dev/null 2>&1; then
    log_error "仍存在 master 进程，请手动检查后再启动"
    exit 1
  fi
  log_info "历史 master 实例已清理"
fi

# 创建并启用虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 后台启动 master，日志落在 vibe.log
nohup python3 master.py >> /dev/null 2>&1 &
log_info "master 已后台启动，日志写入 vibe.log"

# 健康检查：等待 master 上线并验证关键 worker
if ! python3 scripts/master_healthcheck.py --project hyphavibebotbackend; then
  log_error "master 健康检查失败，请查看 logs/start.log / vibe.log"
  exit 1
fi
log_info "master 健康检查通过"
