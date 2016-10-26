#include "connection.hpp"

namespace tqec {
namespace conn {
auto Connection::_countCosts(const Routes& routes) -> int {
  auto count = 0;
  for(const auto& route_pair : routes) {
    count += route_pair.second.size();
  }
  return count;
}

auto Connection::_updateWeights(const Routes& routes) -> void {
  for(const auto& route_pair : routes) {
    const auto& src_node = route_pair.first;
    const auto& dst_node = route_pair.second.back();
    // 始点と終点の兄弟Nodeの数は1
    auto sibling_nodes_count = 1;

    for(const auto& node : route_pair.second) {
      if(node == dst_node) {
        this->weights_.update(node, src_node, 1);
        break;
      }

      this->weights_.update(node, src_node, sibling_nodes_count);
      sibling_nodes_count = this->bfs_.expandNode(node).size();
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
  : endpoints_(endpoints), obstacles_(obstacles), weights_(endpoints.size()),
    bfs_(&this->obstacles_, &this->weights_) {
  for(const auto& endpoint : this->endpoints_) {
    this->weights_.addRoute(endpoint.first);
  }
}

auto Connection::search() -> Routes {
  //auto bias = 0.0f;
  auto bias = 1.0f;

  while(true) {
    Routes routes;

    for(const auto& endpoint : this->endpoints_) {
      const auto& src_node = endpoint.first;
      const auto& dst_node = endpoint.second;
      const auto route = this->bfs_.search(src_node, dst_node, bias);
      routes[src_node] = route;
    }

    //if(bias < 1.0f) bias += 0.05f;
    this->_updateWeights(routes);

    if(this->_isNonOverlappedRoutes(routes)) return routes;
    std::cout << "Cost: " << this->_countCosts(routes) << std::endl;
  }

  return Routes();
}
}
}
