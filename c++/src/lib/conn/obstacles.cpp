#include "obstacles.hpp"

namespace tqec {
namespace conn {
auto Obstacles::has(const Node& node) const -> bool {
  return this->obstacles_.find(node) != this->obstacles_.cend();
}

auto Obstacles::add(const Node& node) -> void {
  this->obstacles_.insert(node);
}

auto Obstacles::addRectangular(const Node& pos, const Size& size) -> void {
  for(auto i = 0; i <= size.w; i++) {
    for(auto j = 0; j <= size.h; j++) {
      for(auto k = 0; k <= size.d; k++) {
        const auto node = Node(pos.x + i, pos.y + j, pos.z + k);
        this->add(node);
      }
    }
  }
}

auto Obstacles::remove(const Node& node) -> void {
  this->obstacles_.erase(node);
}

Size::Size(int w, int h, int d) : w(w), h(h), d(d) {}
}
}
