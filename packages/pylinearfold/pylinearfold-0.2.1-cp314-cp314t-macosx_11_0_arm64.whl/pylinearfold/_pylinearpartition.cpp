#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <LinearPartition.h>

#include <vector>

namespace py = pybind11;

// helper function to avoid making a copy when returning a py::array_t
// author: https://github.com/YannickJadoul
// source: https://github.com/pybind/pybind11/issues/1042#issuecomment-642215028
template<typename Sequence>
inline py::array_t<typename Sequence::value_type>
as_pyarray(Sequence&& seq)
{
  auto size = seq.size();
  auto data = seq.data();
  std::unique_ptr<Sequence> seq_ptr =
    std::make_unique<Sequence>(std::move(seq));
  auto capsule = py::capsule(seq_ptr.get(), [](void* p) {
    std::unique_ptr<Sequence>(reinterpret_cast<Sequence*>(p));
  });
  seq_ptr.release();
  return py::array(size, data, capsule);
}

struct Prob
{
  int i;
  int j;
  pf_type prob;
};

PYBIND11_MODULE(_pylinearpartition, m)
{
  m.doc() = "Python Bindings for linearpartition";

  PYBIND11_NUMPY_DTYPE(Prob, i, j, prob);

  m.def(
    "partition",
    [](std::string seq, int beam_size, bool verbose, bool sharpturn) {
      BeamCKYParser parser(
        beam_size, !sharpturn, verbose, "", "", false, 0.0, "", true);
      double free_energy = parser.parse(seq);

      // Convert Pij to a vector of Prob structs in order to be exposable
      // as a numpy array.
      std::vector<Prob> probs;
      for (const auto& [key, value] : parser.Pij) {
        probs.push_back({ key.first, key.second, value });
      }

      using namespace pybind11::literals;
      return py::dict("structure"_a = parser.exported_structure,
                      "free_energy"_a = free_energy,
                      "probabilities"_a = as_pyarray(std::move(probs)));
    },
    py::arg("seq"),
    py::arg("beamsize") = 100,
    py::arg("verbose") = false,
    py::arg("sharpturn") = false);
}
