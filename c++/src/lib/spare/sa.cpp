#include "sa.hpp"

#include "util/math.hpp"

#include <cassert>
#include <cmath>
#include <random>
#include <iostream>

namespace tqec {
namespace spare {
int SA::max_iter = 500;
float SA::max_temperature = 100.0f;
float SA::min_temperature = 20.0f;
float SA::rambda = 0.9f;
float SA::penalty = 10.0f;

auto SA::_init() const -> Counts {
  return Counts(this->modules_.size(), 0);
}

auto SA::_generate(const Counts& counts) const -> Counts {
  using Uid = std::uniform_int_distribution<int>;

  static std::random_device random;
  static std::mt19937 mt(random());
  static Uid gen_index(0, static_cast<int>(counts.size()) - 1);
  static Uid gen_direction(0, 1);

  auto next_counts = counts;
  auto index = gen_index(mt);
  if(next_counts[index] <= 0) {
    next_counts[index] = 1;
  }
  else {
    next_counts[index] += gen_direction(mt) ? 1 : -1;
  }
  return std::move(next_counts);
}

auto SA::_accept(float temperature, float prev_energy,
                 float next_energy) const -> bool {
  static std::random_device rnd;
  static std::mt19937 mt(rnd());
  static std::uniform_int_distribution<int> i(0, 1);

  auto diff = prev_energy - next_energy;
  if(diff > 0.0f) return true;
  return i(mt) < std::exp(diff / temperature);
}

auto SA::_reduce(float temperature) const -> float {
  return temperature * SA::rambda;
}

auto SA::_weight(float energy, bool satisfied) const -> float {
  static auto max_energy = 0.0f;
  max_energy = std::max(max_energy, energy + SA::penalty);
  return satisfied ? energy : max_energy;
}

auto SA::_constraints(const Counts& counts) const -> bool {
  auto g = [](float e, int n, int x) {
    float res = 0.0f;
    for(auto i = 0; i <= x; i++) {
      res += util::combination(n + x, n + i) *
             std::pow(e, x - i) * std::pow(1.0f - e, n + i);
      // combination()の結果ががオーバーフローした場合の対処
      if(res < 0.0f) return 0.0f;
    }
    return res;
  };

  auto success_rate = 1.0f;
  for(auto i = 0; i < static_cast<int>(counts.size()); i++) {
    const auto& module = this->modules_[i];
    success_rate *= g(module.error_rate, module.count, counts[i]);
  }
  return this->error_rate_threshold_ >= 1.0f - success_rate;
}

auto SA::_evaluate(const Counts& counts) const -> float {
  auto value = 0.0f;
  for(auto i = 0; i < static_cast<int>(counts.size()); i++) {
    value += this->modules_[i].cost * counts[i];
  }
  return value;
}

auto SA::_optimize(Counts counts) const -> Counts {
  auto temperature = SA::max_temperature;

  auto value = this->_evaluate(counts);
  auto satisfied = this->_constraints(counts);
  auto energy = this->_weight(value, satisfied);

  auto result_counts = counts;
  auto result_energy = energy;

  while(temperature >= SA::min_temperature) {
    for(auto i = 0; i < SA::max_iter; i++) {
      auto next_counts = this->_generate(counts);
      auto next_value = this->_evaluate(next_counts);
      auto next_satisfied = this->_constraints(next_counts);
      auto next_energy = this->_weight(next_value, next_satisfied);

      if(!this->_accept(temperature, energy, next_energy)) continue;

      if(next_satisfied && (!satisfied || result_energy > next_energy)) {
        satisfied = true;
        result_counts = next_counts;
        result_energy = next_energy;
      }

      counts = std::move(next_counts);
      energy = next_energy;
    }
    temperature = this->_reduce(temperature);
  }

  return satisfied ? std::move(result_counts) : Counts();
}

auto SA::optimize(const Modules& modules,
                  float error_rate_threshold) const -> Counts {
  this->modules_ = modules;
  this->error_rate_threshold_ = error_rate_threshold;

  auto spare_counts = this->_optimize(this->_init());

  this->modules_.shrink_to_fit();

  return std::move(spare_counts);
}
}
}
