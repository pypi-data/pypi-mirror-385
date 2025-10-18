// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "ck/ck.hpp"
#include "ck/tensor_operation/gpu/device/tensor_layout.hpp"
#include "ck/tensor_operation/gpu/device/gemm_specialization.hpp"
#include "ck/tensor_operation/gpu/device/impl/device_gemm_wmma_cshuffle_v3.hpp"

#include "ck/library/tensor_operation_instance/add_device_operation_instance.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

using F8   = f8_t;
using BF16 = bhalf_t;
using F32  = float;

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

template <GemmSpecialization GemmSpec>
using device_gemm_wmma_universal_f8_f8_bf16_mk_kn_mn_comp_instances =
    std::tuple<
        // clang-format off
        //#########################| ALayout| BLayout| CLayout|AData| BData| CData| AccData| CShuffle|           A|           B|           C| GemmSpec| Block|  MPer|  NPer|  KPer| AK1| BK1| MPer| NPer| MRepeat| NRepeat|    ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockTransfer| ABlockLds|    BBlockTransfer| BBlockTransfer| BBlockTransfer| BBlockTransfer| BBlockTransfer| BBlockTransfer| BBlockLds|   CShuffle|   CShuffle| CShuffleBlockTransfer| CShuffleBlockTransfer|    BlkGemm|                      BlkGemm| Compute| Compute|
        //#########################|        |        |        | Type|  Type|  Type|    Type| DataType| Elementwise| Elementwise| Elementwise|         |  Size| Block| Block| Block|    |    | Wmma| Wmma|        |        |     ThreadCluster|  ThreadCluster| SrcAccessOrder|   SrcVectorDim|      SrcScalar|      DstScalar|    ExtraM|     ThreadCluster|  ThreadCluster| SrcAccessOrder|   SrcVectorDim|      SrcScalar|      DstScalar|    ExtraN|    MRepeat|    NRepeat|        ClusterLengths|       ScalarPerVector|  PipeSched|                  PipelineVer|   TypeA|   TypeB|
        //#########################|        |        |        |     |      |      |        |         |   Operation|   Operation|   Operation|         |      |      |      |      |    |    |     |     |        |        | Lengths_AK0_M_AK1|   ArrangeOrder|               |               |      PerVector|  PerVector_AK1|          | Lengths_BK0_N_BK1|   ArrangeOrder|               |               |      PerVector|  PerVector_BK1|          | PerShuffle| PerShuffle|     _MBlock_MPerBlock|            _NPerBlock|           |                             |        |        |
        //#########################|        |        |        |     |      |      |        |         |            |            |            |         |      |      |      |      |    |    |     |     |        |        |                  |               |               |               |               |               |          |                  |               |               |               |               |               |          |           |           |     _NBlock_NPerBlock|                      |           |                             |        |        |
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    32,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   128,   128,    64,    64,   8,   8,   16,   16,       4,       2,       S<4, 32, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         0,       S<4, 32, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         0,          1,          1,        S<1, 32, 1, 4>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   256,    64,   8,   8,   16,   16,       4,       4,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    64,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,    64,    32,    64,    64,   8,   8,   16,   16,       2,       2,       S<4, 16, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 16, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 16, 1, 4>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   128,    64,    64,    32,   8,   8,   16,   16,       2,       2,       S<4, 32, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         0,       S<4, 32, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              2,              4,         1,          1,          1,        S<1, 32, 1, 2>,                     8,  Intrawave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    32,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Interwave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    64,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Interwave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   128,   128,   128,    32,   8,   8,   16,   16,       4,       4,       S<4, 32, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 32, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 4>,                     8,  Interwave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,    64,    32,    64,    64,   8,   8,   16,   16,       2,       2,       S<4, 16, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 16, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 16, 1, 4>,                     8,  Interwave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   128,    64,    64,    32,   8,   8,   16,   16,       2,       2,       S<4, 32, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         0,       S<4, 32, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              2,              4,         1,          1,          1,        S<1, 32, 1, 2>,                     8,  Interwave, BlockGemmPipelineVersion::v1,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    32,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Intrawave, BlockGemmPipelineVersion::v3,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   256,   128,   128,    64,   8,   8,   16,   16,       4,       2,       S<4, 64, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 64, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 32, 1, 8>,                     8,  Intrawave, BlockGemmPipelineVersion::v3,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,    64,    32,    64,    64,   8,   8,   16,   16,       2,       2,       S<4, 16, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         1,       S<4, 16, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              1,              8,         1,          1,          1,        S<1, 16, 1, 4>,                     8,  Intrawave, BlockGemmPipelineVersion::v3,      F8,      F8>,
        DeviceGemm_Wmma_CShuffleV3<      Row,     Row,     Row,   F8,    F8,  BF16,     F32,     BF16, PassThrough, PassThrough, PassThrough, GemmSpec,   128,    64,    64,    32,   8,   8,   16,   16,       2,       2,       S<4, 32, 1>,     S<1, 0, 2>,     S<1, 0, 2>,              2,              8,              8,         0,       S<4, 32, 1>,     S<0, 2, 1>,     S<0, 2, 1>,              1,              2,              4,         1,          1,          1,        S<1, 32, 1, 2>,                     8,  Intrawave, BlockGemmPipelineVersion::v3,      F8,      F8>
        // clang-format on
        >;
} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
