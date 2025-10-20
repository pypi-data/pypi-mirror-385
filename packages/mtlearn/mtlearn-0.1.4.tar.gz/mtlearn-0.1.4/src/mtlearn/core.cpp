#include "core.hpp"

#include <sstream>

namespace mtlearn {

TreeStats summarizeTree(const mmcfilters::MorphologicalTree& tree)
{
    TreeStats stats;
    stats.numNodes = tree.getNumNodes();
    return stats;
}

TreeStats makeTreeStats(int numNodes)
{
    TreeStats stats;
    stats.numNodes = numNodes;
    return stats;
}

std::string describeTree(const mmcfilters::MorphologicalTree& tree)
{
    const auto stats = summarizeTree(tree);
    std::ostringstream oss;
    oss << "Morphological tree with " << stats.numNodes << " nodes";
    return oss.str();
}

std::string describeTree(const TreeStats& stats)
{
    std::ostringstream oss;
    oss << "Morphological tree with " << stats.numNodes << " nodes";
    return oss.str();
}

} // namespace mtlearn
