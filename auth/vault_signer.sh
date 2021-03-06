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
	        -description="Vault CA engine for cluster $cluster_id" \
            -path=$cluster_pki_path pki
    else
        return 1
    fi
	vault secrets tune -max-lease-ttl=87600h $cluster_pki_path
	vault write \
		$cluster_pki_path/root/generate/internal \
        common_name=kubernetes-ca@`date +%s` \
        ttl=43800h > /dev/null # 5 years of CA lifetime.
    echo "Successfully generated Vault PKI engine at path '$cluster_pki_path'."
}


function sign_csr() {

	local vault_role=$1
	local csr_filepath=$2
	local certs_dir=$3

	# Vault tokens must be in place to contact the remote
	# Vault server running on the DU.
	# `vault write` will refer to $VAULT_ADDR for the remote.
	vault write pmk-ca-$CLUSTER_ID/sign/$vault_role \
		csr=@$csr_filepath -format=json \
		> $certs_dir/request.json

	cat $certs_dir/request.json | jq -r .data.certificate > $certs_dir/request.crt
	cat $certs_dir/request.json | jq -r .data.issuing_ca > $certs_dir/ca.crt

}
