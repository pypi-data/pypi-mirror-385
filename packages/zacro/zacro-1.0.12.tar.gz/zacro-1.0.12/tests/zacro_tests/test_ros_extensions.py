#!/usr/bin/env python

import os
import tempfile
import unittest

import zacro


class TestROSExtensions(unittest.TestCase):
    """Test ROS-specific xacro extensions"""

    def test_env_function(self):
        """Test $(env VARIABLE) function"""
        # Set a test environment variable
        os.environ['TEST_ENV_VAR'] = 'test_value_123'

        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="env_val" value="$(env TEST_ENV_VAR)"/>
  <link name="${env_val}_link">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('<link name="test_value_123_link">', result)

        # Clean up
        del os.environ['TEST_ENV_VAR']

    def test_env_function_missing_variable(self):
        """Test $(env VARIABLE) with non-existent variable"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="env_val" value="$(env NONEXISTENT_VAR_XYZ)"/>
</robot>'''

        with self.assertRaises(Exception) as context:
            zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('Environment variable not found', str(context.exception))

    def test_optenv_function(self):
        """Test $(optenv VARIABLE default) function"""
        # Test with existing environment variable
        os.environ['TEST_OPTENV_VAR'] = 'actual_value'

        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="opt1" value="$(optenv TEST_OPTENV_VAR default_value)"/>
  <xacro:property name="opt2" value="$(optenv MISSING_VAR default_value)"/>
  <xacro:property name="opt3" value="$(optenv MISSING_VAR_2)"/>
  <link name="${opt1}_${opt2}_${opt3}">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('<link name="actual_value_default_value_">', result)

        # Clean up
        del os.environ['TEST_OPTENV_VAR']

    def test_arg_element(self):
        """Test xacro:arg element with $(arg name) substitution"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:arg name="robot_name" default="my_robot"/>
  <xacro:arg name="robot_color" default="red"/>
  <xacro:property name="full_name" value="$(arg robot_name)_$(arg robot_color)"/>
  <link name="${full_name}">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('<link name="my_robot_red">', result)
        self.assertNotIn('xacro:arg', result)

    def test_arg_with_command_line_override(self):
        """Test xacro:arg with command line parameter override"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:arg name="robot_name" default="default_robot"/>
  <xacro:property name="name" value="$(arg robot_name)"/>
  <link name="${name}">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        # Test with override
        result = zacro.xacro_from_string(
            xml_str,
            mappings={'robot_name': 'custom_robot'},
            validate_urdf=False
        )
        self.assertIn('<link name="custom_robot">', result)

    def test_eval_function(self):
        """Test $(eval expression) function"""
        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="radius" value="0.5"/>
  <xacro:property name="pi" value="3.14159"/>
  <xacro:property name="circumference" value="$(eval 2 * ${pi} * ${radius})"/>
  <xacro:property name="area" value="$(eval ${pi} * ${radius} * ${radius})"/>
  <link name="test_link">
    <visual>
      <geometry>
        <cylinder radius="${radius}" length="${circumference}"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        # Check that eval was processed
        self.assertIn('length="3.14159"', result)  # 2 * pi * 0.5 = pi
        self.assertNotIn('$(eval', result)

    def test_find_function_with_ros_package_path(self):
        """Test $(find package) function with ROS_PACKAGE_PATH"""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = os.path.join(tmpdir, 'test_package')
            os.makedirs(package_dir)

            # Set ROS_PACKAGE_PATH
            old_path = os.environ.get('ROS_PACKAGE_PATH', '')
            os.environ['ROS_PACKAGE_PATH'] = tmpdir

            xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="pkg_path" value="$(find test_package)"/>
  <link name="${pkg_path}_link">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

            result = zacro.xacro_from_string(xml_str, validate_urdf=False)
            self.assertIn(f'<link name="{package_dir}_link">', result)

            # Restore ROS_PACKAGE_PATH
            if old_path:
                os.environ['ROS_PACKAGE_PATH'] = old_path
            else:
                del os.environ['ROS_PACKAGE_PATH']

    def test_combined_features(self):
        """Test combination of multiple ROS extensions"""
        os.environ['TEST_PREFIX'] = 'robot'

        xml_str = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:arg name="suffix" default="arm"/>
  <xacro:property name="prefix" value="$(env TEST_PREFIX)"/>
  <xacro:property name="suffix_val" value="$(arg suffix)"/>
  <xacro:property name="optional" value="$(optenv MISSING_VAR default)"/>

  <link name="${prefix}_${suffix_val}_${optional}">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        result = zacro.xacro_from_string(xml_str, validate_urdf=False)
        self.assertIn('<link name="robot_arm_default">', result)

        # Clean up
        del os.environ['TEST_PREFIX']


if __name__ == '__main__':
    unittest.main()
