#include "area.hpp"

#include "node.hpp"
#include "size.hpp"

#include <limits>

namespace tqec {
namespace conn {
Area::Area(const Node& pos, const Size& size)
  : x(Range(pos.x, pos.x + size.w)),
    y(Range(pos.y, pos.y + size.h)),
    z(Range(pos.z, pos.z + size.d)) {}

Area::Range::Range() : min(std::numeric_limits<int>::min()),
                       max(std::numeric_limits<int>::max()) {}

Area::Range::Range(int min, int max) : min(min), max(max) {}

auto Area::contains(const Node& node) const -> bool {
  return
    node.x >= this->x.min && node.x < this->x.max &&
    node.y >= this->y.min && node.y < this->y.max &&
    node.z >= this->z.min && node.z < this->z.max;
}

}
}
