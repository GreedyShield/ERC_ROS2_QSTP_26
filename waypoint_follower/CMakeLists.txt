cmake_minimum_required(VERSION 3.8)
project(waypoint_follower)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclpy REQUIRED)

# Generate Mission action
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Mission.action"
)

# Install Mission Server
install(
  PROGRAMS
    scripts/mission_server.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME mission_server
)

# Install Mission Client
install(
  PROGRAMS
    scripts/mission_client.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME mission_client
)

# Install mission YAML files
install(
  DIRECTORY missions
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)

  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)

  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
