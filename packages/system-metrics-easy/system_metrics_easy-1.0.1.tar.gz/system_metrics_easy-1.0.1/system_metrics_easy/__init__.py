"""
Server Metrics Monitor
A comprehensive server monitoring tool that collects and sends system metrics to a Socket.IO server.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server_metrics import ServerMetrics, main

__all__ = ["ServerMetrics", "main"]
