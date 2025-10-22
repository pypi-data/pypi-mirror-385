#include <string>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include "roboflex_core/core.h"
#include "roboflex_webcam_gst/webcam_gst.h"

namespace py = pybind11;

using namespace roboflex;
using namespace roboflex::core;
using namespace roboflex::webcam_gst;


PYBIND11_MODULE(roboflex_webcam_gst_ext, m) {
    m.doc() = "roboflex_webcam_gst_ext";

    m.def("get_device_list", &get_device_list);
    m.def("get_device_list_string", &get_device_list_string);

    py::register_exception<WebcamException>(m, "WebcamException");

    py::class_<DeviceDescriptor, std::shared_ptr<DeviceDescriptor>>(m, "DeviceDescriptor")
        .def_readonly("display_name", &DeviceDescriptor::display_name)
        .def_readonly("device_class", &DeviceDescriptor::device_class)
        .def_readonly("gst_factory_name", &DeviceDescriptor::gst_factory_name)
        .def_readonly("device_path", &DeviceDescriptor::device_path)
        .def_readonly("caps_strings", &DeviceDescriptor::caps_strings)
        .def("__repr__", &DeviceDescriptor::to_string)
    ;

    py::class_<WebcamDataRaw, Message, std::shared_ptr<WebcamDataRaw>>(m, "WebcamDataRaw")
        .def(py::init([](const std::shared_ptr<core::Message> o) {
            return std::make_shared<WebcamDataRaw>(*o); }),
            "Construct a WebcamDataRaw from a core message",
            py::arg("other"))
        .def_property_readonly("t0", &WebcamDataRaw::get_t0)
        .def_property_readonly("t1", &WebcamDataRaw::get_t1)
        .def_property_readonly("width", &WebcamDataRaw::get_width)
        .def_property_readonly("height", &WebcamDataRaw::get_height)
        .def_property_readonly("data", &WebcamDataRaw::get_data)
        .def_property_readonly("data_size_bytes", &WebcamDataRaw::get_data_size_bytes)
        .def_property_readonly("pixel_format", &WebcamDataRaw::get_pixel_format)
        .def_property_readonly("sequence", &WebcamDataRaw::get_sequence)
        .def_property_readonly("capture_time", &WebcamDataRaw::get_capture_time)
        .def("__repr__", &WebcamDataRaw::to_string)
    ;

    py::class_<WebcamDataRGB, Message, std::shared_ptr<WebcamDataRGB>>(m, "WebcamDataRGB")
        .def(py::init([](const std::shared_ptr<core::Message> o) {
            return std::make_shared<WebcamDataRGB>(*o); }),
            "Construct a WebcamDataRGB from a core message",
            py::arg("other"))
        .def_property_readonly("t0", &WebcamDataRGB::get_t0)
        .def_property_readonly("t1", &WebcamDataRGB::get_t1)
        .def_property_readonly("rgb", &WebcamDataRGB::get_rgb)
        .def_property_readonly("pixel_format", &WebcamDataRGB::get_pixel_format)
        .def_property_readonly("sequence", &WebcamDataRGB::get_sequence)
        .def_property_readonly("capture_time", &WebcamDataRGB::get_capture_time)
        .def("__repr__", &WebcamDataRGB::to_string)
    ;

    py::class_<WebcamSensor, RunnableNode, std::shared_ptr<WebcamSensor>>(m, "WebcamSensor")
        .def(
            py::init<uint16_t, uint16_t, uint16_t, int8_t, const std::string&, bool, const std::string&>(),
            "Create a Webcam sensor",
            py::arg("width"),
            py::arg("height"),
            py::arg("fps"),
            py::arg("device_index") = -1,
            py::arg("format") = "",
            py::arg("emit_rgb") = true,
            py::arg("name") = "WebcamSensor")
        .def("print_device_info", &WebcamSensor::print_device_info)
    ;

    py::class_<WebcamRawToRGBConverter, Node, std::shared_ptr<WebcamRawToRGBConverter>>(m, "WebcamRawToRGBConverter")
        .def(
            py::init<const std::string&>(),
            "Create a WebcamRawToRGBConverter",
            py::arg("name") = "WebcamRawToRGBConverter")
    ;
}
