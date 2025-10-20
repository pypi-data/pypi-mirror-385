#include <cassert>

#include <mmcfilters/utils/Common.hpp>

#include "mtlearn/core.hpp"

int main()
{
    
    auto stats = mtlearn::makeTreeStats(42);
    assert(stats.numNodes == 42);

    return 0;
}
