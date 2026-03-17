#!/usr/bin/env bash
set -e

############################################
# デフォルト設定
############################################
DEFAULT_HF_TOKEN="YOUR_HF_TOKEN_HERE"
DEFAULT_MODEL_REPO="kmd2525/test105_v8"

HF_TOKEN="${1:-$DEFAULT_HF_TOKEN}"
MODEL_REPO="${2:-$DEFAULT_MODEL_REPO}"

############################################
# 1. 環境変数設定
############################################
export HF_TOKEN="$HF_TOKEN"
echo "Using HF_TOKEN=${HF_TOKEN:0:6}******"
echo "Using MODEL_REPO=$MODEL_REPO"

############################################
# 2. AgentBenchディレクトリ確認
############################################
if [ ! -f "update_model.sh" ]; then
  echo "Error: Please run this script inside the AgentBench directory."
  exit 1
fi

############################################
# 3. vLLMモデル更新
############################################
echo "Updating model..."
./update_model.sh "$MODEL_REPO"

############################################
# 4. サービス再起動
############################################
echo "Restarting services..."
sudo systemctl restart agentbench-controller.service
sudo systemctl restart agentbench-worker-dbbench.service
sudo systemctl restart agentbench-worker-alfworld.service

############################################
# 5. ALFWORLD 実行
############################################
LOGFILE_ALF="alfworld_vllm_$(date +%Y%m%d_%H%M).log"

{
  echo "===== START ALFWORLD: $(date '+%Y-%m-%d %H:%M') ====="
  python3 -m src.assigner -c configs/assignments/alfworld-vllm.yaml
  EXIT_CODE=$?
  echo "===== END ALFWORLD:   $(date '+%Y-%m-%d %H:%M') ====="
  echo "===== EXIT CODE: $EXIT_CODE ====="
} 2>&1 | tee "$LOGFILE_ALF"

############################################
# 6. DBBench 実行
############################################
LOGFILE_DB="dbbench_vllm_$(date +%Y%m%d_%H%M).log"

{
 echo "===== START DBBENCH: $(date '+%Y-%m-%d %H:%M') ====="
 python3 -m src.assigner -c configs/assignments/dbbench-vllm.yaml
 EXIT_CODE=$?
 echo "===== END DBBENCH:   $(date '+%Y-%m-%d %H:%M') ====="
 echo "===== EXIT CODE: $EXIT_CODE ====="
} 2>&1 | tee "$LOGFILE_DB"

############################################
# 7. ログ集約＆圧縮
############################################
mkdir -p outputs
find . -maxdepth 1 -type f -name "*_vllm_*.log" -exec mv {} outputs/ \;
ARCHIVE_NAME="outputs_$(date +%Y%m%d_%H%M).tar.gz"
tar -czf "$ARCHIVE_NAME" outputs/

echo "Archive created: $ARCHIVE_NAME"

echo "===== ALL DONE ====="
