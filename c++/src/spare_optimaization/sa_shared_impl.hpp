#pragma once

namespace optimization {
template <class State, class Costs, class Rates>
template <class... Args>
SASharedT<State, Costs, Rates>::SASharedT(Args... args)
  : SA<State, Costs, Rates>(std::forward<Args>(args)...) {}

template <class State, class Costs, class Rates>
auto SASharedT<State, Costs, Rates>::_init() const -> State {
  State state;
  state.reserve(this->c.size());
  for(const auto& ci : this->c) {
    state.push_back(typename State::value_type(ci.size(), 0));
  }
  return std::move(state);
}

template <class State, class Costs, class Rates>
auto SASharedT<State, Costs, Rates>::_generate(const State& x) const
  -> State {
  using Uid = std::uniform_int_distribution<int>;

  static std::random_device random;
  static std::mt19937 mt(random());
  static Uid gen_index_i(0, static_cast<int>(x.size()) - 1);
  static Uid gen_direction(0, 1);

  auto gen_index_j_wrapper = [&x](std::mt19937& mt, int index_i) {
    Uid gen_index_j(0, static_cast<int>(x[index_i].size()) - 1);
    return gen_index_j(mt);
  };

  auto next_x = x;
  auto index_i = gen_index_i(mt);
  auto index_j = gen_index_j_wrapper(mt, index_i);
  if(next_x[index_i][index_j] <= 0) {
    next_x[index_i][index_j] = 1;
  }
  else {
    next_x[index_i][index_j] += gen_direction(mt) ? 1 : -1;
  }
  return std::move(next_x);
}

template <class State, class Costs, class Rates>
auto SASharedT<State, Costs, Rates>::_constraints(const State& x) const
  -> bool {
  auto g = [](float e, int n, int x) {
    float res = 0.0f;
    for(auto i = 0; i <= x; i++) {
      res += combination(n + x, n + i) *
             std::pow(e, x - i) * std::pow(1.0f - e, n + i);
      // combination()の結果ががオーバーフローした場合の対処
      if(res < 0.0f) return 0.0f;
    }
    return res;
  };

  auto success_rate = 1.0f;
  for(auto i = 0; i < static_cast<int>(x.size()); i++) {
    auto ni = static_cast<int>(x[i].size());
    auto xi = std::accumulate(x[i].cbegin(), x[i].cend(), 0);
    success_rate *= g(this->e[i], ni, xi);
  }
  return this->et >= 1.0f - success_rate;
}

template <class State, class Costs, class Rates>
auto SASharedT<State, Costs, Rates>::_evaluate(const State& x) const
  -> float {
  auto res = 0.0f;
  for(auto i = 0; i < static_cast<int>(x.size()); i++) {
    for(auto j = 0; j < static_cast<int>(x[i].size()); j++) {
      res += this->c[i][j] * x[i][j];
    }
  }
  return res;
}

template <class T>
auto combination(T n, T k) -> T {
  k = std::min(k, n - k);
  T res(1);
  for(auto i = 1; i <= k; i++) {
    res *= n--;
    res /= i;
  }
  return res;
}
}
