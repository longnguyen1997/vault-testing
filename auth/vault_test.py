from os import system
from vault import *

try:
	c = get_client()
except:
	exit()

mock_root_ca(c)
mock_cluster_init(c, 'long-du')
generate_and_sign_intermediate(c, 'long-du')

# By this point, the cluster 'long-du' is ready to issue certs to hosts.