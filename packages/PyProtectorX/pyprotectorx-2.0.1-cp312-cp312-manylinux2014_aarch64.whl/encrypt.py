#!/usr/bin/env python3
"""
PyProtectorX v2.0.0 - Command Line Interface
Copyright (c) 2025 Zain Alkhalil (VIP). All Rights Reserved.
Website: https://pyprotectorx.netlify.app
"""

import sys
import argparse
from pathlib import Path

try:
    import PyProtectorX
except ImportError:
    print("❌ Error: PyProtectorX module not found!")
    print("Please install it first: pip install PyProtectorX")
    sys.exit(1)


LOADER_TEMPLATE = '''#!/usr/bin/env python3
# Protected by PyProtectorX v2.0.1
# Website: https://pyprotectorx.netlify.app
import PyProtectorX

__encrypted__ = {encrypted_data!r}

if __name__ == "__main__":
    try:
        PyProtectorX.Run(__encrypted__)
    except Exception as e:
        print(f"Error executing protected code: {{e}}")
        import sys
        sys.exit(1)
'''


def encode_file(input_path, output_path=None):
    """Encode (encrypt) a Python file with PyProtectorX"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ Error: File '{input_path}' not found!")
        return False
    
    if not input_file.suffix == '.py':
        print(f"❌ Error: File must be a Python file (.py)")
        return False
    
    # Read source code
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Encrypt with PyProtectorX
    try:
        print(f"🔒 Encoding '{input_file.name}' with military-grade encryption...")
        encrypted = PyProtectorX.dumps(source_code)
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return False
    
    # Generate output filename
    if output_path is None:
        output_path = input_file.parent / f"{input_file.stem}_Enc.py"
    else:
        output_path = Path(output_path)
    
    # Create protected file
    try:
        protected_code = LOADER_TEMPLATE.format(encrypted_data=encrypted)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(protected_code)
        
        print(f"✅ Successfully encrypted!")
        print(f"📁 Output: {output_path}")
        print(f"📊 Original size: {len(source_code)} bytes")
        print(f"📊 Protected size: {len(protected_code)} bytes")
        print(f"🌐 Docs: https://pyprotectorx.netlify.app/docs")
        return True
        
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return False


def show_info():
    """Show system and encryption information"""
    try:
        info = PyProtectorX.get_system_info()
        print("\n" + "="*60)
        print("🔒 PyProtectorX v2.0.0 - Military-Grade Encryption")
        print("="*60)
        print(f"📊 Version: {info['version']}")
        print(f"💻 Architecture: {info['architecture']}")
        print(f"🖥️  Operating System: {info['os']}")
        print(f"⚙️  64-bit: {info['is_64bit']}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("="*60)
        print("🌐 Website: https://pyprotectorx.netlify.app")
        print("📚 Documentation: https://pyprotectorx.netlify.app/docs")
        print("👤 Author: Zain Alkhalil (VIP)")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error getting info: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='PyProtectorX - Military-Grade Python Code Protection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  PyProtectorX encode script.py              # Encrypt script.py -> script_Enc.py
  PyProtectorX encode script.py -o out.py    # Encrypt with custom output name
  PyProtectorX info                          # Show system information

Website: https://pyprotectorx.netlify.app
Docs: https://pyprotectorx.netlify.app/docs
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode (encrypt) a Python file')
    encode_parser.add_argument('input', help='Input Python file to protect')
    encode_parser.add_argument('-o', '--output', help='Output file name (optional)')
    
    # Info command
    subparsers.add_parser('info', help='Show system and encryption information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if args.command == 'encode':
        success = encode_file(args.input, args.output)
        sys.exit(0 if success else 1)
    elif args.command == 'info':
        show_info()
        sys.exit(0)


if __name__ == "__main__":
    main()
