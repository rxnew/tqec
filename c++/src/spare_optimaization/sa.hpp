#pragma once

namespace optimization {
template <class State, class Costs, class Rates>
class SA {
 protected:
  mutable Costs c;
  mutable Rates e;
  mutable float et;

  virtual auto _init() const -> State = 0;
  virtual auto _generate(const State& x) const -> State = 0;
  auto _accept(float temperature, float prev_energy,
               float next_energy) const -> bool;
  auto _reduce(float temperature) const -> float;
  auto _weight(float energy, bool satisfied) const -> float;
  virtual auto _constraints(const State& x) const -> bool = 0;
  virtual auto _evaluate(const State& x) const -> float = 0;
  auto _optimize(State x) const -> State;

 public:
  static int max_iter;
  static float max_temperature;
  static float min_temperature;
  static float rambda;
  static float penalty;

  SA() = default;
  virtual ~SA() = default;

  auto optimize(const Costs& c, const Rates& e, float et) const -> State;
};
}

#include "sa_impl.hpp"
