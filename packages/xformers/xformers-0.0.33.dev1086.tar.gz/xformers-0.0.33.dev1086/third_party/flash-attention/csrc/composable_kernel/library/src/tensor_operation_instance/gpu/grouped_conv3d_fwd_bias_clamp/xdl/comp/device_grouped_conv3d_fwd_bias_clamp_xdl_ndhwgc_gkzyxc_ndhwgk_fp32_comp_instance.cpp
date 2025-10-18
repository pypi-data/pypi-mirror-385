// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "ck/library/tensor_operation_instance/gpu/grouped_conv_fwd/device_grouped_conv_fwd_xdl_comp_instance.hpp"
#include "ck/library/tensor_operation_instance/add_device_operation_instance.hpp"
#include "ck/host_utility/device_prop.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

void add_device_grouped_conv3d_fwd_bias_clamp_xdl_ndhwgc_gkzyxc_ndhwgk_f32_comp_instances(
    std::vector<std::unique_ptr<DeviceGroupedConvFwdMultipleABD<3,
                                                                NDHWGC,
                                                                GKZYXC,
                                                                Tuple<NDHWGK>,
                                                                NDHWGK,
                                                                F32,
                                                                F32,
                                                                Tuple<F32>,
                                                                F32,
                                                                PassThrough,
                                                                PassThrough,
                                                                AddClamp>>>& instances)
{
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f32_comp_instances<3,
                                                                                  NDHWGC,
                                                                                  GKZYXC,
                                                                                  Tuple<NDHWGK>,
                                                                                  NDHWGK,
                                                                                  ConvFwdDefault,
                                                                                  Tuple<F32>,
                                                                                  AddClamp>{});
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f32_comp_instances<3,
                                                                                  NDHWGC,
                                                                                  GKZYXC,
                                                                                  Tuple<NDHWGK>,
                                                                                  NDHWGK,
                                                                                  ConvFwd1x1P0,
                                                                                  Tuple<F32>,
                                                                                  AddClamp>{});
    add_device_operation_instances(instances,
                                   device_grouped_conv_fwd_xdl_f32_comp_instances<3,
                                                                                  NDHWGC,
                                                                                  GKZYXC,
                                                                                  Tuple<NDHWGK>,
                                                                                  NDHWGK,
                                                                                  ConvFwd1x1S1P0,
                                                                                  Tuple<F32>,
                                                                                  AddClamp>{});
}

} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
