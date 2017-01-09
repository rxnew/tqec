#include "qc/circuit.hpp"
#include "qc/algorithm.hpp"
#include "qc/io.hpp"

auto main(int argc, char* argv[]) -> int {
  auto input = argc >= 2 ? argv[1] : "circuit_data/t.json";
  auto circuit = qc::io::Json::open(input);
  circuit = qc::tqc_parallelize(circuit);
  qc::io::Json::print(circuit);
  return 0;
}
