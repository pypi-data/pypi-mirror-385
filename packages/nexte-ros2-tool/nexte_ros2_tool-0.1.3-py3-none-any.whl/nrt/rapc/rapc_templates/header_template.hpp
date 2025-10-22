#ifndef {{define_name}}
#define {{define_name}}

#include "rclcpp/rclcpp.hpp"

{{namespace_start}}
class {{class_name}} : public rclcpp::Node
{
public:
    {{class_name}}(const rclcpp::NodeOptions & options);
    ~{{class_name}}();
};
{{namespace_end}}

#endif // {{define_name}}