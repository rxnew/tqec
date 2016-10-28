#pragma once

#include "node.hpp"
#include "size.hpp"

#include <unordered_set>

namespace tqec {
namespace conn {
class Obstacles {
 private:
  std::unordered_set<Node> obstacles_;

 public:
  auto has(const Node& node) const -> bool;
  auto add(const Node& node) -> void;
  // posは直方体の頂点
  auto addRectangular(const Node& pos, const Size& size) -> void;
  auto remove(const Node& node) -> void;
};
}
}
