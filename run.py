#!/usr/bin/env python3
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f"🚀 Freakinbeats Server")
    print(f"🌐 Running at: http://localhost:{Config.PORT}")
    print(f"⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)

