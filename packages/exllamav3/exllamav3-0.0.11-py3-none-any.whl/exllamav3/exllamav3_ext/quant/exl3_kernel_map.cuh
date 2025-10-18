#pragma once

int select_gemm_shape(int cc, int size_m, int size_k, int size_n, int bits, bool multi);
int exl3_gemm_num_kernel_shapes();
bool exl3_gemm_shape_compat(int shape_idx, int size_m, int size_k, int size_n, int bits);

#define EXL3_GEMM_T_ARGS \
    int bits, \
    bool c_fp32, \
    int cb, \
    int TILESIZE_M, \
    int TILESIZE_K, \
    int TILESIZE_N, \
    int SH_STAGES, \
    int FRAG_STAGES

#define EXL3_GEMM_ARGS \
    const half* __restrict__  A, \
    const uint16_t* __restrict__ B, \
    void* __restrict__ C, \
    int size_m, \
    int size_k, \
    int size_n, \
    int* __restrict__ locks, \
    const half* __restrict__ suh, \
    half* __restrict__ A_had, \
    const half* __restrict__ svh

#define EXL3_MGEMM_ARGS \
    const half* __restrict__  A, \
    const uint16_t** __restrict__ B_list, \
    void* __restrict__ C, \
    int size_m, \
    int size_k, \
    int size_n, \
    int* __restrict__ locks, \
    const half** __restrict__ suh_list, \
    half* __restrict__ A_had, \
    const half** __restrict__ svh_list, \
    int64_t* B_indices, \
    half* B_weights, \
    int bszm_in, \
    int bszm_out, \
    int min_index, \
    int max_index

typedef void (*fp_exl3_gemm_kernel) (EXL3_GEMM_ARGS);
typedef void (*fp_exl3_mgemm_kernel) (EXL3_MGEMM_ARGS);

#define EXL3_GEMM_SHAPE_1     16,     16,    128,     6,     5
#define EXL3_GEMM_SHAPE_2     16,     32,    128,     4,     3
#define EXL3_GEMM_SHAPE_3     16,     32,    256,     4,     3
#define EXL3_GEMM_SHAPE_4     16,     16,    512,     4,     3

#define EXL3_GEMM_TILESIZE_K  0, 16, 32, 32, 16
#define EXL3_GEMM_TILESIZE_N  0, 128, 128, 256, 512
#define EXL3_GEMM_BLOCKDIM  0, 256, 512, 512, 256

#define EXL3_GEMM_NUM_SHAPES 4

// Shape 1 not currently used anywhere
#define EXL3_GEMM_KERNEL_INSTANCES(_bits, _c_fp32, cb) \
    nullptr, \
    exl3_gemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_1>, \
    exl3_gemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_2>, \
    exl3_gemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_3>, \
    exl3_gemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_4>

#define EXL3_MGEMM_KERNEL_INSTANCES(_bits, _c_fp32, cb) \
    nullptr, \
    exl3_mgemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_1>, \
    exl3_mgemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_2>, \
    exl3_mgemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_3>, \
    exl3_mgemm_kernel<_bits, _c_fp32, cb, EXL3_GEMM_SHAPE_4>

#define EXL3_GEMM_BASE_THREADS 256

#define ALL_EXL3_KERNEL_EXTERNS(K) \
    extern fp_exl3_gemm_kernel tfp_exl3_gemm_kernel_fp32_b##K[]; \
    extern fp_exl3_gemm_kernel tfp_exl3_gemm_kernel_fp16_b##K[]; \
    extern fp_exl3_mgemm_kernel tfp_exl3_mgemm_kernel_fp32_b##K[]; \
    extern fp_exl3_mgemm_kernel tfp_exl3_mgemm_kernel_fp16_b##K[]; \

#define ALL_EXL3_KERNEL_INSTANCES(K) \
    fp_exl3_gemm_kernel tfp_exl3_gemm_kernel_fp32_b##K[] = { \
        EXL3_GEMM_KERNEL_INSTANCES(K, true, 0), \
        EXL3_GEMM_KERNEL_INSTANCES(K, true, 1), \
        EXL3_GEMM_KERNEL_INSTANCES(K, true, 2) \
    }; \
    \
    fp_exl3_gemm_kernel tfp_exl3_gemm_kernel_fp16_b##K[] = { \
        EXL3_GEMM_KERNEL_INSTANCES(K, false, 0), \
        EXL3_GEMM_KERNEL_INSTANCES(K, false, 1), \
        EXL3_GEMM_KERNEL_INSTANCES(K, false, 2) \
    }; \
    \
    fp_exl3_mgemm_kernel tfp_exl3_mgemm_kernel_fp32_b##K[] = { \
        EXL3_MGEMM_KERNEL_INSTANCES(K, true, 0), \
        EXL3_MGEMM_KERNEL_INSTANCES(K, true, 1), \
        EXL3_MGEMM_KERNEL_INSTANCES(K, true, 2) \
    }; \
    \
    fp_exl3_mgemm_kernel tfp_exl3_mgemm_kernel_fp16_b##K[] = { \
        EXL3_MGEMM_KERNEL_INSTANCES(K, false, 0), \
        EXL3_MGEMM_KERNEL_INSTANCES(K, false, 1), \
        EXL3_MGEMM_KERNEL_INSTANCES(K, false, 2) \
    };

fp_exl3_gemm_kernel select_exl3_gemm_kernel
(
    int cc,
    int size_m,
    int size_k,
    int size_n,
    int bits,
    bool c_fp32,
    int force_shape_idx,
    int* out_block_dim,
    int* out_shape_idx,
    int* out_num_sms,
    int cb
);

fp_exl3_mgemm_kernel select_exl3_mgemm_kernel
(
    int cc,
    int size_m,
    int size_k,
    int size_n,
    int K,
    bool c_fp32,
    int force_shape_idx,
    int* out_block_dim,
    int* out_shape_idx,
    int* out_num_sms,
    int cb,
    int bszm_in,
    int bszm_out
);

struct TSample {
    int cc;
    int K;
    int m;
    int k;
    int n;
    int shape_idx;
    int num_sms;
};

struct TMSample {
    int cc;
    int K;
    int m;
    int k;
    int n;
    int shape_idx;
    int num_sms;
    int bszm_in;
    int bszm_out;
};

struct TResult
{
    fp_exl3_gemm_kernel kernel;
    fp_exl3_mgemm_kernel mkernel;
    int shape_idx;
    int num_sms;
    int block_dim;
};

TResult* select_exl3_gemm_mgemm_kernel_new
(
    int cc,
    int size_m,
    int size_k,
    int size_n,
    int K,
    bool c_fp32,
    int force_shape_idx,
    int force_num_sms,
    int cb
);
