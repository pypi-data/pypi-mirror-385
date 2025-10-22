#include <iostream>
#include "roboflex_core/core.h"
#include "roboflex_core/core_nodes/core_nodes.h"
#include "roboflex_webcam_gst/webcam_gst.h"

using namespace roboflex;

int main()
{
    auto webcam = webcam_gst::WebcamSensor(640, 480, 30);
    webcam.print_device_info();
    auto message_printer = nodes::MessagePrinter();
    webcam > message_printer;

    webcam.start();
    core::sleep_ms(5000);
    webcam.stop();

    std::cout << "DONE" << std::endl;
    return 0;
}
