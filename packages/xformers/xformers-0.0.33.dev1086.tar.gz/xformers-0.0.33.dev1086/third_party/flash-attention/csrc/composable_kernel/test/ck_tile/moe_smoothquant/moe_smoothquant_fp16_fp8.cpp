// Copyright © Advanced Micro Devices, Inc., or its affiliates.
// SPDX-License-Identifier:  MIT

#include "moe_smoothquant.inc"

int main()
{
    std::vector<std::vector<std::string>> test_cases = generate_test_cases("fp16", "fp8");

    return !run_test_cases<ck_tile::half_t, ck_tile::fp8_t>(test_cases);
}
