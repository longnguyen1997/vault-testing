from os import system
from vault import *

try:
	c = get_client()
except:
	exit()

mock_root_ca(c)
mock_cluster_init(c, 'long-testbed')
generate_and_sign_intermediate(c, 'long-testbed')

# By this point, the cluster 'long-testbed' is ready to issue certs to hosts.