#pragma once

#include "module.hpp"

#include <vector>

namespace tqec {
class SA {
 public:
  using Counts = std::vector<int>;
  using Modules = std::vector<Module>;

  static int max_iter;
  static float max_temperature;
  static float min_temperature;
  static float rambda;
  static float penalty;

  SA() = default;
  virtual ~SA() = default;

  auto optimize(Modules const& modules,
                float error_rate_threshold) const -> Counts;

 protected:
  mutable Modules modules_;
  mutable float error_rate_threshold_;

  auto _init() const -> Counts;
  auto _generate(Counts const& x) const -> Counts;
  auto _accept(float temperature, float prev_energy,
               float next_energy) const -> bool;
  auto _reduce(float temperature) const -> float;
  auto _weight(float energy, bool satisfied) const -> float;
  auto _constraints(Counts const& x) const -> bool;
  auto _evaluate(Counts const& x) const -> float;
  auto _optimize(Counts x) const -> Counts;
};
}
