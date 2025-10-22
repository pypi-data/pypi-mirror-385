set(additional_include "path1;path2,path3 path4")
set(additional_link "")

string(REPLACE " " ";" additional_include "${additional_include}")
string(REPLACE "," ";" additional_link "${additional_link}")

# try download cross toolchain
if(NOT DEFINED ENV{CROSS_TOOLCHAINS})
    message("CROSS_TOOLCHAINS was not defined, try source download_toolchain.sh")
    execute_process(
        COMMAND bash -c "CHIP=${CHIP} DEV_MODE=${DEV_MODE} source $ENV{PPL_PROJECT_ROOT}/deps/scripts/download_toolchain.sh && env"
        RESULT_VARIABLE result
        OUTPUT_VARIABLE output
    )
    if(NOT result EQUAL "0")
        message(FATAL_ERROR "Not able to source download_toolchain.sh: ${output}")
    endif()
    string(REGEX MATCH "CROSS_TOOLCHAINS=([^\n]*)" _ ${output})
    set(ENV{CROSS_TOOLCHAINS} "${CMAKE_MATCH_1}")
endif()
# Set the C compiler
if(${CHIP} STREQUAL "tpub_7_1" OR ${CHIP} STREQUAL "tpul_6_0")
  set(CMAKE_C_COMPILER $ENV{CROSS_TOOLCHAINS}/Xuantie-900-gcc-linux-5.10.4-glibc-x86_64-V2.6.1/bin/riscv64-unknown-linux-gnu-gcc)
else()
  set(CMAKE_C_COMPILER $ENV{CROSS_TOOLCHAINS}/gcc-arm-10.3-2021.07-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-gcc)
endif()

# Set the include directories for the shared library
set(SCRIPTS_CMAKE_DIR "$ENV{PPL_RUNTIME_PATH}/scripts/")
list(APPEND CMAKE_MODULE_PATH "${SCRIPTS_CMAKE_DIR}")
include(GenChipDef)
include(${SCRIPTS_CMAKE_DIR}/../chip/${CHIP}/config_common.cmake)
include_directories(
  include
  ${CMAKE_BINARY_DIR}
  ${CMAKE_BINARY_DIR}/include
  ${KERNEL_TOP}
  ${TPUKERNEL_TOP}/kernel/include
  ${TPUKERNEL_TOP}/tpuDNN/include
  ${CUS_TOP}/dev/utils/include
  ${RUNTIME_TOP}/include
  ${CUS_TOP}/host/include
  ${CUS_TOP}/dev/utils/include
  ${CHECKER}
  ${EXTRA_IDIRS}
  ${additional_include}
)
link_directories(${BACKEND_LIB_PATH} ${RUNTIME_TOP}/lib ${EXTRA_LDIRS})
# generate ppl
include(AddPPL)  #AddPPL.cmake including pplgen
file(GLOB PPL_SOURCE ppl/*.pl)
set(OPT_LEVEL 2)
set_ppl_chip(${CHIP})
foreach(ppl_file ${PPL_SOURCE})
	set(input ${ppl_file})
	set(output ${CMAKE_CURRENT_BINARY_DIR})
	ppl_gen(${input} ${output} ${OPT_LEVEL})
endforeach()

# Set the output file for the shared library
set(SHARED_LIBRARY_OUTPUT_FILE libkernel)

# Create the shared library
aux_source_directory(${CMAKE_CURRENT_BINARY_DIR}/device DEVICE_SRCS)

add_library(${SHARED_LIBRARY_OUTPUT_FILE} SHARED ${DEVICE_SRCS} ${CUS_TOP}/dev/utils/src/ppl_helper.c)

# Link the libraries for the shared library
target_link_libraries(${SHARED_LIBRARY_OUTPUT_FILE} -Wl,--whole-archive libfirmware_core.a -Wl,--no-whole-archive dl m)

if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
  MESSAGE (STATUS "Current is Debug mode")
  SET (FW_DEBUG_FLAGS "-DUSING_FW_DEBUG")
ENDIF ()

# Set the output file properties for the shared library
set_target_properties(${SHARED_LIBRARY_OUTPUT_FILE} PROPERTIES
  PREFIX ""
  SUFFIX ".so"
  COMPILE_FLAGS "-fPIC ${FW_DEBUG_FLAGS}"
  LINK_FLAGS "-shared"
)
install(TARGETS ${SHARED_LIBRARY_OUTPUT_FILE} DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/lib)
# Set the path to the input file
set(INPUT_FILE "${CMAKE_BINARY_DIR}/${SHARED_LIBRARY_OUTPUT_FILE}.so")
# Set the path to the output file
set(KERNEL_HEADER "${CMAKE_BINARY_DIR}/include/kernel_module_data.h")
add_custom_command(
    OUTPUT ${KERNEL_HEADER}
    DEPENDS ${SHARED_LIBRARY_OUTPUT_FILE}
    COMMAND echo "const unsigned int kernel_module_data[] = {" > ${KERNEL_HEADER}
    COMMAND hexdump -v -e '1/4 \"0x%08x,\\n\"' ${INPUT_FILE} >> ${KERNEL_HEADER}
    COMMAND echo "}\;" >> ${KERNEL_HEADER}
)

# Add a custom target that depends on the custom command
add_custom_target(gen_kernel_module_data_target DEPENDS ${KERNEL_HEADER})
# Add a custom target for the shared library
add_custom_target(dynamic_library DEPENDS ${SHARED_LIBRARY_OUTPUT_FILE})

aux_source_directory(${CMAKE_CURRENT_BINARY_DIR}/host PPL_SRC_FILES)
aux_source_directory(src SRC_FILES)
add_executable(test_case ${PPL_SRC_FILES} ${SRC_FILES})
add_dependencies(test_case dynamic_library gen_kernel_module_data_target)
target_link_libraries(test_case PRIVATE ${RUNTIME_LIBS} tpudnn pthread ${additional_link})
set_target_properties(test_case PROPERTIES INSTALL_RPATH "$ORIGIN/lib")
set(TPUDNN_SO "${BACKEND_LIB_PATH}/libtpudnn.so")
install(TARGETS test_case DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
install(FILES ${TPUDNN_SO} DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/lib)
