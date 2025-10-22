cmake_minimum_required(VERSION 3.18)

project(roboflex_webcam_gst)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)


# --------------------
# Resolve dependencies

include(FetchContent)
find_package(PkgConfig REQUIRED)

pkg_check_modules(GSTREAMER REQUIRED
    gstreamer-1.0>=1.18
    gstreamer-video-1.0
    gstreamer-app-1.0
)

set(ROBOFLEX_CORE_SOURCE_DIR "" CACHE PATH "Path to an existing roboflex_core checkout")
if(NOT ROBOFLEX_CORE_SOURCE_DIR)
    set(_roboflex_candidate "${CMAKE_CURRENT_LIST_DIR}/../roboflex")
    if(EXISTS "${_roboflex_candidate}/CMakeLists.txt")
        set(ROBOFLEX_CORE_SOURCE_DIR "${_roboflex_candidate}")
    endif()
endif()

if(ROBOFLEX_CORE_SOURCE_DIR)
    FetchContent_Declare(roboflex_core
        SOURCE_DIR ${ROBOFLEX_CORE_SOURCE_DIR}
    )
else()
    FetchContent_Declare(roboflex_core
        GIT_REPOSITORY https://github.com/flexrobotics/roboflex.git
        GIT_TAG        main
    )
endif()

set(BUILD_ROBOFLEX_PYTHON_EXT OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(roboflex_core)


# --------------------
# Define the library

add_library(roboflex_webcam_gst STATIC
    src/webcam_gst.cpp
    include/roboflex_webcam_gst/webcam_gst.h
)

set_property(TARGET roboflex_webcam_gst PROPERTY
    POSITION_INDEPENDENT_CODE ON
)

target_include_directories(roboflex_webcam_gst PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${GSTREAMER_INCLUDE_DIRS}
)

target_link_directories(roboflex_webcam_gst PRIVATE ${GSTREAMER_LIBRARY_DIRS})

target_link_libraries(roboflex_webcam_gst PUBLIC
    roboflex_core
    ${GSTREAMER_LIBRARIES}
)


# --------------------
# Examples

add_executable(run_webcam_cpp examples/run_webcam_cpp.cpp)
target_link_directories(run_webcam_cpp PRIVATE ${GSTREAMER_LIBRARY_DIRS})
target_link_libraries(run_webcam_cpp PRIVATE
    roboflex_core
    roboflex_webcam_gst
    ${GSTREAMER_LIBRARIES}
)

# Propagate GStreamer directories to dependents (e.g., Python module)
target_link_directories(roboflex_webcam_gst PUBLIC ${GSTREAMER_LIBRARY_DIRS})


# --------------------
# install

install(TARGETS roboflex_webcam_gst
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/roboflex_webcam_gst
    DESTINATION include
)


# --------------------
# build python bindings

add_subdirectory(python)
