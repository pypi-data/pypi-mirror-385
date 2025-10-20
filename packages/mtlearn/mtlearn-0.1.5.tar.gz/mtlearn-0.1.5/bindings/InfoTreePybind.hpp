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

class InfoTreePybind {
public:

    
    static torch::Tensor getResidues(MorphologicalTreePybindPtr tree) {
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }

        int numNodes = tree->getNumNodes();
        float* residues = new float[numNodes];

        for (NodeId nodeId : tree->getNodeIds()) {
            residues[nodeId] = static_cast<float>(tree->getResidueById(nodeId));
        }

        return PybindTorchUtils::toTensor(residues, numNodes);
    }

    static torch::Tensor getJacobian(MorphologicalTreePybindPtr tree){
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }

        std::vector<int64_t> rowIndices;
        std::vector<int64_t> colIndices;
        auto imageSize = tree->getNumRowsOfImage() * tree->getNumColsOfImage();

        for(auto nodeId : tree->getNodeIds()){
            mmcfilters::NodeMT node = tree->proxy(nodeId);
            auto pixelsOfCC = node.getPixelsOfCC();

            for(auto pixel : pixelsOfCC){
                rowIndices.push_back(nodeId);
                colIndices.push_back(pixel);
            }
        }

        return PybindTorchUtils::toSparseCooTensor(
            rowIndices,
            colIndices,
            tree->getNumNodes(),
            imageSize
        );//.to_dense();
    }
};

} // namespace mtlearn
