#ifndef ROBOFLEX_WEBCAM_GST__H
#define ROBOFLEX_WEBCAM_GST__H

#include <vector>
#include <string_view>
#include <iostream>
#include <optional>
#include <xtensor/containers/xtensor.hpp>
#include "gst/gst.h"
#include "gst/app/gstappsink.h"
#include "gst/video/video.h"
#include "roboflex_core/node.h"
#include "roboflex_core/serialization/flex_xtensor.h"

using std::optional, std::string, std::vector, std::exception, std::ostream;

namespace roboflex {
namespace webcam_gst {

constexpr char ModuleName[] = "webcam_gst";

/**
 * Wrapper class for GstDevice information.
 */
struct DeviceDescriptor {
    DeviceDescriptor(GstDevice* device);

    string display_name;
    string device_class;
    string gst_factory_name;
    string device_path;
    vector<string> caps_strings;

    string to_string() const;
};


/*
 * Function to get list of DeviceDescriptors
 */
vector<DeviceDescriptor> get_device_list();
string get_device_list_string();


/**
 * The datatype containing webcam frames.
 */
struct WebcamDataRaw : public core::Message {

    inline static const char MessageName[] = "WebcamDataRaw";

    WebcamDataRaw(core::Message& other): core::Message(other) {}
    WebcamDataRaw(
        const uint8_t* data,
        size_t data_size_bytes,
        uint32_t width,
        uint32_t height,
        const string& format,
        uint32_t sequence,
        double t0,
        double t1,
        double capture_time);

    double get_t0() const {
        return root_map()["t0"].AsDouble();
    }

    double get_t1() const {
        return root_map()["t1"].AsDouble();
    }

    double get_capture_time() const {
        return root_map()["t"].AsDouble();
    }

    string get_pixel_format() const {
        return root_map()["fmt"].AsString().str();
    }

    uint32_t get_width() const {
        return root_map()["w"].AsUInt32();
    }

    uint32_t get_height() const {
        return root_map()["h"].AsUInt32();
    }

    uint32_t get_sequence() const {
        return root_map()["s"].AsUInt32();
    }

    const uint8_t* get_data() const {
        auto data_portion = root_map()["data"].AsBlob();
        const uint8_t* const_data = data_portion.data();
        return const_data;
    }

    size_t get_data_size_bytes() const {
        auto data_portion = root_map()["data"].AsBlob();
        return data_portion.size();
    }

    void print_on(ostream& os) const override;
};

/**
 * The datatype containing webcam frames already converted to RGB.
 */
struct WebcamDataRGB : public core::Message {

    typedef xt::xtensor<uint8_t, 3> WebcamFrame;

    inline static const char MessageName[] = "WebcamDataRGB";

    WebcamDataRGB(core::Message& other): Message(other) {}
    WebcamDataRGB(
        const uint8_t* rgb_data,
        size_t data_size_bytes,
        uint32_t width,
        uint32_t height,
        const string& format,
        uint32_t sequence,
        double t0,
        double t1,
        double capture_time);

    double get_t0() const {
        return root_map()["t0"].AsDouble();
    }

    double get_t1() const {
        return root_map()["t1"].AsDouble();
    }

    double get_capture_time() const {
        return root_map()["t"].AsDouble();
    }

    string get_pixel_format() const {
        return root_map()["fmt"].AsString().str();
    }

    uint32_t get_sequence() const {
        return root_map()["s"].AsUInt32();
    }

    WebcamFrame get_rgb() const {
        return serialization::deserialize_flex_tensor<uint8_t, 3>(root_map()["rgb"]);
    }

    void print_on(ostream& os) const override;
};


/**
 * Can be thrown by WebcamSensor
 */
struct WebcamException : exception {
    string reason;
    explicit WebcamException(const string& reason) : std::exception(), reason(reason) {}
    const char* what() const noexcept override {
        return reason.c_str();
    }
};


/**
 * Reads from webcam via GStreamer.
 */
class WebcamSensor : public core::RunnableNode {
public:
    WebcamSensor(
        uint16_t width,
        uint16_t height,
        uint16_t fps,
        int8_t device_index = -1,
        const string& pixel_format = "",
        bool emit_rgb = true,
        const string& name = "webcam_sensor");
    ~WebcamSensor() override = default;

    void print_device_info();

protected:
    void child_thread_fn() override;

    uint16_t width;
    uint16_t height;
    uint16_t fps;
    int8_t device_index;
    string pixel_format;
    bool emit_rgb;
    optional<DeviceDescriptor> selected_device;
};

class WebcamRawToRGBConverter: public core::Node {
public:
    explicit WebcamRawToRGBConverter(
        const string& name = "webcam_raw_to_rgb"):
            core::Node(name) {}

    void receive(core::MessagePtr m) override;
};

}  // namespace webcam_gst
}  // namespace roboflex

#endif  // ROBOFLEX_WEBCAM_GST__H
