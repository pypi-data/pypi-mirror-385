cmake_minimum_required(VERSION 3.14)

# ---------------------------------------------------------------------------
# Configuração dos testes do projeto mtlearn.
# ---------------------------------------------------------------------------
# Este arquivo cria executáveis de teste em C++, scripts Python e trata das
# dependências (Torch, pybind11, Python) necessárias para executar casos de uso
# que envolvem bindings.

function(mtl_add_test TARGET_NAME)
    add_executable(${TARGET_NAME} ${ARGN})
    target_link_libraries(${TARGET_NAME} PRIVATE mtlearn::core)
    target_compile_features(${TARGET_NAME} PRIVATE cxx_std_20)
    target_compile_definitions(${TARGET_NAME} PRIVATE
        MTLEARN_PYTHON_DIR="${PROJECT_SOURCE_DIR}/python"
        MTLEARN_BINDINGS_DIR="${CMAKE_BINARY_DIR}/bindings"
        MTLEARN_EMBED_DEFAULT=$<BOOL:${MTLEARN_ENABLE_EMBED}>
        MTLEARN_WITH_TORCH=$<BOOL:${MTLEARN_WITH_TORCH}>)
    if(Python3_INCLUDE_DIRS)
        target_include_directories(${TARGET_NAME} PRIVATE ${Python3_INCLUDE_DIRS})
    endif()
    if(TARGET Python3::Embed)
        target_link_libraries(${TARGET_NAME} PRIVATE Python3::Embed)
    elseif(TARGET Python3::Module)
        target_link_libraries(${TARGET_NAME} PRIVATE Python3::Module)
    endif()
    if(TARGET pybind11::embed)
        target_link_libraries(${TARGET_NAME} PRIVATE pybind11::embed)
    endif()
    add_test(NAME ${TARGET_NAME} COMMAND ${TARGET_NAME})
endfunction()

find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
find_package(Python3 COMPONENTS Development.Embed)

if(NOT TARGET pybind11::embed)
    find_package(pybind11 CONFIG REQUIRED)
endif()

# Tenta localizar um Python que possua torch para execução dos testes.
set(_mtlearn_python_exec "${Python3_EXECUTABLE}")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "-c" "import torch"
    RESULT_VARIABLE _mtlearn_python_has_torch
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT _mtlearn_python_has_torch EQUAL 0)
    if(DEFINED ENV{CONDA_PREFIX})
        foreach(_suffix python3.12 python3 python)
            set(_candidate "$ENV{CONDA_PREFIX}/bin/${_suffix}")
            if(EXISTS "${_candidate}")
                set(_mtlearn_python_exec "${_candidate}")
                break()
            endif()
        endforeach()
    endif()
endif()

if(NOT _mtlearn_python_has_torch EQUAL 0)
    if(NOT EXISTS "${_mtlearn_python_exec}")
        set(_mtlearn_python_exec "/opt/anaconda3/bin/python3.12")
    endif()
endif()

if(NOT "${_mtlearn_python_exec}" STREQUAL "${Python3_EXECUTABLE}" AND EXISTS "${_mtlearn_python_exec}")
    set(Python3_EXECUTABLE "${_mtlearn_python_exec}" CACHE FILEPATH "Python interpreter with torch" FORCE)
endif()

# Checagem final opcional: o teste Python realiza skip se torch não estiver
# disponível, então não falhamos durante o configure.

if(WIN32)
    set(_mtlearn_pythonpath "${PROJECT_SOURCE_DIR}/python;${CMAKE_BINARY_DIR}/bindings")
else()
    set(_mtlearn_pythonpath "${PROJECT_SOURCE_DIR}/python:${CMAKE_BINARY_DIR}/bindings")
endif()

add_test(
    NAME mtl_python_bindings
    COMMAND
        ${CMAKE_COMMAND} -E env
            PYTHONPATH=${_mtlearn_pythonpath}
            ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/python/test_bindings.py
)

# Testes C++: um smoke test simples e o interpretador embutido (caso Torch esteja
# habilitado na build).
mtl_add_test(mtl_basic_test basic.cpp)

if(MTLEARN_WITH_TORCH)
    mtl_add_test(mtl_interpreter_test test_interpreter.cpp)
endif()

# No fluxo de `ctest` os testes de C++ herdam PYTHONPATH e deixam o modo embed
# desligado; para depuração local basta exportar MTLEARN_ENABLE_EMBED=1 antes de
# rodar `mtl_interpreter_test`.
if(MTLEARN_ENABLE_EMBED)
    set(_mtlearn_embed_env "MTLEARN_ENABLE_EMBED=1")
else()
    set(_mtlearn_embed_env "MTLEARN_ENABLE_EMBED=0")
endif()

set(_mtlearn_test_env "PYTHONPATH=${_mtlearn_pythonpath};${_mtlearn_embed_env}")
if(MTLEARN_WITH_TORCH)
    set_tests_properties(mtl_interpreter_test PROPERTIES ENVIRONMENT "${_mtlearn_test_env}")
endif()
set_tests_properties(mtl_python_bindings mtl_basic_test PROPERTIES ENVIRONMENT "${_mtlearn_test_env}")
