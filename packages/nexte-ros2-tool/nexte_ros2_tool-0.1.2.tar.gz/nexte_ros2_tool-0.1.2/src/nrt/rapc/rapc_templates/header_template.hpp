#ifndef {{define_name}}
#define {{define_name}}

#include "rclcpp/rclcpp.hpp"

{{namespace_start}}
class {{class_name}} : public rclcpp::Node
{
public:
    DemoPkgNode(const rclcpp::NodeOptions & options);
    ~DemoPkgNode();
};
{{namespace_end}}

#endif // {{define_name}}