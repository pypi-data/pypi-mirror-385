// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "ck/library/tensor_operation_instance/gpu/grouped_conv_fwd/device_grouped_conv_fwd_xdl_merged_groups_instance.hpp"
#include "ck/library/tensor_operation_instance/add_device_operation_instance.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

void add_device_grouped_conv3d_fwd_clamp_xdl_merged_groups_ndhwgc_gkzyxc_ndhwgk_bf16_instances(
    std::vector<std::unique_ptr<DeviceGroupedConvFwdMultipleABD<3,
                                                                NDHWGC,
                                                                GKZYXC,
                                                                Tuple<>,
                                                                NDHWGK,
                                                                BF16,
                                                                BF16,
                                                                Tuple<>,
                                                                BF16,
                                                                PassThrough,
                                                                PassThrough,
                                                                Clamp>>>& instances)
{
    add_device_operation_instances(
        instances,
        device_grouped_conv_fwd_xdl_merged_groups_bf16_instances<3,
                                                                 NDHWGC,
                                                                 GKZYXC,
                                                                 Tuple<>,
                                                                 NDHWGK,
                                                                 ConvFwdDefault,
                                                                 Tuple<>,
                                                                 Clamp>{});
    add_device_operation_instances(
        instances,
        device_grouped_conv_fwd_xdl_merged_groups_bf16_instances<3,
                                                                 NDHWGC,
                                                                 GKZYXC,
                                                                 Tuple<>,
                                                                 NDHWGK,
                                                                 ConvFwd3x3,
                                                                 Tuple<>,
                                                                 Clamp>{});
}

} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
