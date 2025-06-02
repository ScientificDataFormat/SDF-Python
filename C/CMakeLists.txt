cmake_minimum_required (VERSION 3.20)

cmake_policy(SET CMP0177 NEW)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
# set(CMAKE_POLICY_DEFAULT_CMP0091 NEW)

project (NDTable)

set(ARCHITECTURE "" CACHE STRING "Architecture")
set_property(CACHE ARCHITECTURE PROPERTY STRINGS "" "aarch64" "x86" "x86_64")

if (NOT ARCHITECTURE)
    if (${CMAKE_HOST_SYSTEM_PROCESSOR} MATCHES "AMD64|x86_64")
        set(ARCHITECTURE "x86_64")
    elseif (${CMAKE_HOST_SYSTEM_PROCESSOR} MATCHES "aarch64")
        set(ARCHITECTURE "aarch64")
    else ()
        message(FATAL_ERROR "Unknown System Architecture: ${CMAKE_SYSTEM_PROCESSOR}")
    endif ()
endif ()

if (WIN32)
    set(PLATFORM "${ARCHITECTURE}-windows")
elseif (APPLE)
    set(PLATFORM "${ARCHITECTURE}-darwin")
else ()
    set(PLATFORM "${ARCHITECTURE}-linux")
endif ()

message(STATUS "PLATFORM: ${PLATFORM}")

add_library(NDTable SHARED
    "include/Python.h"
    "src/Python.c"
    "NDTable/include/NDTable.h"
    "NDTable/src/Core.c"
    "NDTable/src/Interpolation.c"
)

target_include_directories(NDTable PRIVATE
	"include"
	"NDTable/include"
)

install(TARGETS NDTable DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/../src/sdf/${PLATFORM}")
