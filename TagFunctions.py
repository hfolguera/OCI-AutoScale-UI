import oci
from flask import flash, Response

def tagResource(config, PredefinedTag, OCID, ScheduleTags):
            # Execute the resource tagging

            # Lookup resource type
            search_client = oci.resource_search.ResourceSearchClient(config)
            searchDetails = oci.resource_search.models.StructuredSearchDetails()
            searchDetails.query = "query all resources where identifier = '"+OCID+"'"
            
            response = search_client.search_resources(searchDetails)

            if len(response.data.items) > 0:
                # Resource found

                # Get existing defined_tags to avoid removing them
                new_defined_tags = response.data.items[0].defined_tags
                # Add/Update new Schedule tag
                new_defined_tags.update({PredefinedTag: ScheduleTags})

                # Tag the OCI resource
                resource_type = response.data.items[0].resource_type
                if resource_type == "Instance":
                        # Tagging Instance resource
                        changedetails = oci.core.models.UpdateInstanceDetails()
                        changedetails.defined_tags = new_defined_tags

                        compute = oci.core.ComputeClient(config)
                        response = compute.update_instance(instance_id=OCID, update_instance_details=changedetails)

                        return response                        
                        # if response.status == 200:
                        #     flash('Resource '+OCID+' set successfully!', 'success')
                        # else:
                        #     flash('Error adding the resource '+OCID+'!', 'danger')
                        #     return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action=Action)
                        
                # elif resource_type == "DbSystem":
                #     # TODO

                # elif resource_type == "VmCluster":
                #     # TODO

                # elif resource_type == "AutonomousDatabase":
                #     # TODO

                # elif resource_type == "InstancePool":
                #     # TODO

                else:
                    # Resource type not supported!
                    flash('Resource type '+resource_type+' not supported!', 'danger')
                    # return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action=Action)
                    # TODO: Return a failed response. How?
                    return Response(status=500)
            else:
                flash('Resource '+OCID+' not found!', 'danger')
                return Response(status=500)