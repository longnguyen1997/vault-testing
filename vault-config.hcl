ui=true

backend "consul" {
  path="vault-test"
}

listener "tcp" {
  tls_disable = 1 
  address="127.0.0.1:8200"
}

disable_mlock = true
