#!/bin/bash
export MODEL_DIR=$1

bert-serving-start \
  -model_dir $MODEL_DIR \
  -num_worker 4 \
  -ckpt_name bert_model.ckpt \
  -gpu_memory_fraction 0.2 \
  -http_port 8081 \
  -http_max_connect 10000 \
  -max_batch_size 32 \
  -max_seq_len 64 \
  -pooling_layer -1 \
  -xla