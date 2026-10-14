#!/bin/bash

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$ROOT"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

CONFIG_YAML="examples/OpenArmO6/train_files/fdm_pi05_causal_openarm_o6.yaml"

: "${PI05_MODEL_PATH:?PI05_MODEL_PATH is required}"
: "${PI05_TOKENIZER_PATH:?PI05_TOKENIZER_PATH is required}"
: "${WAN_VAE_PATH:?WAN_VAE_PATH is required}"

NPROC_PER_NODE="${NPROC_PER_NODE:-1}"
MAX_STEPS="${MAX_STEPS:-3}"
PER_DEVICE_BATCH_SIZE="${PER_DEVICE_BATCH_SIZE:-1}"
GLOBAL_BATCH_SIZE="${GLOBAL_BATCH_SIZE:-1}"

RUN_ROOT_DIR="${RUN_ROOT_DIR:-./results/Checkpoints/openarm_o6}"
RUN_ID="${RUN_ID:-openarm_o6_pi05causal_h100_smoke}"

mkdir -p "${RUN_ROOT_DIR}/${RUN_ID}"

echo "=================================================="
echo "FDM Pi05Causal OpenArm + O6"
echo "=================================================="
echo "config            = ${CONFIG_YAML}"
echo "PI05_MODEL_PATH   = ${PI05_MODEL_PATH}"
echo "PI05_TOKENIZER    = ${PI05_TOKENIZER_PATH}"
echo "WAN_VAE_PATH      = ${WAN_VAE_PATH}"
echo "GPUs              = ${NPROC_PER_NODE}"
echo "per_device_batch  = ${PER_DEVICE_BATCH_SIZE}"
echo "global_batch      = ${GLOBAL_BATCH_SIZE}"
echo "max_steps         = ${MAX_STEPS}"
echo "run_id            = ${RUN_ID}"
echo "=================================================="

accelerate launch \
    --config_file FDM/config/deepseeds/deepspeed_zero2.yaml \
    --num_processes "${NPROC_PER_NODE}" \
    FDM/training/train_fdm.py \
    --config_yaml "${CONFIG_YAML}" \
    --datasets.vla_data.data_mix openarm_o6_pourwater \
    --datasets.vla_data.disable_state true \
    --datasets.vla_data.per_device_batch_size "${PER_DEVICE_BATCH_SIZE}" \
    --framework.action_model.action_horizon 40 \
    --trainer.global_batch_size "${GLOBAL_BATCH_SIZE}" \
    --trainer.max_train_steps "${MAX_STEPS}" \
    --trainer.enable_compile false \
    --trainer.logging_frequency 1 \
    --trainer.eval_interval 999999 \
    --trainer.save_interval 999999 \
    --trainer.resume_from_checkpoint null \
    --run_root_dir "${RUN_ROOT_DIR}" \
    --run_id "${RUN_ID}" \
    2>&1 | tee "${RUN_ROOT_DIR}/${RUN_ID}/train.log"
