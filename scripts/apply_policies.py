import os
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api
from intentionet.bfe.proto import policies_api_pb2 as policies_api
import const
from send_to_slack import sendToSlack

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ['BFE_SSL_CERT'] = SCRIPT_DIR+'/../cert/test.crt'

bf = Session(host=const.BFE_HOST, port=const.BFE_PORT)
if bf:
    print()
    print("***********************************************")
    print("Created BFE session on host {}".format(const.BFE_HOST))
    print("***********************************************")
    print()

REF_SNAPSHOT = ''
NEW_SNAPSHOT = ''
bf.set_network(const.NETWORK_NAME)
print()
print("***********************************************")
print("Network is set as {}".format(const.NETWORK_NAME))
print("***********************************************")
print()

snapshots = bf.list_snapshots()
if len(snapshots) == 2:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
        else: NEW_SNAPSHOT = snapshot
else:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
            break
    NEW_SNAPSHOT = snapshots[0]



def policy_status_to_string(status):
    if status == policies_api.POLICY_STATUS_UNKNOWN:
        return "UNKNOWN"
    elif status == policies_api.POLICY_STATUS_FAIL:
        return "FAIL"
    elif status == policies_api.POLICY_STATUS_PASS:
        return "PASS"
    elif status == policies_api.POLICY_STATUS_PASS_WARN:
        return "WARN"
    else:
        raise RuntimeError("Unknown policy status {}".format(status))

#def get_policy_results(bf: Session, snapshot: str):
def get_policy_results(bf: Session):
    """
    Get policy evaluation results for a snapshot.
    
    Returns a map from policy title to status
    """
    response = bf._api_gw.ListPolicyResultsMetadata(
        api.ListPolicyResultsMetadataRequest(
            network_name=bf.network, snapshot_name=bf.snapshot
            #network_name=bf.network, snapshot_name=snapshot
        )
    )
    status = {}
    for result in response.metadata:
        policy_response = bf._api_gw.GetPolicy(
            api.GetPolicyRequest(
                network_name=bf.network, policy_id=result.policy_id
            )
        )
        status[policy_response.policy.input.title] = policy_status_to_string(result.status)
    print(result)
    return status

print()
print("***********************************************")
print("Snapshot against which policies are checked: ", NEW_SNAPSHOT)
print("***********************************************")
print()

bf.set_snapshot(NEW_SNAPSHOT)
#print(bf.snapshot)
status = get_policy_results(bf)
print(status)
print(type(status))

msg = f"Summary of policy results for the snapshot \'{NEW_SNAPSHOT}\' is shown below.\n\n"
for k, v in status.items():
    msg = msg + (k + " : " + str(v)) + "\n"

msg = msg + "\nPlease refer the below URL for further details:\n\n"
policy_url = f'https://{const.BFE_HOST}/dashboard/{const.NETWORK_NAME}/{NEW_SNAPSHOT}/policies/'
msg = msg + policy_url
print(msg)
sendToSlack(const.SLACK_CHANNEL,msg)
