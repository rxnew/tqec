#include "passage_counters.hpp"

#include <cassert>

namespace tqec {
namespace conn {
PassageCounters::PassageCounters(int route_count) : counts_map_(route_count) {}

auto PassageCounters::count(const Node& node,
                            const Node& src_node) const -> int {
  assert(this->counts_map_.count(src_node));

  const auto& counts_route = this->counts_map_.at(src_node);

  const auto count_all =
    this->counts_all_.count(node) ? this->counts_all_.at(node) : 0;
  const auto count_route =
    counts_route.count(node) ? counts_route.at(node) : 0;

  return count_all - count_route;
}

auto PassageCounters::update(const Node& node, const Node& src_node) -> void {
  this->counts_all_[node]++;
  this->counts_map_[src_node][node]++;
}

auto PassageCounters::addRoute(const Node& src_node) -> void {
  this->counts_map_.emplace(src_node, std::unordered_map<Node, int>());
}
}
}
