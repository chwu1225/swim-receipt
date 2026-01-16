"""
Swimming Pool Receipt System - Application Entry Point
"""
import os
from app import create_app

# Create data directory if not exists
data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Determine environment (default to production for Zeabur)
env = os.environ.get('FLASK_ENV', 'production')

# Create application
app = create_app(env)

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 8989))
    debug = env == 'development'

    print('=' * 50)
    print('Swimming Pool Receipt System (Demo Mode)')
    print('Starting server...')
    print('=' * 50)
    print()
    print(f'Access the application at: http://127.0.0.1:{port}')
    print()
    print('Demo Mode: No login required')
    print()
    print('Press Ctrl+C to stop the server')
    print('=' * 50)

    app.run(host='0.0.0.0', port=port, debug=debug)
