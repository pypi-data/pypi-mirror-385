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



};

} // namespace mtlearn
