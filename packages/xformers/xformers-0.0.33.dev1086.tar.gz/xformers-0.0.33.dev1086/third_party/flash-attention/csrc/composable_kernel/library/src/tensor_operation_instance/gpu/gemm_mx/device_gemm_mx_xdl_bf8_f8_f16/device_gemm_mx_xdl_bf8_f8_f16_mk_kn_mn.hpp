// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "ck/ck.hpp"
#include "ck/tensor_operation/gpu/device/tensor_layout.hpp"
#include "ck/tensor_operation/gpu/device/gemm_specialization.hpp"
#include "ck/tensor_operation/gpu/device/impl/device_gemm_xdl_cshuffle_v3_mx.hpp"

#include "ck/library/tensor_operation_instance/add_device_operation_instance.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

using F8     = f8_t;
using BF8    = bf8_t;
using F16    = half_t;
using BF16   = bhalf_t;
using F32    = float;
using E8M0   = ck::e8m0_bexp_t;
using E8M0PK = int32_t;

using Row = tensor_layout::gemm::RowMajor;
using Col = tensor_layout::gemm::ColumnMajor;

template <index_t... Is>
using S = Sequence<Is...>;

using PassThrough = element_wise::PassThrough;

static constexpr auto GemmDefault    = GemmSpecialization::Default;
static constexpr auto GemmKPadding   = GemmSpecialization::KPadding;
static constexpr auto GemmMNPadding  = GemmSpecialization::MNPadding;
static constexpr auto GemmMNKPadding = GemmSpecialization::MNKPadding;

static constexpr auto Intrawave = BlockGemmPipelineScheduler::Intrawave;
static constexpr auto Interwave = BlockGemmPipelineScheduler::Interwave;

static constexpr auto ScaleBlockSize = 32;

template <BlockGemmPipelineScheduler BlkGemmPipeSched, GemmSpecialization GemmSpec>
using device_gemm_mx_xdl_bf8_f8_f16_mk_kn_mn_instances = std::tuple<
#if 0 // TODO: Fix RRR
    // clang-format off
        //#########################| ALayout| BLayout| CLayout|AData|   AScale|BData|  BScale| CData| AccData| Cshuffle|           A|           B|           C|          GEMM|    Scale Block| Block|  MPer|  NPer|  KPer| AK1| BK1|MPer| NPer| MXdl| NXdl|  ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockLds|  BBlockTransfer| BBlockTransfer| BBlockTransfer| BlockTransfer| BBlockTransfer| BBlockTransfer| BBlockLds|    CShuffle|    CShuffle|     CBlockTransferClusterLengths|  CBlockTransfer|    Block-wiseGemm|               Block-wiseGemm|
        //#########################|        |        |        | Type|     Data| Type|    Data|  Type|    Type|     Type| Elementwise| Elementwise| Elementwise|Specialization|           Size|  Size| Block| Block| Block|    |    | XDL|  XDL|  Per|  Per|   ThreadCluster|  ThreadCluster| SrcAccessOrder|   SrcVectorDim|      SrcScalar|      DstScalar| AddExtraM|   ThreadCluster|  ThreadCluster| SrcAccessOrder|  SrcVectorDim|      SrcScalar|      DstScalar| AddExtraN| MXdlPerWave| NXdlPerWave| _MBlock_MXdlPerWave_MWaveMPerXdl| ScalarPerVector|          Pipeline|                     Pipeline|
        //#########################|        |        |        |     |     Type|     |    Type|      |        |         |   Operation|   Operation|   Operation|              |               |      |      |      |      |    |    |    |     | Wave| Wave| Lengths_K0_M_K1|   ArrangeOrder|               |               |      PerVector|   PerVector_K1|          | Lengths_K0_N_K1|   ArrangeOrder|               |              |      PerVector|   PerVector_K1|          |  PerShuffle|  PerShuffle| _NBlock_NXdlPerWave_NWaveNPerXdl|   _NWaveNPerXdl|         Scheduler|                     Verision|
        //#########################|        |        |        |     |         |     |        |      |        |         |            |            |            |              |               |      |      |      |      |    |    |    |     |     |     |                |               |               |               |               |               |          |                |               |               |              |               |               |          |            |            |                                 |                |                  |                             |
      DeviceGemmMX_Xdl_CShuffleV3<       Row,     Row,     Row,   BF8,  E8M0PK,   F8,  E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   128,    64,    16,   128,  16,   4,  16,   16,    2,    1,     S<8, 16, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,         0,     S<32, 4, 1>,     S<0, 2, 1>,    S<0, 2, 1>,              1,              4,              4,         0,           1,           1,                   S<1, 16, 1, 8>,               2,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v1>,
      DeviceGemmMX_Xdl_CShuffleV3<       Row,     Row,     Row,   BF8,  E8M0PK,   F8,  E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   256,   256,   256,  16,   4,  32,   32,    4,    4,     S<4, 64, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     false,    S<16, 16, 1>,     S<0, 2, 1>,    S<0, 2, 1>,              1,             16,              4,     false,           1,           1,                   S<1, 32, 1, 8>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v1>,
      DeviceGemmMX_Xdl_CShuffleV3<       Row,     Row,     Row,   BF8,  E8M0PK,   F8,  E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    64,    64,   256,  16,   4,  32,   32,    1,    1,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,         0,     S<32, 8, 1>,     S<0, 2, 1>,    S<0, 2, 1>,              1,              8,              4,         0,           1,           1,                   S<1, 32, 1, 8>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v1>,
      DeviceGemmMX_Xdl_CShuffleV3<       Row,     Row,     Row,   BF8,  E8M0PK,   F8,  E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   128,   128,   128,  16,   4,  32,   32,    2,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,         0,     S<32, 8, 1>,     S<0, 2, 1>,    S<0, 2, 1>,              1,             16,              4,         0,           1,           1,                   S<1, 32, 1, 8>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v1>,
      DeviceGemmMX_Xdl_CShuffleV3<       Row,     Row,     Row,   BF8,  E8M0PK,   F8,  E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   128,    16,    32,   512,  16,   8,  16,   16,    1,    1,     S<8, 16, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,         0,     S<64, 2, 1>,     S<0, 2, 1>,    S<0, 2, 1>,              1,             16,              8,         0,           1,           1,                   S<1, 16, 1, 8>,               4,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v1>
    // clang-format on
#endif
    >;

} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
