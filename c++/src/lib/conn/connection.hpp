#pragma once

#include "obstacles.hpp"
#include "passage_counters.hpp"

#include <list>

namespace tqec {
namespace conn {
class Connection {
 public:
  using Endpoint = std::pair<Node, Node>;
  using Endpoints = std::list<Endpoint>;
  using Route = std::list<Node>;
  // 経路の始点がキー
  using Routes = std::unordered_map<Node, Route>;

 private:
  Endpoints endpoints_;
  Obstacles obstacles_;
  PassageCounters counters_;

  auto _updatePassageCounters(const Routes& routes) -> void;
  auto _isNonOverlappedRoutes(const Routes& routes) const -> bool;

 public:
  Connection(const Endpoints& endpoints, const Obstacles& obstacles);
  ~Connection() = default;

  auto search() -> Routes;
};
}
}
