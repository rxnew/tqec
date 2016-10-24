#include "best_first_search.hpp"

namespace tqec {
namespace conn {
auto BestFirstSearch::_evaluateNode(const Node& node) const -> float {
  std::unordered_map<Node, float> cache;

  if(cache.count(node)) return cache[node];

  const auto dst_distance = this->dst_node_.distance(node);
  const auto count = this->counters_ptr_->count(node, this->src_node_);
  return cache[node] = dst_distance + (count * this->bias_);
}

auto BestFirstSearch::_compareNode(const Node& lhs,
                                   const Node& rhs) const -> bool {
  return this->_evaluateNode(lhs) > this->_evaluateNode(rhs);
}

auto BestFirstSearch::_isObstacleNode(const Node& node) const -> bool {
  if(node != this->src_node_ || node != this->dst_node_) return false;
  return this->obstacles_ptr_->has(node);
}

auto BestFirstSearch::_expandNode(const Node& node) const -> std::vector<Node> {
  static constexpr std::array<int, 6> nx{1, 0, 0, -1, 0, 0};
  static constexpr std::array<int, 6> ny{0, 1, 0, 0, -1, 0};
  static constexpr std::array<int, 6> nz{0, 0, 1, 0, 0, -1};

  std::vector<Node> expanded_nodes;
  expanded_nodes.reserve(6);

  for(auto i = 0; i < 6; i++) {
    const auto next_node = Node(node.x + nx[i], node.y + ny[i], node.z + nz[i]);

    if(this->_isObstacleNode(next_node)) continue;

    expanded_nodes.push_back(next_node);
  }

  return std::move(expanded_nodes);
}

auto BestFirstSearch::_isDestinationNode(const Node& node) const -> bool {
  return node == this->dst_node_;
}

auto BestFirstSearch::_createRoute(const NodeMap& visited_nodes) const
  -> std::list<Node> {
  std::list<Node> route;

  auto node = this->dst_node_;
  while(node != this->src_node_) {
    route.push_front(node);
    node = visited_nodes.at(node);
  }
  route.push_front(node);

  return std::move(route);
}

BestFirstSearch::BestFirstSearch(const Obstacles* const obstacles_ptr,
                                 const PassageCounters* const counters_ptr)
  : obstacles_ptr_(obstacles_ptr), counters_ptr_(counters_ptr),
    compare_node_(std::bind(&BestFirstSearch::_compareNode, this,
                            std::placeholders::_1, std::placeholders::_2)) {}

auto BestFirstSearch::search(const Node& src_node, const Node& dst_node,
                             float bias) const -> std::list<Node> {
  this->src_node_ = src_node;
  this->dst_node_ = dst_node;
  this->bias_ = bias;

  // キーは探索済みNode・値は一つ前のNode
  NodeMap visited_nodes;
  NodeQueue queue(this->compare_node_);

  visited_nodes.emplace(this->src_node_, Node());
  queue.push(this->src_node_);

  while(!queue.empty()) {
    auto node = queue.top();
    queue.pop();
    if(this->_isDestinationNode(node)) return this->_createRoute(visited_nodes);
    for(const auto& next_node : this->_expandNode(node)) {
      if(!visited_nodes.count(next_node)) {
        visited_nodes.emplace(next_node, node);
        queue.push(next_node);
      }
    }
  }

  return std::list<Node>();
}
}
}
