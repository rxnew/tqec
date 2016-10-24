#pragma once

#include "obstacles.hpp"
#include "passage_counters.hpp"

#include <list>
#include <queue>

namespace tqec {
namespace conn {
class BestFirstSearch {
 private:
  const Obstacles* const obstacles_ptr_;
  const PassageCounters* const counters_ptr_;
  const std::function<bool(const Node&, const Node&)> compare_node_;

  using NodeMap = std::unordered_map<Node, Node>;
  using NodeQueue =
    std::priority_queue<Node, std::vector<Node>, decltype(compare_node_)>;

  mutable Node src_node_;
  mutable Node dst_node_;
  mutable float bias_;

  auto _evaluateNode(const Node& node) const -> float;
  auto _compareNode(const Node& lhs, const Node& rhs) const -> bool;
  auto _isObstacleNode(const Node& node) const -> bool;
  auto _expandNode(const Node& node) const -> std::vector<Node>;
  auto _isDestinationNode(const Node& node) const -> bool;
  auto _createRoute(const NodeMap& visited_nodes) const -> std::list<Node>;

 public:
  BestFirstSearch(const Obstacles* const obstacles_ptr,
                  const PassageCounters* const counters_ptr);
  ~BestFirstSearch() = default;

  auto search(const Node& src_node, const Node& dst_node,
              float bias) const -> std::list<Node>;
};
}
}
