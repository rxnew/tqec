#pragma once

#include "area.hpp"
#include "obstacles.hpp"
#include "weights.hpp"

#include <list>
#include <queue>

namespace tqec {
namespace conn {
class BestFirstSearch {
 private:
  const Obstacles* const obstacles_ptr_;
  const Weights* const weights_ptr_;
  const Area area_;
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
  auto _isOutsideArea(const Node& node) const -> bool;
  auto _isDestinationNode(const Node& node) const -> bool;
  auto _createRoute(const NodeMap& visited_nodes) const -> std::list<Node>;

 public:
  BestFirstSearch(const Obstacles* const obstacles_ptr,
                  const Weights* const weights_ptr, const Area& area);
  ~BestFirstSearch() = default;

  auto search(const Node& src_node, const Node& dst_node,
              float bias) const -> std::list<Node>;
  auto expandNode(const Node& node) const -> std::vector<Node>;
};
}
}
