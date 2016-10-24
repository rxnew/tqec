#pragma once

#include "node.hpp"

#include <unordered_set>

namespace tqec {
namespace conn {
struct Size;

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

struct Size {
  int w, h, d;

  Size(int w, int h, int d);
};
}
}
