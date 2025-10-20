#pragma once


#include <mmcfilters/attributes/AttributeComputedIncrementally.hpp>
#include <mmcfilters/trees/NodeMT.hpp>
#include <mmcfilters/trees/MorphologicalTree.hpp>
#include <mmcfilters/utils/Common.hpp>

#include "MorphologicalTreePybind.hpp"
#include "PybindTorchUtils.hpp"

#include <memory>
#include <vector>
#include <tuple>

#include <pybind11/pybind11.h>
#include <torch/extension.h>
#include <ATen/ops/_sparse_mm.h>



namespace mtlearn {

namespace py = pybind11;

using mmcfilters::AttributeComputedIncrementally;
using mmcfilters::InvalidNode;
using mmcfilters::MorphologicalTreePybindPtr;
using mmcfilters::NodeId;

class ConnectedFilterByJacobian {
public:

    
    static torch::Tensor filtering(
                                            const torch::Tensor& pixel_to_node,         // [N_pixels]
                                            const torch::Tensor& residues,             // [N_nodes]
                                            const torch::Tensor& sigmoid              // [N_nodes]
                                        ) {

        auto node_filter = residues * sigmoid;     // [N_nodes]
        return node_filter.index_select(0, pixel_to_node);  // [N_pixels]
    }


    static py::tuple gradients(const torch::Tensor& jacobian,  
                                                    const torch::Tensor& residues, 
                                                    const torch::Tensor& attributes, 
                                                    const torch::Tensor& sigmoid,  
                                                    const torch::Tensor& grad_output) { 

        // 1. Gradiente da sigmoide
        auto d_sigmoid = sigmoid * (1 - sigmoid); // Element-wise, Shape: [N_nodes]

        // 2. Gradientes para os nós
        auto grad_filter = residues * d_sigmoid; // Shape: [N_nodes]
        auto grad_bias_nodes = grad_filter.unsqueeze(1); // Shape: [N_nodes, 1]
        auto grad_weight_nodes = grad_bias_nodes * attributes; // Shape: [N_nodes, D_attributes]

        // 3. Projeção com Jacobiana
        auto grad_bias_pixels = at::_sparse_mm(jacobian.t(), grad_bias_nodes); // [N_pixels, 1]
        auto grad_weight_pixels = at::_sparse_mm(jacobian.t(), grad_weight_nodes); // [N_pixels, D_attributes]

        // 4. Gradientes finais
        auto grad_bias = grad_output.t().matmul(grad_bias_pixels); // Scalar [1]
        auto grad_weight = grad_output.t().matmul(grad_weight_pixels).reshape({-1, 1});  // Shape: [D_attributes, 1]; // [1, D_attributes]

        return py::make_tuple(grad_bias, grad_weight); 
    }






    static py::tuple computeGradientsEfficient(
                                                const torch::Tensor& pixel_to_node,            // [N_pixels]                                        
                                                const torch::Tensor& residues,                 // [N_nodes]
                                                const torch::Tensor& sigmoid,                  // [N_nodes]                                        
                                                const torch::Tensor& attributes,               // [N_nodes, D]
                                                const torch::Tensor& grad_output               // [N_pixels]
                                                ) {
        // 1. Derivada da sigmoide
        auto d_sigmoid = sigmoid * (1 - sigmoid);      // [N_nodes]
    
        // 2. Gradiente do filtro por nó
        auto node_filter_grad = residues * d_sigmoid;  // [N_nodes]
    
        // 3. Gradiente da saída dos pixels: para cada pixel, obter o gradiente do nó correspondente
        auto node_grad_per_pixel = node_filter_grad.index_select(0, pixel_to_node);  // [N_pixels]
    
        // 4. Gradientes por pixel
        auto grad_bias_pixels = node_grad_per_pixel;  // [N_pixels]
        auto grad_weight_pixels = grad_bias_pixels.unsqueeze(1) * attributes.index_select(0, pixel_to_node);  // [N_pixels, D]
    
        // 5. Projeção final (produto com grad_output)
        auto grad_bias = (grad_output * grad_bias_pixels).sum();                       // Escalar
        //auto grad_weight = (grad_output.unsqueeze(1) * grad_weight_pixels).sum(0);     // [D]
        auto grad_weight = (grad_output.unsqueeze(1) * grad_weight_pixels).sum(0).unsqueeze(1); // [D, 1]

        return py::make_tuple(grad_weight, grad_bias.unsqueeze(0).unsqueeze(0));
    }
        


};

} // namespace mtlearn
