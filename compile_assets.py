#!/usr/bin/env python3
"""Compile SCSS assets for the Flask application."""

from app import create_app

app = create_app()

with app.app_context():
    # Get the assets environment
    from flask import current_app
    assets_env = current_app.jinja_env.assets_environment
    
    # Build all registered bundles
    print("🔨 Building SCSS assets...")
    for name, bundle in assets_env._named_bundles.items():
        print(f"  Building {name}...")
        urls = bundle.urls()
        for url in urls:
            print(f"    ✓ {url}")
    
    print("✅ All assets built successfully!")
