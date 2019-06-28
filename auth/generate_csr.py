from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import DNSName
from cryptography.x509 import IPAddress
from cryptography.x509.oid import NameOID
from ipaddress import ip_address
import sys


def generate_csr(cn, csr_path, private_key_path, pki_dir, sans={}, org=None):
    '''
    Returns an X509 CSR in
    cryptography.hazmat.backends.openssl.x509._CertificateSigningRequest
    format. See documentation for more details on how to sign.

    cn (str): Common name.
    csr_path (str): Path to store CSR file.
    private_key_path (str): Path to store private key.
    pki_dir (str): Path for PKI directory.
    sans (dict: str -> str): Maps type to value {types, ex. 'IP' -> values, ex. '10.5.1.16'}.
    '''

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    builder = x509.CertificateSigningRequestBuilder()

    # Add the basic attributes. Includes CN.
    builder = builder.subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sunnyvale"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Platform9 Systems"),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ]))

    # Convert the SANs to Python objects.
    sans_converted = []
    for san in sans:
        print(san)
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

    return csr

# # Example CSR generation call.
# csr = generate_csr('etcd', '/tmp/authbs-certs.wTmw/etcd/peer/request.csr', '/tmp/authbs-certs.wTmw/etcd/peer/request.key',
#                    '/tmp/authbs-certs.wTmw/etcd/peer/pki', {'IP': ['127.0.0.1', '10.5.1.16', '10.5.1.16', '10.5.1.16']})
# # Print the CSR, PEM-encoded bytes.
# print(csr.public_bytes(Encoding.PEM))

if __name__ == '__main__':
    args = sys.argv
    args.pop(0)
    params = []
    while args:
        params.append(args.pop(0))
    for i in range(len(params)):
                 print(params[i])

    # Parse the subject alternative names (SANs).
    sans = {'IP': [], 'DNS': []}
    sans_string = params[4]
    kv_pairs = sans_string.split(',')
    for pair in kv_pairs:
        key, value = pair.split(':')
        sans[key].append(value)
    params[4] = sans
    csr = generate_csr(*params)

    from time import time()

    csr_file = open("/root/csrs/%s-%d" % (params[0], time()),"wb")
    csr_file.write(csr.public_bytes(Encoding.PEM))
