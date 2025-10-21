"""QArk Formatter for Behave"""

import os
import zipfile
from allure_behave.formatter import AllureFormatter


class QArkFormatter(AllureFormatter):
    """QArk Behave formatter.
    
    This formatter generates test results in a specified directory (default: qark-results).
    """
    
    name = "qark"
    description = "QArk formatter for Behave test results"
    
    def __init__(self, stream_opener, config):
        """Initialize the QArk formatter.
        
        Args:
            stream_opener: Stream opener for output
            config: Behave configuration object
        """
        # Set default output directory if not specified
        if not hasattr(config, 'output') or not config.output:
            config.output = ["qark-results"]
        elif isinstance(config.output, list) and len(config.output) == 0:
            config.output = ["qark-results"]
        
        # Ensure output directory exists
        output_dir = config.output[0] if isinstance(config.output, list) else config.output
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        super().__init__(stream_opener, config)
        
        self._original_stream = self.stream
        self.stream = self._create_filtered_stream()
    
    def _create_filtered_stream(self):
        class FilteredStream:
            def __init__(self, original_stream):
                self.original_stream = original_stream
            
            def write(self, text):
                filtered_text = text.replace("Allure", "QArk")
                filtered_text = filtered_text.replace("allure", "qark")
                return self.original_stream.write(filtered_text)
            
            def flush(self):
                return self.original_stream.flush()
            
            def __getattr__(self, name):
                return getattr(self.original_stream, name)
        
        return FilteredStream(self._original_stream)
    
    def feature(self, feature):
        """Process feature start."""
        super().feature(feature)
    
    def scenario(self, scenario):
        """Process scenario start."""
        super().scenario(scenario)
    
    def step(self, step):
        """Process step execution."""
        super().step(step)
    
    def close(self):
        """Close the formatter and finalize output."""
        super().close()

        # Determine output directory
        output_dir = self.config.output[0] if isinstance(self.config.output, list) else self.config.output
        zip_path = os.path.join(output_dir, "results.zip")

        # Create zip archive with all files under output_dir (excluding the zip itself)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    # Skip the zip file if it already exists in the directory
                    if os.path.abspath(file_path) == os.path.abspath(zip_path):
                        continue
                    # Store files with relative paths inside the archive
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)

        print(f"\nQArk test results compressed to: {zip_path}")
        # Print completion message
        output_dir = self.config.output[0] if isinstance(self.config.output, list) else self.config.output
        print(f"\nQArk test results generated in: {output_dir}")