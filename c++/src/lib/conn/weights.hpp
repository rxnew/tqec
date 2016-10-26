#pragma once

#include "node.hpp"

#include <unordered_map>

namespace tqec {
namespace conn {
class Weights {
 private:
  // 全経路の重み
  std::unordered_map<Node, int> weights_all_;
  // 各経路の重みのハッシュ
  // 経路の始点がキー
  std::unordered_map<Node, std::unordered_map<Node, int>> weights_map_;

 public:
  Weights() = default;
  explicit Weights(int route_count);
  ~Weights() = default;

  auto calculate(const Node& node, const Node& src_node) const -> int;
  auto update(const Node& node, const Node& src_node,
              int sibling_nodes_count) -> void;
  // 経路(始点で管理)を追加
  auto addRoute(const Node& src_node) -> void;
};
}
}
