from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import Encoding

def generate_csr():
  '''
  Returns an X509 CSR in 
  cryptography.hazmat.backends.openssl.x509._CertificateSigningRequest
  format. See documentation for more details on how to sign.
  '''
  private_key = rsa.generate_private_key(
                     public_exponent=65537,
                                  key_size=2048,
                                               backend=default_backend()
                                                        )
  builder = x509.CertificateSigningRequestBuilder()
  builder = builder.subject_name(x509.Name([
               x509.NameAttribute(NameOID.COMMON_NAME, u'cryptography.io'),
                    ]))
  builder = builder.add_extension(
                       x509.BasicConstraints(ca=False, path_length=None), critical=True,
                                )
  request = builder.sign(
                       private_key, hashes.SHA256(), default_backend()
                                )
  print(request.public_bytes(Encoding.PEM))
  isinstance(request, x509.CertificateSigningRequest)
  return request

generate_csr()