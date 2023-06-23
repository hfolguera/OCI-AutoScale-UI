import oci
import datetime
import json
import pandas as pd

def getInstanceStatusMetrics(config, signer, OCID, CompartmentId, ScheduleTags):
    # Select metric namespace and metric name for Instance
    metric_namespace = "oci_compute_infrastructure_health"
    metric_name = "instance_status"

    ## Get current date
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now.replace(minute=0, second=0, microsecond=0)
    start_time = now - datetime.timedelta(days=7)
    end_time = now

    ## Request OCI API Monitoring Datapoints
    metric_client = oci.monitoring.MonitoringClient(config=config, signer=signer)

    metric_detail = oci.monitoring.models.SummarizeMetricsDataDetails()

    metric_detail.query = metric_name+'[1h]{resourceId = "'+OCID+'"}.mean()'
    metric_detail.start_time = start_time.isoformat()
    metric_detail.end_time = end_time.isoformat()
    #metric_detail.resolution = "1h"
    metric_detail.namespace = metric_namespace

    response = metric_client.summarize_metrics_data(compartment_id = CompartmentId, summarize_metrics_data_details=metric_detail)
    metric_data = response.data[0].aggregated_datapoints

    labels = []
    status_data = []
    schedule_data = []
    ## Build Dataframe
    for day in range(7):
        position = 0
        for hour in range(24):
            now_iso = now - datetime.timedelta(days=day, hours=hour)
            labels.append(now_iso.isoformat())
            
            # TODO: Improve timestamp search
            found = 0
            for item in metric_data:
                if item.timestamp == now_iso:
                    if item.value == 0:
                        # For instance_status metric, transform 0 values to 1
                        status_data.append(1)
                        found = 1
                        break
                
            if found == 0:
                # For instance_status metric, when instance is stopped no value is found
                status_data.append(0)

            schedule_data.append(ScheduleTags['AnyDay'][position])
            position += 2

    monitoring_data = {"labels": labels, "status_data": status_data, "schedule_data": schedule_data}
    
    return monitoring_data