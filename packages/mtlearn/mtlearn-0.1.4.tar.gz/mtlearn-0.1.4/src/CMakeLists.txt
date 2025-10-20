# ---------------------------------------------------------------------------
# Alvo principal em C++ (biblioteca mtlearn_core) e executável de exemplo.
# ---------------------------------------------------------------------------

# Arquivos de implementação do núcleo C++ do projeto.
set(MTLEARN_CORE_SOURCES
    mtlearn/core.cpp
)

add_library(mtlearn_core ${MTLEARN_CORE_SOURCES})
add_library(mtlearn::core ALIAS mtlearn_core)

# Exportamos os headers de src/ e reaproveitamos o include do mmcfilters para
# permitir `#include <mmcfilters/...>` nos consumidores.
target_include_directories(mtlearn_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${MTLEARN_MMCFILTERS_DIR}
)

target_compile_features(mtlearn_core PUBLIC cxx_std_20)

# Os algoritmos do mtlearn dependem diretamente do mmcfilters::core.
target_link_libraries(mtlearn_core
    PUBLIC
        mmcfilters::core
)

# Executável simples usado como ferramenta de linha de comando ou para smoke
# tests locais.
add_executable(mtlearn_app main.cpp)
target_link_libraries(mtlearn_app PRIVATE mtlearn::core)

# Regras de instalação para quem utiliza o projeto como biblioteca externa.
install(TARGETS mtlearn_core
        EXPORT mtlearnTargets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/mtlearn
        DESTINATION include
        FILES_MATCHING PATTERN "*.hpp")
