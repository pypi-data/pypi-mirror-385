# moe

Mixture of Experts (MoE) divides computation among multiple expert subnetworks. The MoE layer in DeepSeek is a transformer feed-forward block replaced by a sparse mixture of many MLP experts, where only a few are chosen for each token by a gating network.

Axes (9 dimensions):
- `seq_len`: variable
- `num_experts`, `num_local_experts`, `hidden_size`, `intermediate_size`, `gemm1_out_size`, `num_hidden_blocks`, `num_intermediate_blocks`, `num_gemm1_out_blocks`: constant

Inputs (8 tensors + 2 scalars):
- `routing_logits`: Tensor of routing logits for expert selection [seq_len, num_experts]
- `routing_bias`: Bias tensor for routing. Pass all zeros for no bias [num_experts]
- `hidden_states`: Input hidden states tensor (FP8 quantized) [seq_len, hidden_size]
- `hidden_states_scale`: Block-wise scaling factors for hidden states [num_hidden_blocks, seq_len]
- `gemm1_weights`: First GEMM weights for all local experts (gate and up projections) [num_local_experts, gemm1_out_size, hidden_size]
- `gemm1_weights_scale`: Block-wise scaling factors for first GEMM weights [num_local_experts, num_gemm1_out_blocks, num_hidden_blocks]
- `gemm2_weights`: Second GEMM weights for all local experts (down projection) [num_local_experts, hidden_size, intermediate_size]
- `gemm2_weights_scale`: Block-wise scaling factors for second GEMM weights [num_local_experts, num_hidden_blocks, num_intermediate_blocks]
- `local_expert_offset`: Offset of local experts in global expert space (scalar)
- `routed_scaling_factor`: Scaling factor for routing weights (scalar)

Outputs (1 tensor):
- `output`: Final MoE output tensor [seq_len, hidden_size]
