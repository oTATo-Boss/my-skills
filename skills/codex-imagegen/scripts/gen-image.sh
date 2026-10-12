#!/bin/bash
# gen-image.sh — Codex 内置 image_gen 生图封装
#
# 提示词从 stdin 读（避免引号/JSON 转义问题）。
# 沙箱参数在脚本内写死，不接受外部覆盖 —— 这是本脚本可以被 permissions.allow
# 整体放行的前提。不要加入任何能绕过沙箱的开关。
#
# 用法:
#   gen-image.sh --out <绝对路径.png> [--workdir <dir>] [--ref <图片>]... <<'EOF'
#   <提示词>
#   EOF
#
# 不传 --out 时默认写到 <workdir>/outputs/<日期>_image_<序号>.png
# 目标文件已存在时自动递增序号，不覆盖。

set -euo pipefail

OUT=""
WORKDIR="$PWD"
SLUG="image"
REFS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --out)     OUT="${2:?--out 需要一个路径}"; shift 2 ;;
    --workdir) WORKDIR="${2:?--workdir 需要一个目录}"; shift 2 ;;
    --slug)    SLUG="${2:?--slug 需要一个名字}"; shift 2 ;;
    --ref)     REFS+=("${2:?--ref 需要一个文件}"); shift 2 ;;
    -h|--help)
      sed -n '2,16p' "$0"; exit 0 ;;
    *)
      echo "gen-image.sh: 未知参数 '$1'" >&2; exit 2 ;;
  esac
done

# --- 解析 codex 二进制 -------------------------------------------------------
CODEX="$(command -v codex 2>/dev/null || true)"
if [ -z "$CODEX" ]; then
  CODEX="/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
fi
if [ ! -x "$CODEX" ]; then
  echo "gen-image.sh: 找不到可执行的 codex (试过 PATH 和 ChatGPT.app 内置路径)" >&2
  exit 1
fi

# --- 目标路径 ----------------------------------------------------------------
mkdir -p "$WORKDIR"
if [ -z "$OUT" ]; then
  mkdir -p "$WORKDIR/outputs"
  OUT="$WORKDIR/outputs/$(date +%F)_${SLUG}_01.png"
fi
mkdir -p "$(dirname "$OUT")"

# 不覆盖已有文件：递增序号
if [ -e "$OUT" ]; then
  base="${OUT%.png}"
  base="${base%_[0-9][0-9]}"
  n=2
  while [ -e "$(printf '%s_%02d.png' "$base" "$n")" ]; do n=$((n + 1)); done
  OUT="$(printf '%s_%02d.png' "$base" "$n")"
fi

# --- 提示词 ------------------------------------------------------------------
PF="$(mktemp -t codex-imgprompt)"
trap 'rm -f "$PF"' EXIT
cat > "$PF"

if [ ! -s "$PF" ]; then
  echo "gen-image.sh: 提示词为空 (需要从 stdin 传入)" >&2
  exit 2
fi

{
  echo
  echo "保存要求：生成后把最终图片复制到这个绝对路径（目录已存在）："
  echo "$OUT"
  echo "最后只用一行输出该文件的绝对路径。"
} >> "$PF"

# --- 参考图 ------------------------------------------------------------------
IMG_ARGS=()
if [ "${#REFS[@]}" -gt 0 ]; then
  for r in "${REFS[@]}"; do
    if [ ! -f "$r" ]; then
      echo "gen-image.sh: 参考图不存在: $r" >&2
      exit 2
    fi
    IMG_ARGS+=(-i "$r")
  done
fi

# --- 调用 Codex --------------------------------------------------------------
STAMP="$(mktemp -t codex-imgstamp)"   # 用来界定"本次运行之后产生的文件"
LAST="$(mktemp -t codex-imglast)"
trap 'rm -f "$PF" "$STAMP" "$LAST"' EXIT

"$CODEX" exec \
  --skip-git-repo-check \
  -s workspace-write \
  -C "$WORKDIR" \
  ${IMG_ARGS[@]+"${IMG_ARGS[@]}"} \
  -o "$LAST" \
  - < "$PF"

# --- 兜底：Codex 没把图拷到目标路径时，从默认落盘位置捞回来 ------------------
if [ ! -f "$OUT" ]; then
  GEN_DIR="${CODEX_HOME:-$HOME/.codex}/generated_images"
  LATEST="$(find "$GEN_DIR" -type f -name '*.png' -newer "$STAMP" \
            -exec stat -f '%m %N' {} + 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)"
  if [ -n "$LATEST" ] && [ -f "$LATEST" ]; then
    cp "$LATEST" "$OUT"
    echo "gen-image.sh: 已从默认位置回收 -> $LATEST" >&2
  fi
fi

if [ ! -f "$OUT" ]; then
  echo "gen-image.sh: 生成失败，目标文件不存在: $OUT" >&2
  echo "--- Codex 最后一条消息 ---" >&2
  cat "$LAST" >&2 || true
  exit 1
fi

# --- 结果 --------------------------------------------------------------------
file "$OUT" >&2
echo "$OUT"
