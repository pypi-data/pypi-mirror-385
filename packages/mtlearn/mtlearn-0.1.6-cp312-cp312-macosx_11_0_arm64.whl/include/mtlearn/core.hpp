#pragma once

#include <string>

#include <mmcfilters/trees/MorphologicalTree.hpp>

namespace mtlearn {

struct TreeStats {
    int numNodes{0};
};

TreeStats summarizeTree(const mmcfilters::MorphologicalTree& tree);

TreeStats makeTreeStats(int numNodes);

std::string describeTree(const mmcfilters::MorphologicalTree& tree);

std::string describeTree(const TreeStats& stats);

} // namespace mtlearn
