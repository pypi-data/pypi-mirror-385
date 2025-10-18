// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Advanced Micro Devices, Inc. All rights reserved.

#include "device_gemm_mx_xdl_bf6_bf6_bf16_mk_nk_mn.hpp"

namespace ck {
namespace tensor_operation {
namespace device {
namespace instance {

void add_device_gemm_mx_xdl_bf6_bf6_bf16_mk_nk_mn_default_instances(
    std::vector<std::unique_ptr<DeviceGemmMX<Row,
                                             Col,
                                             Row,
                                             BF6,
                                             E8M0PK,
                                             BF6,
                                             E8M0PK,
                                             BF16,
                                             32,
                                             PassThrough,
                                             PassThrough,
                                             PassThrough>>>& instances)
{
    add_device_operation_instances(
        instances, device_gemm_mx_xdl_bf6_bf6_bf16_mk_nk_mn_instances<Intrawave, GemmDefault>{});
}

} // namespace instance
} // namespace device
} // namespace tensor_operation
} // namespace ck
