#include "weights.hpp"

#include <cassert>

namespace tqec {
namespace conn {
Weights::Weights(int route_count) : weights_map_(route_count) {}

auto Weights::calculate(const Node& node, const Node& src_node) const -> int {
  assert(this->weights_map_.count(src_node));

  const auto& weights_route = this->weights_map_.at(src_node);

  const auto weight_all =
    this->weights_all_.count(node) ? this->weights_all_.at(node) : 0;
  const auto weight_route =
    weights_route.count(node) ? weights_route.at(node) : 0;

  return weight_all - weight_route;
}

auto Weights::update(const Node& node, const Node& src_node,
                     int sibling_nodes_count) -> void {
  // 兄弟Nodeの数が少ない程重みは大きい
  auto additional_weight = 7 - sibling_nodes_count;
  this->weights_all_[node] += additional_weight;
  this->weights_map_[src_node][node] += additional_weight;
}

auto Weights::addRoute(const Node& src_node) -> void {
  this->weights_map_.emplace(src_node, std::unordered_map<Node, int>());
}
}
}
