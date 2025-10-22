# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NVIDIA-SOFTWARE-LICENSE

# This code was automatically generated with version 12.9.0. Do not modify it directly.
cimport cuda.bindings._bindings.cynvrtc as cynvrtc

cdef const char* nvrtcGetErrorString(nvrtcResult result) except ?NULL nogil:
    return cynvrtc._nvrtcGetErrorString(result)

cdef nvrtcResult nvrtcVersion(int* major, int* minor) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcVersion(major, minor)

cdef nvrtcResult nvrtcGetNumSupportedArchs(int* numArchs) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetNumSupportedArchs(numArchs)

cdef nvrtcResult nvrtcGetSupportedArchs(int* supportedArchs) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetSupportedArchs(supportedArchs)

cdef nvrtcResult nvrtcCreateProgram(nvrtcProgram* prog, const char* src, const char* name, int numHeaders, const char** headers, const char** includeNames) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcCreateProgram(prog, src, name, numHeaders, headers, includeNames)

cdef nvrtcResult nvrtcDestroyProgram(nvrtcProgram* prog) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcDestroyProgram(prog)

cdef nvrtcResult nvrtcCompileProgram(nvrtcProgram prog, int numOptions, const char** options) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcCompileProgram(prog, numOptions, options)

cdef nvrtcResult nvrtcGetPTXSize(nvrtcProgram prog, size_t* ptxSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetPTXSize(prog, ptxSizeRet)

cdef nvrtcResult nvrtcGetPTX(nvrtcProgram prog, char* ptx) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetPTX(prog, ptx)

cdef nvrtcResult nvrtcGetCUBINSize(nvrtcProgram prog, size_t* cubinSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetCUBINSize(prog, cubinSizeRet)

cdef nvrtcResult nvrtcGetCUBIN(nvrtcProgram prog, char* cubin) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetCUBIN(prog, cubin)

cdef nvrtcResult nvrtcGetNVVMSize(nvrtcProgram prog, size_t* nvvmSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetNVVMSize(prog, nvvmSizeRet)

cdef nvrtcResult nvrtcGetNVVM(nvrtcProgram prog, char* nvvm) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetNVVM(prog, nvvm)

cdef nvrtcResult nvrtcGetLTOIRSize(nvrtcProgram prog, size_t* LTOIRSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetLTOIRSize(prog, LTOIRSizeRet)

cdef nvrtcResult nvrtcGetLTOIR(nvrtcProgram prog, char* LTOIR) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetLTOIR(prog, LTOIR)

cdef nvrtcResult nvrtcGetOptiXIRSize(nvrtcProgram prog, size_t* optixirSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetOptiXIRSize(prog, optixirSizeRet)

cdef nvrtcResult nvrtcGetOptiXIR(nvrtcProgram prog, char* optixir) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetOptiXIR(prog, optixir)

cdef nvrtcResult nvrtcGetProgramLogSize(nvrtcProgram prog, size_t* logSizeRet) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetProgramLogSize(prog, logSizeRet)

cdef nvrtcResult nvrtcGetProgramLog(nvrtcProgram prog, char* log) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetProgramLog(prog, log)

cdef nvrtcResult nvrtcAddNameExpression(nvrtcProgram prog, const char* name_expression) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcAddNameExpression(prog, name_expression)

cdef nvrtcResult nvrtcGetLoweredName(nvrtcProgram prog, const char* name_expression, const char** lowered_name) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetLoweredName(prog, name_expression, lowered_name)

cdef nvrtcResult nvrtcGetPCHHeapSize(size_t* ret) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetPCHHeapSize(ret)

cdef nvrtcResult nvrtcSetPCHHeapSize(size_t size) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcSetPCHHeapSize(size)

cdef nvrtcResult nvrtcGetPCHCreateStatus(nvrtcProgram prog) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetPCHCreateStatus(prog)

cdef nvrtcResult nvrtcGetPCHHeapSizeRequired(nvrtcProgram prog, size_t* size) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcGetPCHHeapSizeRequired(prog, size)

cdef nvrtcResult nvrtcSetFlowCallback(nvrtcProgram prog, void* callback, void* payload) except ?NVRTC_ERROR_INVALID_INPUT nogil:
    return cynvrtc._nvrtcSetFlowCallback(prog, callback, payload)
