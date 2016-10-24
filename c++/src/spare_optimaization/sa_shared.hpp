#pragma once

#include "sa.hpp"

#include <vector>

namespace optimization {
template <class State, class Costs, class Rates>
class SASharedT : public SA<State, Costs, Rates> {
 private:
  auto _init() const -> State;
  auto _generate(const State& x) const -> State;
  auto _constraints(const State& x) const -> bool;
  auto _evaluate(const State& x) const -> float;

 public:
  template <class... Args>
  SASharedT(Args... args);
  ~SASharedT() = default;
};

using SAShared = SASharedT<std::vector<std::vector<int>>,
                           std::vector<std::vector<int>>,
                           std::vector<float>>;

template <class T>
auto combination(T n, T k) -> T;
}

#include "sa_shared_impl.hpp"
