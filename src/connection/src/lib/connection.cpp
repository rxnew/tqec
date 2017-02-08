#include "connection.hpp"

#include <limits>

namespace tqec {
namespace conn {
auto Connection::_countCosts(const Routes& routes) const -> int {
  auto count = 0;
  for(const auto& route_pair : routes) {
    count += route_pair.second.size();
  }
  return count;
}

auto Connection::_countOverlappedNodes(const Routes& routes) const -> int {
  auto count = 0;
  std::unordered_set<Node> passed_nodes;
  for(const auto& route_pair : routes) {
    for(const auto& node : route_pair.second) {
      if(passed_nodes.count(node)) count++;
      else                         passed_nodes.insert(node);
    }
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

Connection::Connection(const Endpoints& endpoints, const Obstacles& obstacles,
                       const Area& area)
  : endpoints_(endpoints), obstacles_(obstacles), weights_(endpoints.size()),
    bfs_(&this->obstacles_, &this->weights_, area) {
  for(const auto& endpoint : this->endpoints_) {
    this->weights_.addRoute(endpoint.first);
    this->obstacles_.add(endpoint.first);
    this->obstacles_.add(endpoint.second);
  }
}

auto Connection::search() -> Routes {
  Routes result_routes;
  auto result_cost = std::numeric_limits<int>::max();
  auto result_intersection_count = std::numeric_limits<int>::max();
  auto count = 0;
  //auto non_update_count = 0;
  auto bias = 0.0f;

  while(true) {
    Routes routes;

    for(const auto& endpoint : this->endpoints_) {
      const auto& src_node = endpoint.first;
      const auto& dst_node = endpoint.second;
      const auto route = this->bfs_.search(src_node, dst_node, bias);
      routes[src_node] = route;
    }

    auto cost = this->_countCosts(routes);
    auto intersection_count = this->_countOverlappedNodes(routes);
    /*
    std::cout << "Cost: " << cost << ' '
              << "Over: " << intersection_count
              << std::endl;
    */
    if(intersection_count <= result_intersection_count) {
      if(intersection_count < result_intersection_count || cost < result_cost) {
        result_cost = cost;
        result_intersection_count = intersection_count;
        result_routes = routes;
        //non_update_count = 0;
      }
    }

    if(result_intersection_count == 0) break;
    // とりあえず100回試行
    if(count++ > 100) break;
    // とりあえず20回経路の更新が行われなかったら終了
    //if(count > 50 && non_update_count++ > 10) break;

    if(bias < 1.0f) bias += 0.01f;
    this->_updateWeights(routes);
  }

  /*
    std::cout << "Cost: " << this->_countCosts(result_routes) << ' '
              << "Over: " << this->_countOverlappedNodes(result_routes)
              << std::endl;
  */

  return result_routes;
}
}
}
