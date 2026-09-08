cmake_minimum_required(VERSION 3.5)
project(g1_development_environment_meta_workspace)

# Tell CLion where your active C++ packages are located
# This allows CLion to index them under the same project tree
add_subdirectory(workspace/src/g1_control_nodes)

# If you have other packages, you can add them here as you create them:
# add_subdirectory(workspace/src/another_cpp_node)