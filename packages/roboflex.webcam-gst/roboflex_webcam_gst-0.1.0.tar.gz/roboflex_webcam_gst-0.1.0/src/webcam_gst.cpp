#include <mutex>
#include <cstdlib>
#include <array>
#include <sstream>
#include <iomanip>
#include <xtensor/containers/xadapt.hpp>
#include <xtensor/io/xio.hpp>
#include "roboflex_core/util/utils.h"
#include "roboflex_core/serialization/flex_eigen.h"
#include "roboflex_webcam_gst/webcam_gst.h"

namespace roboflex {
namespace webcam_gst {

namespace {

std::once_flag gst_init_flag;

void ensure_gst_initialized()
{
    std::call_once(gst_init_flag, []() {
        gst_init(nullptr, nullptr);
    });
}

optional<std::pair<DeviceDescriptor, GstDevice*>> get_device_by_index(int8_t index)
{
    if (index < 0) {
        return std::nullopt;
    }

    ensure_gst_initialized();

    GstDeviceMonitor* monitor = gst_device_monitor_new();
    if (monitor == nullptr) {
        return std::nullopt;
    }

    gst_device_monitor_add_filter(monitor, "Video/Source", nullptr);
    if (!gst_device_monitor_start(monitor)) {
        g_object_unref(monitor);
        return std::nullopt;
    }

    optional<std::pair<DeviceDescriptor, GstDevice*>> result;
    GList* devices = gst_device_monitor_get_devices(monitor);
    int i = 0;
    for (GList* it = devices; it != nullptr; it = it->next, ++i) {
        GstDevice* device = GST_DEVICE(it->data);
        if (device == nullptr) {
            continue;
        }
        if (i == index) {
            gst_object_ref(device);
            result = std::make_pair(DeviceDescriptor(device), device);
            break;
        }
    }

    g_list_free_full(devices, g_object_unref);
    gst_device_monitor_stop(monitor);
    g_object_unref(monitor);
    return result;
}

void append_bus_errors(GstBus* bus)
{
    if (bus == nullptr) {
        return;
    }

    while (true) {
        GstMessage* msg = gst_bus_pop_filtered(bus, GST_MESSAGE_ERROR);
        if (msg == nullptr) {
            break;
        }
        GError* err = nullptr;
        gchar* dbg = nullptr;
        gst_message_parse_error(msg, &err, &dbg);
        if (err != nullptr) {
            std::cerr << "GStreamer error: " << err->message << std::endl;
            g_error_free(err);
        }
        if (dbg != nullptr) {
            std::cerr << "Debug details: " << dbg << std::endl;
            g_free(dbg);
        }
        gst_message_unref(msg);
    }
}

}  // namespace


// --- Device Descriptor ---

DeviceDescriptor::DeviceDescriptor(GstDevice* device)
{
    if (device == nullptr) {
        display_name = "UNKNOWN";
        device_class = "UNKNOWN";
        gst_factory_name = "UNKNOWN";
        device_path = "";
        return;
    }

    const gchar* display = gst_device_get_display_name(device);
    display_name = display != nullptr ? display : "UNKNOWN";

    const gchar* klass = gst_device_get_device_class(device);
    device_class = klass != nullptr ? klass : "UNKNOWN";
    const gchar* factory_name = gst_object_get_name(GST_OBJECT(device));
    gst_factory_name = factory_name != nullptr ? factory_name : "UNKNOWN";

    GstStructure* props = gst_device_get_properties(device);
    if (props != nullptr) {
        const gchar* path = gst_structure_get_string(props, "device.path");
        if (path != nullptr) {
            device_path = path;
        }
        gst_structure_free(props);
    }

    GstCaps* caps = gst_device_get_caps(device);
    if (caps != nullptr) {
        guint caps_size = gst_caps_get_size(caps);
        for (guint i = 0; i < caps_size; ++i) {
            const GstStructure* structure = gst_caps_get_structure(caps, i);
            gchar* caps_str = gst_structure_to_string(structure);
            if (caps_str != nullptr) {
                caps_strings.emplace_back(caps_str);
                g_free(caps_str);
            }
        }

        gst_caps_unref(caps);
    }
}

string DeviceDescriptor::to_string() const
{
    std::stringstream sst;
    sst << "<DeviceDescriptor"
        << " display_name: " << (!this->display_name.empty() ? this->display_name : "UNKNOWN")
        << " factory: " << (!this->gst_factory_name.empty() ? this->gst_factory_name : "UNKNOWN")
        << " device_class: " << (!this->device_class.empty() ? this->device_class : "UNKNOWN")
        << " device_path: " << (!this->device_path.empty() ? this->device_path : "UNKNOWN")
        << ">";
    return sst.str();
}


vector<DeviceDescriptor> get_device_list()
{
    ensure_gst_initialized();

    vector<DeviceDescriptor> devices;

    GstDeviceMonitor* monitor = gst_device_monitor_new();
    if (monitor == nullptr) {
        return devices;
    }

    gst_device_monitor_add_filter(monitor, "Video/Source", nullptr);
    if (!gst_device_monitor_start(monitor)) {
        g_object_unref(monitor);
        return devices;
    }

    GList* list = gst_device_monitor_get_devices(monitor);
    for (GList* it = list; it != nullptr; it = it->next) {
        GstDevice* device = GST_DEVICE(it->data);
        if (device != nullptr) {
            devices.emplace_back(device);
        }
    }

    g_list_free_full(list, g_object_unref);
    gst_device_monitor_stop(monitor);
    g_object_unref(monitor);
    return devices;
}

string get_device_list_string()
{
    std::stringstream sst;
    auto devices = get_device_list();
    for (size_t i = 0; i < devices.size(); ++i) {
        sst << i << ": " << devices[i].to_string();
        if (!devices[i].caps_strings.empty()) {
            sst << "\n    caps:";
            for (const auto& c : devices[i].caps_strings) {
                sst << "\n      " << c;
            }
        }
        sst << std::endl;
    }
    return sst.str();
}


// --- WebcamDataRaw ---

WebcamDataRaw::WebcamDataRaw(
    const uint8_t* data,
    size_t data_size_bytes,
    uint32_t width,
    uint32_t height,
    const string& format,
    uint32_t sequence,
    double t0,
    double t1,
    double capture_time):
        Message(ModuleName, MessageName)
{
    flexbuffers::Builder fbb = get_builder();
    WriteMapRoot(fbb, [&]() {
        fbb.Double("t0", t0);
        fbb.Double("t1", t1);
        fbb.Double("t", capture_time);
        fbb.String("fmt", format);
        fbb.UInt("s", sequence);
        fbb.UInt("w", width);
        fbb.UInt("h", height);
        fbb.Key("data");
        fbb.Blob(data, data_size_bytes);
    });
}

void WebcamDataRaw::print_on(ostream& os) const
{
    os << "<WebcamDataRaw"
       << "  t0: " << std::fixed << std::setprecision(3) << get_t0()
       << "  t1: " << get_t1()
       << "  sequence: " << get_sequence()
       << "  width: " << get_width()
       << "  height: " << get_height()
       << "  pixel_format: " << get_pixel_format()
       << "  bytes: " << get_data_size_bytes()
       << "  data: " << static_cast<const void*>(get_data())
       << "  capture_time: " << get_capture_time() << " ";
    Message::print_on(os);
    os << ">";
}


// --- WebcamDataRGB ---

WebcamDataRGB::WebcamDataRGB(
    const uint8_t* rgb_data,
    size_t data_size_bytes,
    uint32_t width,
    uint32_t height,
    const string& format,
    uint32_t sequence,
    double t0,
    double t1,
    double capture_time):
        Message(ModuleName, MessageName)
{
    auto rgb_tensor = xt::adapt(
        rgb_data,
        data_size_bytes,
        xt::no_ownership(),
        std::array<size_t, 3>{height, width, 3});

    flexbuffers::Builder fbb = get_builder();
    WriteMapRoot(fbb, [&]() {
        fbb.Double("t0", t0);
        fbb.Double("t1", t1);
        fbb.Double("t", capture_time);
        fbb.String("fmt", format);
        fbb.UInt("s", sequence);
        serialization::serialize_flex_tensor<uint8_t, 3>(fbb, rgb_tensor, "rgb");
    });
}

void WebcamDataRGB::print_on(ostream& os) const
{
    os << "<WebcamDataRGB"
       << " t0: " << std::fixed << std::setprecision(3) << get_t0()
       << " t1: " << get_t1()
       << " rgb shape: " << xt::adapt(get_rgb().shape())
       << " pixel_format: " << get_pixel_format()
       << " sequence: " << get_sequence()
       << " capture_time: " << get_capture_time() << " ";
    Message::print_on(os);
    os << ">";
}


// --- WebcamSensor ---

WebcamSensor::WebcamSensor(
    uint16_t width,
    uint16_t height,
    uint16_t fps,
    int8_t device_index,
    const string& pixel_format,
    bool emit_rgb,
    const string& name):
        core::RunnableNode(name),
        width(width),
        height(height),
        fps(fps),
        device_index(device_index),
        pixel_format(pixel_format),
        emit_rgb(emit_rgb)
{
    if (device_index >= 0) {
        auto devices = get_device_list();
        if (static_cast<size_t>(device_index) >= devices.size()) {
            std::stringstream ss;
            ss << "device_index " << static_cast<int>(device_index)
               << " out of range for " << devices.size() << " devices";
            throw WebcamException(ss.str());
        }
        selected_device = devices[device_index];
    }
}

void WebcamSensor::print_device_info()
{
    if (selected_device.has_value()) {
        std::cerr << "Selected device: " << selected_device->to_string() << std::endl;
        if (!selected_device->caps_strings.empty()) {
            std::cerr << "Caps:" << std::endl;
            for (const auto& caps : selected_device->caps_strings) {
                std::cerr << "  " << caps << std::endl;
            }
        }
    } else {
        std::cerr << "No explicit device selected; using autovideosrc." << std::endl;
    }
    if (!pixel_format.empty()) {
        std::cerr << "Requested pixel format: " << pixel_format << std::endl;
    }
}

void WebcamSensor::child_thread_fn()
{
    ensure_gst_initialized();

    GstElement* pipeline = gst_pipeline_new("roboflex_webcam_pipeline");
    if (pipeline == nullptr) {
        throw WebcamException("cannot create GStreamer pipeline");
    }

    GstDevice* gst_device = nullptr;
    GstElement* source = nullptr;

    if (device_index >= 0) {
        auto device_pair = get_device_by_index(device_index);
        if (!device_pair.has_value()) {
            gst_object_unref(pipeline);
            std::stringstream ss;
            ss << "cannot retrieve device at index " << static_cast<int>(device_index);
            throw WebcamException(ss.str());
        }
        if (!selected_device.has_value()) {
            selected_device = device_pair->first;
        }
        gst_device = device_pair->second;
        source = gst_device_create_element(gst_device, "source");
        if (source == nullptr) {
            gst_object_unref(gst_device);
            gst_object_unref(pipeline);
            throw WebcamException("cannot create source element from GstDevice");
        }
    } else {
        source = gst_element_factory_make("autovideosrc", "source");
        if (source == nullptr) {
            gst_object_unref(pipeline);
            throw WebcamException("cannot create autovideosrc");
        }
    }

    GstElement* capsfilter = gst_element_factory_make("capsfilter", "caps");
    GstElement* convert = emit_rgb ? gst_element_factory_make("videoconvert", "convert") : nullptr;
    GstElement* appsink = gst_element_factory_make("appsink", "sink");

    if (capsfilter == nullptr || appsink == nullptr || (emit_rgb && convert == nullptr)) {
        if (gst_device != nullptr) {
            gst_object_unref(gst_device);
        }
        if (source != nullptr) {
            gst_object_unref(source);
        }
        if (capsfilter != nullptr) {
            gst_object_unref(capsfilter);
        }
        if (convert != nullptr) {
            gst_object_unref(convert);
        }
        gst_object_unref(pipeline);
        throw WebcamException("failed to create required GStreamer elements");
    }

    GstCaps* caps = gst_caps_new_simple(
        "video/x-raw",
        "width", G_TYPE_INT, static_cast<int>(width),
        "height", G_TYPE_INT, static_cast<int>(height),
        "framerate", GST_TYPE_FRACTION, static_cast<int>(fps), 1,
        nullptr);

    if (!emit_rgb && !pixel_format.empty()) {
        gst_caps_set_simple(caps, "format", G_TYPE_STRING, pixel_format.c_str(), nullptr);
    }

    g_object_set(capsfilter, "caps", caps, nullptr);
    gst_caps_unref(caps);

    g_object_set(appsink,
        "emit-signals", FALSE,
        "sync", FALSE,
        "max-buffers", 1,
        "drop", TRUE,
        nullptr);

    GstCaps* sink_caps = nullptr;
    if (emit_rgb) {
        sink_caps = gst_caps_new_simple(
            "video/x-raw",
            "format", G_TYPE_STRING, "RGB",
            "width", G_TYPE_INT, static_cast<int>(width),
            "height", G_TYPE_INT, static_cast<int>(height),
            "framerate", GST_TYPE_FRACTION, static_cast<int>(fps), 1,
            nullptr);
    } else {
        sink_caps = gst_caps_new_simple(
            "video/x-raw",
            "width", G_TYPE_INT, static_cast<int>(width),
            "height", G_TYPE_INT, static_cast<int>(height),
            nullptr);
        if (!pixel_format.empty()) {
            gst_caps_set_simple(sink_caps, "format", G_TYPE_STRING, pixel_format.c_str(), nullptr);
        }
    }

    gst_app_sink_set_caps(GST_APP_SINK(appsink), sink_caps);
    gst_caps_unref(sink_caps);

    if (emit_rgb) {
        gst_bin_add_many(GST_BIN(pipeline), source, capsfilter, convert, appsink, nullptr);
        if (!gst_element_link_many(source, capsfilter, convert, appsink, nullptr)) {
            gst_object_unref(pipeline);
            if (gst_device != nullptr) {
                gst_object_unref(gst_device);
            }
            throw WebcamException("cannot link GStreamer elements (RGB path)");
        }
    } else {
        gst_bin_add_many(GST_BIN(pipeline), source, capsfilter, appsink, nullptr);
        if (!gst_element_link_many(source, capsfilter, appsink, nullptr)) {
            gst_object_unref(pipeline);
            if (gst_device != nullptr) {
                gst_object_unref(gst_device);
            }
            throw WebcamException("cannot link GStreamer elements (raw path)");
        }
    }

    GstBus* bus = gst_element_get_bus(pipeline);

    GstStateChangeReturn state_ret = gst_element_set_state(pipeline, GST_STATE_PLAYING);
    if (state_ret == GST_STATE_CHANGE_FAILURE) {
        append_bus_errors(bus);
        gst_element_set_state(pipeline, GST_STATE_NULL);
        if (bus != nullptr) {
            gst_object_unref(bus);
        }
        if (gst_device != nullptr) {
            gst_object_unref(gst_device);
        }
        gst_object_unref(pipeline);
        throw WebcamException("failed to set pipeline to PLAYING");
    }

    uint32_t sequence = 0;

    while (!this->stop_requested()) {
        double t0 = core::get_current_time();
        GstSample* sample = gst_app_sink_try_pull_sample(
            GST_APP_SINK(appsink),
            static_cast<GstClockTime>(GST_SECOND / 2));
        double t1 = core::get_current_time();

        if (sample == nullptr) {
            GstMessage* msg = gst_bus_pop_filtered(
                bus,
                static_cast<GstMessageType>(GST_MESSAGE_ERROR | GST_MESSAGE_EOS));
            if (msg != nullptr) {
                if (GST_MESSAGE_TYPE(msg) == GST_MESSAGE_ERROR) {
                    GError* err = nullptr;
                    gchar* dbg = nullptr;
                    gst_message_parse_error(msg, &err, &dbg);
                    string reason = "unknown";
                    if (err != nullptr) {
                        reason = err->message;
                        g_error_free(err);
                    }
                    if (dbg != nullptr) {
                        std::cerr << "Debug details: " << dbg << std::endl;
                        g_free(dbg);
                    }
                    gst_message_unref(msg);
                    throw WebcamException(reason);
                } else {
                    gst_message_unref(msg);
                    break;
                }
            }
            continue;
        }

        GstBuffer* buffer = gst_sample_get_buffer(sample);
        if (buffer == nullptr) {
            gst_sample_unref(sample);
            continue;
        }

        GstMapInfo map;
        if (!gst_buffer_map(buffer, &map, GST_MAP_READ)) {
            gst_sample_unref(sample);
            continue;
        }

        GstCaps* sample_caps = gst_sample_get_caps(sample);
        GstStructure* caps_struct = gst_caps_get_structure(sample_caps, 0);
        gint sample_width = 0;
        gint sample_height = 0;
        gst_structure_get_int(caps_struct, "width", &sample_width);
        gst_structure_get_int(caps_struct, "height", &sample_height);
        const gchar* format_str = gst_structure_get_string(caps_struct, "format");
        string frame_format = format_str != nullptr ? string(format_str) : string("");
        if (emit_rgb) {
            frame_format = "RGB";
        } else if (frame_format.empty() && !pixel_format.empty()) {
            frame_format = pixel_format;
        }

        GstClockTime pts = GST_BUFFER_PTS(buffer);
        double capture_time = GST_CLOCK_TIME_IS_VALID(pts)
            ? static_cast<double>(pts) / static_cast<double>(GST_SECOND)
            : t1;

        if (emit_rgb) {
            auto message = std::make_shared<WebcamDataRGB>(
                map.data,
                map.size,
                static_cast<uint32_t>(sample_width),
                static_cast<uint32_t>(sample_height),
                frame_format,
                sequence++,
                t0,
                t1,
                capture_time);
            this->signal(message);
        } else {
            auto message = std::make_shared<WebcamDataRaw>(
                map.data,
                map.size,
                static_cast<uint32_t>(sample_width),
                static_cast<uint32_t>(sample_height),
                frame_format,
                sequence++,
                t0,
                t1,
                capture_time);
            this->signal(message);
        }

        gst_buffer_unmap(buffer, &map);
        gst_sample_unref(sample);
    }

    gst_element_set_state(pipeline, GST_STATE_NULL);
    append_bus_errors(bus);

    if (bus != nullptr) {
        gst_object_unref(bus);
    }
    if (gst_device != nullptr) {
        gst_object_unref(gst_device);
    }
    gst_object_unref(pipeline);
}


// --- WebcamRawToRGBConverter ---

void WebcamRawToRGBConverter::receive(core::MessagePtr m)
{
    WebcamDataRaw raw(*m);

    if (raw.get_pixel_format() != "RGB") {
        throw WebcamException("WebcamRawToRGBConverter currently supports only RGB-formatted raw frames");
    }

    auto message = std::make_shared<WebcamDataRGB>(
        raw.get_data(),
        raw.get_data_size_bytes(),
        raw.get_width(),
        raw.get_height(),
        raw.get_pixel_format(),
        raw.get_sequence(),
        raw.get_t0(),
        raw.get_t1(),
        raw.get_capture_time());

    this->signal(message);
}

}  // namespace webcam_gst
}  // namespace roboflex
