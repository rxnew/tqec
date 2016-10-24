#pragma once

#include <cassert>
#include <cmath>
#include <random>
#include <iostream>

namespace optimization {
template <class State, class Costs, class Rates>
int SA<State, Costs, Rates>::max_iter = 500;

template <class State, class Costs, class Rates>
float SA<State, Costs, Rates>::max_temperature = 100.0f;

template <class State, class Costs, class Rates>
float SA<State, Costs, Rates>::min_temperature = 20.0f;

template <class State, class Costs, class Rates>
float SA<State, Costs, Rates>::rambda = 0.9f;

template <class State, class Costs, class Rates>
float SA<State, Costs, Rates>::penalty = 10.0f;

template <class State, class Costs, class Rates>
auto SA<State, Costs, Rates>::_accept(float temperature, float prev_energy,
                                      float next_energy) const -> bool {
  static std::random_device rnd;
  static std::mt19937 mt(rnd());
  static std::uniform_int_distribution<int> i(0, 1);

  auto diff = prev_energy - next_energy;
  if(diff > 0.0f) return true;
  return i(mt) < std::exp(diff / temperature);
}

template <class State, class Costs, class Rates>
auto SA<State, Costs, Rates>::_reduce(float temperature) const -> float {
  return temperature * SA::rambda;
}

template <class State, class Costs, class Rates>
auto SA<State, Costs, Rates>::_weight(float energy,
                                      bool satisfied) const -> float {
  static auto max_energy = 0.0f;
  max_energy = std::max(max_energy, energy + SA::penalty);
  return satisfied ? energy : max_energy;
}

template <class State, class Costs, class Rates>
auto SA<State, Costs, Rates>::_optimize(State x) const -> State {
  auto temperature = SA::max_temperature;

  auto value = this->_evaluate(x);
  auto satisfied = this->_constraints(x);
  auto energy = this->_weight(value, satisfied);

  auto result_x = x;
  auto result_energy = energy;

  while(temperature >= SA::min_temperature) {
    for(auto i = 0; i < SA::max_iter; i++) {
      auto next_x = this->_generate(x);
      auto next_value = this->_evaluate(next_x);
      auto next_satisfied = this->_constraints(next_x);
      auto next_energy = this->_weight(next_value, next_satisfied);

      if(!this->_accept(temperature, energy, next_energy)) continue;

      if(next_satisfied && (!satisfied || result_energy > next_energy)) {
        satisfied = true;
        result_x = next_x;
        result_energy = next_energy;
      }

      x = std::move(next_x);
      energy = next_energy;
    }
    temperature = this->_reduce(temperature);
  }

  return satisfied ? std::move(result_x) : State();
}

template <class State, class Costs, class Rates>
auto SA<State, Costs, Rates>::optimize(const Costs& c, const Rates& e,
                                       float et) const -> State {
  assert(c.size() == e.size());

  this->c = c;
  this->e = e;
  this->et = et;

  auto res = this->_optimize(this->_init());

  this->c.shrink_to_fit();
  this->e.shrink_to_fit();

  return std::move(res);
}
}
