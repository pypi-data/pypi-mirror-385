// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "gemm_mx_common.hpp"

using ADataType = ck::f8_t;
using BDataType = ck::bf8_t;

using XDataType = ck::e8m0_bexp_t;

using CDataType        = ck::bhalf_t;
using AccDataType      = float;
using CShuffleDataType = CDataType;

using ALayout = Row;
using BLayout = Row;
using CLayout = Row;

using AElementOp = PassThrough; // elementwise transformation for A matrix
using BElementOp = PassThrough; // elementwise transformation for B matrix
using CElementOp = PassThrough; // elementwise transformation for C matrix

constexpr ck::index_t ScaleBlockSize = 32; // scaling block size

constexpr auto GemmSpec      = ck::tensor_operation::device::GemmSpecialization::Default;
constexpr auto BlkGemmPSched = ck::BlockGemmPipelineScheduler::Intrawave;
constexpr auto BlkGemmPVer   = ck::BlockGemmPipelineVersion::v3;

using DeviceOpInstance = ck::tensor_operation::device::DeviceGemmMX_Xdl_CShuffleV3<
    ALayout,          // ALayout
    BLayout,          // BLayout
    CLayout,          // CLayout
    ADataType,        // ADataType
    XDataType,        // AScaleDataType
    BDataType,        // BDataType
    XDataType,        // BScaleDataType
    CDataType,        // CDataType
    AccDataType,      // GemmAccDataType
    CShuffleDataType, // CShuffleDataType
    AElementOp,       // AElementwiseOperation
    BElementOp,       // BElementwiseOperation
    CElementOp,       // CElementwiseOperation
    GemmSpec,         // GemmSpec
    ScaleBlockSize,   // ScaleBlockSize: Scaling block size
    256,              // BlockSize: Thread block size
    128,              // MPerBlock
    128,              // NPerBlock
    256,              // KPerBlock
    16,               // AK1
    8,                // BK1
    16,               // MPerXDL
    16,               // NPerXDL
    4,                // MXdlPerWave
    4,                // NXdlPerWave
    S<16, 16, 1>,     // ABlockTransferThreadClusterLengths_AK0_M_AK1
    S<1, 0, 2>,       // ABlockTransferThreadClusterArrangeOrder
    S<1, 0, 2>,       // ABlockTransferSrcAccessOrder
    2,                // ABlockTransferSrcVectorDim
    16,               // ABlockTransferSrcScalarPerVector
    16,               // ABlockTransferDstScalarPerVector_AK1
    false,            // ABlockLdsExtraM
    S<32, 8, 1>,      // BBlockTransferThreadClusterLengths_BK0_N_BK1
    S<0, 2, 1>,       // BBlockTransferThreadClusterArrangeOrder
    S<0, 2, 1>,       // BBlockTransferSrcAccessOrder
    1,                // BBlockTransferSrcVectorDim
    16,               // BBlockTransferSrcScalarPerVector
    8,                // BBlockTransferDstScalarPerVector_BK1
    false,            // BBlockLdsExtraN
    2,                // CShuffleMXdlPerWavePerShuffle
    2,                // CShuffleNXdlPerWavePerShuffle
    S<1, 32, 1, 8>,   // CShuffleBlockTransferClusterLengths_MBlock_MPerBlock_NBlock_NPerBlock
    8,                // CShuffleBlockTransferScalarPerVector_NPerBlock
    BlkGemmPSched,    // BlkGemmPipeSched
    BlkGemmPVer,      // BlkGemmPipelineVer
    ADataType,        // ComputeTypeA
    BDataType         // ComputeTypeB
    >;

int main(int argc, char* argv[])
{
    return run_mx_gemm_example<DeviceOpInstance,
                               ADataType,
                               BDataType,
                               XDataType,
                               XDataType,
                               CDataType,
                               ALayout,
                               BLayout,
                               CLayout,
                               AElementOp,
                               BElementOp,
                               CElementOp,
                               AccDataType,
                               CShuffleDataType,
                               ScaleBlockSize>(argc, argv)
               ? 0
               : -1;
}
