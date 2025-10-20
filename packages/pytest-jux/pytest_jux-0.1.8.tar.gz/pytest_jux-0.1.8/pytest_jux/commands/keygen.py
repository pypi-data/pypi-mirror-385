# Copyright 2025 Georges Martin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""jux-keygen: Generate cryptographic keys for signing JUnit XML reports."""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Union

import configargparse
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID
from rich.console import Console

# Type alias for private keys
PrivateKeyTypes = Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]

console = Console()


def generate_rsa_key(key_size: int) -> rsa.RSAPrivateKey:
    """Generate an RSA private key.

    Args:
        key_size: RSA key size in bits (2048, 3072, or 4096)

    Returns:
        RSA private key

    Raises:
        ValueError: If key_size is not valid
    """
    if key_size not in (2048, 3072, 4096):
        raise ValueError(f"Key size must be 2048, 3072, or 4096 bits, got {key_size}")

    return rsa.generate_private_key(
        public_exponent=65537,  # F4
        key_size=key_size,
    )


def generate_ecdsa_key(curve_name: str) -> ec.EllipticCurvePrivateKey:
    """Generate an ECDSA private key.

    Args:
        curve_name: Curve name (P-256, P-384, or P-521)

    Returns:
        ECDSA private key

    Raises:
        ValueError: If curve_name is not supported
    """
    curves = {
        "P-256": ec.SECP256R1(),
        "P-384": ec.SECP384R1(),
        "P-521": ec.SECP521R1(),
    }

    if curve_name not in curves:
        raise ValueError(
            f"Unsupported curve: {curve_name}. "
            f"Supported curves: {', '.join(curves.keys())}"
        )

    return ec.generate_private_key(curves[curve_name])


def save_key(key: PrivateKeyTypes, output_path: Path) -> None:
    """Save private key to file with secure permissions.

    Args:
        key: Private key to save
        output_path: Path to save key file

    Raises:
        PermissionError: If unable to set secure file permissions
        OSError: If unable to write file
    """
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize key to PEM format
    pem_data = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Write key to file
    output_path.write_bytes(pem_data)

    # Set secure file permissions (owner read/write only)
    output_path.chmod(0o600)


def generate_self_signed_cert(
    key: PrivateKeyTypes,
    cert_path: Path,
    subject_name: str = "CN=pytest-jux",
    days_valid: int = 365,
) -> None:
    """Generate a self-signed X.509 certificate.

    Args:
        key: Private key for the certificate
        cert_path: Path to save certificate file
        subject_name: Certificate subject (RFC 4514 format)
        days_valid: Number of days the certificate is valid

    Raises:
        OSError: If unable to write certificate file
    """
    # Parse subject name (simple RFC 4514 parsing)
    # For now, just use the CN if provided, otherwise use default
    if "=" in subject_name:
        # Parse CN=value format
        cn_value = subject_name.split("=", 1)[1]
    else:
        cn_value = subject_name

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, cn_value),
        ]
    )

    # Generate certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=days_valid))
        .sign(key, hashes.SHA256())
    )

    # Save certificate to file
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    cert_path.write_bytes(cert_pem)


def main() -> int:
    """Main entry point for jux-keygen command.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = configargparse.ArgumentParser(
        description="Generate cryptographic keys for signing JUnit XML reports",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        help="Config file path",
    )

    parser.add_argument(
        "--type",
        choices=["rsa", "ecdsa"],
        default="rsa",
        help="Key type (rsa or ecdsa)",
    )

    parser.add_argument(
        "--bits",
        type=int,
        choices=[2048, 3072, 4096],
        default=2048,
        help="RSA key size in bits (for RSA keys only)",
    )

    parser.add_argument(
        "--curve",
        choices=["P-256", "P-384", "P-521"],
        default="P-256",
        help="ECDSA curve (for ECDSA keys only)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for private key (PEM format)",
    )

    parser.add_argument(
        "--cert",
        action="store_true",
        help="Generate self-signed X.509 certificate",
    )

    parser.add_argument(
        "--subject",
        default="CN=pytest-jux",
        help="Certificate subject (RFC 4514 format)",
    )

    parser.add_argument(
        "--days-valid",
        type=int,
        default=365,
        help="Certificate validity period in days",
    )

    try:
        args = parser.parse_args()

        # Generate key
        console.print(f"[bold]Generating {args.type.upper()} key...[/bold]")

        if args.type == "rsa":
            key = generate_rsa_key(args.bits)
            console.print(f"  Key size: {args.bits} bits")
        else:  # ecdsa
            key = generate_ecdsa_key(args.curve)
            console.print(f"  Curve: {args.curve}")

        # Save private key
        save_key(key, args.output)
        console.print(f"  [green]✓[/green] Private key saved: {args.output}")

        # Generate certificate if requested
        if args.cert:
            cert_path = args.output.with_suffix(".crt")
            generate_self_signed_cert(key, cert_path, args.subject, args.days_valid)
            console.print(f"  [green]✓[/green] Certificate saved: {cert_path}")
            console.print(
                "  [yellow]⚠[/yellow] Self-signed certificate - "
                "NOT suitable for production use"
            )

        console.print("\n[green]Key generation complete![/green]")
        return 0

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        console.print(
            f"[red]Permission denied:[/red] {e}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        console.print(
            f"[red]Unexpected error:[/red] {e}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
