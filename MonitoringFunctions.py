import oci
import datetime
import json
import pandas as pd

def getStatusMetrics(config, signer, OCID, ResourceType, CompartmentId, ScheduleTags, TimeRange):
    # Select metric namespace and metric name by Resource Type
    if ResourceType == "Instance":
        metric_namespace = "oci_compute_infrastructure_health"
        metric_name = "instance_status"

    elif ResourceType == "DbSystem":
        metric_namespace = "oci_database_cluster"
        metric_name = "NodeStatus"

    elif ResourceType == "AutonomousDatabase":
        metric_namespace = "oci_autonomous_database"
        metric_name = "DatabaseAvailability"

    else:
        # ResourceType not implemented!
        return None

    ## Get current date
    now = datetime.datetime.now(datetime.timezone.utc)
    now = now.replace(minute=0, second=0, microsecond=0)
    start_time = now - datetime.timedelta(days=TimeRange)
    end_time = now

    ## Request OCI API Monitoring Datapoints
    metric_client = oci.monitoring.MonitoringClient(config=config, signer=signer)

    metric_detail = oci.monitoring.models.SummarizeMetricsDataDetails()

    metric_detail.query = metric_name+'[1h]{resourceId = "'+OCID+'"}.mean()'
    metric_detail.start_time = start_time.isoformat()
    metric_detail.end_time = end_time.isoformat()
    metric_detail.namespace = metric_namespace

    response = metric_client.summarize_metrics_data(compartment_id = CompartmentId, summarize_metrics_data_details=metric_detail)
    metric_data = response.data[0].aggregated_datapoints

    labels = []
    status_data = []
    schedule_data = []
    ## Build Dataframe
    for day in range(TimeRange):
        position = 0
        for hour in range(24):
            now_iso = start_time + datetime.timedelta(days=day, hours=hour)

            # Add label (X-Axis)
            labels.append(now_iso.isoformat())
            
            # Add resource status value (Y-Axis)
            ## TODO: Improve timestamp search
            found = 0
            for item in metric_data:
                if item.timestamp == now_iso:
                    status_data.append(1)
                    found = 1
                    break
                
            if found == 0:
                # For instance_status metric, when instance is stopped no value is found
                status_data.append(0)

            # Add resource schedule value (Y-Axis)
            ## Schedule values are added by priority: Day of month > Day of week > WeekDay or WeekEnd > AnyDay
            if now_iso.day in ScheduleTags:
                schedule_data.append(ScheduleTags[now_iso.day][position])
            elif now_iso.strftime('%A') in ScheduleTags:
                schedule_data.append(ScheduleTags[now_iso.strftime('%A')][position])
            elif 'WeekDay' in ScheduleTags and now_iso.weeday() < 5:
                schedule_data.append(ScheduleTags['WeekDay'][position])
            elif 'WeekEnd' in ScheduleTags and now_iso.weekday() > 4:
                schedule_data.append(ScheduleTags['WeekEnd'][position])
            elif 'AnyDay' in ScheduleTags:
                schedule_data.append(ScheduleTags['AnyDay'][position])
            else:
                schedule_data.append('*')
                 
            position += 2

    monitoring_data = {"labels": labels, "status_data": status_data, "schedule_data": schedule_data}
    
    return monitoring_data