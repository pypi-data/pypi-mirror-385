#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration utilities for finding config files in both development and installed environments.
"""
import os
import sys
from pathlib import Path
from typing import Optional


def find_config_file(relative_path: str) -> Optional[str]:
    """
    Find configuration file in both development and installed environments.
    
    Args:
        relative_path: Relative path to config file from project root (e.g., "config/simunet/simunet.yml")
    
    Returns:
        Absolute path to config file if found, None otherwise
    """
    # Method 1: Try current working directory (development environment)
    cwd_path = Path.cwd() / relative_path
    if cwd_path.exists():
        return str(cwd_path)
    
    # Method 2: Try to find config in site-packages using sys.path
    for path in sys.path:
        if 'site-packages' in path:
            site_packages_path = Path(path) / relative_path
            if site_packages_path.exists():
                return str(site_packages_path)
    
    # Method 3: Try relative to this module (installed environment)
    # Go up from components/netdriver/utils to find config
    module_dir = Path(__file__).parent  # utils/
    project_root = module_dir.parent.parent.parent  # go up 3 levels
    installed_path = project_root / relative_path
    if installed_path.exists():
        return str(installed_path)
    
    # Method 4: Try to find config using pkg_resources
    try:
        import pkg_resources
        try:
            # Try to get the distribution
            dist = pkg_resources.get_distribution('simunet-netdriver')
            site_packages_path = Path(dist.location) / relative_path
            if site_packages_path.exists():
                return str(site_packages_path)
        except pkg_resources.DistributionNotFound:
            pass
    except ImportError:
        pass
    
    # Method 5: Try finding netdriver module and look for config relative to it
    try:
        import netdriver
        if hasattr(netdriver, '__file__') and netdriver.__file__:
            netdriver_path = Path(netdriver.__file__).parent
            # Look for config at the same level as netdriver
            config_path = netdriver_path.parent / relative_path
            if config_path.exists():
                return str(config_path)
    except (ImportError, AttributeError):
        pass
    
    return None


def get_config_path(config_name: str) -> str:
    """
    Get the path to a specific config file.
    
    Args:
        config_name: Name of the config ('agent' or 'simunet')
    
    Returns:
        Path to the config file
        
    Raises:
        FileNotFoundError: If config file cannot be found
    """
    if config_name == 'agent':
        relative_path = "config/agent/agent.yml"
    elif config_name == 'simunet':
        relative_path = "config/simunet/simunet.yml"
    else:
        raise ValueError(f"Unknown config name: {config_name}")
    
    config_path = find_config_file(relative_path)
    if config_path is None:
        # Provide more detailed error information
        error_msg = f"Could not find config file: {relative_path}\n"
        error_msg += "Searched in:\n"
        error_msg += f"  - Current directory: {Path.cwd() / relative_path}\n"
        
        for path in sys.path:
            if 'site-packages' in path:
                error_msg += f"  - Site packages: {Path(path) / relative_path}\n"
        
        try:
            import netdriver
            if hasattr(netdriver, '__file__') and netdriver.__file__:
                netdriver_path = Path(netdriver.__file__).parent
                config_path_attempt = netdriver_path.parent / relative_path
                error_msg += f"  - Relative to netdriver: {config_path_attempt}\n"
        except ImportError:
            error_msg += "  - Could not import netdriver module\n"
        
        raise FileNotFoundError(error_msg)
    
    return config_path