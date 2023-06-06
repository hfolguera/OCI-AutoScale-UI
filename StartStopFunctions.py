import oci
from flask import Response

def startInstance(config, OCID):
    compute = oci.core.ComputeClient(config)

    resourceDetails = compute.get_instance(instance_id=OCID).data

    if resourceDetails.lifecycle_state != "RUNNING":
        try:
            response = compute.instance_action(instance_id=OCID, action="START")
            return response
        except oci.exceptions.ServiceError as response:
            return Response(status=500)
    else:
        return Response(status=200)

def stopInstance(config, OCID):
    compute = oci.core.ComputeClient(config)

    resourceDetails = compute.get_instance(instance_id=OCID).data

    if resourceDetails.lifecycle_state != "STOPPED":
        try:
            response = compute.instance_action(instance_id=OCID, action=ComputeShutdownMethod)
            return response
        except oci.exceptions.ServiceError as response:
            return Response(status=500)
    else:
        return Response(status=200)