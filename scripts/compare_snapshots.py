import os, json
from typing import Dict
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api
import const
import os
import logging
from send_to_slack import sendToSlack

logging.basicConfig(level=logging.ERROR)

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

def snapshots_to_compare():
    snapshots = bf.list_snapshots()
    #case when tere are just 2 snapshots, where reference snapshot is called baseline and is manually uploaded
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
    return REF_SNAPSHOT, NEW_SNAPSHOT

REF_SNAPSHOT, NEW_SNAPSHOT = snapshots_to_compare()

print()
print("***********************************************")
print("Snapshots being compared are {}, {}".format(NEW_SNAPSHOT, REF_SNAPSHOT))
print("***********************************************")
print()

def get_compare_metadata_results(bf: Session, snapshot_name: str, reference_snapshot_name: str):
    """
    Gets snapshot comparison results.
    Returns a map from comparison type to either a count of changes or whether that type has changed.
    """
    resp = bf._api_gw.GetSnapshotComparisonMetadata(
        api.GetSnapshotComparisonMetadataRequest(
            network_name=bf.network,
            snapshot_name=snapshot_name,
            reference_snapshot_name=reference_snapshot_name
        )
    )
    return resp

def init_snapshot_comparison(bf: Session, snapshot_name: str, reference_snapshot_name: str):

    init_resp = bf._api_gw.InitSnapshotComparison(
        api.InitSnapshotComparisonRequest(
            network_name=bf.network,
            snapshot_name=snapshot_name,
            reference_snapshot_name=reference_snapshot_name
        )
    )

def get_result_from_response(resp):

    result = {}
    
    # pick some categories to embed in the result 
    result["device_configuration"] = resp.configurations.num_results
    result["devices"] = resp.devices.num_results
    result["interfaces"] = resp.interfaces.num_results
    result["increased_flows"] = resp.reachability.has_increased_flows
    result["decreased_flows"] = resp.reachability.has_decreased_flows
    result["devices_routing"] = resp.routes.num_results
    result["bgp_peer_attributes"] = resp.rp_bgp_peer_attributes.num_results
    result["bgp_process_attributes"] = resp.rp_bgp_process_attributes.num_results
    result["ospf_interface"] = resp.rp_ospf_interface.num_results
    result["ospf_neighbors"] = resp.rp_ospf_neighbors.num_results
    result["ospf_process"] = resp.rp_ospf_process.num_results

    result = json.dumps(result, indent=4)
    return result


print("REF_SNAPSHOT: ", REF_SNAPSHOT)
print("NEW_SNAPSHOT: ", NEW_SNAPSHOT)

def process_and_post_msg(comparison_result: Dict) -> str:
    result = json.loads(comparison_result)
    keys = result.keys()
    msg = "Summary of changes between the snapshots \'{}\' and \'{}\' are shown below:\n\n".format(NEW_SNAPSHOT, REF_SNAPSHOT)
    for k, v in result.items():
        msg = msg + (k + " : " + str(v)) + "\n"
    #print(msg)
    msg = msg + "\nPlease refer the below URL for further details:\n\n"
    dashboard_url = f"https://{const.BFE_HOST}/dashboard/{const.NETWORK_NAME}/{NEW_SNAPSHOT}/compare/{REF_SNAPSHOT}/configurations"
    msg = msg + dashboard_url
    return msg

def compare_snapshots(snapshot_name: str, reference_snapshot_name: str) -> Dict:

    if snapshot_name == reference_snapshot_name:
        msg = "Nothing to compare as both snapshots are the same."
        print(msg)
        sendToSlack(const.SLACK_CHANNEL,msg)
    else:
        response = get_compare_metadata_results(bf, snapshot_name, reference_snapshot_name)
        #print(response)
        comparison_result = {}
        if response.uninitialized:
            init_snapshot_comparison(bf, snapshot_name, reference_snapshot_name)
            response = get_compare_metadata_results(bf, snapshot_name, reference_snapshot_name)
            #print(response)
            while (response.aws_security_groups.status != 2):
                response = get_compare_metadata_results(bf, snapshot_name, reference_snapshot_name)
                #print(response)
            else: 
                comparison_result = get_result_from_response(response)
        else:
            comparison_result = get_result_from_response(response)

        #print(type(comparison_result))
        msg = process_and_post_msg(comparison_result) 
        print(msg)
        sendToSlack(const.SLACK_CHANNEL,msg)

compare_snapshots(NEW_SNAPSHOT, REF_SNAPSHOT)