// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#pragma once

#include <iomanip>
#include <iostream>
#include <typeinfo>

#include "ck/ck.hpp"
#include "ck/tensor_operation/gpu/device/tensor_layout.hpp"
#include "ck/tensor_operation/gpu/element/element_wise_operation.hpp"

#include "ck/library/tensor_operation_instance/gpu/grouped_convolution_forward_bias_clamp.hpp"

#include "ck/library/utility/algorithm.hpp"
#include "ck/library/utility/check_err.hpp"
#include "ck/library/utility/device_memory.hpp"
#include "ck/library/utility/host_tensor.hpp"
#include "ck/library/utility/host_tensor_generator.hpp"
#include "ck/library/utility/convolution_parameter.hpp"
#include "ck/library/utility/convolution_host_tensor_descriptor_helper.hpp"
#include "ck/library/reference_tensor_operation/cpu/reference_conv_fwd.hpp"

namespace ck {
namespace profiler {

// NOTE: Usage of NHWGK layout for GK bias is a workaround. This test is to
// just keep such implementation valid.
// TODO: Add possiblity to pass GK layout and GK lengths for bias and reuse
// the same instances.

template <ck::index_t NDimSpatial>
auto get_bias_desc(ck::index_t G, ck::index_t K)
{
    if constexpr(NDimSpatial == 1)
    {
        return HostTensorDescriptor({G, 1, K, 1}, {K, 0, 1, 0});
    }
    else if constexpr(NDimSpatial == 2)
    {
        return HostTensorDescriptor({G, 1, K, 1, 1}, {K, 0, 1, 0, 0});
    }
    else
    {
        return HostTensorDescriptor({G, 1, K, 1, 1, 1}, {K, 0, 1, 0, 0, 0});
    }
}

template <ck::index_t NDimSpatial,
          typename InLayout,
          typename WeiLayout,
          typename OutLayout,
          typename InDataType,
          typename WeiDataType,
          typename OutDataType,
          typename AComputeType = InDataType,
          typename BComputeType = AComputeType,
          typename IndexType    = ck::index_t,
          bool BiasGK           = false>
bool profile_grouped_conv_fwd_bias_clamp_impl(int do_verification,
                                              int init_method,
                                              bool do_log,
                                              bool time_kernel,
                                              const ck::utils::conv::ConvParam& conv_param)
{
    using InElementOp  = ck::tensor_operation::element_wise::PassThrough;
    using WeiElementOp = ck::tensor_operation::element_wise::PassThrough;
    using OutElementOp = ck::tensor_operation::element_wise::AddClamp;

    const float floor = 0.f;
    const float ceil  = 256.f;

    const auto in_element_op  = InElementOp{};
    const auto wei_element_op = WeiElementOp{};
    const auto out_element_op = OutElementOp{floor, ceil};

    const auto in_g_n_c_wis_desc =
        ck::utils::conv::make_input_host_tensor_descriptor_g_n_c_wis_packed<InLayout>(conv_param);

    const auto wei_g_k_c_xs_desc =
        ck::utils::conv::make_weight_host_tensor_descriptor_g_k_c_xs_packed<WeiLayout>(conv_param);

    const auto out_g_n_k_wos_desc =
        ck::utils::conv::make_output_host_tensor_descriptor_g_n_k_wos_packed<OutLayout>(conv_param);

    const index_t G = conv_param.G_;
    const index_t K = conv_param.K_;

    std::array<IndexType, NDimSpatial + 3> a_g_n_c_wis_lengths{};
    std::array<IndexType, NDimSpatial + 3> a_g_n_c_wis_strides{};
    std::array<IndexType, NDimSpatial + 3> b_g_k_c_xs_lengths{};
    std::array<IndexType, NDimSpatial + 3> b_g_k_c_xs_strides{};
    std::array<IndexType, NDimSpatial + 3> e_g_n_k_wos_lengths{};
    std::array<IndexType, NDimSpatial + 3> e_g_n_k_wos_strides{};
    std::array<IndexType, NDimSpatial + 3> d_g_n_k_wos_strides{};
    std::array<IndexType, NDimSpatial> conv_filter_strides{};
    std::array<IndexType, NDimSpatial> conv_filter_dilations{};
    std::array<IndexType, NDimSpatial> input_left_pads{};
    std::array<IndexType, NDimSpatial> input_right_pads{};

    auto copy = [](const auto& x, auto& y) { ck::ranges::copy(x, y.begin()); };

    copy(in_g_n_c_wis_desc.GetLengths(), a_g_n_c_wis_lengths);
    copy(in_g_n_c_wis_desc.GetStrides(), a_g_n_c_wis_strides);
    copy(wei_g_k_c_xs_desc.GetLengths(), b_g_k_c_xs_lengths);
    copy(wei_g_k_c_xs_desc.GetStrides(), b_g_k_c_xs_strides);
    copy(out_g_n_k_wos_desc.GetLengths(), e_g_n_k_wos_lengths);
    copy(out_g_n_k_wos_desc.GetStrides(), e_g_n_k_wos_strides);
    copy(out_g_n_k_wos_desc.GetStrides(), d_g_n_k_wos_strides);
    copy(conv_param.conv_filter_strides_, conv_filter_strides);
    copy(conv_param.conv_filter_dilations_, conv_filter_dilations);
    copy(conv_param.input_left_pads_, input_left_pads);
    copy(conv_param.input_right_pads_, input_right_pads);

    Tensor<InDataType> input(in_g_n_c_wis_desc);
    Tensor<WeiDataType> weight(wei_g_k_c_xs_desc);
    Tensor<OutDataType> host_output(out_g_n_k_wos_desc);
    Tensor<OutDataType> device_output(out_g_n_k_wos_desc);
    const auto bias_desc = BiasGK ? get_bias_desc<NDimSpatial>(G, K) : out_g_n_k_wos_desc;
    Tensor<OutDataType> bias(bias_desc);

    std::cout << "input: " << input.mDesc << std::endl;
    std::cout << "weight: " << weight.mDesc << std::endl;
    std::cout << "output: " << host_output.mDesc << std::endl;
    std::cout << "bias: " << bias.mDesc << std::endl;

    switch(init_method)
    {
    case 0: break;
    case 1:
        input.GenerateTensorValue(GeneratorTensor_2<InDataType>{-5, 5});
        weight.GenerateTensorValue(GeneratorTensor_2<WeiDataType>{-5, 5});
        bias.GenerateTensorValue(GeneratorTensor_2<OutDataType>{-5, 5});
        break;
    default:
        input.GenerateTensorValue(GeneratorTensor_3<InDataType>{0.0, 1.0});
        weight.GenerateTensorValue(GeneratorTensor_3<WeiDataType>{-0.5, 0.5});
        bias.GenerateTensorValue(GeneratorTensor_3<OutDataType>{-0.5, 0.5});
    }

    DeviceMem in_device_buf(sizeof(InDataType) * input.mDesc.GetElementSpaceSize());
    DeviceMem wei_device_buf(sizeof(WeiDataType) * weight.mDesc.GetElementSpaceSize());
    DeviceMem out_device_buf(sizeof(OutDataType) * device_output.mDesc.GetElementSpaceSize());

    const std::size_t bias_dev_buf_size =
        BiasGK ? sizeof(OutDataType) * G * K
               : sizeof(OutDataType) * device_output.mDesc.GetElementSpaceSize();
    DeviceMem bias_device_buf(bias_dev_buf_size);

    in_device_buf.ToDevice(input.mData.data());
    wei_device_buf.ToDevice(weight.mData.data());
    bias_device_buf.ToDevice(bias.mData.data());

    // run reference op
    if(do_verification)
    {
        auto ref_conv = ck::tensor_operation::host::ReferenceConvFwd<NDimSpatial,
                                                                     InDataType,
                                                                     WeiDataType,
                                                                     OutDataType,
                                                                     InElementOp,
                                                                     WeiElementOp,
                                                                     OutElementOp,
                                                                     0,
                                                                     0,
                                                                     1>{};

        std::array<Tensor<OutDataType>, 1> d_tensors = {bias};
        auto ref_invoker                             = ref_conv.MakeInvoker();
        auto ref_argument                            = ref_conv.MakeArgument(input,
                                                  weight,
                                                  host_output,
                                                  conv_param.conv_filter_strides_,
                                                  conv_param.conv_filter_dilations_,
                                                  conv_param.input_left_pads_,
                                                  conv_param.input_right_pads_,
                                                  in_element_op,
                                                  wei_element_op,
                                                  out_element_op,
                                                                             {},
                                                                             {},
                                                  d_tensors);

        // init host output to zero
        host_output.SetZero();

        ref_invoker.Run(ref_argument);
    }

    std::string best_op_name;
    float best_avg_time   = 0;
    float best_tflops     = 0;
    float best_gb_per_sec = 0;

    // profile device op instances
    bool pass = true;

    auto run_impl = [&](auto& op_ptr, auto& argument_ptr) {
        // workspace_sz will be equal to 0 for other layout than NGCHW
        const std::size_t workspace_sz = op_ptr->GetWorkSpaceSize(argument_ptr.get());
        DeviceMem workspace_dev(workspace_sz);
        op_ptr->SetWorkSpacePointer(argument_ptr.get(), workspace_dev.GetDeviceBuffer());

        if(op_ptr->IsSupportedArgument(argument_ptr.get()))
        {
            // re-init output to zero before profiling next kernel
            out_device_buf.SetZero();

            std::string op_name = op_ptr->GetTypeString();

            auto invoker_ptr = op_ptr->MakeInvokerPointer();

            float avg_time =
                invoker_ptr->Run(argument_ptr.get(), StreamConfig{nullptr, time_kernel});

            std::size_t flop      = conv_param.GetFlops();
            std::size_t num_btype = conv_param.GetByte<InDataType, WeiDataType, OutDataType>();

            float tflops = static_cast<float>(flop) / 1.E9 / avg_time;

            float gb_per_sec = num_btype / 1.E6 / avg_time;

            std::cout << "Perf: " << std::setw(10) << avg_time << " ms, " << tflops << " TFlops, "
                      << gb_per_sec << " GB/s, " << op_name << std::endl;

            if(tflops > best_tflops)
            {
                best_op_name    = op_name;
                best_tflops     = tflops;
                best_avg_time   = avg_time;
                best_gb_per_sec = gb_per_sec;
            }

            if(do_verification)
            {
                out_device_buf.FromDevice(device_output.mData.data());

                pass = pass & ck::utils::check_err(device_output, host_output);

                if(do_log)
                {
                    LogRangeAsType<float>(std::cout << "input : ", input.mData, ",") << std::endl;
                    LogRangeAsType<float>(std::cout << "weight: ", weight.mData, ",") << std::endl;
                    LogRangeAsType<float>(std::cout << "host_output  : ", host_output.mData, ",")
                        << std::endl;
                    LogRangeAsType<float>(std::cout << "device_output: ", device_output.mData, ",")
                        << std::endl;
                }
            }
        }
        else
        {
            std::cout << op_ptr->GetTypeString() << " does not support this problem" << std::endl;
        }
    };

    using DeviceOp =
        ck::tensor_operation::device::DeviceGroupedConvFwdMultipleABD<NDimSpatial,
                                                                      InLayout,
                                                                      WeiLayout,
                                                                      ck::Tuple<OutLayout>,
                                                                      OutLayout,
                                                                      InDataType,
                                                                      WeiDataType,
                                                                      ck::Tuple<OutDataType>,
                                                                      OutDataType,
                                                                      InElementOp,
                                                                      WeiElementOp,
                                                                      OutElementOp,
                                                                      AComputeType,
                                                                      BComputeType>;

    // get device op instances
    const auto op_ptrs = ck::tensor_operation::device::instance::DeviceOperationInstanceFactory<
        DeviceOp>::GetInstances();

    std::cout << "ckProfiler found " << op_ptrs.size() << " instances" << std::endl;

    if constexpr(BiasGK)
    {
        constexpr ck::index_t spatial_offset = 3;
        d_g_n_k_wos_strides[1]               = 0;
        for(int i = 0; i < NDimSpatial; i++)
        {
            d_g_n_k_wos_strides[i + spatial_offset] = 0;
        }
    }

    for(auto& op_ptr : op_ptrs)
    {
        auto argument_ptr = op_ptr->MakeArgumentPointer(in_device_buf.GetDeviceBuffer(),
                                                        wei_device_buf.GetDeviceBuffer(),
                                                        {bias_device_buf.GetDeviceBuffer()},
                                                        out_device_buf.GetDeviceBuffer(),
                                                        a_g_n_c_wis_lengths,
                                                        a_g_n_c_wis_strides,
                                                        b_g_k_c_xs_lengths,
                                                        b_g_k_c_xs_strides,
                                                        {e_g_n_k_wos_lengths},
                                                        {d_g_n_k_wos_strides},
                                                        e_g_n_k_wos_lengths,
                                                        e_g_n_k_wos_strides,
                                                        conv_filter_strides,
                                                        conv_filter_dilations,
                                                        input_left_pads,
                                                        input_right_pads,
                                                        in_element_op,
                                                        wei_element_op,
                                                        out_element_op);

        run_impl(op_ptr, argument_ptr);
    }

    std::cout << "Best configuration parameters:" << "\nname: " << best_op_name
              << "\navg_time: " << best_avg_time << "\ntflops: " << best_tflops
              << "\nGB/s: " << best_gb_per_sec << std::endl;

    return pass;
}

} // namespace profiler
} // namespace ck
