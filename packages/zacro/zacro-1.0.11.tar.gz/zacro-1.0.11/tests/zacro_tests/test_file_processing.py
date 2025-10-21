#!/usr/bin/env python

import os
import tempfile
import unittest

import zacro


class TestFileProcessing(unittest.TestCase):
    """Test file processing functionality"""

    def setUp(self):
        """Set up temporary files for testing"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_xacro_to_file(self):
        """Test processing xacro file to output file"""
        # Create test input file
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro" name="test_robot">
  <xacro:property name="size" value="1.0"/>
  <link name="base">
    <visual>
      <geometry>
        <box size="${size} ${size} ${size}"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        input_file = os.path.join(self.temp_dir, "test.xacro")
        output_file = os.path.join(self.temp_dir, "test.urdf")

        with open(input_file, 'w') as f:
            f.write(input_content)

        # Process file
        zacro.xacro_to_file(input_file, output_file, format_output=True)

        # Check output file exists and has correct content
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            result = f.read()

        self.assertIn('<link name="base">', result)
        self.assertIn('size="1.0 1.0 1.0"', result)
        self.assertNotIn('${size}', result)

    def test_xacro_to_string_from_file(self):
        """Test processing xacro file to string"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="wheel" params="name radius">
    <link name="${name}">
      <visual>
        <geometry>
          <cylinder radius="${radius}" length="0.05"/>
        </geometry>
      </visual>
    </link>
  </xacro:macro>

  <xacro:wheel name="front_wheel" radius="0.1"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "wheel.xacro")

        with open(input_file, 'w') as f:
            f.write(input_content)

        result = zacro.xacro_to_string(input_file, format_output=True)

        self.assertIn('<link name="front_wheel">', result)
        self.assertIn('radius="0.1"', result)
        self.assertNotIn('<xacro:wheel', result)

    def test_class_api_file_processing(self):
        """Test file processing with class-based API"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="simple_link"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "simple.xacro")

        with open(input_file, 'w') as f:
            f.write(input_content)

        processor = zacro.XacroProcessor()
        processor.set_format_output(True)

        result = processor.process_file(input_file)

        self.assertIn('<link name="simple_link"', result)
        self.assertTrue(result.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

    def test_file_with_all_options(self):
        """Test file processing with all options enabled"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="module" params="prefix">
    <joint name="${prefix}connection" type="fixed">
      <parent link="base"/>
      <child link="${prefix}link"/>
    </joint>
    <link name="${prefix}link"/>
  </xacro:macro>

  <link name="base"/>
  <xacro:module prefix="test_"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "full_test.xacro")
        output_file = os.path.join(self.temp_dir, "full_test.urdf")

        with open(input_file, 'w') as f:
            f.write(input_content)

        # Test with all options (format is default,
        # disable validation since remove_root_link creates disconnected links)
        zacro.xacro_to_file(
            input_file,
            output_file,
            remove_root_link="base",
            validate_urdf=False
        )

        with open(output_file, 'r') as f:
            result = f.read()

        # Should be formatted
        self.assertTrue(result.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertGreater(result.count('\n'), 2)  # Should have at least some line breaks

        # Should have removed the base link and connecting joint
        self.assertEqual(result.count('<joint'), 0)
        self.assertNotIn('<link name="base"', result)  # base link should be removed

        # Should still have the test link
        self.assertIn('<link name="test_link"', result)

    def test_pr2_robot(self):
        """Test processing complex PR2 robot file"""
        # Get the path to PR2 test file
        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pr2_file = os.path.join(test_dir, "robots", "pr2", "pr2.urdf.xacro")

        # Check if PR2 file exists
        if not os.path.exists(pr2_file):
            self.skipTest(f"PR2 test file not found at {pr2_file}")

        # Process PR2 file without validation (PR2 has many links/joints)
        result = zacro.xacro_to_string(pr2_file, validate_urdf=False)

        # Basic checks for PR2 robot
        self.assertIn('<robot name="pr2">', result)

        # Check for key PR2 components
        self.assertIn('base_link', result)
        self.assertIn('torso_lift_link', result)
        self.assertIn('head_pan_link', result)

        # Check for gripper components
        self.assertIn('r_gripper_palm_link', result)
        self.assertIn('l_gripper_palm_link', result)

        # Check that complex expressions were evaluated correctly
        # The gear_ratio="${(729.0/25.0)*(22.0/16.0)}" should evaluate to 40.095
        # This appears in transmission elements
        self.assertIn('40.095', result)

        # Check that reflect parameter was properly substituted
        self.assertIn('r_shoulder_pan_joint', result)
        self.assertIn('l_shoulder_pan_joint', result)

        # Should not have any xacro: elements (except in comments) in the output
        # Check that we don't have xacro elements by looking for actual XML tags
        import re
        xacro_elements = re.findall(r'<[^!].*?xacro:', result)
        self.assertEqual(len(xacro_elements), 0, f"Found unexpanded xacro elements: {xacro_elements}")

        # Should not have any ${} expressions in the output (except in comments)
        # Remove comments before checking for expressions
        result_no_comments = re.sub(r'<!--.*?-->', '', result, flags=re.DOTALL)
        dollar_expressions = re.findall(r'\$\{[^}]+\}', result_no_comments)
        self.assertEqual(len(dollar_expressions), 0, f"Found unexpanded expressions: {dollar_expressions}")


if __name__ == '__main__':
    unittest.main()
