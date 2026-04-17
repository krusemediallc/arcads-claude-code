#!/bin/bash
# Extract evenly-spaced frames + audio from a video for analysis.
# Usage: extract-frames.sh <video_path> <output_dir> [num_frames]
#
# Outputs:
#   <output_dir>/frame_001.jpg ... frame_NNN.jpg
#   <output_dir>/audio.wav  (16 kHz mono, for transcription)
#   <output_dir>/metadata.txt  (duration, fps, resolution)

set -euo pipefail

FFMPEG="${FFMPEG:-/opt/homebrew/bin/ffmpeg}"
FFPROBE="${FFPROBE:-/opt/homebrew/bin/ffprobe}"

VIDEO="$1"
OUT_DIR="$2"
NUM_FRAMES="${3:-12}"

if [ ! -f "$VIDEO" ]; then
  echo "Error: video not found: $VIDEO" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# Get video duration and metadata
DURATION=$("$FFPROBE" -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null)
RESOLUTION=$("$FFPROBE" -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=s=x:p=0 "$VIDEO" 2>/dev/null)
FPS=$("$FFPROBE" -v error -select_streams v:0 \
  -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null)

echo "duration_seconds=$DURATION" > "$OUT_DIR/metadata.txt"
echo "resolution=$RESOLUTION" >> "$OUT_DIR/metadata.txt"
echo "fps=$FPS" >> "$OUT_DIR/metadata.txt"
echo "num_frames_extracted=$NUM_FRAMES" >> "$OUT_DIR/metadata.txt"

echo "Video: $(basename "$VIDEO")"
echo "Duration: ${DURATION}s | Resolution: $RESOLUTION | FPS: $FPS"

# Extract evenly-spaced frames
# fps filter = num_frames / duration → one frame per interval
FPS_FILTER=$(echo "scale=6; $NUM_FRAMES / $DURATION" | bc)
echo "Extracting $NUM_FRAMES frames (1 every $(echo "scale=1; $DURATION / $NUM_FRAMES" | bc)s)..."

"$FFMPEG" -v warning -i "$VIDEO" \
  -vf "fps=$FPS_FILTER" \
  -q:v 2 \
  "$OUT_DIR/frame_%03d.jpg" 2>&1

FRAME_COUNT=$(ls "$OUT_DIR"/frame_*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "Extracted $FRAME_COUNT frames"

# Extract audio (16kHz mono WAV for transcription)
echo "Extracting audio..."
"$FFMPEG" -v warning -i "$VIDEO" \
  -vn -acodec pcm_s16le -ar 16000 -ac 1 \
  "$OUT_DIR/audio.wav" 2>&1 || echo "No audio stream found (silent video)"

echo "Done. Output in: $OUT_DIR"
