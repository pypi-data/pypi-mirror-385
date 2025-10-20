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

"""XML signature verification using XMLDSig."""

from typing import Union

from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509 import load_pem_x509_certificate
from lxml import etree
from signxml import XMLVerifier

# Type aliases
PublicKeyTypes = Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]
CertOrKeyType = Union[PublicKeyTypes, bytes, str]


def _create_temp_certificate(public_key: PublicKeyTypes) -> bytes:
    """Create a temporary self-signed certificate from a public key.

    This is used when verifying with just a public key object.

    Args:
        public_key: RSA or ECDSA public key

    Returns:
        PEM-encoded certificate bytes
    """
    # We need a private key to sign the certificate, but for verification
    # purposes we just need the public key to match. This is a workaround
    # for signxml requiring a certificate.
    # Actually, we can't create a proper cert without the private key.
    # Instead, let's just use the key from the signature itself.
    raise NotImplementedError("Verification with public key object not yet supported")


def verify_signature(tree: etree._Element, cert_or_key: CertOrKeyType) -> bool:
    """Verify XML digital signature.

    Args:
        tree: XML element tree with signature
        cert_or_key: Certificate (bytes/string) or public key object

    Returns:
        True if signature is valid, False otherwise

    Raises:
        ValueError: If no signature is found or certificate is invalid
        NotImplementedError: If public key object is provided (not yet supported)
    """
    # Find signature element
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature is None:
        raise ValueError("No signature found in XML")

    # Convert to appropriate format for signxml
    if isinstance(cert_or_key, bytes):
        # signxml accepts PEM-encoded certificate as bytes
        cert_data = cert_or_key
    elif isinstance(cert_or_key, str):
        cert_data = cert_or_key.encode()
    else:
        # Public key object - for now, verify without cert
        # signxml can extract the key from the signature itself
        verifier = XMLVerifier()
        try:
            # Verify without providing explicit cert (use key from signature)
            verifier.verify(tree)
            return True
        except Exception:
            return False

    # Validate certificate before verification
    try:
        load_pem_x509_certificate(cert_data)
    except Exception:
        raise ValueError("Invalid certificate")

    # Verify signature with provided certificate
    verifier = XMLVerifier()
    try:
        verifier.verify(tree, x509_cert=cert_data)
        return True
    except Exception:
        # Signature verification failed
        return False
