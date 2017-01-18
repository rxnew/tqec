#pragma once

namespace tqec {
struct Module {
  int cost;
  float error_rate;
  int count;

  Module() = default;
  Module(int cost, float error_rate, int count = 1);
  ~Module() = default;
};
}
