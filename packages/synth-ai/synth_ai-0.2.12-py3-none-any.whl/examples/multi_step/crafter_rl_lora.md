# Crafter RL LoRA (10-step runs)

This walkthrough shows how to fine-tune the Crafter task app with our 10-step RL LoRA config.

1. **Start the Crafter task app on Modal (with tracing + text-only prompts)**

   ```bash
   BACKEND_BASE_URL=https://agent-learning.onrender.com/api \
   uvx synth-ai modal-serve grpo-crafter \
     --env-file examples/warming_up_to_rl/.env \
     --name grpo-crafter-task-app
   ```

   * Deploys the Modal task app with the tracing/text-only fixes baked in.*

2. **Launch the RL job using the updated LoRA config**

   ```bash
   uvx synth-ai train --type rl \
     --config tests/artifacts/configs/rl.lora.small.toml \
     --backend https://agent-learning.onrender.com/api \
     --env-file .env \
     --no-poll
   ```

   * This config forces 10 agent turns per rollout, reduces batch size to avoid OOMs, and enforces Crafter-specific defaults.*

  INFO - 🎉 Training completed successfully!
  INFO - All batch rewards: [0.0625, 0.0625, 0.125, 0.0625, 0.0625, 0.3125, 0.375, 0.4375, 0.5, 0.9375]