#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/numpy.h>

#include "VAQ.hpp"
#include "utils/Types.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pyvaq, m) {
    py::class_<VAQ>(m, "VAQ")
        .def(py::init([](const std::string &methodString) {
            auto obj = std::make_unique<VAQ>();   // default constructor
            obj->parseMethodString(methodString);        // call your setup method
            return obj;
        }), py::arg("methodString"))

        .def("train", [](VAQ &self, py::array_t<float, py::array::c_style | py::array::forcecast> arr) {
            py::buffer_info info = arr.request();
            if (info.ndim != 2) {
                throw std::runtime_error("Input must be a 2D array");
            }
            RowMatrixXf mat = Eigen::Map<RowMatrixXf>((float*)info.ptr, info.shape[0], info.shape[1]);
            self.train(mat);
        })

        .def("encode", [](VAQ &self, py::array_t<float, py::array::c_style | py::array::forcecast> arr) {
            py::buffer_info info = arr.request();
            if (info.ndim != 2) {
                throw std::runtime_error("Input must be a 2D array");
            }
            RowMatrixXf mat = Eigen::Map<RowMatrixXf>((float*)info.ptr, info.shape[0], info.shape[1]);
            self.encode(mat);
            return py::array_t<uint16_t>(
                {self.mCodebook.rows(), self.mCodebook.cols()},  // shape
                {sizeof(uint16_t) * self.mCodebook.cols(),      // stride for row
                 sizeof(uint16_t)},                            // stride for col
                self.mCodebook.data(),                          // data pointer
                py::cast(self.mCodebook)                        // keep Eigen object alive
            );
        });
}