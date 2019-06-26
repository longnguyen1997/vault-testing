import hvac
from generate_csr import *


CLIENT_CERTS = {}
SERVER_CERTS = {}


# The client cert etcdctl uses to talk to etcd.
CLIENT_CERTS["etcdctl/etcd"]="--cn=etcdctl --cert_type=client"
# The client cert flannel uses to talk to etcd.
CLIENT_CERTS["flannel/etcd"]="--cn=flannel --cert_type=client"
# The client cert kube-apiserver uses to talk to etcd.
CLIENT_CERTS["apiserver/etcd"]="--cn=apiserver --cert_type=client"
# The client cert kube-apiserver uses to talk to etcd.
CLIENT_CERTS["kubelet/apiserver"]="--cn=kubelet --cert_type=client"
# The client cert kube-proxy uses to talk to kube-apiserver.
CLIENT_CERTS["kube-proxy/apiserver"]="--cn=kube-proxy --cert_type=client"
# The client cert the admin user uses to talk to kube-apiserver.
CLIENT_CERTS["admin"]="--cn=admin --cert_type=client --org=system:masters"
# The client cert calico uses to talk to kube-apiserver.
CLIENT_CERTS["calico/etcd"]="--cn=calico --cert_type=client"
# The client cert the kube api aggregator uses to talk to kube-apiserver.
CLIENT_CERTS["aggregator"]="--cn=aggregator --cert_type=client"


# The server cert etcd presents to clients.
SERVER_CERTS["etcd/client"]="--cn=etcd --cert_type=server --sans=${trimmed_etcd_sans} "
# The server cert that etcd presents to peers.
SERVER_CERTS["etcd/peer"]="--cn=etcd --cert_type=server --sans=${trimmed_etcd_sans} "
# The server cert kube-apiserver presents to clients.
SERVER_CERTS["apiserver"]="--cn=apiserver --cert_type=server --sans=${trimmed_apiserver_sans} --needs_svcacctkey=true "
# The server cert kubelet presents to kube-apiserver (not used currently).
SERVER_CERTS["kubelet/server"]="--cn=kubelet --cert_type=server --sans=${trimmed_kubelet_sans} "
# The server cert the authn webhook presents to kube-apiserver.
SERVER_CERTS["authn_webhook"]="--cn=admin --cert_type=server --sans=${trimmed_auth_webhook}"
# The server cert the kubernetes dashboard presents to users.
SERVER_CERTS["dashboard"]="--cn=dashboard  --cert_type=server --sans=${trimmed_dashboard_sans}"

print(CLIENT_CERTS)
print(SERVER_CERTS)