#!/usr/bin/env bash

# Runs on the entity hosting the Vault server.

# If there's no Vault to talk to, exit gracefully.
if [[ -z ${VAULT_ADDR} ]]; then
	echo -e "Provide a Vault server to talk to, \$VAULT_ADDR."
fi


# These Vault roles are directly used in certificate management
# for the various PMK components as part of pf9-kube.
unset VAULT_ROLES
VAULT_ROLES=( "etcdctl-client" "etcd-server" "flannel-client" \
    "apiserver-server" "apiserver-client" "kubelet-client" \
    "kubelet-server" "kube-proxy-client" "admin-client" \
    "admin-server" "dashboard-server" "calico-client" \
    "aggregator-client" )


# Must provide the cluster PKI engine path!
function create_vault_roles() {

	cluster_vault_pki_path=$1

    # Parse based on cert type (client or server).
	for role in ${VAULT_ROLES[@]}; do
		if [[ ${role} = *-server ]]; then
            vault write ${cluster_vault_pki_path}/roles/${role} \
				allow_any_name=true server_flag=true client_flag=false
        else
            vault write ${cluster_vault_pki_path}/roles/${role} \
                allow_any_name=true server_flag=false client_flag=true
        fi
	done

	# Last edge case: admin-client must have O: "system:masters" for K8S.
	vault write ${cluster_vault_pki_path}/roles/admin-client \
					allow_any_name=true \
					organization=system:masters
}
