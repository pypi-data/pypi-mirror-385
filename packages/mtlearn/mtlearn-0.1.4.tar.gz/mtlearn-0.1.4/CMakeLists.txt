cmake_minimum_required(VERSION 3.20)

# ---------------------------------------------------------------------------
# Projeto principal do mtlearn
# ---------------------------------------------------------------------------
# Este arquivo prepara o ambiente CMake para compilar tanto a biblioteca C++
# quanto os bindings Python e executáveis de teste. Ele pressupõe que o
# repositório MorphologicalAttributeFilters esteja disponível como submódulo em
# external/MorphologicalAttributeFilters.

project(mtlearn LANGUAGES CXX)

# Opções expostas para quem consome o projeto via CMake ou pyproject.toml.
# - MTLEARN_BUILD_PYTHON : habilita o módulo pybind11 exportado para Python.
# - MTLEARN_BUILD_TESTS  : compila os testes C++ e scripts auxiliares.
# - MTLEARN_ENABLE_ASSERTS: controla o uso de asserts na biblioteca base.
# - MTLEARN_ENABLE_EMBED : ativa testes que inicializam o interpretador Python
#   embutido (útil apenas em ambientes com PyTorch completo).
option(MTLEARN_BUILD_PYTHON "Build pybind11 bindings" ON)
option(MTLEARN_BUILD_TESTS "Build C++ tests" OFF)
option(MTLEARN_ENABLE_ASSERTS "Keep runtime asserts even in Release" OFF)
option(MTLEARN_ENABLE_EMBED "Enable embedded Python interpreter tests" OFF)
option(MTLEARN_WITH_TORCH "Build bindings/tests that depend on LibTorch" ON)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Diretório extra para macros utilitárias do projeto.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Respeita variáveis fornecidas via linha de comando/pyproject para localizar o
# mesmo interpretador Python em todos os subprojetos.
if(DEFINED PYTHON_EXECUTABLE AND NOT DEFINED Python3_EXECUTABLE)
    set(Python3_EXECUTABLE "${PYTHON_EXECUTABLE}" CACHE FILEPATH "Python interpreter" FORCE)
endif()
if(DEFINED PYTHON_LIBRARY_DIR AND NOT DEFINED Python3_LIBRARY_DIR)
    set(Python3_LIBRARY_DIR "${PYTHON_LIBRARY_DIR}" CACHE PATH "Python library directory" FORCE)
endif()
if(DEFINED Python3_EXECUTABLE AND NOT DEFINED Python3_ROOT_DIR)
    get_filename_component(_mtlearn_py_bin "${Python3_EXECUTABLE}" DIRECTORY)
    get_filename_component(_mtlearn_py_root "${_mtlearn_py_bin}" DIRECTORY)
    set(Python3_ROOT_DIR "${_mtlearn_py_root}" CACHE PATH "Python root" FORCE)
endif()

set(MTLEARN_MMCFILTERS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external/MorphologicalAttributeFilters")
# Garante que o submódulo do mmcfilters está disponível (obrigatório).
if(NOT EXISTS "${MTLEARN_MMCFILTERS_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "Dependência mmcfilters não encontrada em ${MTLEARN_MMCFILTERS_DIR}. Adicione como submódulo ou ajuste o caminho.")
endif()

add_subdirectory(${MTLEARN_MMCFILTERS_DIR} mmcfilters)

set(_mmc_target "")
if(TARGET mmcfilters_lib)
    set(_mmc_target mmcfilters_lib)
elseif(TARGET mmcfilters::core)
    set(_mmc_target mmcfilters::core)
endif()

if(NOT _mmc_target)
    message(FATAL_ERROR "Não foi possível localizar o alvo principal do mmcfilters.")
endif()

# O mmcfilters oferece o alvo principal de algoritmos morfológicos. Ajustamos as
# flags globais de asserts dependendo da opção fornecida ao projeto.
if(MTLEARN_ENABLE_ASSERTS)
    target_compile_definitions(${_mmc_target} PUBLIC MMCFILTERS_ENABLE_ASSERTS)
    target_compile_options(${_mmc_target}
        PUBLIC
            $<$<CXX_COMPILER_ID:MSVC>:/UNDEBUG>
            $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-UNDEBUG>
    )
else()
    target_compile_definitions(${_mmc_target} PUBLIC NDEBUG)
endif()

# Diretório com as bibliotecas/aplicações C++ próprias do mtlearn.
add_subdirectory(src)

if(MTLEARN_BUILD_PYTHON)
    # Inclui os bindings pybind11 que produzem o módulo _mtlearn e o pacote
    # Python correspondente.
    add_subdirectory(bindings)
endif()

if(MTLEARN_BUILD_TESTS)
    enable_testing()
    # Suite de testes C++ (smoke tests e interpretador python embutido).
    add_subdirectory(tests)
endif()
