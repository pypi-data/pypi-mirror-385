"""
Clean Python file with no PII patterns.
This file should produce zero detections across all detection levels.
"""

import math
import datetime
import json
from typing import List, Dict, Any, Optional

# Configuration without sensitive data
APP_CONFIG = {
    "app_name": "SampleApplication",
    "version": "1.2.3",
    "debug": False,
    "max_retries": 5,
    "timeout_seconds": 30,
    "supported_formats": ["json", "xml", "csv"],
    "default_language": "en",
    "feature_flags": {
        "enable_caching": True,
        "enable_compression": True,
        "enable_analytics": False
    }
}

class Calculator:
    """Simple calculator with mathematical operations."""
    
    def __init__(self):
        self.history = []
        self.precision = 2
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = round(a + b, self.precision)
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        result = round(a - b, self.precision)
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = round(a * b, self.precision)
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = round(a / b, self.precision)
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate power of a number."""
        result = round(math.pow(base, exponent), self.precision)
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, number: float) -> float:
        """Calculate square root."""
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = round(math.sqrt(number), self.precision)
        self.history.append(f"sqrt({number}) = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()

class DataProcessor:
    """Generic data processing utilities."""
    
    @staticmethod
    def filter_numbers(data: List[Any]) -> List[float]:
        """Filter numeric values from a list."""
        return [item for item in data if isinstance(item, (int, float))]
    
    @staticmethod
    def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of numbers."""
        if not numbers:
            return {
                "count": 0,
                "sum": 0,
                "mean": 0,
                "min": 0,
                "max": 0
            }
        
        return {
            "count": len(numbers),
            "sum": sum(numbers),
            "mean": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers)
        }
    
    @staticmethod
    def group_by_range(numbers: List[float], range_size: float) -> Dict[str, List[float]]:
        """Group numbers by ranges."""
        if not numbers or range_size <= 0:
            return {}
        
        groups = {}
        for number in numbers:
            range_key = f"{int(number // range_size) * range_size}-{int(number // range_size + 1) * range_size}"
            if range_key not in groups:
                groups[range_key] = []
            groups[range_key].append(number)
        
        return groups

class FileManager:
    """File management utilities."""
    
    def __init__(self, base_directory: str = "/tmp"):
        self.base_directory = base_directory
        self.supported_extensions = ['.txt', '.json', '.csv', '.log']
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file extension is supported."""
        return any(filename.lower().endswith(ext) for ext in self.supported_extensions)
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get basic file information."""
        return {
            "filename": filename,
            "extension": self.get_file_extension(filename),
            "is_supported": self.is_supported_file(filename),
            "estimated_size": len(filename) * 100,  # Mock size calculation
            "created_at": datetime.datetime.now().isoformat()
        }
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension."""
        parts = filename.split('.')
        return f".{parts[-1]}" if len(parts) > 1 else ""
    
    def generate_backup_name(self, original_name: str) -> str:
        """Generate backup filename."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            return f"{name_parts[0]}_backup_{timestamp}.{name_parts[1]}"
        else:
            return f"{original_name}_backup_{timestamp}"

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    return f"{amount:.2f} {currency}"

def validate_age(age: int) -> bool:
    """Validate if age is within reasonable range."""
    return 0 <= age <= 150

def generate_random_id(prefix: str = "id") -> str:
    """Generate a random identifier."""
    import random
    random_number = random.randint(100000, 999999)
    timestamp = int(datetime.datetime.now().timestamp())
    return f"{prefix}_{timestamp}_{random_number}"

def parse_configuration(config_data: str) -> Dict[str, Any]:
    """Parse JSON configuration string."""
    try:
        return json.loads(config_data)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {str(e)}"}

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes} minutes, {remaining_seconds} seconds"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours} hours, {remaining_minutes} minutes"

def main():
    """Main function demonstrating clean code usage."""
    print("Starting clean code demonstration")
    
    # Calculator usage
    calc = Calculator()
    result1 = calc.add(10.5, 20.3)
    result2 = calc.multiply(result1, 2)
    result3 = calc.sqrt(result2)
    
    print(f"Calculation results: {result1}, {result2}, {result3}")
    print(f"Calculation history: {calc.get_history()}")
    
    # Data processing
    sample_data = [1, 2.5, 3, 4.7, 5, 6.2, 7, 8.9, 9, 10]
    numbers = DataProcessor.filter_numbers(sample_data)
    stats = DataProcessor.calculate_statistics(numbers)
    
    print(f"Data statistics: {stats}")
    
    # File management
    file_manager = FileManager()
    file_info = file_manager.get_file_info("sample_data.json")
    backup_name = file_manager.generate_backup_name("important_file.txt")
    
    print(f"File info: {file_info}")
    print(f"Backup name: {backup_name}")
    
    # Utility functions
    formatted_amount = format_currency(123.456, "EUR")
    is_valid_age = validate_age(25)
    random_id = generate_random_id("user")
    duration_str = format_duration(3661)
    
    print(f"Formatted amount: {formatted_amount}")
    print(f"Age valid: {is_valid_age}")
    print(f"Random ID: {random_id}")
    print(f"Duration: {duration_str}")
    
    print("Clean code demonstration completed successfully")

if __name__ == "__main__":
    main()
