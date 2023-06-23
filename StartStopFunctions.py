import oci
from flask import Response

def startInstance(config, signer, OCID):
    compute = oci.core.ComputeClient(config=config, signer=signer)

    resourceDetails = compute.get_instance(instance_id=OCID).data

    if resourceDetails.lifecycle_state != "RUNNING":
        try:
            response = compute.instance_action(instance_id=OCID, action="START")
            return response
        except oci.exceptions.ServiceError as response:
            return oci.response.Response(status=500, headers=None, data=None, request=None)
    else:
        return oci.response.Response(status=200, headers=None, data=None, request=None)

def stopInstance(config, signer, OCID):
    compute = oci.core.ComputeClient(config=config, signer=signer)

    resourceDetails = compute.get_instance(instance_id=OCID).data

    if resourceDetails.lifecycle_state != "STOPPED":
        try:
            response = compute.instance_action(instance_id=OCID, action=ComputeShutdownMethod)
            return response
        except oci.exceptions.ServiceError as response:
            return oci.response.Response(status=500, headers=None, data=None, request=None)
    else:
        return oci.response.Response(status=200, headers=None, data=None, request=None)

def startAutonomousDatabase(config, signer, OCID):
    database = oci.database.DatabaseClient(config, signer=signer)

    resourceDetails = database.get_autonomous_database(autonomous_database_id=OCID).data

    if resourceDetails.lifecycle_state != "AVAILABLE":
        try:
            response = database.start_autonomous_database(autonomous_database_id=OCID)
            return response
        except oci.exceptions.ServiceError as response:
            return oci.response.Response(status=500, headers=None, data=None, request=None)
    else:
        return oci.response.Response(status=200, headers=None, data=None, request=None)

def stopAutonomousDatabase(config, signer, OCID):
    database = oci.database.DatabaseClient(config, signer=signer)

    resourceDetails = database.get_autonomous_database(autonomous_database_id=OCID).data

    if resourceDetails.lifecycle_state != "STOPPED":
        try:
            response = database.stop_autonomous_database(autonomous_database_id=OCID)
            return response
        except oci.exceptions.ServiceError as response:
            return oci.response.Response(status=500, headers=None, data=None, request=None)
    else:
        return oci.response.Response(status=200, headers=None, data=None, request=None)