#pragma once

#include "module.hpp"

#include <vector>

namespace tqec {
namespace spare {
using Counts = std::vector<int>;
using Modules = std::vector<Module>;

class SA {
 protected:
  mutable Modules modules_;
  mutable float error_rate_threshold_;

  auto _init() const -> Counts;
  auto _generate(const Counts& x) const -> Counts;
  auto _accept(float temperature, float prev_energy,
               float next_energy) const -> bool;
  auto _reduce(float temperature) const -> float;
  auto _weight(float energy, bool satisfied) const -> float;
  auto _constraints(const Counts& x) const -> bool;
  auto _evaluate(const Counts& x) const -> float;
  auto _optimize(Counts x) const -> Counts;

 public:
  static int max_iter;
  static float max_temperature;
  static float min_temperature;
  static float rambda;
  static float penalty;

  SA() = default;
  virtual ~SA() = default;

  auto optimize(const Modules& modules,
                float error_rate_threshold) const -> Counts;
};
}
}
