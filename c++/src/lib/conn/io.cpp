#include "io.hpp"

#include "node.hpp"

namespace tqec {
namespace conn {
auto IO::_simplifyRoute(const Route& route) -> Route {
  if(route.size() < 2) return route;

  auto axis = [](const Node& node1, const Node& node2) {
    if(node1.x != node2.x) return 0;
    if(node1.y != node2.y) return 1;
    if(node1.z != node2.z) return 2;
    return -1;
  };

  Route simple_route;

  simple_route.push_back(route.front());

  auto prev_node = route.front();
  auto prev_axis = -1;

  for(auto it = route.cbegin()++; it != route.cend(); it++) {
    auto cur_node = *it;
    auto cur_axis = axis(prev_node, cur_node);

    if(prev_axis != -1 && cur_axis != prev_axis) {
      simple_route.push_back(prev_node);
    }

    prev_axis = cur_axis;
    prev_node = cur_node;
  }

  simple_route.push_back(route.back());

  return std::move(simple_route);
}


auto IO::output(const Route& route, int indent_count,
                std::ostream& os) -> void {
  if(static_cast<int>(route.size()) < 2) return;

  std::string indent1(4 * indent_count, ' ');
  std::string indent2(4 * (indent_count + 1), ' ');

  os << indent1 << '{' << std::endl;

  os << indent2
     << "\"source\": "
     << route.front()
     << ','
     << std::endl;

  os << indent2
     << "\"destination\": "
     << route.back()
     << ','
     << std::endl;

  os << indent2 << "\"route\": [";

  {
    auto middles = route;
    middles.pop_front();
    middles.pop_back();

    auto first = true;
    for(const auto& node : middles) {
      if(!first) os << ", ";
      else       first = false;
      os << node;
    }
  }

  os << ']' << std::endl;

  os << indent1 << '}';
}

auto IO::output(const Routes& routes, std::ostream& os) -> void {
  os << "\"connections\": [" << std::endl;

  {
    auto first = true;
    for(const auto& route_pair : routes) {
      if(!first) os << ',' << std::endl;
      else       first = false;
      output(_simplifyRoute(route_pair.second), 1, os);
    }
  }

  os << std::endl;

  os << ']' << std::endl;
}
}
}
