#!/usr/bin/env bash

# Runs on the entity hosting the Vault server.

# If there's no Vault to talk to, exit gracefully.
if [[ -z $VAULT_ADDR ]]; then
	echo -e "Provide a Vault server to talk to, \$VAULT_ADDR."
	exit 1
fi

source vault_roles.sh

if [[ -z $CLUSTER_PATH ]]; then echo "Please set \$CLUSTER_PATH for this cluster's Vault PKI engine.";
else create_vault_roles $CLUSTER_PATH; fi
