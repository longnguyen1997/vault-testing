mkdir -p .certs

export CERTIFICATE_ENDPOINT="localhost"
export ISSUED_CERT_LOC=".certs/issued-cert.json"

# STEP 1: ENABLE PKI ENGINE AND GENERATE ROOT CERT.
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki # 10yrs of root CA lifetime -> root CA might be P9's
# See vault path-help pki for available API commands.
vault write -field=certificate pki/root/generate/internal \
        common_name="Platform9" \
        ttl=87600h > .certs/CA_cert.crt
vault write pki/config/urls \
	# Replace the issuing points w/ relevant Platform9 endpoints. \
        issuing_certificates="${CERTIFICATE_ENDPOINT}:8200/v1/pki/ca" \
        crl_distribution_points="${CERTIFICATE_ENDPOINT}:8200/v1/pki/crl"

# STEP 2: ENABLE PKI ENGINE AT INTERMEDIATE ENDPOINT AND GENERATE INT. CERT.
vault secrets enable -path=pki-int pki
vault secrets tune -max-lease-ttl=43800h pki-int
vault write -format=json pki-int/intermediate/generate/internal \
        common_name="Platform9 Intermediate Authority" ttl="43800h" \
        | jq -r '.data.csr' > .certs/pki_intermediate.csr # CSR gets saved. Need to sign it.
# Signing the CSR and putting it back into vault to represent the intermediary now.
vault write -format=json pki/root/sign-intermediate csr=@.certs/pki_intermediate.csr \
        format=pem_bundle ttl="43800h" \
        | jq -r '.data.certificate' > .certs/intermediate.cert.pem
# Still unsure of why @ notation is needed.
vault write pki-int/intermediate/set-signed certificate=@.certs/intermediate.cert.pem

# STEP 3: CREATE ROLES (ACCESS CONTROL).
# Of particular importance are allowed_domains, allow_subdomains, allow_glob_domains.
# To see all, do vault read pki-int/roles/platform9 after making the example.
vault write pki-int/roles/platform9 \
        allowed_domains="platform9.com" \
        allow_subdomains=true \
        max_ttl="720h"

# STEP 4: REQUEST CERTS.
vault write pki-int/issue/platform9 common_name="docs.platform9.com" ttl="24h" -format=json > $ISSUED_CERT_LOC
# Below command gives the keys you can query.
jq -r keys $ISSUED_CERT_LOC
# Distribute certificate, ca_chain, issuing_ca, private_key, and serial_number.

# STEP 5: REVOKE.
vault write pki-int/revoke serial_number=`jq -r .data.serial_number $ISSUED_CERT_LOC` # SN obtained from Step 4.

# STEP 6: GARBAGE COLLECTION.
vault write pki-int/tidy tidy_cert_store=true tidy_revoked_certs=true