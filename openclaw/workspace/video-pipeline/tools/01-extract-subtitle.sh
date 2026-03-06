#!/bin/bash
# 01-extract-subtitle.sh
# 영상에서 음성 분리 후 Whisper로 자막 추출
# Usage: ./01-extract-subtitle.sh <video.mp4> <output_dir>

set -e

VIDEO="$1"
OUTDIR="${2:-.}"

if [ -z "$VIDEO" ]; then
  echo "Usage: $0 <video.mp4> [output_dir]"
  exit 1
fi

BASENAME=$(basename "$VIDEO" .mp4)

echo "=== Step 1: 음성 분리 (ffmpeg) ==="
ffmpeg -y -i "$VIDEO" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$OUTDIR/${BASENAME}.wav" 2>/dev/null
echo "→ $OUTDIR/${BASENAME}.wav"

echo ""
echo "=== Step 2: Whisper 자막 생성 ==="
whisper "$OUTDIR/${BASENAME}.wav" \
  --model medium \
  --language ko \
  --output_format srt \
  --output_dir "$OUTDIR" \
  2>/dev/null

echo "→ $OUTDIR/${BASENAME}.srt"
echo ""
echo "=== 완료 ==="
cat "$OUTDIR/${BASENAME}.srt"
