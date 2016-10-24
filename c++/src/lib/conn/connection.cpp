#include "connection.hpp"

#include "best_first_search.hpp"

namespace tqec {
namespace conn {
auto Connection::_updatePassageCounters(const Routes& routes) -> void {
  for(const auto& route_pair : routes) {
    const auto& src_node = route_pair.first;
    for(const auto& node : route_pair.second) {
      this->counters_.update(node, src_node);
    }
  }
}

auto Connection::_isNonOverlappedRoutes(const Routes& routes) const -> bool {
  std::unordered_set<Node> passed_nodes;
  for(const auto& route_pair : routes) {
    for(const auto& node : route_pair.second) {
      if(passed_nodes.count(node)) return false;
      passed_nodes.insert(node);
    }
  }
  return true;
}

Connection::Connection(const Endpoints& endpoints, const Obstacles& obstacles)
  : endpoints_(endpoints), obstacles_(obstacles), counters_(endpoints.size()) {
  for(const auto& endpoint : this->endpoints_) {
    this->counters_.addRoute(endpoint.first);
  }
}

auto Connection::search() -> Routes {
  BestFirstSearch bfs(&this->obstacles_, &this->counters_);
  auto bias = 0.0f;

  while(true) {
    Routes routes;

    for(const auto& endpoint : this->endpoints_) {
      const auto& src_node = endpoint.first;
      const auto& dst_node = endpoint.second;
      const auto route = bfs.search(src_node, dst_node, bias);
      routes[src_node] = route;
    }

    bias += 0.1f;
    this->_updatePassageCounters(routes);

    if(this->_isNonOverlappedRoutes(routes)) return routes;
    std::cout << "retry" << std::endl;
  }

  return Routes();
}
}
}
