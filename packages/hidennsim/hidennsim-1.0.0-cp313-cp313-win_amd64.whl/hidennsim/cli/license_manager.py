"""License management CLI tool."""

import argparse
import sys
from pathlib import Path

from ..auth.hardware import generate_hardware_fingerprint
from ..auth.license import get_license_path, load_license, validate_license


def activate_license(license_file: Path):
    """
    Activate license from file.

    Args:
        license_file: Path to license file received from vendor
    """
    try:
        # Get license directory
        license_dir = get_license_path().parent
        license_dir.mkdir(parents=True, exist_ok=True)

        # Copy license file
        target_path = get_license_path()
        license_file = Path(license_file)

        if not license_file.exists():
            print(f"❌ License file not found: {license_file}")
            return False

        # Copy to hidennsim directory
        import shutil
        shutil.copy(license_file, target_path)

        # Validate
        if validate_license(use_cache=False):
            print("✅ License activated successfully!")

            # Show license info
            license_data = load_license()
            print(f"\n📄 License Information:")
            print(f"   License ID: {license_data['license_id']}")
            print(f"   Issued to:  {license_data['issued_to']}")
            print(f"   Expires:    {license_data['expires_at']}")
            return True
        else:
            print("❌ License validation failed")
            return False

    except Exception as e:
        print(f"❌ Error activating license: {e}")
        return False


def show_status():
    """Show current license status."""
    try:
        if validate_license(use_cache=False):
            license_data = load_license()
            print("✅ License is active")
            print(f"\n📄 License Information:")
            print(f"   License ID: {license_data['license_id']}")
            print(f"   Issued to:  {license_data['issued_to']}")
            print(f"   Expires:    {license_data['expires_at']}")
        else:
            print("❌ No valid license found")
    except Exception as e:
        print(f"❌ Error checking license: {e}")


def show_hardware_info():
    """Show hardware fingerprint for license binding."""
    fingerprint = generate_hardware_fingerprint()
    print("🖥️  Hardware Fingerprint:")
    print(f"   {fingerprint}")
    print("\n📝 Provide this fingerprint when purchasing a license.")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HIDENNSIM License Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show hardware fingerprint for license purchase
  hidennsim-license hardware

  # Activate license from file
  hidennsim-license activate /path/to/license.key

  # Check license status
  hidennsim-license status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Activate command
    activate_parser = subparsers.add_parser(
        "activate",
        help="Activate license from file"
    )
    activate_parser.add_argument(
        "license_file",
        type=str,
        help="Path to license file"
    )

    # Status command
    subparsers.add_parser(
        "status",
        help="Show current license status"
    )

    # Hardware command
    subparsers.add_parser(
        "hardware",
        help="Show hardware fingerprint"
    )

    args = parser.parse_args()

    if args.command == "activate":
        success = activate_license(Path(args.license_file))
        sys.exit(0 if success else 1)

    elif args.command == "status":
        show_status()

    elif args.command == "hardware":
        show_hardware_info()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
