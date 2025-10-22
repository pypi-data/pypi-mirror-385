# Agora EX - Qwen3 MoE Training

## Model: Qwen3-30B-A3B (Small MoE)

**Architecture:**
- Total Parameters: 30B
- Activated per Token: 3B (~10% activation)
- Type: Mixture of Experts (MoE)
- Context: 4K tokens

**Why MoE for Agora EX?**
- ✅ Efficient: Only 3B params active → faster inference
- ✅ Powerful: 30B total capacity → better code generation
- ✅ Cost-effective: Lower memory footprint than dense 30B
- ✅ H200 friendly: Fits comfortably on 2x80GB setup

## Hardware: 2xH200

**Configuration:**
- GPU 0 (H200): vLLM inference server
- GPU 1 (H200): LoRA training
- Memory: 80GB per GPU (160GB total)
- Topology: Single-node split

**Resource Usage:**
- vLLM (MoE): ~40GB VRAM (3B active + routing)
- Training: ~50GB VRAM (gradients + optimizer states)
- Headroom: ~70GB available

## Training Configuration

### File: `configs/rl_lora_qwen3_moe_2xh200.toml`

**Key Parameters:**
```toml
[model]
base = "Qwen/Qwen3-30B-A3B"      # MoE with 3B activation
trainer_mode = "lora"

[lora]
r = 16                            # LoRA rank
target_modules = ["all-linear"]   # Wide coverage for MoE

[rollout]
episodes_per_batch = 16           # 16 episodes per batch
max_concurrent_rollouts = 4       # Limited by human judge
batches_per_step = 2              # 32 episodes per training step

[training]
num_epochs = 3
iterations_per_epoch = 4          # 12 total iterations
batch_size = 2
group_size = 4                    # GSPO advantage estimation
learning_rate = 3e-5              # Conservative for MoE
```

## Usage

### 1. Start Task App (with Human Judge)

```bash
cd /Users/joshpurtell/Documents/GitHub/synth-ai

# Set environment variables
export GROQ_API_KEY=gsk_...                              # For inference
export ENVIRONMENT_API_KEY=sk_env_...                    # For auth
export EAMES_JUDGE_URL=https://eames-judge-api...        # Human judge

# Serve task app
uvx synth-ai serve agora-ex --port 8101
```

### 2. Run RL Training

```bash
# Train with MoE on 2xH200
uvx synth-ai train \
  --type rl \
  --config examples/agora_ex/configs/rl_lora_qwen3_moe_2xh200.toml \
  --task-url http://localhost:8101 \
  --env-file backend/.env.dev
```

### 3. Monitor Progress

```bash
# Check logs
tail -f ~/.synth-ai/logs/train_*.log

# View checkpoints
ls -lh ~/.synth-ai/checkpoints/agora-ex-qwen3-moe-rl/
```

## Expected Training Time

**With Human Judge (5-30 min per eval):**
- 12 iterations × 32 episodes = 384 rollouts
- At 10 min average: ~64 hours (2.7 days)
- At 4 concurrent: ~16 hours wall time

**Speedup Options:**
1. **Use AI Judge:** 10 sec/eval → 2 hours total
2. **Increase concurrency:** More parallel rollouts
3. **Reduce episodes:** Fewer samples per iteration

## Training Timeline

```
Iteration 1:  32 rollouts → ~5 hours
Iteration 2:  32 rollouts → ~5 hours
...
Iteration 12: 32 rollouts → ~5 hours
────────────────────────────────────
Total:       384 rollouts → ~60 hours

With 4 concurrent: ~15 hours wall time
```

## Memory Usage

### vLLM Server (GPU 0)

```
Model weights (MoE):        ~25GB  (BF16, 3B active + routing)
KV cache:                   ~10GB  (batch_size=4, context=4K)
Overhead:                   ~5GB   (vLLM runtime)
────────────────────────────────────
Total:                      ~40GB / 80GB
```

### Training (GPU 1)

```
LoRA adapters:              ~2GB   (r=16, all-linear)
Gradients:                  ~10GB  (accumulation)
Optimizer states:           ~20GB  (AdamW)
Activations:                ~15GB  (forward pass)
Overhead:                   ~3GB   (PyTorch)
────────────────────────────────────
Total:                      ~50GB / 80GB
```

## Hyperparameter Tuning

### If overfitting (train reward >> eval reward):
```toml
[lora]
dropout = 0.1              # Increase from 0.05

[training]
learning_rate = 1e-5       # Decrease from 3e-5
```

### If underfitting (slow improvement):
```toml
[training]
learning_rate = 5e-5       # Increase from 3e-5
gradient_accumulation_steps = 16  # More accumulation
```

### If out of memory:
```toml
[training]
batch_size = 1             # Reduce from 2
gradient_accumulation_steps = 16  # Compensate with more accumulation
```

## Comparison: MoE vs Dense

| Metric | Qwen3-30B-A3B (MoE) | Qwen2.5-Coder-7B (Dense) |
|--------|---------------------|--------------------------|
| **Total Params** | 30B | 7B |
| **Active Params** | 3B | 7B |
| **Inference Speed** | ~30 tok/s | ~50 tok/s |
| **VRAM (vLLM)** | ~40GB | ~20GB |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Training Time** | Same | Same |
| **Best For** | Code quality | Speed/cost |

## Next Steps

1. **Baseline:** Train MoE with human judge
2. **Fast iteration:** Switch to AI judge (10s/eval)
3. **Scale up:** Move to larger MoE (235B-A22B)
4. **Deploy:** Export trained adapter for production

## Troubleshooting

### Out of Memory (OOM)
```bash
# Reduce batch size
[training]
batch_size = 1

# Or reduce context length
[vllm]
max_model_len = 3072
```

### Slow Rollouts
```bash
# Switch to AI judge for development
uvx synth-ai serve agora-ex-ai-judge --port 8102

# Update task_url in training command
--task-url http://localhost:8102
```

### Model Not Found
```bash
# Ensure model is in permitted list
python3 -c "
from backend.app.routes.clustered_training.core.algorithms.gspo.permitted_models import list_permitted_models
print('\n'.join(list_permitted_models()))
"
```

---

**Status:** ✅ Ready for training  
**Model:** Qwen3-30B-A3B (MoE, 3B active)  
**Hardware:** 2xH200 (160GB total)  
**Judge:** Human (Eames) or AI (gpt-oss-120b)

