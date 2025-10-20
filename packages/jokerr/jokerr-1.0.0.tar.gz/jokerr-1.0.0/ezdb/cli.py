"""
EzDB Command Line Interface
"""
import sys
import argparse


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='EzDB - Easy-to-use vector database',
        prog='ezdb'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Server command
    server_parser = subparsers.add_parser('server', help='Start EzDB server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    server_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    server_parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show package information')

    args = parser.parse_args()

    if args.command == 'server':
        start_server(args)
    elif args.command == 'version':
        show_version()
    elif args.command == 'info':
        show_info()
    else:
        parser.print_help()
        sys.exit(1)


def start_server(args):
    """Start the EzDB server"""
    try:
        import uvicorn
        from ezdb.server.app import app
    except ImportError:
        print("Error: Server dependencies not installed.")
        print("Install with: pip install ezdb[server]")
        sys.exit(1)

    print(f"Starting EzDB server on {args.host}:{args.port}")
    print(f"API docs available at: http://{args.host}:{args.port}/docs")
    print()

    uvicorn.run(
        "ezdb.server.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )


def show_version():
    """Show version information"""
    from ezdb import __version__, __tier__, __stability__

    print(f"EzDB {__tier__} v{__version__}")
    print(f"Status: {__stability__}")


def show_info():
    """Show package information"""
    from ezdb import __version__, __tier__, __stability__, __license__

    print("=" * 60)
    print(f"EzDB {__tier__} - Vector Database")
    print("=" * 60)
    print(f"Version: {__version__}")
    print(f"Tier: {__tier__}")
    print(f"Status: {__stability__}")
    print(f"License: {__license__}")
    print()
    print("Features:")
    print("  - Vector storage and search")
    print("  - HNSW indexing")
    print("  - Multiple similarity metrics")
    print("  - Collections management")
    print("  - Metadata filtering")

    # Check optional features
    optional_features = []

    try:
        import fastapi
        optional_features.append("  ✓ REST API Server")
    except ImportError:
        optional_features.append("  ✗ REST API Server (install with: pip install ezdb[server])")

    try:
        import sentence_transformers
        optional_features.append("  ✓ Built-in Embeddings")
    except ImportError:
        optional_features.append("  ✗ Built-in Embeddings (install with: pip install ezdb[embeddings])")

    try:
        import openai
        optional_features.append("  ✓ OpenAI Support")
    except ImportError:
        optional_features.append("  ✗ OpenAI Support (install with: pip install ezdb[openai])")

    print()
    print("Optional Features:")
    for feature in optional_features:
        print(feature)

    print()
    print("Documentation: https://github.com/yourusername/ezdb")
    print("=" * 60)


if __name__ == '__main__':
    main()
