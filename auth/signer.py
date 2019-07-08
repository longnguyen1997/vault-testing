from hvac import Client as VaultClient
from os import getenv
from time import time
from secrets_engines import *
import sys
from fire import Fire

def get_client(dev=False):
    if dev is False:
        return VaultClient(url=getenv(
            'VAULT_ADDR', 'http://127.0.0.1:8200'), token=getenv('VAULT_TOKEN'))
    return VaultClient()  # No authentication needed if dev mode.


def generate_root_ca(cluster_id='1199'):
    '''
    cluster_id (str): ID of the PMK cluster. Mocked to 1199.

    Generates/enables a new Vault PKI engine for the cluster provided, if it does
    not already exist. This will be an internal PKI engine, so the private key is
    not exported.

    Also generates a new Vault role, 'root', for this cluster CA to sign certs.

    Uses the Python HVAC Vault API:
    https://hvac.readthedocs.io/en/stable/usage/secrets_engines/pki.html.
    '''

    # Assumes Vault is on localhost if no information is found.

    cluster_id = str(cluster_id)
    vault_path = 'pmk-ca-' + cluster_id + '/'
    common_name = 'kubernetes-ca@%d' % time()

    client = get_client(True)

    if vault_path not in get_secrets_engines_paths(client):
        enable_new_pki_secrets_engine(
            client,
            vault_path,
            description='PMK CA engine for cluster UUID ' + cluster_id)

    # Tune the max TTL for the CA certificate.
    client.sys.tune_mount_configuration(
        path=vault_path,
        default_lease_ttl='47300h',  # 5 years by default.
        max_lease_ttl='87600h',
    )

    # Generate root CA for this cluster.
    # Private key is NOT ever exposed.
    ca_response = client.secrets.pki.generate_root(
        type='internal',
        common_name=common_name,
        mount_point=vault_path,
        extra_params={
            'ttl': '87600h'
        })

    # Need the 'root' role to sign PMK CSRs.
    create_root_role_response = client.secrets.pki.create_or_update_role(
        'root',
        {
            'allow_any_name': 'true'
        },
        mount_point=vault_path
    )

    # Create a policy for later use with this cluster's hosts.
    # TODO: Somehow push this policy to configuration for hosts to use later.
    policy = \
'''
path "%s/*" {
    capabilities = ["create", "read", "list"]
}
''' % vault_path

    return ca_response


def read_root_ca(cluster_id='1199'):
    '''
    Get the CA certificate for the cluster UUID specified.
    Returned as a string in '-----BEGIN ... -----END CERTIFICATE-----' format.
    '''
    return get_client(True).secrets.pki.read_ca_certificate(
        mount_point='pmk-ca-' + str(cluster_id))


def sign_csr(role, csr_path, cluster_id='1199'):
    '''
    Signs a CSR, given the path to its file.
    Cluster UUID must also be specified.
    '''
    with open(csr_path, 'r') as csr:
        csr_contents = csr.read()
    signed_certificate = get_client(True).secrets.pki.sign_certificate(
        name=role,
        csr=csr_contents,
        common_name='',
        mount_point='pmk-ca-' + str(cluster_id)
    ).json()['data']['certificate']
    print(signed_certificate)

if __name__ == '__main__':
    Fire() # Expose the functions to the command line. For sign_csr and read_root_ca only.
