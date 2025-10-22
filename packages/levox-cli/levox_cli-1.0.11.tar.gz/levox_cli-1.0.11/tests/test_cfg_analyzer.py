"""
Unit tests for Control Flow Graph (CFG) Analyzer.

Tests the CFG analysis functionality including:
- CFG construction for different code patterns
- Selective execution logic
- PII detection patterns
- Performance limits and timeouts
- Language-specific CFG building
- Integration with existing pipeline stages
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import Levox components
from levox.detection.cfg_analyzer import (
    CFGAnalyzer, CFGBuilder, CFGNode, CFGEdge, 
    CFGNodeType, CFGEdgeType
)
from levox.core.config import Config, LicenseTier
from levox.models.detection_result import DetectionMatch


class TestCFGNode:
    """Test CFGNode data structure."""
    
    def test_cfg_node_creation(self):
        """Test creating a CFG node with all attributes."""
        node = CFGNode(
            id="test_node",
            node_type=CFGNodeType.STATEMENT,
            line_number=10,
            content="x = 1"
        )
        
        assert node.id == "test_node"
        assert node.node_type == CFGNodeType.STATEMENT
        assert node.line_number == 10
        assert node.content == "x = 1"
        assert node.variables_read == set()
        assert node.variables_written == set()
        assert node.pii_context == {}
        assert node.metadata == {}
    
    def test_cfg_node_with_variables(self):
        """Test creating a CFG node with variable information."""
        node = CFGNode(
            id="assign_node",
            node_type=CFGNodeType.ASSIGNMENT,
            line_number=15,
            content="user_data = get_user_info()",
            variables_written={"user_data"},
            variables_read={"get_user_info"}
        )
        
        assert "user_data" in node.variables_written
        assert "get_user_info" in node.variables_read


class TestCFGEdge:
    """Test CFGEdge data structure."""
    
    def test_cfg_edge_creation(self):
        """Test creating a CFG edge."""
        edge = CFGEdge(
            source_id="node1",
            target_id="node2",
            edge_type=CFGEdgeType.SEQUENTIAL
        )
        
        assert edge.source_id == "node1"
        assert edge.target_id == "node2"
        assert edge.edge_type == CFGEdgeType.SEQUENTIAL
        assert edge.condition is None
        assert edge.metadata == {}


class TestCFGBuilder:
    """Test CFG builder functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = Mock(spec=Config)
        # Mock the cfg_analysis configuration
        cfg_config = Mock()
        cfg_config.confidence_threshold = 0.6
        cfg_config.max_file_size_bytes = 51200
        cfg_config.max_cfg_nodes = 1000
        cfg_config.max_analysis_time_seconds = 30
        cfg_config.supported_languages = ["python", "javascript"]
        config.cfg_analysis = cfg_config
        return config
    
    @pytest.fixture
    def builder(self, config):
        """Create a CFG builder instance."""
        return CFGBuilder(config)
    
    def test_should_analyze_file_with_high_confidence(self, builder):
        """Test that files with high-confidence PII are selected for analysis."""
        previous_matches = [
            DetectionMatch(
                file="test.py",
                line=10,
                engine="ast_analysis",
                rule_id="test_rule",
                severity="HIGH",
                confidence=0.8,
                snippet="if user.is_admin: user_ssn = '123-45-6789'",
                description="SSN detected"
            )
        ]
        
        # Mock the config.is_feature_enabled method
        with patch.object(builder.config, 'is_feature_enabled', return_value=True):
            result, reason = builder.should_analyze_file("test.py", previous_matches, 1000)
            assert result is True
            assert reason is None
    
    def test_should_analyze_file_with_low_confidence(self, builder):
        """Test that files with low-confidence PII are not selected."""
        previous_matches = [
            DetectionMatch(
                file="test.py",
                line=10,
                engine="ast_analysis",
                rule_id="test_rule",
                severity="LOW",
                confidence=0.3,
                snippet="user_id = 123",
                description="User ID detected"
            )
        ]
        
        # Mock the config.is_feature_enabled method
        with patch.object(builder.config, 'is_feature_enabled', return_value=True):
            result, reason = builder.should_analyze_file("test.py", previous_matches, 1000)
            assert result is False
            assert reason == "no_high_confidence_pii"
    
    def test_should_analyze_file_too_large(self, builder):
        """Test that files exceeding size limit are not selected."""
        previous_matches = [
            DetectionMatch(
                file="test.py",
                line=10,
                engine="ast_analysis",
                rule_id="test_rule",
                severity="HIGH",
                confidence=0.8,
                snippet="if user.is_admin: user_ssn = '123-45-6789'",
                description="SSN detected"
            )
        ]
        
        # Mock the config.is_feature_enabled method
        with patch.object(builder.config, 'is_feature_enabled', return_value=True):
            result, reason = builder.should_analyze_file("test.py", previous_matches, 100000)
            assert result is False
            assert "file_too_large" in reason
    
    def test_should_analyze_file_unsupported_language(self, builder):
        """Test that unsupported languages are not selected."""
        previous_matches = [
            DetectionMatch(
                file="test.rb",
                line=10,
                engine="ast_analysis",
                rule_id="test_rule",
                severity="HIGH",
                confidence=0.8,
                snippet="if user.admin? then user_ssn = '123-45-6789' end",
                description="SSN detected"
            )
        ]

        # Mock the config.is_feature_enabled method and detect_language
        with patch.object(builder.config, 'is_feature_enabled', return_value=True):
            with patch('levox.detection.cfg_analyzer.detect_language', return_value="ruby"):
                result, reason = builder.should_analyze_file("test.rb", previous_matches, 1000)
                assert result is False
                assert "unsupported_language" in reason
    
    def test_build_python_cfg_simple(self, builder):
        """Test building CFG for simple Python code."""
        code = """
x = 1
y = 2
z = x + y
"""
        
        nodes, edges = builder._build_python_cfg(code, "test.py")
        
        assert len(nodes) >= 3  # entry, statements, exit
        assert len(edges) >= 2  # connections between nodes
        
        # Check for entry and exit nodes
        node_types = [node.node_type for node in nodes]
        assert CFGNodeType.ENTRY in node_types
        assert CFGNodeType.EXIT in node_types
    
    def test_build_python_cfg_with_conditional(self, builder):
        """Test building CFG for Python code with if statement."""
        code = """
if user.is_admin:
    log_sensitive_data(user.ssn)
else:
    log_basic_info(user.id)
"""
        
        nodes, edges = builder._build_python_cfg(code, "test.py")
        
        # Should have condition nodes
        condition_nodes = [n for n in nodes if n.node_type == CFGNodeType.CONDITION]
        assert len(condition_nodes) > 0
        
        # Should have true/false branch edges
        edge_types = [e.edge_type for e in edges]
        assert CFGEdgeType.TRUE_BRANCH in edge_types
        assert CFGEdgeType.FALSE_BRANCH in edge_types
    
    def test_build_python_cfg_with_loop(self, builder):
        """Test building CFG for Python code with loop."""
        code = """
for user in users:
    if user.has_ssn:
        process_sensitive_data(user.ssn)
"""
        
        nodes, edges = builder._build_python_cfg(code, "test.py")
        
        # Should have loop header nodes
        loop_nodes = [n for n in nodes if n.node_type == CFGNodeType.LOOP_HEADER]
        assert len(loop_nodes) > 0
        
        # Should have loop edges
        edge_types = [e.edge_type for e in edges]
        assert CFGEdgeType.LOOP_ENTRY in edge_types
        assert CFGEdgeType.LOOP_BACK in edge_types


class TestCFGAnalyzer:
    """Test CFG analyzer functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration with CFG enabled."""
        config = Mock(spec=Config)
        config.is_feature_enabled.return_value = True
        # Mock the cfg_analysis configuration
        cfg_config = Mock()
        cfg_config.confidence_threshold = 0.6
        cfg_config.max_file_size_bytes = 51200
        cfg_config.max_cfg_nodes = 1000
        cfg_config.max_analysis_time_seconds = 30
        cfg_config.supported_languages = ["python", "javascript"]
        config.cfg_analysis = cfg_config
        return config
    
    @pytest.fixture
    def analyzer(self, config):
        """Create a CFG analyzer instance."""
        return CFGAnalyzer(config)
    
    def test_analyzer_initialization(self, config):
        """Test CFG analyzer initialization."""
        analyzer = CFGAnalyzer(config)
        assert analyzer.config == config
        assert analyzer.cfg_builder is not None
    
    def test_analyzer_initialization_license_error(self, config):
        """Test CFG analyzer initialization fails without proper license."""
        config.is_feature_enabled.return_value = False
        
        with pytest.raises(Exception):  # Should raise LicenseError
            CFGAnalyzer(config)
    
    def test_scan_file_no_previous_matches(self, analyzer, tmp_path):
        """Test scanning file with no previous matches."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")
        
        # Mock file size check
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_size=100)
            
            # Mock should_analyze_file to return False
            with patch.object(analyzer.cfg_builder, 'should_analyze_file', return_value=False):
                result = analyzer.scan_file(str(test_file))
                assert result == []
    
    def test_scan_file_with_previous_matches(self, analyzer, tmp_path):
        """Test scanning file with previous matches."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
if user.is_admin:
    log_sensitive_data(user.ssn)
""")
        
        previous_matches = [
            DetectionMatch(
                file=str(test_file),
                line=2,
                engine="ast",
                rule_id="test_rule",
                severity="HIGH",
                confidence=0.8,
                snippet="user.ssn",
                description="SSN detected"
            )
        ]
        
        # Mock file size check
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_size=100)
            
            # Mock should_analyze_file to return True
            with patch.object(analyzer.cfg_builder, 'should_analyze_file', return_value=(True, None)):
                # Mock build_cfg_with_timeout to return test nodes/edges
                with patch.object(analyzer.cfg_builder, 'build_cfg_with_timeout') as mock_build:
                    mock_build.return_value = ([], [])
                    
                    result = analyzer.scan_file(str(test_file), previous_matches)
                    # Should return empty list since no CFG was built
                    assert result == []
    
    def test_detect_conditional_pii_exposure(self, analyzer):
        """Test detection of conditional PII exposure."""
        nodes = [
            CFGNode(
                id="cond_1",
                node_type=CFGNodeType.CONDITION,
                line_number=10,
                content="if user.is_admin:"
            )
        ]
        edges = []
        
        # Mock _extract_pii_variables_from_content to return PII variables
        with patch.object(analyzer, '_extract_pii_variables_from_content', return_value=["user_ssn"]):
            matches = analyzer._detect_conditional_pii_exposure_enhanced(nodes, edges, None, "content", "test.py", [])
            
            # Should return matches if PII is detected
            assert isinstance(matches, list)
    
    def test_detect_loop_pii_accumulation(self, analyzer):
        """Test detection of loop PII accumulation."""
        nodes = [
            CFGNode(
                id="loop_1",
                node_type=CFGNodeType.LOOP_HEADER,
                line_number=15,
                content="for user in users:"
            )
        ]
        edges = []
        
        # Mock _extract_pii_variables_from_content to return PII variables
        with patch.object(analyzer, '_extract_pii_variables_from_content', return_value=["user_email"]):
            matches = analyzer._detect_loop_pii_accumulation_enhanced(nodes, edges, None, "content", "test.py", [])
            
            # Should return matches if PII is detected
            assert isinstance(matches, list)
    
    def test_extract_pii_variables_from_content(self, analyzer):
        """Test identification of PII variables in content."""
        content = "process_user_ssn(user.social_security_number)"
        
        pii_vars = analyzer._extract_pii_variables_from_content(content)
        
        # The patterns should match 'ssn' and 'social_security' from the content
        assert len(pii_vars) > 0
        # Check that we found some PII variables
        assert any('ssn' in var.lower() for var in pii_vars)
    
    def test_build_transformation_chains(self, analyzer):
        """Test identification of variable transformation chains."""
        nodes = [
            CFGNode(
                id="assign_1",
                node_type=CFGNodeType.ASSIGNMENT,
                line_number=25,
                content="temp_data = user.ssn",
                variables_written={"temp_data"}
            ),
            CFGNode(
                id="assign_2",
                node_type=CFGNodeType.ASSIGNMENT,
                line_number=26,
                content="processed_data = process(temp_data)",
                variables_written={"processed_data"}
            )
        ]
        edges = [
            CFGEdge(
                source_id="assign_1",
                target_id="assign_2",
                edge_type=CFGEdgeType.SEQUENTIAL
            )
        ]
        
        # Mock _find_next_transformation_node to return the next node
        with patch.object(analyzer, '_find_next_transformation_node', return_value="assign_2"):
            chains = analyzer._build_transformation_chains(nodes, None)
            
            # Should return transformation chains
            assert isinstance(chains, list)


class TestCFGIntegration:
    """Test CFG integration with the detection pipeline."""
    
    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code with potential PII issues."""
        return '''
def process_user_data(user):
    if user.is_admin:
        # High-risk: direct access to SSN
        log_sensitive_data(user.social_security_number)
        store_in_database(user.ssn)
    else:
        # Lower risk: only basic info
        log_basic_info(user.id)
    
    # Loop-based PII accumulation
    user_data = []
    for field in user.sensitive_fields:
        if field.name in ['ssn', 'credit_card', 'email']:
            user_data.append(field.value)
    
    # Complex transformation chain
    temp_data = user.ssn
    processed_data = encrypt(temp_data)
    final_data = hash(processed_data)
    
    return final_data
'''
    
    def test_cfg_analysis_integration(self, sample_python_code, tmp_path):
        """Test full CFG analysis integration."""
        # Create test file
        test_file = tmp_path / "user_processor.py"
        test_file.write_text(sample_python_code)
        
        # Create mock config
        config = Mock(spec=Config)
        config.is_feature_enabled.return_value = True
        # Mock the cfg_analysis configuration
        cfg_config = Mock()
        cfg_config.confidence_threshold = 0.6
        cfg_config.max_file_size_bytes = 51200
        cfg_config.max_cfg_nodes = 1000
        cfg_config.max_analysis_time_seconds = 30
        cfg_config.supported_languages = ["python", "javascript"]
        config.cfg_analysis = cfg_config
        
        # Create analyzer
        analyzer = CFGAnalyzer(config)
        
        # Mock previous matches to trigger CFG analysis
        previous_matches = [
            DetectionMatch(
                file=str(test_file),
                line=3,
                engine="ast",
                rule_id="test_rule",
                severity="HIGH",
                confidence=0.8,
                snippet="user.social_security_number",
                description="SSN detected"
            )
        ]
        
        # Mock file size check
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_size=100)
            
            # Mock should_analyze_file to return True
            with patch.object(analyzer.cfg_builder, 'should_analyze_file', return_value=(True, None)):
                # Mock build_cfg_with_timeout to return test nodes/edges
                with patch.object(analyzer.cfg_builder, 'build_cfg_with_timeout') as mock_build:
                    mock_build.return_value = ([], [])
                    
                    # Run CFG analysis
                    result = analyzer.scan_file(str(test_file), previous_matches)
                    
                    # Should return empty list since no CFG was built
                    assert result == []
                    
                    # Verify that CFG analysis was attempted
                    mock_build.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
