import os
from intentionet.bfe.proto.datamodel.device_pb2 import ConfigStructure
from pybfe.client.session import Session
import my_policies, const

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ['BFE_SSL_CERT'] = SCRIPT_DIR+'/../cert/test.crt'

bf = Session(host=const.BFE_HOST, port=const.BFE_PORT)
bf.set_network(const.NETWORK_NAME)

def create_policies(bf: Session):
    bf._experimental_create_policy(my_policies.devices_have_routes)
    bf._experimental_create_policy(my_policies.filter_behavior_denied)
    bf._experimental_create_policy(my_policies.filter_behavior_allowed)

create_policies(bf)
print(const.INIT_SNAPSHOT_DIR)
bf.init_snapshot(const.INIT_SNAPSHOT_DIR, name=const.INIT_SNAPSHOT_NAME, overwrite=True)