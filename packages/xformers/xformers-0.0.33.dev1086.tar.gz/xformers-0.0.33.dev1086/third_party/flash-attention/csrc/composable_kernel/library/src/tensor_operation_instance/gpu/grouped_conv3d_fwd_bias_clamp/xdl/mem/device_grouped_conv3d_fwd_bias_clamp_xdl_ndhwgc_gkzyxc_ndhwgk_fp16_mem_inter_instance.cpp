// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "ck/library/tensor_operation_instance/gpu/grouped_conv_fwd/device_grouped_conv_fwd_xdl_mem_instance.hpp"
#include "ck/library/tensor_operation_instance/add_device_operation_instance.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

void add_device_grouped_conv3d_fwd_bias_clamp_xdl_ndhwgc_gkzyxc_ndhwgk_f16_mem_inter_instances(
    std::vector<std::unique_ptr<DeviceGroupedConvFwdMultipleABD<3,
                                                                NDHWGC,
                                                                GKZYXC,
                                                                Tuple<NDHWGK>,
                                                                NDHWGK,
                                                                F16,
                                                                F16,
                                                                Tuple<F16>,
                                                                F16,
                                                                PassThrough,
                                                                PassThrough,
                                                                AddClamp>>>& instances)
{
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f16_mem_instances<3,
                                                                                 NDHWGC,
                                                                                 GKZYXC,
                                                                                 Tuple<NDHWGK>,
                                                                                 NDHWGK,
                                                                                 ConvFwdDefault,
                                                                                 Interwave,
                                                                                 Tuple<F16>,
                                                                                 AddClamp>{});
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f16_mem_instances<3,
                                                                                 NDHWGC,
                                                                                 GKZYXC,
                                                                                 Tuple<NDHWGK>,
                                                                                 NDHWGK,
                                                                                 ConvFwd1x1P0,
                                                                                 Interwave,
                                                                                 Tuple<F16>,
                                                                                 AddClamp>{});
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f16_mem_instances<3,
                                                                                 NDHWGC,
                                                                                 GKZYXC,
                                                                                 Tuple<NDHWGK>,
                                                                                 NDHWGK,
                                                                                 ConvFwd1x1S1P0,
                                                                                 Interwave,
                                                                                 Tuple<F16>,
                                                                                 AddClamp>{});
}

} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
