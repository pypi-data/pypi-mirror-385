#include "test_gemm_pipeline_kernel_types.hpp"
#include "test_gemm_pipeline_util.hpp"
#include "gtest/gtest.h"

template <typename T>
class TestCkTileGemmPipelineCompV4 : public TestCkTileGemmPipeline<T>
{
};

#define TEST_SUITE_NAME TestCkTileGemmPipelineCompV4

TYPED_TEST_SUITE(TestCkTileGemmPipelineCompV4, KernelTypesCompV4);

#include "test_gemm_pipeline_ut_cases.inc"

#undef TEST_SUITE_NAME
