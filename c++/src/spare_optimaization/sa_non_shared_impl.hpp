#pragma once

namespace optimization {
template <class State, class Costs, class Rates>
template <class... Args>
SANonSharedT<State, Costs, Rates>::SANonSharedT(Args... args)
  : SA<State, Costs, Rates>(std::forward<Args>(args)...) {}

template <class State, class Costs, class Rates>
auto SANonSharedT<State, Costs, Rates>::_init() const -> State {
  return State(this->c.size(), 0);
}

template <class State, class Costs, class Rates>
auto SANonSharedT<State, Costs, Rates>::_generate(const State& x) const
  -> State {
  using Uid = std::uniform_int_distribution<int>;

  static std::random_device random;
  static std::mt19937 mt(random());
  static Uid gen_index(0, static_cast<int>(x.size()) - 1);
  static Uid gen_direction(0, 1);

  auto next_x = x;
  auto index = gen_index(mt);
  if(next_x[index] <= 0) {
    next_x[index] = 1;
  }
  else {
    next_x[index] += gen_direction(mt) ? 1 : -1;
  }
  return std::move(next_x);
}

template <class State, class Costs, class Rates>
auto SANonSharedT<State, Costs, Rates>::_constraints(const State& x) const
  -> bool {
  auto success_rate = 1.0f;
  for(auto i = 0; i < static_cast<int>(x.size()); i++) {
    success_rate *= 1.0f - std::pow(this->e[i], static_cast<float>(x[i] + 1));
  }
  return this->et >= 1.0f - success_rate;
}

template <class State, class Costs, class Rates>
auto SANonSharedT<State, Costs, Rates>::_evaluate(const State& x) const
  -> float {
  auto res = 0.0f;
  for(auto i = 0; i < static_cast<int>(x.size()); i++) {
    res += this->c[i] * x[i];
  }
  return res;
}
}
