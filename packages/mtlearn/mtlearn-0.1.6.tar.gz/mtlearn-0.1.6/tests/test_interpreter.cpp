#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <pybind11/pytypes.h>

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <string>

// MTLEARN_EMBED_DEFAULT é definido via CMake (0 = desabilita, 1 = executa o
// teste automaticamente). O usuário pode sobrepor via variável de ambiente
// MTLEARN_ENABLE_EMBED.

namespace py = pybind11;

#ifndef MTLEARN_EMBED_DEFAULT
#define MTLEARN_EMBED_DEFAULT 0
#endif

int main()
{
#if !MTLEARN_WITH_TORCH
    std::cout << "SKIP embed test: build sem suporte ao LibTorch" << std::endl;
    return 0;
#else
    try {
        constexpr bool kEmbedDefault = MTLEARN_EMBED_DEFAULT != 0;
        bool should_embed = kEmbedDefault;
        if (const char* flag = std::getenv("MTLEARN_ENABLE_EMBED")) {
            should_embed = std::string(flag) != "0";
        }

        if (!should_embed) {
            std::cout << "SKIP embed test disabled" << std::endl;
            return 0;
        }

        py::scoped_interpreter guard{};

        auto sys = py::module::import("sys");
        auto path = sys.attr("path");

        std::filesystem::path python_dir = std::filesystem::weakly_canonical(MTLEARN_PYTHON_DIR);
        std::filesystem::path bindings_dir = std::filesystem::weakly_canonical(MTLEARN_BINDINGS_DIR);

        path.attr("insert")(0, python_dir.string());
        path.attr("insert")(0, bindings_dir.string());

        try {
            py::module::import("torch");
        } catch (const py::error_already_set& e) {
            if (e.matches(PyExc_ImportError)) {
                std::cout << "SKIP torch indisponível: " << e.what() << std::endl;
                return 0;
            }
            throw;
        }

        auto mtlearn = py::module::import("mtlearn");
        auto result = mtlearn.attr("make_tree_tensor")(6).cast<py::tuple>();

        auto stats = result[0];
        auto tensor = result[1];

        int num_nodes = stats.attr("num_nodes").cast<int>();
        if (num_nodes != 6) {
            std::cerr << "Unexpected num_nodes=" << num_nodes << std::endl;
            return 1;
        }

        auto tensor_sum = tensor.attr("sum")().cast<float>();
        if (tensor_sum != 15.0f) {
            std::cerr << "Unexpected tensor sum=" << tensor_sum << std::endl;
            return 1;
        }

        std::cout << "mtlearn.make_tree_tensor(6) -> num_nodes=" << num_nodes
                  << ", sum=" << tensor_sum << std::endl;
        return 0;
    }
    catch (const py::error_already_set& e) {
        std::cerr << "Python exception:\n" << e.what() << std::endl;
        return 1;
    }
    catch (const std::exception& e) {
        std::cerr << "C++ exception:\n" << e.what() << std::endl;
        return 1;
    }
#endif
}
