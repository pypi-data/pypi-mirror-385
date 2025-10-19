cmake_minimum_required(VERSION 3.24)

project(gempyrepy LANGUAGES CXX C)

if(SKBUILD)
    find_package(PythonExtensions REQUIRED)
endif()

if(UNIX AND NOT APPLE AND NOT RASPBERRY)
    set(LINUX ON)
endif()

if (APPLE)
    if (NOT DEFINED NATIVE_ARCHITECURE)
        set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "Universal binary" FORCE)
    endif()    
endif()

if(ADD_PATH)
    # for GH actions
    string(REPLACE "+" ";" LIB_PATH ${ADD_PATH})
    message("Append to CMAKE_MODULE_PATH: '${LIB_PATH}'")
    link_directories(${LIB_PATH})
endif()

if(MSVC)
    # for GH actions
    list(APPEND CMAKE_LIBRARY_PATH ${LIB_PATH})
   
    find_program(PYTHON "python" HINTS "${PYTHON_PATH}" REQUIRED)
    set (PYTHON3 python)
    find_package(Python3 HINTS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        find_package(Python3 COMPONENTS Interpreter Development) # this works event not found
    endif()
    find_path(PYTHON_HEADER_PATH "Python.h" HINTS ${Python3_INCLUDE_DIRS})
elseif(MINGW)
    #find_package(Python3 3.10 COMPONENTS  REQUIRED)
    #find_program(PYTHON "python" HINTS "${PYTHON_PATH}" NO_DEFAULT_PATH)    
    set (PYTHON3 python)
    find_package(Python3 HINTS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        find_package(Python3 COMPONENTS Interpreter Development) # the below hack helps as mingw is not really supported
    endif()
    if(NOT Python3)
        execute_process(
                    COMMAND ${PYTHON3} --version
                    OUTPUT_VARIABLE PY_VERSION)
        string(REGEX MATCHALL [0-9]+ VER ${PY_VERSION})
        list(GET VER 0 Python3_VERSION_MAJOR)
        list(GET VER 1 Python3_VERSION_MINOR)
        get_filename_component(PARENT_DIR "${PYTHON_PATH}" DIRECTORY)
        find_path(PYTHON_HEADER_PATH "Python.h" 
            HINTS "${PARENT_DIR}/include/python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}" REQUIRED)
        set(PYTHON_INCLUDE_PATH ${PYTHON_HEADER_PATH})
    endif()        
else() 
    find_program(PYTHON "python3" HINTS "${PYTHON_PATH}" REQUIRED)
    set (PYTHON3 python3)
    find_package(Python3 PATHS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        execute_process(COMMAND ${PYTHON3}  -c "import sys; print(sys.executable)" OUTPUT_VARIABLE PY_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
        find_package(Python3 PATHS ${PY_DIR} COMPONENTS Interpreter Development)
        if(NOT Python3)
             find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
        endif()
    endif() 
    find_path(PYTHON_HEADER_PATH "Python.h" HINTS ${Python3_INCLUDE_DIRS})
    add_compile_options(-fPIC)
endif()

include_directories(${PYTHON_INCLUDE_PATH})


include(GNUInstallDirs)


include(ExternalProject)
include(FetchContent)

if(NOT PYTHON_HEADER_PATH)
    message(FATAL_ERROR "I assume you need '$sudo apt-get install python3-dev'")
else()
    message("Using Python headers ar ${PYTHON_HEADER_PATH}")    
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# gempyre has to be installed
find_package(gempyre QUIET)

if(NOT gempyre_FOUND)
    message("Locally installed Gempyre lib was not found - retrieve one from repository")
    set (HAS_AFFILIATES OFF CACHE INTERNAL "Turn off")
    set (HAS_TEST OFF CACHE INTERNAL "Turn off")
    set (NO_EXPORT TRUE CACHE INTERNAL "Turn off")
    FetchContent_Declare(gempyre
    GIT_REPOSITORY https://github.com/mmertama/Gempyre.git
    )

    FetchContent_MakeAvailable(gempyre)
    #FetchContent_GetProperties(gempyre)
    #
    #if(NOT gempyre_POPULATED)
    #    FetchContent_Populate(gempyre)
    #    add_subdirectory(${gempyre_SOURCE_DIR} ${gempyre_BINARY_DIR}) 
    #endif()
endif()    

include_directories (
    /usr/local/include
    include
)

# TODO remove this and just mark pybind11 as a dependency
FetchContent_Declare( pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.13.6
)

FetchContent_MakeAvailable(pybind11)
#FetchContent_GetProperties(pybind11)
#
#if(NOT pybind11_POPULATED)
#    FetchContent_Populate(pybind11)
#    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
#endif()

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/README.md
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR})


if(NOT DEFINED Python3_VERSION_MAJOR)
    execute_process(COMMAND ${PYTHON3} --version OUTPUT_VARIABLE PY_VER OUTPUT_STRIP_TRAILING_WHITESPACE)
else()
    set(PY_VER "${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}")
endif()

if(SKBUILD)
    set(LIB_NAME _gempyre)
else()
    set(LIB_NAME Gempyre)
endif()  

add_compile_definitions(GEMPYRE_NAME=${LIBNAME})

add_definitions(-DPYBIND11_PYTHON_VERSION="${PY_VER}")
set(PYBIND11_PYTHON_VERSION ${PY_VER})
pybind11_add_module(${LIB_NAME}
        src/Gempyre/gempyre_python.cpp)

set_target_properties(${LIB_NAME} PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)    

add_custom_command(
  TARGET ${LIB_NAME}
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E echo "Building file: $<TARGET_FILE:${LIB_NAME}>"
)

if(NOT SKBUILD)
    add_custom_command(
    TARGET ${LIB_NAME}
    POST_BUILD
    COMMAND ${PYTHON3} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py sdist bdist_wheel
    )
endif()

message("gempyre_BINARY_DIR:${gempyre_BINARY_DIR}")
message("SKBUILD:${SKBUILD}")
message("WIN32:${WIN32}")
message("USE_UWEBSOCKETS:${USE_UWEBSOCKETS}")

if( DEFINED gempyre_BINARY_DIR )
    if(SKBUILD)
        if(WIN32)
            #option(USE_UWEBSOCKETS "Turn on if Gempyre uses uwebsockets" OFF)
            if (USE_UWEBSOCKETS)
                # Otherwise this is injected withing find_package
                # Look path as lib may not exits at this phase
                file(GLOB_RECURSE GEMPYRE_LIB_FIND LIST_DIRECTORIES true ${CMAKE_SOURCE_DIR}/_skbuild/*gempyrelib)
                list(FILTER GEMPYRE_LIB_FIND INCLUDE REGEX gempyre-build)
                if(NOT GEMPYRE_LIB_FIND)
                    message(FATAL_ERROR "Cannot find gempyrelib from ${CMAKE_SOURCE_DIR}/_skbuild")
                endif()
                list(GET GEMPYRE_LIB_FIND 0 GEMPYRE_LIB_FOLDER)
           
                set(UVA_PATH  "${GEMPYRE_LIB_FOLDER}/gempyrelib/libuv-prefix/src/libuv-build")
                # target_link_libraries requires that a the lib can be resolved - however
                # as here we get it only when the fetch's add_external project has done it
                # it is is added only as a compiler parameter.
                target_link_options(${LIB_NAME} PRIVATE "/LIBPATH:${UVA_PATH};uv_a.lib")
            else() # as above
                file(GLOB_RECURSE LWS_LIB_FIND LIST_DIRECTORIES true ${CMAKE_SOURCE_DIR}/_skbuild/gempyre-build)
                list(FILTER LWS_LIB_FIND INCLUDE REGEX libwebsockets-build)
                if(NOT LWS_LIB_FIND)
                    message(FATAL_ERROR "Cannot find libwebsockets from ${CMAKE_SOURCE_DIR}/_skbuild")
                endif()
                list(GET LWS_LIB_FIND 0 LWS_LIB_FOLDER)
                set(LWS_LIB_PATH  "${LWS_LIB_FOLDER}/lib")
                if (NOT EXISTS ${LWS_LIB_PATH}/websockets_static.lib)
                    message(WARNING "The ${LWS_LIB_PATH}/websockets_static.lib not found")
                endif()    
                target_link_options(${LIB_NAME} PRIVATE "/LIBPATH:${LWS_LIB_PATH};websockets_static.lib")
            endif()   
        endif()
    endif()
    target_link_libraries (${LIB_NAME} PRIVATE gempyre)
else()    
    target_link_libraries (${LIB_NAME} PRIVATE gempyre::gempyre)
endif()


# scikit - build wants to install...
#python_extension_module(Gempyre)
if(SKBUILD)
    #string(REPLACE "/" ";" NDIR ${CMAKE_BINARY_DIR})
    #list(POP_BACK NDIR)
    #list(APPEND NDIR "cmake-install")
    #list(JOIN NDIR "/" NDIR)
    #set(NDIR "${NDIR}/cmake-install")

    #message("Target: ${CMAKE_BINARY_DIR} ${NDIR}")

    install (TARGETS ${LIB_NAME} DESTINATION .)
    #        LIBRARY DESTINATION src/Gempyre)

    #install(DIRECTORY Gempyre DESTINATION ${SKTARGET}) 
    #install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/Gempyre_utils DESTINATION ${SKTARGET})         

    #file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/Gempyre DESTINATION ${CMAKE_BINARY_DIR}) 
    #file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/Gempyre_utils DESTINATION ${CMAKE_BINARY_DIR})         
endif()