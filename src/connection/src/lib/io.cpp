#include "io.hpp"
#include "io_private.hpp"

#include <fstream>

namespace tqec {
namespace conn {
namespace io {
auto open(std::string const& filename)
  -> std::tuple<Endpoints, Obstacles, Area> {
  auto ifs = std::ifstream(filename);

  assert(!ifs.fail());

  auto buf = std::string();
  auto tmp = std::string();
  while(std::getline(ifs, tmp)) buf += tmp;

  ifs.close();

  auto err = std::string();
  auto json_obj = json11::Json::parse(buf, err);

  auto endpoints = _make_endpoints(json_obj["endpoints"]);
  auto obstacles = _make_obstacles(json_obj["obstacles"]);
  auto region    = _make_region(json_obj["region"]);

  return std::make_tuple(endpoints, obstacles, region);
}

auto print(Routes const& routes, std::ostream& os) -> void {
  auto json_obj = _to_json(routes);
  os << json_obj.dump() << std::endl;
}

auto _make_endpoints(json11::Json const& json_array) -> Endpoints {
  assert(json_array.is_array());
  auto endpoints = Endpoints();
  for(auto const& endpoint_json_array : json_array.array_items()) {
    endpoints.push_back(_make_endpoint(endpoint_json_array));
  }
  return endpoints;
}

auto _make_endpoint(json11::Json const& json_array) -> Endpoint {
  assert(json_array.is_array());
  auto nodes = std::vector<Node>();
  for(auto const& node_json_array : json_array.array_items()) {
    nodes.push_back(_make_node(node_json_array));
  }
  return Endpoint(nodes[0], nodes[1]);
}

auto _make_obstacles(json11::Json const& json_array) -> Obstacles {
  assert(json_array.is_array());
  auto obstacles = Obstacles();
  for(auto const& obstacle_json_array : json_array.array_items()) {
    _set_obstacle(obstacle_json_array, obstacles);
  }
  return obstacles;
}

auto _set_obstacle(json11::Json const& json_obj, Obstacles& obstacles)
  -> void {
  assert(json_obj.is_object());
  auto node = _make_node(json_obj["position"]);
  auto size = _make_size(json_obj["size"]);
  obstacles.addRectangular(node, size);
}

auto _make_region(json11::Json const& json_obj) -> Area {
  assert(json_obj.is_object());
  auto node = _make_node(json_obj["position"]);
  auto size = _make_size(json_obj["size"]);
  return Area(node, size);
}

auto _make_node(json11::Json const& json_array) -> Node {
  assert(json_array.is_array());
  auto values = std::vector<int>();
  for(auto const& json_value : json_array.array_items()) {
    assert(json_value.is_number());
    values.push_back(json_value.int_value());
  }
  return Node(values[0], values[1], values[2]);
}

auto _make_size(json11::Json const& json_array) -> Size {
  assert(json_array.is_array());
  auto values = std::vector<int>();
  for(auto const& json_value : json_array.array_items()) {
    assert(json_value.is_number());
    values.push_back(json_value.int_value());
  }
  return Size(values[0], values[1], values[2]);
}

auto _to_json(Routes const& routes) -> json11::Json {
  auto json_array = json11::Json::array();
  for(auto const& route_pair : routes) {
    json_array.push_back(_to_json(_simplify_route(route_pair.second)));
  }
  return json11::Json::object{
    {"connections", json_array}
  };
}

auto _to_json(Route const& route) -> json11::Json {
  auto json_array = json11::Json::array();
  for(auto const& node : route) {
    json_array.push_back(_to_json(node));
  }
  return json_array;
}

auto _to_json(Node const& node) -> json11::Json {
  return json11::Json::array{node.x, node.y, node.z};
}

auto _simplify_route(Route const& route) -> Route {
  if(route.size() < 2) return route;

  auto axis = [](Node const& node1, Node const& node2) {
    if(node1.x != node2.x) return 0;
    if(node1.y != node2.y) return 1;
    if(node1.z != node2.z) return 2;
    return -1;
  };

  auto simple_route = Route();

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

  return simple_route;
}
}

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
