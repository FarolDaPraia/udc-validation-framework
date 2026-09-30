"""
Serial2 Log Parser Module
Reads and parses Serial2 .s2db databases
"""

from .parser import Serial2LogParser
from .filter import FilterConfig

__all__ = ['Serial2LogParser', 'FilterConfig']
