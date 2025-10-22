#include "{{pkg_name}}/{{header_file_name}}"

{{namespace_start}}
{{class_name}}::{{class_name}}(const rclcpp::NodeOptions & options)
    :Node("{{node_name}}", options)
{
    RCLCPP_INFO(this->get_logger(), "{{node_name}} node starting...");
    // Put your code here.
    RCLCPP_INFO(this->get_logger(), "{{node_name}} node started.");
}

{{class_name}}::~{{class_name}}()
{
    RCLCPP_INFO(this->get_logger(), "{{node_name}} node stopping...");
    // Put your code here.
    RCLCPP_INFO(this->get_logger(), "{{node_name}} node stopped.");
}
{{namespace_end}}

//==================================================================================================//

#include "rclcpp_components/register_node_macro.hpp"

// Register the component with class_loader.
// This acts as a sort of entry point, allowing the component to be discoverable when its library
// is being loaded into a running process.
RCLCPP_COMPONENTS_REGISTER_NODE({{namespace}}{{class_name}})