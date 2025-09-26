#!/usr/bin/env python3
"""
Test suite for OpenVPN Prometheus Exporter v2.0
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from pathlib import Path

# Import the exporter modules
import sys
sys.path.insert(0, '.')

from openvpn_exporter import SecurityValidator, OpenVPNStatusParser, OpenVPNExporter

class TestSecurityValidator(unittest.TestCase):
    """Test security validation functionality"""
    
    def setUp(self):
        self.validator = SecurityValidator()
    
    def test_validate_path_allowed(self):
        """Test path validation for allowed paths"""
        # Test with examples directory
        self.assertTrue(self.validator.validate_path("./examples/client.status"))
        self.assertTrue(self.validator.validate_path("examples/client.status"))
    
    def test_validate_path_blocked(self):
        """Test path validation blocks dangerous paths"""
        # Test path traversal attempts
        self.assertFalse(self.validator.validate_path("../../../etc/passwd"))
        self.assertFalse(self.validator.validate_path("/etc/passwd"))
        self.assertFalse(self.validator.validate_path("/root/.ssh/id_rsa"))
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test normal filenames
        self.assertEqual(self.validator.sanitize_filename("client.status"), "client.status")
        self.assertEqual(self.validator.sanitize_filename("server-1.status"), "server-1.status")
        
        # Test dangerous filenames
        self.assertEqual(self.validator.sanitize_filename("../../../etc/passwd"), "etcpasswd")
        self.assertEqual(self.validator.sanitize_filename("file<script>"), "filescript")
        self.assertEqual(self.validator.sanitize_filename(""), "unknown")
        self.assertEqual(self.validator.sanitize_filename(None), "unknown")
    
    def test_validate_ip_address(self):
        """Test IP address validation"""
        # Valid IPs
        self.assertTrue(self.validator.validate_ip_address("192.168.1.1"))
        self.assertTrue(self.validator.validate_ip_address("10.0.0.1"))
        self.assertTrue(self.validator.validate_ip_address("unknown"))
        
        # Invalid IPs
        self.assertFalse(self.validator.validate_ip_address("999.999.999.999"))
        self.assertFalse(self.validator.validate_ip_address("not-an-ip"))
    
    def test_validate_file_content(self):
        """Test file content validation"""
        # Valid content
        valid_content = "OpenVPN STATISTICS\nUpdated,Mon Jan 1 12:00:00 2024\nEND"
        self.assertTrue(self.validator.validate_file_content(valid_content))
        
        # Suspicious content
        suspicious_content = "<script>alert('xss')</script>"
        self.assertFalse(self.validator.validate_file_content(suspicious_content))
        
        # Empty content
        self.assertFalse(self.validator.validate_file_content(""))
        self.assertFalse(self.validator.validate_file_content(None))

class TestOpenVPNStatusParser(unittest.TestCase):
    """Test OpenVPN status file parsing"""
    
    def setUp(self):
        self.status_paths = ["examples/client.status"]
        self.parser = OpenVPNStatusParser(self.status_paths, ignore_individuals=False)
    
    def test_parse_client_status(self):
        """Test parsing client status file"""
        client_content = """OpenVPN STATISTICS
Updated,Tue Mar 21 10:39:09 2017
TUN/TAP read bytes,153789941
TUN/TAP write bytes,308764078
TCP/UDP read bytes,292806201
TCP/UDP write bytes,197558969
Auth read bytes,308854782
pre-compress bytes,45388190
post-compress bytes,45446864
pre-decompress bytes,162596168
post-decompress bytes,216965355
END"""
        
        result = self.parser._parse_content(client_content, "test_client.status")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "parsed")
    
    def test_parse_server_status_v2(self):
        """Test parsing server status file v2"""
        server_content = """TITLE,OpenVPN 2.3.2 x86_64-pc-linux-gnu
TIME,Tue Mar 21 10:39:14 2017,1490089154
HEADER,CLIENT_LIST,Common Name,Real Address,Virtual Address,Bytes Received,Bytes Sent,Connected Since,Connected Since (time_t),Username
CLIENT_LIST,client1,192.168.1.100:12345,10.8.0.2,139583,710764,Thu Mar 16 17:09:03 2017,1489680543,user1
HEADER,ROUTING_TABLE,Virtual Address,Common Name,Real Address,Last Ref,Last Ref (time_t)
ROUTING_TABLE,10.8.0.2,client1,192.168.1.100:12345,Tue Mar 21 10:26:48 2017,1490088408
GLOBAL_STATS,Max bcast/mcast queue length,0
END"""
        
        result = self.parser._parse_content(server_content, "test_server.status")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["connected_clients"], 1)
    
    def test_parse_server_status_v3(self):
        """Test parsing server status file v3"""
        server_content = """TITLE	OpenVPN 2.3.2 x86_64-pc-linux-gnu
TIME	Tue Mar 21 10:39:14 2017	1490089154
HEADER	CLIENT_LIST	Common Name	Real Address	Virtual Address	Bytes Received	Bytes Sent	Connected Since	Connected Since (time_t)	Username
CLIENT_LIST	client1	192.168.1.100:12345	10.8.0.2	139583	710764	Thu Mar 16 17:09:03 2017	1489680543	user1
HEADER	ROUTING_TABLE	Virtual Address	Common Name	Real Address	Last Ref	Last Ref (time_t)
ROUTING_TABLE	10.8.0.2	client1	192.168.1.100:12345	Tue Mar 21 10:26:48 2017	1490088408
GLOBAL_STATS	Max bcast/mcast queue length	0
END"""
        
        result = self.parser._parse_content(server_content, "test_server.status")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["connected_clients"], 1)

class TestOpenVPNExporter(unittest.TestCase):
    """Test main exporter functionality"""
    
    def setUp(self):
        self.status_paths = ["examples/client.status"]
        self.exporter = OpenVPNExporter(self.status_paths, ignore_individuals=False)
    
    def test_exporter_initialization(self):
        """Test exporter initialization"""
        self.assertIsNotNone(self.exporter.parser)
        self.assertIsNotNone(self.exporter.validator)
        self.assertEqual(self.exporter.status_paths, self.status_paths)
    
    @patch('openvpn_exporter.OpenVPNStatusParser.parse_status_file')
    def test_collect_metrics(self, mock_parse):
        """Test metrics collection"""
        mock_parse.return_value = {"status": "parsed"}
        
        # Should not raise an exception
        self.exporter.collect_metrics()
        
        # Verify parse_status_file was called
        mock_parse.assert_called()
    
    def test_get_metrics(self):
        """Test metrics generation"""
        # This will use the actual parser, so we need to handle potential file not found
        try:
            metrics = self.exporter.get_metrics()
            self.assertIsInstance(metrics, str)
            self.assertIn("openvpn_up", metrics)
        except FileNotFoundError:
            # Expected if examples files don't exist
            pass

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow with real example files"""
        # Check if example files exist
        example_files = [
            "examples/client.status",
            "examples/server2.status", 
            "examples/server3.status"
        ]
        
        existing_files = [f for f in example_files if os.path.exists(f)]
        
        if not existing_files:
            self.skipTest("No example files found for integration test")
        
        # Test with existing files
        exporter = OpenVPNExporter(existing_files, ignore_individuals=False)
        
        try:
            metrics = exporter.get_metrics()
            self.assertIsInstance(metrics, str)
            self.assertIn("openvpn_up", metrics)
        except Exception as e:
            self.fail(f"Integration test failed: {e}")

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestSecurityValidator))
    suite.addTest(unittest.makeSuite(TestOpenVPNStatusParser))
    suite.addTest(unittest.makeSuite(TestOpenVPNExporter))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
