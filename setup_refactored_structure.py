#!/usr/bin/env python3
"""
Enhanced Media Scraper - Refactoring Setup Script
=================================================

This script helps migrate from the old monolithic structure to the new
organized, secure, and maintainable structure.

Usage:
    python setup_refactored_structure.py [--backup] [--force]
    
Options:
    --backup    Create backups of existing files before migration
    --force     Overwrite existing files without confirmation
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

def create_directory_structure():
    """Create the new organized directory structure."""
    directories = [
        # CSS directories
        'static/css/base',
        'static/css/components', 
        'static/css/utilities',
        'static/css/themes',
        
        # JavaScript directories
        'static/js/modules',
        'static/js/utils',
        'static/js/components',
        
        # Template directories
        'templates/components',
        'templates/components/modals',
        'templates/layouts',
        
        # Asset directories (if needed)
        'static/images',
        'static/fonts',
        'static/icons',
        
        # Documentation
        'docs',
        'docs/api',
        'docs/components',
        
        # Backup directory
        'backups'
    ]
    
    print("🏗️  Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")

def backup_existing_files():
    """Create backups of existing files."""
    backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    files_to_backup = [
        'templates/index.html',
        'static/css/style.css',  # If exists
        'static/js/app.js',      # If exists
    ]
    
    print(f"💾 Creating backups in {backup_dir}...")
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backed up: {file_path} → {backup_path}")
        else:
            print(f"   ⚠️  File not found: {file_path}")

def create_index_files():
    """Create index.md files for documentation directories."""
    index_files = {
        'docs/README.md': """# Enhanced Media Scraper Documentation

## Directory Structure

- `api/` - API documentation and examples
- `components/` - UI component documentation
- `setup/` - Installation and setup guides
- `development/` - Development guidelines and standards

## Quick Links

- [API Reference](api/)
- [Component Library](components/)
- [Development Guide](development/)
- [Deployment Guide](setup/)
""",
        
        'docs/components/README.md': """# Component Documentation

This directory contains documentation for all UI components.

## Available Components

- Navbar - Navigation bar with authentication
- Sidebar - Application navigation sidebar  
- Asset Grid - Media asset display grid
- Media Viewer - Fullscreen media viewer
- Search Form - Search and filter interface

## Component Standards

Each component should have:
- Semantic HTML structure
- Accessible ARIA labels
- Responsive design
- Dark theme support
- Keyboard navigation
""",

        'static/css/README.md': """# CSS Architecture

## Directory Structure

- `base/` - Foundational styles (reset, variables, typography)
- `components/` - Component-specific styles
- `utilities/` - Utility classes and helpers
- `themes/` - Theme variations and responsive styles

## Naming Conventions

- Use BEM methodology for class names
- Component classes: `.component-name`
- Modifier classes: `.component-name--modifier`
- Utility classes: `.u-utility-name`

## CSS Custom Properties

All styling uses CSS custom properties defined in `base/variables.css`.
This enables runtime theme switching and consistent design system.
""",

        'static/js/README.md': """# JavaScript Architecture

## Directory Structure

- `modules/` - Main application modules
- `utils/` - Utility functions and helpers
- `components/` - Component-specific JavaScript

## Code Standards

- ES6+ syntax and features
- Class-based architecture
- Proper error handling
- Security-first approach
- Comprehensive documentation

## Security Guidelines

- Always sanitize user input
- Use SecurityUtils for DOM manipulation  
- Validate all API responses
- Handle errors gracefully
"""
    }
    
    print("📝 Creating documentation files...")
    for file_path, content in index_files.items():
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"   ✅ Created: {file_path}")

def create_placeholder_files():
    """Create placeholder files for components that need to be implemented."""
    placeholder_files = {
        'static/css/components/sidebar.css': """/* Sidebar Component Styles */
/* TODO: Implement sidebar styles */

.sidebar {
    /* Add sidebar styles here */
}
""",
        
        'static/css/components/cards.css': """/* Card Component Styles */
/* TODO: Implement card styles */

.card {
    /* Add card styles here */
}
""",
        
        'static/css/components/forms.css': """/* Form Component Styles */
/* TODO: Implement form styles */

.form-control {
    /* Add form styles here */
}
""",
        
        'static/css/components/media-viewer.css': """/* Media Viewer Component Styles */
/* TODO: Implement media viewer styles */

.media-viewer-modal {
    /* Add media viewer styles here */
}
""",
        
        'static/js/modules/media-viewer.js': """/**
 * Media Viewer Module
 * TODO: Implement enhanced media viewer functionality
 */

class MediaViewer {
    constructor(app) {
        this.app = app;
        // TODO: Initialize media viewer
    }
    
    // TODO: Implement methods
}

window.MediaViewer = MediaViewer;
""",
        
        'static/js/modules/asset-manager.js': """/**
 * Asset Manager Module  
 * TODO: Implement asset management functionality
 */

class AssetManager {
    constructor(app) {
        this.app = app;
        // TODO: Initialize asset manager
    }
    
    // TODO: Implement methods
}

window.AssetManager = AssetManager;
""",
        
        'static/js/utils/api.js': """/**
 * API Utilities
 * TODO: Implement secure API communication layer
 */

class APIUtils {
    // TODO: Implement API methods
    static async get(endpoint) {
        // TODO: Implement secure GET request
    }
    
    static async post(endpoint, data) {
        // TODO: Implement secure POST request
    }
}

window.APIUtils = APIUtils;
"""
    }
    
    print("📄 Creating placeholder files...")
    for file_path, content in placeholder_files.items():
        if not os.path.exists(file_path):
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"   ✅ Created: {file_path}")
        else:
            print(f"   ⚠️  Already exists: {file_path}")

def print_next_steps():
    """Print instructions for next steps."""
    print("""
🎉 Setup Complete! 

📋 NEXT STEPS:

1. **Review the new structure:**
   - Check the created directories and files
   - Read the documentation in docs/

2. **Migrate your existing code:**
   - Move custom styles to appropriate component CSS files
   - Move JavaScript functions to appropriate modules
   - Update any custom Flask routes

3. **Test the new structure:**
   - Start your Flask application
   - Navigate to templates/index_new.html  
   - Test theme switching and navigation

4. **Complete remaining components:**
   - Fill in the placeholder CSS files
   - Implement the JavaScript modules
   - Test all functionality

5. **Deploy gradually:**
   - Test thoroughly in development
   - Use feature flags for gradual rollout
   - Monitor for any issues

📚 Documentation:
   - See REFACTORING_PROGRESS.md for detailed progress
   - Check docs/ directory for component documentation
   - Review static/css/base/variables.css for design system

🆘 Need Help?
   - Check the refactoring documentation
   - Review the code comments for guidance
   - Test each component individually before integration

Good luck with your refactoring! 🚀
""")

def main():
    parser = argparse.ArgumentParser(description='Setup Enhanced Media Scraper refactored structure')
    parser.add_argument('--backup', action='store_true', help='Create backups of existing files')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files without confirmation')
    
    args = parser.parse_args()
    
    print("""
🚀 Enhanced Media Scraper - Refactoring Setup
============================================

This script will create the new organized directory structure
and help migrate from the old monolithic codebase.
""")
    
    if not args.force:
        confirm = input("Continue with setup? (y/N): ")
        if confirm.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Create the new directory structure
    create_directory_structure()
    
    # Backup existing files if requested
    if args.backup:
        backup_existing_files()
    
    # Create documentation files
    create_index_files()
    
    # Create placeholder files for remaining work
    create_placeholder_files()
    
    # Print next steps
    print_next_steps()

if __name__ == '__main__':
    main() 