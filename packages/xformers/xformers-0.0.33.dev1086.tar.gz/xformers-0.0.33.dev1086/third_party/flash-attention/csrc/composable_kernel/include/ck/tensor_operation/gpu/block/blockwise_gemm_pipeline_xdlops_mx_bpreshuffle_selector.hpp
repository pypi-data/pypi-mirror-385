// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#pragma once

#include "ck/tensor_operation/gpu/block/blockwise_gemm_pipeline_xdlops_v3_mx_bpreshuffle.hpp"

namespace ck {
template <BlockGemmPipelineVersion BlkGemmPipelineVer,
          BlockGemmPipelineScheduler BlkGemmPipeSche,
          index_t ThreadBlockSize,
          index_t ScaleBlockSize,
          typename ADataType,
          typename AScaleDataType,
          typename BDataType,
          typename BScaleDataType,
          typename ComputeDataType, // TODO: remove this as in this pipeline ADataType and BDataType
                                    // must be used for compute
          typename AccDataType,
          typename ATileDesc,
          typename BTileDesc,
          typename AMmaTileDesc,
          typename BMmaTileDesc,
          index_t ABlockTransferSrcScalarPerVector,
          index_t BBlockTransferSrcScalarPerVector,
          index_t MPerBlock,
          index_t NPerBlock,
          index_t KPerBlock,
          index_t MPerXDL,
          index_t NPerXDL,
          index_t MRepeat,
          index_t NRepeat,
          index_t KPack>
constexpr auto BlockGemmMXBPreshufflePipeline_Selector()
{

    // Hardware MX GEMM pipeline
    if constexpr(BlkGemmPipelineVer == BlockGemmPipelineVersion::v3)
    {
        return BlockwiseGemmXdlops_pipeline_v3_mx_bprehuffle<BlkGemmPipeSche,
                                                             ThreadBlockSize,
                                                             ScaleBlockSize,
                                                             ADataType,
                                                             AScaleDataType,
                                                             BDataType,
                                                             BScaleDataType,
                                                             ATileDesc,
                                                             BTileDesc,
                                                             AMmaTileDesc,
                                                             BMmaTileDesc,
                                                             ABlockTransferSrcScalarPerVector,
                                                             BBlockTransferSrcScalarPerVector,
                                                             MPerBlock,
                                                             NPerBlock,
                                                             KPerBlock,
                                                             MPerXDL,
                                                             NPerXDL,
                                                             MRepeat,
                                                             NRepeat,
                                                             KPack>{};
    }
    else
    {
        std::cerr << "MX GEMM Pipeline configuration is not available" << std::endl;
    }
}

} // namespace ck
