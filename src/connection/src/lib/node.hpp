#pragma once

#include <functional>
#include <iostream>

// デバッグ用
#include <cassert>
#include <iostream>

namespace tqec {
namespace conn {
struct Node {
  int x;
  int y;
  int z;

  Node() = default;
  Node(int x, int y, int z);
  Node(const Node&) = default;

  auto operator=(const Node&) -> Node& = default;
  auto operator==(const Node& other) const -> bool;
  auto operator!=(const Node& other) const -> bool;

  auto distance(const Node& other) const -> int;

  friend auto operator<<(std::ostream& os, const Node& node) -> std::ostream&;
};
}
}

namespace std {
template <>
struct hash<tqec::conn::Node> {
  auto operator()(const tqec::conn::Node& node) const -> size_t;
};
}
