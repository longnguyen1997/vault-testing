import hvac
import os
import subprocess


def get_secrets_engines_paths(client):
    """
    Taken from hvac documentation website.
    Lists all secrets engine paths currently enabled.
    """
    secrets_engines_list = client.sys.list_mounted_secrets_engines()[
        'data'].keys()
    return secrets_engines_list


def enable_new_pki_secrets_engine(client, engine_path, description=None):
    """
    client (hvac.Client): HVAC client. Must be authenticated.
    engine_path (str): Desired endpoint for the new PKI secrets engine.
    """
    client.sys.enable_secrets_engine(
        backend_type='pki', path=engine_path, description=description)


def disable_secrets_engine(client, engine_path):
    """
    Uses client to disable the secrets engine at engine_path.
    """
    client.sys.disable_secrets_engine(path=engine_path)
