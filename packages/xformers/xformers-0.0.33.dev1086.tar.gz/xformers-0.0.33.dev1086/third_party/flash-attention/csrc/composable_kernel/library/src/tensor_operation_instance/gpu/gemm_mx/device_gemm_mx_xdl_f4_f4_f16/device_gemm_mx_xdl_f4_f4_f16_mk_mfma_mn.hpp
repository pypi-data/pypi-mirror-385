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

using F4     = f4x2_pk_t;
using F16    = half_t;
using F32    = float;
using E8M0   = ck::e8m0_bexp_t;
using E8M0PK = int32_t;

using Row  = tensor_layout::gemm::RowMajor;
using Col  = tensor_layout::gemm::ColumnMajor;
using MFMA = tensor_layout::gemm::MFMA;

template <index_t... Is>
using S = Sequence<Is...>;

using PassThrough = element_wise::PassThrough;

static constexpr auto GemmDefault    = GemmSpecialization::Default;
static constexpr auto GemmKPadding   = GemmSpecialization::KPadding;
static constexpr auto GemmMPadding   = GemmSpecialization::MPadding;
static constexpr auto GemmMNPadding  = GemmSpecialization::MNPadding;
static constexpr auto GemmMNKPadding = GemmSpecialization::MNKPadding;

static constexpr auto Intrawave = BlockGemmPipelineScheduler::Intrawave;
static constexpr auto Interwave = BlockGemmPipelineScheduler::Interwave;

static constexpr auto ScaleBlockSize = 32;

template <BlockGemmPipelineScheduler BlkGemmPipeSched, GemmSpecialization GemmSpec>
using device_gemm_mx_xdl_f4_f4_f16_mk_mfma_mn_instances = std::tuple<
    // clang-format off
    //#####################| ALayout| BLayout| CLayout|AData| AScale|BData| BScale| CData| AccData| Cshuffle|           A|           B|           C|          GEMM|    Scale Block| Block|  MPer|  NPer|  KPer| AK1| BK1|MPer| NPer| MXdl| NXdl|  ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockLds|  BBlockTransfer| BBlockTransfer| BBlockTransfer| BlockTransfer| BBlockTransfer| BBlockTransfer| BBlockLds|    CShuffle|    CShuffle|     CBlockTransferClusterLengths|  CBlockTransfer|    Block-wiseGemm|               Block-wiseGemm|
    //#####################|        |        |        | Type|   Data| Type|   Data|  Type|    Type|     Type| Elementwise| Elementwise| Elementwise|Specialization|           Size|  Size| Block| Block| Block|    |    | XDL|  XDL|  Per|  Per|   ThreadCluster|  ThreadCluster| SrcAccessOrder|   SrcVectorDim|      SrcScalar|      DstScalar| AddExtraM|   ThreadCluster|  ThreadCluster| SrcAccessOrder|  SrcVectorDim|      SrcScalar|      DstScalar| AddExtraN| MXdlPerWave| NXdlPerWave| _MBlock_MXdlPerWave_MWaveMPerXdl| ScalarPerVector|          Pipeline|                     Pipeline|
    //#####################|        |        |        |     |   Type|     |   Type|      |        |         |   Operation|   Operation|   Operation|              |               |      |      |      |      |    |    |    |     | Wave| Wave| Lengths_K0_M_K1|   ArrangeOrder|               |               |      PerVector|   PerVector_K1|          | Lengths_K0_N_K1|   ArrangeOrder|               |              |      PerVector|   PerVector_K1|          |  PerShuffle|  PerShuffle| _NBlock_NXdlPerWave_NWaveNPerXdl|   _NWaveNPerXdl|         Scheduler|                     Verision|
    //#####################|        |        |        |     |       |     |       |      |        |         |            |            |            |              |               |      |      |      |      |    |    |    |     |     |     |                |               |               |               |               |               |          |                |               |               |              |               |               |          |            |            |                                 |                |                  |                             |

      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    32,   128,   128,  16,  16,  16,   16,    2,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    32,   256,   128,  16,  16,  16,   16,    2,    4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    32,   384,   128,  16,  16,  16,   16,    2,    6,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    32,   512,   128,  16,  16,  16,   16,    2,    8,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    64,   128,   128,  16,  16,  16,   16,    4,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    64,   256,   128,  16,  16,  16,   16,    4,    4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    64,   384,   128,  16,  16,  16,   16,    4,    6,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    64,   512,   128,  16,  16,  16,   16,    4,    8,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    96,   128,   128,  16,  16,  16,   16,    6,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    96,   256,   128,  16,  16,  16,   16,    6,    4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    96,   384,   128,  16,  16,  16,   16,    6,    6,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,    96,   512,   128,  16,  16,  16,   16,    6,    8,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   128,   128,   128,  16,  16,  16,   16,    8,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   128,   256,   128,  16,  16,  16,   16,    8,    4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   128,   384,   128,  16,  16,  16,   16,    8,    6,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           2,                   S<1, 16, 1, 16>,               8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   128,   512,   128,  16,  16,  16,   16,    8,    8,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,

      //new instances for testing
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   256,   256,   128,  16,  16,  16,   16,    16,   4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   256,   256,   128,  16,  16,  16,   16,    8,    8,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           8,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,

      DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   256,   64,    128,  16,  16,  16,   16,    8,    2,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           4,           2,                   S<1, 32, 1, 8>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,
      // DeviceGemmMX_Xdl_CShuffleV3<Row,    MFMA,     Row,   F4, E8M0PK,   F4, E8M0PK,  F16,     F32,      F16, PassThrough, PassThrough, PassThrough,      GemmSpec, ScaleBlockSize,   256,   256,   128,   128,  16,  16,  16,   16,    16,   4,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,               2,             16,             16,     true,     S<8, 32, 1>,     S<1, 0, 2>,    S<1, 0, 2>,              2,             16,             16,     true,           2,           4,                   S<1, 8, 1, 32>,                8,  BlkGemmPipeSched,  BlockGemmPipelineVersion::v3>,

      std::nullptr_t
    // clang-format on
    >;
} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
