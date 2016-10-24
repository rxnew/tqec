#pragma once

#include "sa.hpp"

#include <vector>

namespace optimization {
template <class State, class Costs, class Rates>
class SANonSharedT : public SA<State, Costs, Rates> {
 private:
  auto _init() const -> State;
  auto _generate(const State& x) const -> State;
  auto _constraints(const State& x) const -> bool;
  auto _evaluate(const State& x) const -> float;

 public:
  template <class... Args>
  SANonSharedT(Args... args);
  ~SANonSharedT() = default;
};

using SANonShared = SANonSharedT<std::vector<int>, std::vector<int>,
                                 std::vector<float>>;
}

#include "sa_non_shared_impl.hpp"
