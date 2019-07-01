import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import DNSName
from cryptography.x509 import IPAddress
from cryptography.x509.oid import NameOID
from ipaddress import ip_address


def generate_csr(cn, csr_path, private_key_path, sans={}, org=None):
    '''
    Returns an X509 CSR in
    cryptography.hazmat.backends.openssl.x509._CertificateSigningRequest
    format. See documentation for more details on how to sign.

    cn (str): Common name.
    csr_path (str): Path to store CSR file.
    private_key_path (str): Path to store private key.
    sans (dict: str -> str): Maps type to value {types, ex. 'IP' -> values, ex. '10.5.1.16'}.
    '''

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    key_file = open(private_key_path, "wb")
    key_file.write(private_key.private_bytes(encoding=Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
        ))

    # Add the basic attributes. Includes CN.
    builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sunnyvale"),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, str(org))
    ]))

    # Convert the SANs to Python objects.
    sans_converted = []
    for san in sans:
        if san == 'IP':
            ip_addresses = sans[san]
            for ip in ip_addresses:
                sans_converted.append(IPAddress(ip_address(ip)))
        if san == 'DNS':
            dns_names = sans[san]
            for dns_name in dns_names:
                sans_converted.append(DNSName(dns_name))

    # Add the SANs to the CSR information.
    builder = builder.add_extension(
        x509.SubjectAlternativeName(sans_converted),
        critical=True
    )

    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    )

    # Sign the CSR with our private key.
    csr = builder.sign(
        private_key, hashes.SHA256(), default_backend()
    )

    csr_file = open(csr_path, "wb")
    csr_file.write(csr.public_bytes(Encoding.PEM))

    return csr


def parse_sans(sans_string):
    '''
    sans_string (str): Formatted like 'IP:192.169.0.1,DNS:kubernetes.default.svc', that is,
                       IP and DNS SANs defined by colons and delineated by commas.
    returns (dict): Dictionary mapping IP SANs to their values and same for DNS names.
    '''
    sans = {'IP': [], 'DNS': []}
    kv_pairs = sans_string.split(',')
    for pair in kv_pairs:
        key, value = pair.split(':')
        sans[key].append(value)
    return sans


if __name__ == '__main__':

    # <common_name> </path/to/csr> </path/to/key> [sans] [org]
    args = sys.argv
    args.pop(0)  # Remove script name from args.

    # Parse the subject alternative names (SANs).
    try:
        args[3] = parse_sans(args[3])
    except:
        pass
    generate_csr(*args)
