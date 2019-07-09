#!/usr/bin/env bash

if [[ -z $VAULT_ADDR ]]; then
	echo "WARNING: You do not have a Vault address configured!"
fi


function generate_root_ca() {
	local cluster_id=$CLUSTER_ID
	local cluster_pki_path=pmk-ca-$cluster_id
	# If the PKI engine hasn't already been made, do so.
	if ! vault secrets list | grep -q $cluster_pki_path; then
		vault secrets enable \
			-path=$cluster_pki_path pki \
			-description="Vault CA engine for cluster $cluster_id"
	fi
	# 10 years of CA lifetime.
	vault secrets tune -max-lease-ttl=87600h $cluster_pki_path
	vault write \
		$cluster_pki_path/root/generate/internal \
        common_name=kubernetes-ca@`date +%s`
}


function sign_csr() {
	
	local vault_role=$1
	local csr_filepath=$2
	local certs_dir=$3
	
	# Vault tokens must be in place to contact the remote
	# Vault server running on the DU.
	# `vault write` will refer to $VAULT_ADDR for the remote.
	vault write pmk-$cluster_id/sign/$vault_role \
		csr=@$csr_filepath -format=json \
		> $certs_dir/request.json

	cat $certs_dir/request.json | jq -r .data.certificate > $certs_dir/request.crt
	cat $certs_dir/request.json | jq -r .data.issuing_ca > $certs_dir/ca.crt

}