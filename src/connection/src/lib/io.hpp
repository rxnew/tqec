#pragma once

#include <iostream>
#include <list>
#include <unordered_map>

#include "connection.hpp"

namespace tqec {
namespace conn {
namespace io {
auto open(std::string const& filename)
  -> std::tuple<Connection::Endpoints, Obstacles, Area>;
auto print(Connection::Routes const& routes, std::ostream& os = std::cout)
  -> void;
}

class IO {
 private:
  using Route = std::list<Node>;
  // 経路の始点がキー
  using Routes = std::unordered_map<Node, Route>;

  static auto _simplifyRoute(const Route& route) -> Route;

 public:
  static auto output(const Route& route, int indent_count = 0,
                     std::ostream& os = std::cout) -> void;
  static auto output(const Routes& routes,
                     std::ostream& os = std::cout) -> void;
};
}
}
