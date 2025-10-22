#!/usr/bin/env bash
# ClaudeCode 模型配置

model_configure() {
  MODEL_NAME="claudecode"
  MODEL_WORKDIR="${CLAUDE_WORKDIR:-${MODEL_WORKDIR:-$ROOT_DIR}}"
  local project_key
  project_key="${CLAUDE_PROJECT_KEY:-$(project_slug_from_workdir "$MODEL_WORKDIR")}" 
  local claude_root="${CLAUDE_PROJECT_ROOT:-$HOME/.claude/projects}"
  MODEL_SESSION_ROOT="$claude_root/$project_key"
  MODEL_SESSION_GLOB="${CLAUDE_SESSION_GLOB:-*.jsonl}"
  MODEL_CMD="${CLAUDE_CMD:-claude --dangerously-skip-permissions}"
  MODEL_POINTER_BASENAME="${MODEL_POINTER_BASENAME:-current_session.txt}"
}
