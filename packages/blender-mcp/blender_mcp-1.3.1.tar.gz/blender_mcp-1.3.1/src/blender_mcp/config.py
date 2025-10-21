"""
Configuration for Blender MCP telemetry
"""
from dataclasses import dataclass


@dataclass
class TelemetryConfig:
    """Telemetry configuration settings"""

    # Supabase connection 
    supabase_url: str = "https://yzasssndwqceclzilcdu.supabase.co"  
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6YXNzc25kd3FjZWNsemlsY2R1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5MDc2NjQsImV4cCI6MjA3NjQ4MzY2NH0.SwFLQ-L0pgQC6bGC_PXCrCcDBYrF6QpZsvApj_Ogt7M" 

    # Telemetry settings
    enabled: bool = True  # Default enabled, users can opt-out
    timeout: float = 1.5  # Seconds to wait for telemetry send

# Global config instance
telemetry_config = TelemetryConfig()
