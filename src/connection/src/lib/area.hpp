#pragma once

namespace tqec {
namespace conn {
struct Node;
struct Size;

struct Area {
  struct Range {
    int min;
    int max;

    Range();
    Range(int min, int max);
  };

  Range x;
  Range y;
  Range z;

  Area() = default;
  Area(const Node& pos, const Size& size);

  auto contains(const Node& node) const -> bool;
};
}
}
