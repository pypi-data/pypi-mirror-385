#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <LinearFold.h>

#include <optional>
#include <string>

namespace py = pybind11;

PYBIND11_MODULE(_pylinearfold, m)
{
  m.doc() = "Python Bindings for linearfold";

  m.def(
    "fold",
    [](std::string seq,
       int beam_size,
       bool verbose,
       bool sharpturn,
       bool zuker,
       float delta,
       int dangles) {
      BeamCKYParser parser(beam_size,
                           !sharpturn,
                           verbose,
                           false,
                           zuker,
                           delta,
                           "",
                           false,
                           dangles);
      auto result = parser.parse(seq, {});

      using namespace pybind11::literals;
      return py::dict("structure"_a = result.structure,
                      "free_energy"_a = result.score / -100.0);
    },
    py::arg("seq"),
    py::arg("beamsize") = 100,
    py::arg("verbose") = false,
    py::arg("sharpturn") = false,
    py::arg("zuker") = false,
    py::arg("delta") = 5.0,
    py::arg("dangles") = 2);
}
