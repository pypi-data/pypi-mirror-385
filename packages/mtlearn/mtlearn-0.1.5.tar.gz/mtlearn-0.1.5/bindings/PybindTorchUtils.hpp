#pragma once

#include <mmcfilters/utils/Common.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <torch/torch.h>
#include <vector> // Adicionado

namespace py = pybind11;

namespace mtlearn {

class PybindTorchUtils {
public:
    static torch::Tensor toTensor(float* data, int size) {
        std::shared_ptr<float> data_ptr(data, [](float* ptr) { delete[] ptr; });
        return torch::from_blob(
            data_ptr.get(), // ponteiro para os dados
            {size},       // shape 1D
            [data_ptr](void*) mutable {
                // Mantém o buffer vivo até que o tensor seja liberado no Python.
            },
            torch::kFloat32  // dtype
        );
    }

    static torch::Tensor toTensor2D(float* data, int numRows, int numCols) {
        // usa smart pointer para gerenciar a memória alocada em data
        std::shared_ptr<float> data_ptr(data, [](float* ptr) { delete[] ptr; });

        return torch::from_blob(
            data_ptr.get(),                 // ponteiro para os dados
            {numRows, numCols},             // shape 2D
            [data_ptr](void*) mutable {
                // Mantém o buffer vivo até que o tensor seja liberado no Python
            },
            torch::kFloat32                 // dtype
        );
    }

    static torch::Tensor toSparseCooTensor(
        std::vector<int64_t> rowIndices,
        std::vector<int64_t> colIndices,
        int64_t numRows,
        int64_t numCols,
        torch::Dtype dtype = torch::kFloat32)
    {
        // Usa const_cast para remover a constância do ponteiro
        torch::Tensor row = torch::from_blob(rowIndices.data(), {static_cast<long>(rowIndices.size())}, torch::kInt64);
        torch::Tensor col = torch::from_blob(colIndices.data(), {static_cast<long>(colIndices.size())}, torch::kInt64);

        // Empilha os índices para formar o formato (2, N)
        torch::Tensor indices = torch::stack({row, col});

        // Cria o tensor de valores (todos 1s) com o tipo de dado especificado
        torch::Tensor values = torch::ones({static_cast<int64_t>(rowIndices.size())}, torch::TensorOptions().dtype(dtype));

        // Define o tamanho final da matriz esparsa
        std::vector<int64_t> size = {numRows, numCols};

        // Cria e retorna o tensor esparso
        return torch::sparse_coo_tensor(indices, values, size, torch::TensorOptions().dtype(dtype));
    }


};

} // namespace mtlearn
