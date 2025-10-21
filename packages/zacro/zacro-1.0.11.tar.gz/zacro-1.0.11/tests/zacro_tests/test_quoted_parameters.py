"""
Test quoted parameter handling in xacro macros.

This module tests the fix for handling quoted strings in macro parameters,
specifically for cases like prefix:='' and xyz:='0 0 0' which should be
properly processed without leaving stray quotes in the output.
"""

import unittest

from zacro import xacro_from_string


class TestQuotedParameters(unittest.TestCase):
    """Test handling of quoted parameters in xacro macros."""

    def test_empty_string_parameter(self):
        """Test that empty string parameters (prefix:='') are handled correctly."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_macro" params="prefix:=''">
    <link name="${prefix}base_link"/>
  </xacro:macro>
  <xacro:test_macro/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False)

        # The result should contain 'base_link', not "''base_link"
        self.assertIn('<link name="base_link"', result)
        self.assertNotIn("''base_link", result)
        self.assertNotIn("'base_link", result)

    def test_quoted_vector_parameters(self):
        """Test that quoted vector parameters (xyz:='0 0 0') are handled correctly."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_macro" params="xyz:='0 0 0' rpy:='0 0 0'">
    <link name="base_link"/>
    <origin xyz="${xyz}" rpy="${rpy}"/>
  </xacro:macro>
  <xacro:test_macro/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False, validate_urdf=False)

        # The result should contain proper values without quotes
        self.assertIn('xyz="0 0 0"', result)
        self.assertIn('rpy="0 0 0"', result)
        self.assertNotIn("'0 0 0'", result)
        self.assertNotIn("'0", result)

    def test_complex_macro_with_quoted_params(self):
        """Test a complex macro similar to the screw_pump_module case."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_module" params="prefix:='' parent_link:=world xyz:='0 0 0' rpy:='0 0 0'">
    <joint name="${parent_link}_to_${prefix}base_link_joint" type="fixed">
      <parent link="${parent_link}"/>
      <child link="${prefix}base_link"/>
      <origin xyz="${xyz}" rpy="${rpy}"/>
    </joint>
    <link name="${prefix}base_link"/>
    <link name="${prefix}dummy_link"/>
    <joint name="${prefix}dummy_joint" type="fixed">
      <parent link="${prefix}base_link"/>
      <child link="${prefix}dummy_link"/>
    </joint>
  </xacro:macro>

  <link name="world"/>
  <xacro:test_module/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False)

        # Check that the prefix parameter (empty string) is handled correctly
        self.assertIn('<link name="base_link"', result)
        self.assertIn('<link name="dummy_link"', result)
        self.assertIn('name="world_to_base_link_joint"', result)
        self.assertIn('name="dummy_joint"', result)
        self.assertIn('<parent link="base_link"', result)
        self.assertIn('<child link="dummy_link"', result)

        # Check that xyz and rpy parameters are handled correctly
        self.assertIn('xyz="0 0 0"', result)
        self.assertIn('rpy="0 0 0"', result)

        # Ensure no stray quotes remain
        self.assertNotIn("''", result)
        self.assertNotIn("'0", result)
        self.assertNotIn("'base_link", result)
        self.assertNotIn("'dummy_link", result)

    def test_single_quoted_strings(self):
        """Test that single-quoted strings are handled correctly."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_macro" params="name:='test_name' value:='42'">
    <link name="${name}">
      <visual>
        <geometry>
          <box size="1 1 ${value}"/>
        </geometry>
      </visual>
    </link>
  </xacro:macro>
  <xacro:test_macro/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False)

        # Check that quoted parameters are processed correctly
        self.assertIn('<link name="test_name"', result)
        self.assertIn('size="1 1 42"', result)

        # Ensure no stray quotes remain
        self.assertNotIn("'test_name", result)
        self.assertNotIn("'42", result)

    def test_double_quoted_strings(self):
        """Test that double-quoted strings are handled correctly."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_macro" params='name:="test_name" value:="42"'>
    <link name="${name}">
      <visual>
        <geometry>
          <box size="1 1 ${value}"/>
        </geometry>
      </visual>
    </link>
  </xacro:macro>
  <xacro:test_macro/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False)

        # Check that quoted parameters are processed correctly
        self.assertIn('<link name="test_name"', result)
        self.assertIn('size="1 1 42"', result)

        # Ensure no stray quotes remain (parameters should be unquoted in final output)
        # Note: XML attributes will always have quotes, so we check for double quotes or malformed quotes
        self.assertNotIn('""test_name', result)  # Check for malformed double quotes
        self.assertNotIn('""42', result)  # Check for malformed double quotes

    def test_mixed_quoted_and_unquoted_params(self):
        """Test mixing quoted and unquoted parameters."""
        xacro_content = '''<?xml version="1.0"?>
<robot name="test_robot" xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="test_macro" params="prefix:='' suffix:=_link count:=1 xyz:='1 2 3'">
    <link name="${prefix}test${suffix}${count}"/>
    <origin xyz="${xyz}"/>
  </xacro:macro>
  <xacro:test_macro/>
</robot>'''

        result = xacro_from_string(xacro_content, format_output=False)

        # Check that all parameters are processed correctly
        self.assertIn('<link name="test_link1"', result)
        self.assertIn('xyz="1 2 3"', result)

        # Ensure no stray quotes remain
        self.assertNotIn("''", result)
        self.assertNotIn("'1 2 3'", result)


if __name__ == '__main__':
    unittest.main()
