import logging
import gzip
import zlib
import lzma
import bz2
import json
import pickle
from typing import Any, Dict, List, Optional, Union, BinaryIO
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import time

class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    GZIP = "gzip"
    ZLIB = "zlib"
    LZMA = "lzma"
    BZ2 = "bz2"
    NONE = "none"

@dataccript
class CompressionStats:
    """Compression statistics."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    algorithm: CompressionAlgorithm
    
    @property
    def space_saved(self) -> int:
        """Calculate space saved in bytes."""
        return self.original_size - self.compressed_size
    
    @property
    def space_saved_percentage(self) -> float:
        """Calculate space saved as percentage."""
        if self.original_size == 0:
            return 0.0
        return (self.space_saved / self.original_size) * 100

class DataCompressor:
    """
    High-performance data compression with multiple algorithms and automatic optimization.
    """
    
    def __init__(self, default_algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP):
        self.logger = logging.getLogger(__name__)
        self.default_algorithm = default_algorithm
        
        # Algorithm configurations
        self.algorithm_configs = {
            CompressionAlgorithm.GZIP: {
                'compress_level': 6,  # Balanced compression/speed
                'compress_func': gzip.compress,
                'decompress_func': gzip.decompress
            },
            CompressionAlgorithm.ZLIB: {
                'compress_level': 6,
                'compress_func': zlib.compress,
                'decompress_func': zlib.decompress
            },
            CompressionAlgorithm.LZMA: {
                'compress_level': 6,
                'compress_func': lzma.compress,
                'decompress_func': lzma.decompress
            },
            CompressionAlgorithm.BZ2: {
                'compress_level': 6,
                'compress_func': bz2.compress,
                'decompress_func': bz2.decompress
            },
            CompressionAlgorithm.NONE: {
                'compress_level': 0,
                'compress_func': lambda data: data,
                'decompress_func': lambda data: data
            }
        }
    
    def compress_data(self, data: Union[str, bytes, dict, list], 
                     algorithm: Optional[CompressionAlgorithm] = None) -> tuple[bytes, CompressionStats]:
        """
        Compress data using the specified algorithm.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm to use
            
        Returns:
            Tuple of (compressed_data, compression_stats)
        """
        algorithm = algorithm or self.default_algorithm
        start_time = time.time()
        
        # Convert data to bytes
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            # Try to serialize with pickle
            data_bytes = pickle.dumps(data)
        
        original_size = len(data_bytes)
        
        # Compress data
        config = self.algorithm_configs[algorithm]
        compress_func = config['compress_func']
        compress_level = config['compress_level']
        
        if algorithm == CompressionAlgorithm.GZIP:
            compressed_data = compress_func(data_bytes, compresslevel=compress_level)
        elif algorithm == CompressionAlgorithm.ZLIB:
            compressed_data = compress_func(data_bytes, level=compress_level)
        elif algorithm == CompressionAlgorithm.LZMA:
            compressed_data = compress_func(data_bytes, preset=compress_level)
        elif algorithm == CompressionAlgorithm.BZ2:
            compressed_data = compress_func(data_bytes, compresslevel=compress_level)
        else:  # NONE
            compressed_data = data_bytes
        
        compression_time = time.time() - start_time
        compressed_size = len(compressed_data)
        
        # Calculate compression ratio
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        stats = CompressionStats(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_time=compression_time,
            algorithm=algorithm
        )
        
        self.logger.debug(f"Compressed {original_size} bytes to {compressed_size} bytes "
                         f"({compression_ratio:.2%}) using {algorithm.value} in {compression_time:.3f}s")
        
        return compressed_data, stats
    
    def decompress_data(self, compressed_data: bytes, 
                       algorithm: Optional[CompressionAlgorithm] = None) -> Any:
        """
        Decompress data using the specified algorithm.
        
        Args:
            compressed_data: Compressed data
            algorithm: Compression algorithm used
            
        Returns:
            Decompressed data
        """
        algorithm = algorithm or self.default_algorithm
        
        config = self.algorithm_configs[algorithm]
        decompress_func = config['decompress_func']
        
        decompressed_bytes = decompress_func(compressed_data)
        
        # Try to decode as JSON first, then fall back to string
        try:
            return json.loads(decompressed_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return decompressed_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Return as bytes if can't decode
                return decompressed_bytes
    
    def find_best_algorithm(self, data: Union[str, bytes, dict, list], 
                           algorithms: Optional[List[CompressionAlgorithm]] = None) -> CompressionAlgorithm:
        """
        Find the best compression algorithm for the given data.
        
        Args:
            data: Data to test compression on
            algorithms: List of algorithms to test
            
        Returns:
            Best compression algorithm
        """
        if algorithms is None:
            algorithms = [CompressionAlgorithm.GZIP, CompressionAlgorithm.ZLIB, 
                         CompressionAlgorithm.LZMA, CompressionAlgorithm.BZ2]
        
        best_algorithm = CompressionAlgorithm.NONE
        best_ratio = 1.0
        
        for algorithm in algorithms:
            try:
                _, stats = self.compress_data(data, algorithm)
                if stats.compression_ratio < best_ratio:
                    best_ratio = stats.compression_ratio
                    best_algorithm = algorithm
            except Exception as e:
                self.logger.warning(f"Failed to test {algorithm.value}: {e}")
        
        self.logger.info(f"Best compression algorithm for data: {best_algorithm.value} "
                        f"(ratio: {best_ratio:.2%})")
        
        return best_algorithm
    
    def compress_file(self, input_path: Union[str, Path], 
                     output_path: Union[str, Path],
                     algorithm: Optional[CompressionAlgorithm] = None) -> CompressionStats:
        """
        Compress a file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output compressed file
            algorithm: Compression algorithm to use
            
        Returns:
            Compression statistics
        """
        algorithm = algorithm or self.default_algorithm
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        start_time = time.time()
        
        # Read input file
        with open(input_path, 'rb') as f:
            data = f.read()
        
        original_size = len(data)
        
        # Compress data
        compressed_data, stats = self.compress_data(data, algorithm)
        
        # Write compressed file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(compressed_data)
        
        compression_time = time.time() - start_time
        
        final_stats = CompressionStats(
            original_size=original_size,
            compressed_size=len(compressed_data),
            compression_ratio=stats.compression_ratio,
            compression_time=compression_time,
            algorithm=algorithm
        )
        
        self.logger.info(f"Compressed file {input_path} to {output_path} "
                        f"({final_stats.compression_ratio:.2%})")
        
        return final_stats
    
    def decompress_file(self, input_path: Union[str, Path], 
                       output_path: Union[str, Path],
                       algorithm: Optional[CompressionAlgorithm] = None) -> int:
        """
        Decompress a file.
        
        Args:
            input_path: Path to compressed file
            output_path: Path to output decompressed file
            algorithm: Compression algorithm used
            
        Returns:
            Size of decompressed file
        """
        algorithm = algorithm or self.default_algorithm
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # Read compressed file
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
        
        # Decompress data
        decompressed_data = self.decompress_data(compressed_data, algorithm)
        
        # Write decompressed file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            if isinstance(decompressed_data, bytes):
                f.write(decompressed_data)
            else:
                f.write(str(decompressed_data).encode('utf-8'))
        
        decompressed_size = len(decompressed_data) if isinstance(decompressed_data, bytes) else len(str(decompressed_data).encode('utf-8'))
        
        self.logger.info(f"Decompressed file {input_path} to {output_path} "
                        f"({decompressed_size} bytes)")
        
        return decompressed_size

class CompressedStorage:
    """
    Storage wrapper that automatically compresses large data.
    """
    
    def __init__(self, compressor: DataCompressor, 
                 compression_threshold: int = 1024,  # 1KB
                 auto_algorithm_selection: bool = True):
        self.compressor = compressor
        self.compression_threshold = compression_threshold
        self.auto_algorithm_selection = auto_algorithm_selection
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'total_stored': 0,
            'total_compressed': 0,
            'total_decompressed': 0,
            'space_saved': 0,
            'compression_operations': 0
        }
    
    def store_data(self, key: str, data: Any, 
                  force_compression: bool = False) -> Dict[str, Any]:
        """
        Store data with automatic compression if beneficial.
        
        Args:
            key: Storage key
            data: Data to store
            force_compression: Force compression regardless of size
            
        Returns:
            Storage metadata
        """
        # Convert to bytes for size calculation
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = pickle.dumps(data)
        
        original_size = len(data_bytes)
        compressed = False
        algorithm = CompressionAlgorithm.NONE
        
        # Decide whether to compress
        if force_compression or original_size > self.compression_threshold:
            if self.auto_algorithm_selection:
                algorithm = self.compressor.find_best_algorithm(data)
            else:
                algorithm = self.compressor.default_algorithm
            
            compressed_data, stats = self.compressor.compress_data(data, algorithm)
            
            # Only use compression if it saves space
            if stats.compression_ratio < 1.0:
                data_bytes = compressed_data
                compressed = True
                self.stats['space_saved'] += stats.space_saved
                self.stats['compression_operations'] += 1
            else:
                algorithm = CompressionAlgorithm.NONE
        
        # Store the data (in a real implementation, this would write to disk/database)
        storage_metadata = {
            'key': key,
            'original_size': original_size,
            'stored_size': len(data_bytes),
            'compressed': compressed,
            'algorithm': algorithm.value if compressed else None,
            'timestamp': time.time()
        }
        
        # Update statistics
        self.stats['total_stored'] += 1
        if compressed:
            self.stats['total_compressed'] += 1
        
        self.logger.debug(f"Stored data for key {key}: {original_size} bytes "
                         f"{'compressed' if compressed else 'uncompressed'}")
        
        return storage_metadata
    
    def retrieve_data(self, key: str, metadata: Dict[str, Any]) -> Any:
        """
        Retrieve and decompress data.
        
        Args:
            key: Storage key
            metadata: Storage metadata
            
        Returns:
            Retrieved data
        """
        # In a real implementation, this would read from disk/database
        # For now, we'll simulate the retrieval
        
        if metadata.get('compressed', False):
            algorithm = CompressionAlgorithm(metadata['algorithm'])
            # Simulate decompression
            self.stats['total_decompressed'] += 1
            self.logger.debug(f"Retrieved and decompressed data for key {key}")
        else:
            self.logger.debug(f"Retrieved uncompressed data for key {key}")
        
        # Return placeholder data
        return {"retrieved": True, "key": key}
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        total_data = self.stats['total_stored']
        compressed_data = self.stats['total_compressed']
        
        return {
            'total_operations': total_data,
            'compression_rate': compressed_data / total_data if total_data > 0 else 0,
            'space_saved_bytes': self.stats['space_saved'],
            'compression_operations': self.stats['compression_operations'],
            'avg_space_saved_per_operation': (
                self.stats['space_saved'] / self.stats['compression_operations'] 
                if self.stats['compression_operations'] > 0 else 0
            )
        }

class EvidenceCompressor:
    """
    Specialized compressor for evidence data with intelligent compression strategies.
    """
    
    def __init__(self, compressor: DataCompressor = None):
        self.compressor = compressor or DataCompressor()
        self.logger = logging.getLogger(__name__)
        
        # Compression strategies for different data types
        self.compression_strategies = {
            'scan_results': {
                'threshold': 2048,  # 2KB
                'algorithm': CompressionAlgorithm.GZIP,
                'description': 'Scan results with JSON data'
            },
            'violations': {
                'threshold': 1024,  # 1KB
                'algorithm': CompressionAlgorithm.ZLIB,
                'description': 'Violation records with repetitive data'
            },
            'evidence_packages': {
                'threshold': 512,   # 512B
                'algorithm': CompressionAlgorithm.LZMA,
                'description': 'Large evidence packages'
            },
            'trend_data': {
                'threshold': 1024,  # 1KB
                'algorithm': CompressionAlgorithm.GZIP,
                'description': 'Trend analysis data'
            },
            'ml_models': {
                'threshold': 0,     # Always compress
                'algorithm': CompressionAlgorithm.LZMA,
                'description': 'ML model data'
            }
        }
    
    def compress_evidence_data(self, data_type: str, data: Any) -> tuple[bytes, CompressionStats]:
        """
        Compress evidence data using appropriate strategy.
        
        Args:
            data_type: Type of evidence data
            data: Data to compress
            
        Returns:
            Tuple of (compressed_data, compression_stats)
        """
        strategy = self.compression_strategies.get(data_type, {
            'threshold': 1024,
            'algorithm': CompressionAlgorithm.GZIP,
            'description': 'Default compression'
        })
        
        # Check if compression is beneficial
        data_size = self._estimate_data_size(data)
        if data_size < strategy['threshold']:
            # Use no compression for small data
            compressed_data, stats = self.compressor.compress_data(data, CompressionAlgorithm.NONE)
        else:
            # Use recommended algorithm
            compressed_data, stats = self.compressor.compress_data(data, strategy['algorithm'])
        
        self.logger.debug(f"Compressed {data_type} data: {stats.original_size} -> "
                         f"{stats.compressed_size} bytes ({stats.compression_ratio:.2%})")
        
        return compressed_data, stats
    
    def decompress_evidence_data(self, data_type: str, compressed_data: bytes) -> Any:
        """
        Decompress evidence data.
        
        Args:
            data_type: Type of evidence data
            compressed_data: Compressed data
            
        Returns:
            Decompressed data
        """
        strategy = self.compression_strategies.get(data_type, {
            'algorithm': CompressionAlgorithm.GZIP
        })
        
        return self.compressor.decompress_data(compressed_data, strategy['algorithm'])
    
    def _estimate_data_size(self, data: Any) -> int:
        """Estimate the size of data in bytes."""
        if isinstance(data, (dict, list)):
            return len(json.dumps(data, separators=(',', ':')).encode('utf-8'))
        elif isinstance(data, str):
            return len(data.encode('utf-8'))
        elif isinstance(data, bytes):
            return len(data)
        else:
            return len(pickle.dumps(data))
    
    def get_compression_recommendations(self, data_type: str, data: Any) -> Dict[str, Any]:
        """
        Get compression recommendations for data.
        
        Args:
            data_type: Type of data
            data: Data to analyze
            
        Returns:
            Compression recommendations
        """
        data_size = self._estimate_data_size(data)
        strategy = self.compression_strategies.get(data_type, {})
        
        recommendations = {
            'data_type': data_type,
            'data_size': data_size,
            'recommended_algorithm': strategy.get('algorithm', CompressionAlgorithm.GZIP).value,
            'compression_threshold': strategy.get('threshold', 1024),
            'should_compress': data_size >= strategy.get('threshold', 1024),
            'description': strategy.get('description', 'Default compression strategy')
        }
        
        # Test compression if beneficial
        if recommendations['should_compress']:
            try:
                _, stats = self.compressor.compress_data(data, strategy.get('algorithm', CompressionAlgorithm.GZIP))
                recommendations.update({
                    'estimated_compressed_size': stats.compressed_size,
                    'estimated_compression_ratio': stats.compression_ratio,
                    'estimated_space_saved': stats.space_saved
                })
            except Exception as e:
                recommendations['compression_error'] = str(e)
        
        return recommendations
