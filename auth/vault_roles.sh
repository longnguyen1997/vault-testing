#!/usr/bin/env bash

# Runs on the entity hosting the Vault server.

# If there's no Vault to talk to, exit gracefully.
if [[ -z $VAULT_ADDR ]]; then
	echo -e "Provide a Vault server to talk to, \$VAULT_ADDR."
	exit 1
fi

unset VAULT_ROLES
declare -a VAULT_ROLES

# These Vault roles are directly used in certificate management
# for the various PMK components as part of pf9-kube.
function populate_vault_roles() {
	VAULT_ROLES+="etcdctl-client"
	VAULT_ROLES+="etcd-server"
	VAULT_ROLES+="flannel-client"
	VAULT_ROLES+="apiserver-server"
	VAULT_ROLES+="apiserver-client"
	VAULT_ROLES+="kubelet-client"
	VAULT_ROLES+="kubelet-server"
	VAULT_ROLES+="kube-proxy-client"
	VAULT_ROLES+="admin-client" # O (org): "system:masters"
	VAULT_ROLES+="admin-server"
	VAULT_ROLES+="dashboard-server"
	VAULT_ROLES+="calico-client"
	VAULT_ROLES+="aggregator-client"
}

populate_vault_roles

# Must provide the cluster PKI engine path!
function create_vault_roles() {

	cluster_vault_pki_path=$1

    # Parse based on cert type (client or server).
	for role in "$VAULT_ROLES[@]"; do
		if [[ $role = *-server ]]; then
            vault write $cluster_vault_pki_path/roles/$role \
				allow_any_name=true server_flag=true client_flag=false
        else
            vault write $cluster_vault_pki_path/roles/$role \
                allow_any_name=true server_flag=false client_flag=true
        fi
	done

	# Last edge case: admin-client must have org. "system:masters" for K8S.
	vault write $cluster_vault_pki_path/roles/admin-client \
					allow_any_name=true \
					organization=system:masters
}
