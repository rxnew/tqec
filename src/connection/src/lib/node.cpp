#include "node.hpp"

namespace tqec {
namespace conn {
Node::Node(int x, int y, int z) : x(x), y(y), z(z) {}

auto Node::operator==(const Node& other) const -> bool {
  return this->x == other.x && this->y == other.y && this->z == other.z;
}

auto Node::operator!=(const Node& other) const -> bool {
  return !(*this == other);
}

auto Node::distance(const Node& other) const -> int {
  return
    std::abs(this->x - other.x) +
    std::abs(this->y - other.y) +
    std::abs(this->z - other.z);
}

auto operator<<(std::ostream& os, const Node& node) -> std::ostream& {
  os << '[' << node.x << ", " << node.y << ", " << node.z << ']';
  return os;
}
}
}

namespace std {
auto hash<tqec::conn::Node>::operator()(const tqec::conn::Node& node) const
  -> size_t {
  return node.x ^ (node.y << 2) ^ (node.z << 4);
}
}
