#include "json11.hpp"

#include "connection.hpp"

namespace tqec {
namespace conn {
namespace io {
using Endpoint = Connection::Endpoint;
using Endpoints = Connection::Endpoints;
using Route = Connection::Route;
// 経路の始点がキー
using Routes = Connection::Routes;

auto _make_endpoints(json11::Json const& json_array) -> Endpoints;
auto _make_endpoint(json11::Json const& json_array) -> Endpoint;
auto _make_obstacles(json11::Json const& json_array) -> Obstacles;
auto _set_obstacle(json11::Json const& json_obj, Obstacles& obstacles)
  -> void;
auto _make_region(json11::Json const& json_obj) -> Area;
auto _make_node(json11::Json const& json_array) -> Node;
auto _make_size(json11::Json const& json_array) -> Size;

auto _to_json(Routes const& routes) -> json11::Json;
auto _to_json(Route const& route) -> json11::Json;
auto _to_json(Node const& node) -> json11::Json;

auto _simplify_route(Route const& route) -> Route;
}
}
}
