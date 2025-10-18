// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#pragma once

#include "ck/tensor_operation/gpu/block/blockwise_gemm_pipeline_xdlops_base.hpp"

namespace ck {

// Compute optimized pipeline
// GlobalPrefetchStages: 2
// LocalPreFillStages: 1
// LocalPreFetchStages: 1
// LocalSharedMemoryBuffer: 1

template <BlockGemmPipelineScheduler BlkGemmPipelineVer,
          index_t BlockSize,
          typename ADataType,
          typename BDataType,
          typename ComputeDataType,
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
          index_t KPacks>
struct BlockwiseGemmXdlops_pipeline_bpreshuffle_gufusion_v3
{
};

template <index_t BlockSize,
          typename ADataType,
          typename BDataType,
          typename ComputeDataType,
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
          index_t KPack
          // ,bool TransposeC //disable transposec right now...
          >
struct BlockwiseGemmXdlops_pipeline_bpreshuffle_gufusion_v3<BlockGemmPipelineScheduler::Intrawave,
                                                            BlockSize,
                                                            ADataType,
                                                            BDataType,
                                                            ComputeDataType,
                                                            AccDataType,
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
                                                            KPack>
    : BlockwiseGemmXdlops_pipeline_base<BlockSize,
                                        ADataType,
                                        BDataType,
                                        ComputeDataType,
                                        AccDataType,
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
                                        KPack>

{
    using Base = BlockwiseGemmXdlops_pipeline_base<BlockSize,
                                                   ADataType,
                                                   BDataType,
                                                   ComputeDataType,
                                                   AccDataType,
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
                                                   KPack>;
    using Base::A_K1;
    using Base::B_K1;
    using Base::I0;
    using Base::I1;
    using Base::I2;
    using Base::KGroup;
    using Base::KRepeat;
    using Base::xdlops_gemm;
    using typename Base::HotLoopInstList;

    using Base::a_block_desc_m0_m1_m2_k;
    using Base::CalculateCThreadOriginDataIndex;
    using Base::CalculateCThreadOriginDataIndex8D;
    using Base::GetCBlockDescriptor_G_M0_N0_M1_N1_M2_M3_M4_N2;
    using Base::GetCBlockDescriptor_M0_N0_M1_N1_M2_M3_M4_N2;
    using Base::GetCBlockDescriptor_M0_N0_M1_N1_M2_N2_N3_N4;
    using Base::GetCThreadBuffer;
    using Base::GetCThreadDescriptor_G_M0_N0_M1_N1_M2_M3_M4_N2;
    using Base::GetCThreadDescriptor_M0_N0_M1_N1_M2_M3_M4_N2;
    using Base::GetCThreadDescriptor_M0_N0_M1_N1_M2_N2_N3_N4;
    using Base::MakeCGridDescriptor_G_M0_N0_M1_N1_M2_M3_M4_N2;
    using Base::MakeCGridDescriptor_M0_N0_M1_N1_M2_M3_M4_N2;

    using Base::AMmaKStride;
    using Base::BMmaKStride;

    using Base::MWaves;

    static constexpr index_t PrefetchStages        = 2;
    static constexpr index_t PrefillStages         = 1;
    static constexpr index_t GlobalBufferNum       = 1;
    static constexpr index_t HotloopLocalBufSwitch = MRepeat % 2 == 0 ? 0 : 1;

    template <typename TileDesc_M0_M1_M2_K>
    __host__ __device__ static constexpr auto MakeAGemmMmaTileDescriptor(const TileDesc_M0_M1_M2_K&)
    {
        constexpr index_t M0 = TileDesc_M0_M1_M2_K{}.GetLength(Number<0>{});
        constexpr index_t M1 = TileDesc_M0_M1_M2_K{}.GetLength(Number<1>{});
        constexpr index_t M2 = TileDesc_M0_M1_M2_K{}.GetLength(Number<2>{});
        constexpr index_t K2 = KPack / KGroup;
        constexpr index_t K1 = 64 / NPerXDL;
        constexpr index_t K0 = KRepeat * KGroup;

        return transform_tensor_descriptor(
            TileDesc_M0_M1_M2_K{},
            make_tuple(
                make_pass_through_transform(Number<M0>{}),
                make_pass_through_transform(Number<M1>{}),
                make_pass_through_transform(Number<M2>{}),
                make_unmerge_transform(make_tuple(Number<K0>{}, Number<K1>{}, Number<K2>{}))),
            make_tuple(Sequence<0>{}, Sequence<1>{}, Sequence<2>{}, Sequence<3>{}),
            make_tuple(Sequence<0>{}, Sequence<1>{}, Sequence<2>{}, Sequence<3, 4, 5>{}));
    }

    static constexpr auto a_block_desc_m0_m1_m2_k0_k1_k2 =
        MakeAGemmMmaTileDescriptor(a_block_desc_m0_m1_m2_k);

    __host__ __device__ static constexpr bool BlockHasHotloop(index_t num_loop)
    {
        return num_loop > PrefetchStages;
    }

    __host__ __device__ static constexpr TailNumber BlockLoopTailNum(index_t num_loop)
    {
        return num_loop % 2 == 0 ? TailNumber::Even : TailNumber::Odd;
    }

    __device__ static constexpr auto HotLoopScheduler()
    {
        // A/B split schedule
        // compiler is likely to use ds_read2 when instruction width smaller than 16bytes
        constexpr auto num_ds_read_inst_a =
            HotLoopInstList::A_LDS_Read_Width * sizeof(ADataType) == 16
                ? HotLoopInstList::A_LDS_Read_Inst_Num
                : HotLoopInstList::A_LDS_Read_Inst_Num / 2;

        constexpr auto num_ds_write_inst_a = HotLoopInstList::A_LDS_Write_Inst_Num;

        constexpr auto num_buffer_load_inst_a = HotLoopInstList::A_Buffer_Load_Inst_Num;
        constexpr auto num_buffer_load_inst_b = HotLoopInstList::B_Buffer_Load_Inst_Num * 2;

        static_assert(num_buffer_load_inst_a == num_ds_write_inst_a);

        constexpr auto num_mfma_inst = HotLoopInstList::C_MFMA_Inst_Num * 2;
        constexpr auto mfma_cycle    = HotLoopInstList::C_MFMA_Inst_Cycle;

        constexpr auto ds_read_a_issue_cycle =
            HotLoopInstList::A_LDS_Read_Width * sizeof(ADataType) == 16 ? 8 : 4;
        constexpr auto ds_read_a_mfma_rate =
            math::integer_divide_ceil(mfma_cycle - 4, 2 * ds_read_a_issue_cycle);

        // constexpr auto num_dsread_a_mfma =
        //     (num_ds_read_inst_a + ds_read_a_mfma_rate - 1) / ds_read_a_mfma_rate;

        constexpr auto num_total_stages = MRepeat;

        // Group num_mfma_perstage num_ds_read_a_perstage
        // since we want to reuse a local register buffer
        constexpr auto num_mfma_perstage      = num_mfma_inst / num_total_stages;
        constexpr auto num_ds_read_a_perstage = num_ds_read_inst_a / num_total_stages;

        constexpr auto num_ds_read_a_mfma_perstage =
            math::integer_divide_ceil(num_ds_read_a_perstage, ds_read_a_mfma_rate);

        constexpr auto num_ds_read_a_prefetch_stages = 2;

        constexpr auto buffer_load_perstage_more = math::integer_divide_ceil(
            (num_buffer_load_inst_a + num_buffer_load_inst_b), (num_total_stages - 2));
        constexpr auto buffer_load_perstage_less = math::integer_divide_floor(
            (num_buffer_load_inst_a + num_buffer_load_inst_b), (num_total_stages - 2));

        constexpr auto buffer_load_stages_more =
            (num_buffer_load_inst_a + num_buffer_load_inst_b) -
            math::integer_divide_floor((num_buffer_load_inst_a + num_buffer_load_inst_b),
                                       (num_total_stages - 2)) *
                ((num_total_stages - 2));

        constexpr auto buffer_load_b_stages =
            buffer_load_perstage_more * buffer_load_stages_more > num_buffer_load_inst_b
                ? num_buffer_load_inst_b / buffer_load_perstage_more
                : (buffer_load_stages_more +
                   (num_buffer_load_inst_b - buffer_load_perstage_more * buffer_load_stages_more) /
                       buffer_load_perstage_less);

        constexpr auto buffer_load_a_stages =
            num_total_stages - num_ds_read_a_prefetch_stages - buffer_load_b_stages;

        constexpr auto buffer_load_issue_point_b = 0;
        constexpr auto buffer_load_issue_point_interval_more =
            num_mfma_perstage / buffer_load_perstage_more;
        constexpr auto buffer_load_issue_point_interval_less =
            num_mfma_perstage / buffer_load_perstage_less;
        constexpr auto ds_write_issue_point      = 0;
        constexpr auto buffer_load_issue_point_a = num_mfma_perstage >= 3 ? 1 : 0;

        // B global read
        static_for<0, buffer_load_b_stages, 1>{}([&](auto i) {
            static_for<0, num_mfma_perstage, 1>{}([&](auto imfma) {
                __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA

                if constexpr(((i < buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_more ==
                               buffer_load_issue_point_b)) ||
                             ((i >= buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_less ==
                               buffer_load_issue_point_b)))
                {
                    __builtin_amdgcn_sched_group_barrier(0x020, 1, 0); // VMEM read
                }

                if constexpr(imfma >= (num_mfma_perstage - num_ds_read_a_mfma_perstage))
                {
                    __builtin_amdgcn_sched_group_barrier(0x100, ds_read_a_mfma_rate, 0); // DS read
                }
            });
        });

        // A global read + A local write
        static_for<0, buffer_load_a_stages, 1>{}([&](auto i) {
            static_for<0, num_mfma_perstage, 1>{}([&](auto imfma) {
                __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA
                if constexpr((((i + buffer_load_b_stages) < buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_more ==
                               ds_write_issue_point)) ||
                             (((i + buffer_load_b_stages) >= buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_less ==
                               ds_write_issue_point)))
                {
                    __builtin_amdgcn_sched_group_barrier(0x200, 1, 0); // DS write
                }
                if constexpr((((i + buffer_load_b_stages) < buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_more ==
                               buffer_load_issue_point_a)) ||
                             (((i + buffer_load_b_stages) >= buffer_load_stages_more) &&
                              (imfma % buffer_load_issue_point_interval_less ==
                               buffer_load_issue_point_a)))
                {
                    __builtin_amdgcn_sched_group_barrier(0x020, 1, 0); // VMEM read
                }
                if constexpr(imfma >= (num_mfma_perstage - num_ds_read_a_mfma_perstage))
                {
                    __builtin_amdgcn_sched_group_barrier(0x100, ds_read_a_mfma_rate, 0); // DS read
                }
            });
        });

        // lds synchronization, prefetch next loop local A
        static_for<0, num_ds_read_a_prefetch_stages, 1>{}([&](auto i) {
            ignore = i;
            static_for<0, num_mfma_perstage, 1>{}([&](auto imfma) {
                __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA
                if constexpr(imfma >= (num_mfma_perstage - num_ds_read_a_mfma_perstage))
                {
                    __builtin_amdgcn_sched_group_barrier(0x100, ds_read_a_mfma_rate, 0); // DS read
                }
            });
        });
    }

    template <typename Stage>
    __device__ static constexpr auto EpilogueScheduler_1(Stage stage)
    {
        constexpr auto num_ds_read_inst_a  = HotLoopInstList::A_LDS_Read_Inst_Num;
        constexpr auto num_ds_write_inst_a = HotLoopInstList::A_LDS_Write_Inst_Num;
        constexpr auto num_buffer_load_inst_b =
            MWaves * HotLoopInstList::B_Buffer_Load_Inst_Num * 2;

        constexpr auto num_mfma = HotLoopInstList::C_MFMA_Inst_Num * 2;

        constexpr auto staged_num_ds_read_inst_a = num_ds_read_inst_a / MRepeat;
        constexpr auto staged_num_mfma           = num_mfma / MRepeat;

        constexpr auto staged_num_mfma_per_ds_read_a = staged_num_mfma / staged_num_ds_read_inst_a;

        if constexpr(stage.value == 0)
        {
            constexpr auto staged_num_buffer_load_b_per_ds_read_a =
                num_buffer_load_inst_b / staged_num_ds_read_inst_a;
            constexpr auto staged_num_mfma_per_buffer_load_b =
                staged_num_mfma / num_buffer_load_inst_b;
            // B global
            static_for<0, staged_num_ds_read_inst_a, 1>{}([&](auto i_inst) {
                ignore = i_inst;

                static_for<0, staged_num_buffer_load_b_per_ds_read_a, 1>{}([&](auto ibuf_inst) {
                    ignore = ibuf_inst;
                    __builtin_amdgcn_sched_group_barrier(
                        0x008, staged_num_mfma_per_buffer_load_b, 0);  // MFMA
                    __builtin_amdgcn_sched_group_barrier(0x020, 1, 0); // VMEM read
                });

                __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA
                __builtin_amdgcn_sched_group_barrier(0x100, 1, 0); // DS read
                __builtin_amdgcn_sched_group_barrier(
                    0x008, staged_num_mfma_per_buffer_load_b - 1, 0); // MFMA
                __builtin_amdgcn_sched_group_barrier(0x020, 1, 0);    // VMEM read
            });

            __builtin_amdgcn_sched_barrier(0);
        }
        else if constexpr(stage.value == 1)
        {
            constexpr auto staged_num_mfma_per_ds_write_a =
                math::integer_divide_ceil(staged_num_mfma, num_ds_write_inst_a);

            constexpr auto stage_more_mfma =
                staged_num_mfma - (staged_num_mfma_per_ds_write_a - 1) * num_ds_write_inst_a;

            // A local write
            static_for<0, num_ds_write_inst_a, 1>{}([&](auto i_inst) {
                if constexpr(i_inst.value < stage_more_mfma)
                {
                    if(i_inst.value < staged_num_ds_read_inst_a)
                    {
                        __builtin_amdgcn_sched_group_barrier(
                            0x008, staged_num_mfma_per_ds_write_a - 1, 0); // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x200, 1, 0); // DS Write
                        __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x100, 1, 0); // DS read
                    }
                    else
                    {
                        __builtin_amdgcn_sched_group_barrier(
                            0x008, staged_num_mfma_per_ds_write_a, 0);     // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x200, 1, 0); // DS Write
                    }
                }
                else
                {
                    if(i_inst.value < staged_num_ds_read_inst_a)
                    {
                        __builtin_amdgcn_sched_group_barrier(
                            0x008, staged_num_mfma_per_ds_write_a - 2, 0); // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x200, 1, 0); // DS Write
                        __builtin_amdgcn_sched_group_barrier(0x008, 1, 0); // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x100, 1, 0); // DS read
                    }
                    else
                    {
                        __builtin_amdgcn_sched_group_barrier(
                            0x008, staged_num_mfma_per_ds_write_a - 1, 0); // MFMA
                        __builtin_amdgcn_sched_group_barrier(0x200, 1, 0); // DS Write
                    }
                }
            });
            __builtin_amdgcn_sched_barrier(0);
        }
        else
        {
            // A local Read
            static_for<0, staged_num_ds_read_inst_a, 1>{}([&](auto i_inst) {
                ignore = i_inst;
                __builtin_amdgcn_sched_group_barrier(
                    0x008, staged_num_mfma_per_ds_read_a, 0);      // MFMA
                __builtin_amdgcn_sched_group_barrier(0x100, 1, 0); // DS read
            });

            __builtin_amdgcn_sched_barrier(0);
        }
    }

    __device__ static constexpr auto EpilogueScheduler_2()
    {
        constexpr auto num_ds_read_inst_a = HotLoopInstList::A_LDS_Read_Inst_Num;

        constexpr auto num_mfma = HotLoopInstList::C_MFMA_Inst_Num * 2;

        constexpr auto staged_num_ds_read_inst_a = num_ds_read_inst_a / MRepeat;
        constexpr auto staged_num_mfma           = num_mfma / MRepeat;

        constexpr auto staged_num_mfma_per_ds_read_a = staged_num_mfma / staged_num_ds_read_inst_a;

        // A local Read
        static_for<0, staged_num_ds_read_inst_a, 1>{}([&](auto i_inst) {
            ignore = i_inst;
            __builtin_amdgcn_sched_group_barrier(0x008, staged_num_mfma_per_ds_read_a, 0); // MFMA
            __builtin_amdgcn_sched_group_barrier(0x100, 1, 0); // DS read
        });

        __builtin_amdgcn_sched_barrier(0);
    }

    template <bool HasMainLoop,
              TailNumber TailNum,
              typename AGridDesc,
              typename ABlockDesc,
              typename ABlockTransfer,
              typename AGridBuffer,
              typename ABlockBuffer,
              typename ABlockTransferStep,
              typename BGridDesc,
              typename BBlockTransfer,
              typename BGridBuffer,
              typename BBlockBuffer,
              typename BBlockTransferStep,
              typename CThreadBuffer>
    __device__ void Run(const AGridDesc& a_grid_desc,
                        const ABlockDesc& a_block_desc,
                        ABlockTransfer& a_blockwise_copy,
                        const AGridBuffer& a_grid_buf,
                        ABlockBuffer& a_block_buf,
                        const ABlockTransferStep& a_block_copy_step,
                        const BGridDesc& b_grid_desc,
                        BBlockTransfer& b_blockwise_copy,
                        BBlockTransfer& b_blockwise_copy_up,
                        const BGridBuffer& b_grid_buf,
                        const BGridBuffer& b_grid_buf_up,
                        BBlockBuffer& b_block_buf,
                        const BBlockTransferStep& b_block_copy_step,
                        CThreadBuffer& c_thread_buf,
                        CThreadBuffer& c_thread_buf_up,
                        index_t num_loop) const
    {
        ignore = b_block_buf;
        __builtin_amdgcn_sched_barrier(0);
        auto a_thread_buf = make_static_buffer<AddressSpaceEnum::Vgpr, ComputeDataType>(
            a_thread_desc_.GetElementSpaceSize());
        auto b_thread_buf = make_static_buffer<AddressSpaceEnum::Vgpr, ComputeDataType>(
            b_thread_desc_.GetElementSpaceSize());

        StaticallyIndexedArray<decltype(b_thread_buf), Number<2>{}> b_thread_bufs;
        StaticallyIndexedArray<decltype(b_thread_buf), Number<2>{}> b_thread_bufs_up;
        constexpr auto b_block_origin_idx = make_tuple(I0, I0, I0, I0);

        // Global prefetch A1 B1
        b_blockwise_copy.Run(b_grid_desc,
                             b_grid_buf,
                             b_block_desc_n0_n1_k0_k1,
                             b_block_origin_idx,
                             b_thread_bufs(I0));

        b_blockwise_copy_up.Run(b_grid_desc,
                                b_grid_buf_up,
                                b_block_desc_n0_n1_k0_k1,
                                b_block_origin_idx,
                                b_thread_bufs_up(I0));
        b_blockwise_copy.MoveSrcSliceWindow(b_grid_desc, b_block_copy_step);
        b_blockwise_copy_up.MoveSrcSliceWindow(b_grid_desc, b_block_copy_step);

        a_blockwise_copy.RunRead(a_grid_desc, a_grid_buf);
        a_blockwise_copy.MoveSrcSliceWindow(a_grid_desc, a_block_copy_step);
        __builtin_amdgcn_sched_barrier(0);

        // // Local prefill A1
        a_blockwise_copy.RunWrite(a_block_desc, a_block_buf.At(I0));

        // // Global prefetch A2
        a_blockwise_copy.RunRead(a_grid_desc, a_grid_buf);
        a_blockwise_copy.MoveSrcSliceWindow(a_grid_desc, a_block_copy_step);

        // Local prefetch A1
        block_sync_lds();
        static_for<0, 2, 1>{}([&](auto m0) {
            static_for<0, KRepeat, 1>{}([&](auto k0) {
                static_for<0, KGroup, 1>{}([&](auto kg0) {
                    a_thread_copy_.Run(a_block_desc_m0_m1_m2_k0_k1_k2,
                                       make_tuple(m0, I0, I0, Number<k0 * KGroup + kg0>{}, I0, I0),
                                       a_block_buf.At(I0),
                                       a_thread_desc_,
                                       make_tuple(m0, I0, I0, k0, I0, Number<kg0 * A_K1>{}),
                                       a_thread_buf);
                });
            });
        });

        // Initialize C
        c_thread_buf.Clear();
        c_thread_buf_up.Clear();

        __builtin_amdgcn_sched_barrier(0);

        // main body
        if constexpr(HasMainLoop)
        {
            index_t i = 0;
            do
            {
                auto LoopFunc = [&](auto mfma_reg_buf, auto local_read_buf) {
                    b_blockwise_copy.Run(b_grid_desc,
                                         b_grid_buf,
                                         b_block_desc_n0_n1_k0_k1,
                                         b_block_origin_idx,
                                         b_thread_bufs(local_read_buf));
                    b_blockwise_copy.MoveSrcSliceWindow(b_grid_desc, b_block_copy_step);
                    b_blockwise_copy_up.Run(b_grid_desc,
                                            b_grid_buf_up,
                                            b_block_desc_n0_n1_k0_k1,
                                            b_block_origin_idx,
                                            b_thread_bufs_up(local_read_buf));
                    b_blockwise_copy_up.MoveSrcSliceWindow(b_grid_desc, b_block_copy_step);

                    a_blockwise_copy.RunWrite(a_block_desc, a_block_buf.At(local_read_buf));
                    a_blockwise_copy.RunRead(a_grid_desc, a_grid_buf);
                    a_blockwise_copy.MoveSrcSliceWindow(a_grid_desc, a_block_copy_step);
                    static_for<0, MRepeat, 1>{}([&](auto m0) {
                        static_for<0, KRepeat, 1>{}([&](auto k0) {
                            static_for<0, NRepeat, 1>{}([&](auto n0) {
                                vector_type<ComputeDataType, KPack> a_thread_vec;
                                vector_type<ComputeDataType, KPack> b_thread_vec;
                                vector_type<ComputeDataType, KPack> b_thread_vec_up;

                                static_for<0, KPack, 1>{}([&](auto ik) {
                                    a_thread_vec.template AsType<ComputeDataType>()(ik) =
                                        a_thread_buf[Number<a_thread_desc_.CalculateOffset(
                                            make_tuple((m0 + HotloopLocalBufSwitch * mfma_reg_buf) %
                                                           2,
                                                       I0,
                                                       I0,
                                                       k0,
                                                       I0,
                                                       ik))>{}];
                                    b_thread_vec.template AsType<ComputeDataType>()(ik) =
                                        b_thread_bufs[mfma_reg_buf]
                                                     [Number<b_thread_desc_.CalculateOffset(
                                                         make_tuple(n0, I0, k0, ik))>{}];

                                    b_thread_vec_up.template AsType<ComputeDataType>()(ik) =
                                        b_thread_bufs_up[mfma_reg_buf]
                                                        [Number<b_thread_desc_.CalculateOffset(
                                                            make_tuple(n0, I0, k0, ik))>{}];
                                });

                                using mfma_input_type =
                                    typename vector_type<ComputeDataType,
                                                         xdlops_gemm.K1PerXdlops>::type;

                                constexpr index_t c_offset =
                                    c_thread_desc_.CalculateOffset(make_tuple(m0, n0, 0));

                                xdlops_gemm.Run(
                                    a_thread_vec.template AsType<mfma_input_type>(),
                                    b_thread_vec.template AsType<mfma_input_type>(),
                                    c_thread_buf.GetVectorTypeReference(Number<c_offset>{}));

                                xdlops_gemm.Run(
                                    a_thread_vec.template AsType<mfma_input_type>(),
                                    b_thread_vec_up.template AsType<mfma_input_type>(),
                                    c_thread_buf_up.GetVectorTypeReference(Number<c_offset>{}));
                            });
                        });

                        if constexpr(m0.value == MRepeat - 2)
                        {
                            block_sync_lds();

                            static_for<0, KRepeat, 1>{}([&](auto k0) {
                                static_for<0, KGroup, 1>{}([&](auto kg0) {
                                    a_thread_copy_.Run(
                                        a_block_desc_m0_m1_m2_k0_k1_k2,
                                        make_tuple(Number<(m0 + 2) % MRepeat>{},
                                                   I0,
                                                   I0,
                                                   Number<k0 * KGroup + kg0>{},
                                                   I0,
                                                   I0),
                                        a_block_buf.At(local_read_buf),
                                        a_thread_desc_,
                                        make_tuple(
                                            Number<(m0 + 2 + HotloopLocalBufSwitch * mfma_reg_buf) %
                                                   2>{},
                                            I0,
                                            I0,
                                            k0,
                                            I0,
                                            Number<kg0 * A_K1>{}),
                                        a_thread_buf);
                                });
                            });
                        }
                        else if constexpr(m0.value == (MRepeat - 1))
                        {
                            static_for<0, KRepeat, 1>{}([&](auto k0) {
                                static_for<0, KGroup, 1>{}([&](auto kg0) {
                                    a_thread_copy_.Run(
                                        a_block_desc_m0_m1_m2_k0_k1_k2,
                                        make_tuple(Number<(m0 + 2) % MRepeat>{},
                                                   I0,
                                                   I0,
                                                   Number<k0 * KGroup + kg0>{},
                                                   I0,
                                                   I0),
                                        a_block_buf.At(local_read_buf),
                                        a_thread_desc_,
                                        make_tuple(
                                            Number<(m0 + 2 + HotloopLocalBufSwitch * mfma_reg_buf) %
                                                   2>{},
                                            I0,
                                            I0,
                                            k0,
                                            I0,
                                            Number<kg0 * A_K1>{}),
                                        a_thread_buf);
                                });
                            });
                        }
                        else
                        {
                            static_for<0, KRepeat, 1>{}([&](auto k0) {
                                static_for<0, KGroup, 1>{}([&](auto kg0) {
                                    a_thread_copy_.Run(
                                        a_block_desc_m0_m1_m2_k0_k1_k2,
                                        make_tuple(Number<(m0 + 2) % MRepeat>{},
                                                   I0,
                                                   I0,
                                                   Number<k0 * KGroup + kg0>{},
                                                   I0,
                                                   I0),
                                        a_block_buf.At(mfma_reg_buf),
                                        a_thread_desc_,
                                        make_tuple(
                                            Number<(m0 + 2 + HotloopLocalBufSwitch * mfma_reg_buf) %
                                                   2>{},
                                            I0,
                                            I0,
                                            k0,
                                            I0,
                                            Number<kg0 * A_K1>{}),
                                        a_thread_buf);
                                });
                            });
                        }
                    });
                    HotLoopScheduler();
                };

                LoopFunc(I0, I1);
                LoopFunc(I1, I0);

                i += 2;
            } while(i < (num_loop - 2));
        }
        // tail
        if constexpr(TailNum == TailNumber::Even)
        {
            b_blockwise_copy.Run(b_grid_desc,
                                 b_grid_buf,
                                 b_block_desc_n0_n1_k0_k1,
                                 b_block_origin_idx,
                                 b_thread_bufs(I1));

            b_blockwise_copy_up.Run(b_grid_desc,
                                    b_grid_buf_up,
                                    b_block_desc_n0_n1_k0_k1,
                                    b_block_origin_idx,
                                    b_thread_bufs_up(I1));
            a_blockwise_copy.RunWrite(a_block_desc, a_block_buf.At(I1));
            static_for<0, MRepeat, 1>{}([&](auto m0) {
                static_for<0, KRepeat, 1>{}([&](auto k0) {
                    static_for<0, NRepeat, 1>{}([&](auto n0) {
                        vector_type<ComputeDataType, KPack> a_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec_up;

                        static_for<0, KPack, 1>{}([&](auto ik) {
                            a_thread_vec.template AsType<ComputeDataType>()(ik) =
                                a_thread_buf[Number<a_thread_desc_.CalculateOffset(
                                    make_tuple(m0 % 2, I0, I0, k0, I0, ik))>{}];
                            b_thread_vec.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs[I0][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];

                            b_thread_vec_up.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs_up[I0][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];
                        });

                        using mfma_input_type =
                            typename vector_type<ComputeDataType, xdlops_gemm.K1PerXdlops>::type;

                        constexpr index_t c_offset =
                            c_thread_desc_.CalculateOffset(make_tuple(m0, n0, 0));

                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec.template AsType<mfma_input_type>(),
                                        c_thread_buf.GetVectorTypeReference(Number<c_offset>{}));

                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec_up.template AsType<mfma_input_type>(),
                                        c_thread_buf_up.GetVectorTypeReference(Number<c_offset>{}));
                    });
                });
                if constexpr(m0.value == (MRepeat - 2))
                {
                    block_sync_lds();

                    static_for<0, KRepeat, 1>{}([&](auto k0) {
                        static_for<0, KGroup, 1>{}([&](auto kg0) {
                            a_thread_copy_.Run(
                                a_block_desc_m0_m1_m2_k0_k1_k2,
                                make_tuple(Number<(m0 + 2) % MRepeat>{},
                                           I0,
                                           I0,
                                           Number<k0 * KGroup + kg0>{},
                                           I0,
                                           I0),
                                a_block_buf.At(I1),
                                a_thread_desc_,
                                make_tuple(
                                    Number<(m0 + 2) % 2>{}, I0, I0, k0, I0, Number<kg0 * A_K1>{}),
                                a_thread_buf);
                        });
                    });
                }
                else if constexpr(m0.value == MRepeat - 1)
                {
                    static_for<0, KRepeat, 1>{}([&](auto k0) {
                        static_for<0, KGroup, 1>{}([&](auto kg0) {
                            a_thread_copy_.Run(
                                a_block_desc_m0_m1_m2_k0_k1_k2,
                                make_tuple(Number<(m0 + 2) % MRepeat>{},
                                           I0,
                                           I0,
                                           Number<k0 * KGroup + kg0>{},
                                           I0,
                                           I0),
                                a_block_buf.At(I1),
                                a_thread_desc_,
                                make_tuple(
                                    Number<(m0 + 2) % 2>{}, I0, I0, k0, I0, Number<kg0 * A_K1>{}),
                                a_thread_buf);
                        });
                    });
                }
                else
                {
                    static_for<0, KRepeat, 1>{}([&](auto k0) {
                        static_for<0, KGroup, 1>{}([&](auto kg0) {
                            a_thread_copy_.Run(
                                a_block_desc_m0_m1_m2_k0_k1_k2,
                                make_tuple(Number<(m0 + 2) % MRepeat>{},
                                           I0,
                                           I0,
                                           Number<k0 * KGroup + kg0>{},
                                           I0,
                                           I0),
                                a_block_buf.At(I0),
                                a_thread_desc_,
                                make_tuple(
                                    Number<(m0 + 2) % 2>{}, I0, I0, k0, I0, Number<kg0 * A_K1>{}),
                                a_thread_buf);
                        });
                    });
                }
            });

            HotLoopScheduler();

            static_for<0, MRepeat, 1>{}([&](auto m0) {
                static_for<0, KRepeat, 1>{}([&](auto k0) {
                    static_for<0, NRepeat, 1>{}([&](auto n0) {
                        vector_type<ComputeDataType, KPack> a_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec_up;

                        static_for<0, KPack, 1>{}([&](auto ik) {
                            a_thread_vec.template AsType<ComputeDataType>()(ik) =
                                a_thread_buf[Number<a_thread_desc_.CalculateOffset(make_tuple(
                                    (m0 + HotloopLocalBufSwitch) % 2, I0, I0, k0, I0, ik))>{}];
                            b_thread_vec.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs[I1][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];
                            b_thread_vec_up.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs_up[I1][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];
                        });

                        using mfma_input_type =
                            typename vector_type<ComputeDataType, xdlops_gemm.K1PerXdlops>::type;

                        constexpr index_t c_offset =
                            c_thread_desc_.CalculateOffset(make_tuple(m0, n0, 0));

                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec.template AsType<mfma_input_type>(),
                                        c_thread_buf.GetVectorTypeReference(Number<c_offset>{}));

                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec_up.template AsType<mfma_input_type>(),
                                        c_thread_buf_up.GetVectorTypeReference(Number<c_offset>{}));
                    });
                });

                if constexpr(m0.value < (MRepeat - 2))
                {
                    static_for<0, KRepeat, 1>{}([&](auto k0) {
                        static_for<0, KGroup, 1>{}([&](auto kg0) {
                            a_thread_copy_.Run(
                                a_block_desc_m0_m1_m2_k0_k1_k2,
                                make_tuple(
                                    Number<m0 + 2>{}, I0, I0, Number<k0 * KGroup + kg0>{}, I0, I0),
                                a_block_buf.At(I1),
                                a_thread_desc_,
                                make_tuple(Number<(m0 + 2 + HotloopLocalBufSwitch) % 2>{},
                                           I0,
                                           I0,
                                           k0,
                                           I0,
                                           Number<kg0 * A_K1>{}),
                                a_thread_buf);
                        });
                    });
                }
            });

            HotLoopScheduler();
            // Let's leak last MFMA block to epilogue region, cover the potential lds-shuffle
            // latency
        }
        else if constexpr(TailNum == TailNumber::Odd)
        {
            static_for<0, MRepeat, 1>{}([&](auto m0) {
                static_for<0, KRepeat, 1>{}([&](auto k0) {
                    static_for<0, NRepeat, 1>{}([&](auto n0) {
                        vector_type<ComputeDataType, KPack> a_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec;
                        vector_type<ComputeDataType, KPack> b_thread_vec_up;

                        static_for<0, KPack, 1>{}([&](auto ik) {
                            a_thread_vec.template AsType<ComputeDataType>()(ik) =
                                a_thread_buf[Number<a_thread_desc_.CalculateOffset(
                                    make_tuple(m0 % 2, I0, I0, k0, I0, ik))>{}];
                            b_thread_vec.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs[I0][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];
                            b_thread_vec_up.template AsType<ComputeDataType>()(ik) =
                                b_thread_bufs_up[I0][Number<b_thread_desc_.CalculateOffset(
                                    make_tuple(n0, I0, k0, ik))>{}];
                        });

                        using mfma_input_type =
                            typename vector_type<ComputeDataType, xdlops_gemm.K1PerXdlops>::type;

                        constexpr index_t c_offset =
                            c_thread_desc_.CalculateOffset(make_tuple(m0, n0, 0));

                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec.template AsType<mfma_input_type>(),
                                        c_thread_buf.GetVectorTypeReference(Number<c_offset>{}));
                        xdlops_gemm.Run(a_thread_vec.template AsType<mfma_input_type>(),
                                        b_thread_vec_up.template AsType<mfma_input_type>(),
                                        c_thread_buf_up.GetVectorTypeReference(Number<c_offset>{}));
                    });
                });

                if constexpr(m0.value < (MRepeat - 2))
                {
                    static_for<0, KRepeat, 1>{}([&](auto k0) {
                        static_for<0, KGroup, 1>{}([&](auto kg0) {
                            a_thread_copy_.Run(
                                a_block_desc_m0_m1_m2_k0_k1_k2,
                                make_tuple(
                                    Number<m0 + 2>{}, I0, I0, Number<k0 * KGroup + kg0>{}, I0, I0),
                                a_block_buf.At(I0),
                                a_thread_desc_,
                                make_tuple(
                                    Number<(m0 + 2) % 2>{}, I0, I0, k0, I0, Number<kg0 * A_K1>{}),
                                a_thread_buf);
                        });
                    });
                }
            });
        }
    }

    protected:
    // MRepeat MWave MLane KRepeat KLane KPack
    // KRepeat -> MRepeat-> Mwave->KLane->MLane->KPack
    // Reduce the vgpr usage here.
    static constexpr auto a_thread_desc_ = make_naive_tensor_descriptor_packed(
        make_tuple(I2, I1, I1, Number<KRepeat>{}, I1, Number<KPack>{}));

    using AThreadCopy = ThreadwiseTensorSliceTransfer_v4<ADataType,
                                                         ComputeDataType,
                                                         decltype(a_block_desc_m0_m1_m2_k0_k1_k2),
                                                         decltype(a_thread_desc_),
                                                         Sequence<1, 1, 1, 1, 1, KPack / KGroup>,
                                                         Sequence<0, 1, 2, 3, 4, 5>,
                                                         5,
                                                         A_K1,
                                                         A_K1>;

    AThreadCopy a_thread_copy_{Base::CalculateAThreadOriginDataIndex6D()};

    static constexpr auto b_thread_desc_ = make_naive_tensor_descriptor_packed(
        make_tuple(Number<NRepeat>{}, I1, Number<KRepeat>{}, Number<KPack>{}));

    static constexpr BTileDesc b_block_desc_n0_n1_k0_k1;

    using Base::c_thread_desc_;
};

} // namespace ck
