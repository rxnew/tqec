#pragma once

#include "node.hpp"

#include <unordered_map>

namespace tqec {
namespace conn {
class PassageCounters {
 private:
  // 全経路のカウンタ
  std::unordered_map<Node, int> counts_all_;
  // 各経路のカウンタのハッシュ
  // 経路の始点がキー
  std::unordered_map<Node, std::unordered_map<Node, int>> counts_map_;

 public:
  PassageCounters() = default;
  explicit PassageCounters(int route_count);
  ~PassageCounters() = default;

  auto count(const Node& node, const Node& src_node) const -> int;
  auto update(const Node& node, const Node& src_node) -> void;
  auto addRoute(const Node& src_node) -> void;
};
}
}
