cmake_minimum_required(VERSION 3.5)
project(TPUKernelSamples LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

function(parse_list INPUT OUTPUT CHAR)
  string(REGEX REPLACE ":" "${CHAR}" TMP_LIST "${INPUT}")
  set(${OUTPUT} ${TMP_LIST} PARENT_SCOPE)
endfunction()

set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wl,--no-undefined")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,--no-undefined")

if(NOT DEFINED ENV{PPL_PROJECT_ROOT})
  message(FATAL_ERROR "Please set environ PPL_PROJECT_ROOT to ppl release path")
else()
  set(PPL_TOP $ENV{PPL_PROJECT_ROOT})
  message(NOTICE "PPL_PATH: ${PPL_TOP}")
endif()

if(NOT DEFINED CHIP)
  message(FATAL_ERROR "Please set -DCHIP to chip type")
else()
  message(NOTICE "CHIP: ${CHIP}")
endif()
# Add chip arch defination
add_definitions(-D__${CHIP}__)
add_definitions(-DUSING_CMODEL)


if(DEFINED DEV_MODE)
  message(NOTICE "DEV_MODE: ${DEV_MODE}")
else()
  message(FATAL_ERROR "Please set -DDEV_MODE to cmodel/pcie/soc")
endif()

if(DEBUG)
  set(CMAKE_BUILD_TYPE "Debug")
  add_definitions(-DDEBUG)
else()
  set(CMAKE_BUILD_TYPE "Release")
  if(NOT USING_CUDA)
    add_definitions(-O3)
  endif()
endif()
# complie .pl
set(SCRIPTS_CMAKE_DIR "${PPL_TOP}/deps/scripts/")
list(APPEND CMAKE_MODULE_PATH "${SCRIPTS_CMAKE_DIR}")
include(AddPPL)  #AddPPL.cmake including pplgen
file(GLOB PPL_SOURCE ppl/*.pl)
set(OPT_LEVEL 2)
set_ppl_chip(${CHIP})
foreach(ppl_file ${PPL_SOURCE})
	set(input ${ppl_file})
	set(output ${CMAKE_CURRENT_BINARY_DIR})
	ppl_gen(${input} ${output} ${OPT_LEVEL})
endforeach()
include($ENV{PPL_RUNTIME_PATH}/scripts/GenChipDef.cmake)
include($ENV{PPL_RUNTIME_PATH}/chip/${CHIP}/config_common.cmake)
include_directories(
  ${CMAKE_BINARY_DIR}
  ${CMAKE_BINARY_DIR}/include
  ${KERNEL_TOP}
  ${TPUKERNEL_TOP}/kernel/include
  ${TPUKERNEL_TOP}/tpuDNN/include
  ${CUS_TOP}/dev/utils/include
  ${RUNTIME_TOP}/include
  ${CUS_TOP}/host/include
  ${CUS_TOP}/dev/utils/include
  ${CHECKER})
link_directories(${BACKEND_LIB_PATH} ${RUNTIME_TOP}/lib)

aux_source_directory(${CMAKE_CURRENT_BINARY_DIR}/host PPL_SRC_FILES)
aux_source_directory(src SRC_FILES)
add_executable(test_case ${PPL_SRC_FILES} ${SRC_FILES})
target_link_libraries(test_case PRIVATE ${RUNTIME_LIBS} tpudnn pthread)

set(KERNEL_HEADER "${CMAKE_BINARY_DIR}/include/kernel_module_data.h")
add_custom_command(
    OUTPUT ${KERNEL_HEADER}
    COMMAND echo "const unsigned int kernel_module_data[] = {0}\;" > ${KERNEL_HEADER}
)
add_custom_target(gen_kernel_module_data_target DEPENDS ${KERNEL_HEADER})
add_dependencies(test_case gen_kernel_module_data_target)

install(TARGETS test_case DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
aux_source_directory(${CMAKE_CURRENT_BINARY_DIR}/device KERNEL_SRC_FILES)
add_library(kernel SHARED ${KERNEL_SRC_FILES} ${CUS_TOP}/dev/utils/src/ppl_helper.c ${KERNEL_CHECKER})

target_include_directories(kernel PRIVATE
	include
	${PPL_TOP}/include
	${CUS_TOP}/host/include
  ${CUS_TOP}/dev/utils/include
	${KERNEL_TOP}
	${TPUKERNEL_TOP}/common/include
	${TPUKERNEL_TOP}/kernel/include
	${TPUKERNEL_CUSTOMIZE_TOP}/include
)
target_link_libraries(kernel PRIVATE ${FIRMWARE_CMODEL} m)
install(TARGETS kernel DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/lib)
