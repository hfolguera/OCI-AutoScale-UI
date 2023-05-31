import oci
import time
import argparse
import json
from flask import Flask, request, render_template, url_for, flash, redirect, Response
from prometheus_flask_exporter import PrometheusMetrics

# Global variables
ScheduleKeys = ['AnyDay', 'WeekDay', 'WeekEnd', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Load OCI-Cli configuration from $HOME/.oci
config = oci.config.from_file()
oci.config.validate_config(config)

def getResources(page=None, per_page='5'):
    # Initialize variables
    limit = '9999'
    if per_page == 'All':
        per_page = limit

    # Get all resources with Autoscale tags
    search_client = oci.resource_search.ResourceSearchClient(config)
    searchDetails = oci.resource_search.models.StructuredSearchDetails()
    searchDetails.query = "query all resources where (definedTags.namespace = '"+PredefinedTag+"')"

    if page == None:
        response = oci.pagination.list_call_get_up_to_limit(search_client.search_resources,int(per_page),int(limit),searchDetails)
    else:
        response = oci.pagination.list_call_get_up_to_limit(search_client.search_resources,int(per_page),int(limit),searchDetails, page=page)

    return response

app = Flask(__name__)
app.config.from_pyfile('config.py')

metrics = PrometheusMetrics(app)

strStartTime = time.strftime("%m/%d/%Y, %H:%M:%S")
startTime = time.time()

PredefinedTag = app.config["PREDEFINED_TAG"]
AllowStartStopResources = app.config["ALLOW_START_STOP_RESOURCES"]

@app.route('/', methods=('GET', 'POST'))
def index():
    resources = None
    page = None
    per_page = '5'
    next_page_token = None
    previous_page_token = None

    if request.method == 'GET':
        # Get Method: Homepage has been called
        # Call OCI to search resources
        resources = getResources()

    else:
        # POST Method: Pagination has been used
        if 'page' in request.form:
            page = request.form['page']
        per_page = request.form['per_page']

        # Call OCI to search resources
        resources = getResources(page=page, per_page=per_page)

    if 'opc-next-page' in resources.headers:
        next_page_token = resources.headers['opc-next-page']

    if 'opc-previous-page' in resources.headers:
        previous_page_token = resources.headers['opc-previous-page']

    return render_template('index.html', resources=resources.data, PredefinedTag=PredefinedTag, next_page_token=next_page_token, per_page=per_page, previous_page_token=previous_page_token)

@app.route('/setResource', methods=('GET', 'POST'))
def setResource():
    if request.method == 'POST':
        # Get form parameters
        OCID = request.form['OCID']
        if 'ScheduleTags' in request.form:
            ScheduleTags = request.form['ScheduleTags']
            ScheduleTags = ScheduleTags.replace("\'", "\"")
            ScheduleTags = json.loads(ScheduleTags)
        else:
            # Build ScheduleTags dict from multiple form fields
            ScheduleTags = {}
            for key in request.form:
                if key.startswith('ScheduleKey'):
                    print(key[12:]+' Yes!')
                    id = key[12:]
                    ScheduleTags[request.form[key]] = request.form['Schedule-'+id]

        Action = request.form['Action']

        if Action == 'Update':
            # Redirect to setResource.html passing arguments from index.html update icon
            return render_template('setResource.html', ScheduleKeys=ScheduleKeys, OCID=OCID, ScheduleTags=ScheduleTags, Action=Action)
        
        else:
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
                        
                        if response.status == 200:
                            flash('Resource '+OCID+' set successfully!', 'success')
                        else:
                            flash('Error adding the resource '+OCID+'!', 'danger')
                            return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action=Action)
                        
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
                    return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action=Action)
            else:
                flash('Resource '+OCID+' not found!', 'danger')
                return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action=Action)

            return redirect(url_for('index'))

    return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action="Add")

@app.route('/startResource', methods=('GET', 'POST'))
def startResource():
    if AllowStartStopResources != True:
        flash('START operation is not allowed!!', 'danger')
        return redirect(url_for('index'))

@app.route('/stopResource', methods=('GET', 'POST'))
def stopResource():
    if AllowStartStopResources != True:
        flash('STOP operation is not allowed!!', 'danger')
        return redirect(url_for('index'))

@app.route('/exportJSON')
def exportJSON():
    resources = getResources()

    items = []
    for item in resources.data:
        row = {}
        row['display_name'] = item.display_name
        row['identifier'] = item.identifier
        row['compartment_id'] = item.compartment_id
        row['defined_tags'] = item.defined_tags
        row['lifecycle_state'] = item.lifecycle_state
        items.append(row)
    
    data = {}
    data['items'] = items

    json_data = json.dumps(data, indent=4)

    return Response(json_data, mimetype='application/json', headers={'Content-Disposition':'attachment;filename=AutoScale_Config.json'})

@app.route('/exportCSV')
def exportCSV():
    resources = getResources()

    csv_data = "display_name; identifier; compartment_id; defined_tags; lifecycle_state\n"
    for item in resources.data:
        csv_data = csv_data + item.display_name+"; "+item.identifier+"; "+item.compartment_id+"; "+str(item.defined_tags)+"; "+item.lifecycle_state+";\n"

    return Response(csv_data, mimetype='application/csv', headers={'Content-Disposition':'attachment;filename=AutoScale_Config.csv'})

@app.route('/log')
def Log():
    return render_template('log.html')

@app.route('/getLog')
def getLog():
    def generate():
        # TODO: Point to OCI-AutoScale log file
        with open('test.log') as f:
            while True:
                yield f.read()
                time.sleep(1)

    return app.response_class(generate(), mimetype='text/plain')

@app.route('/health')
def health():
    content = {}

    # Validate OCI connectivity
    try:
        res = getResources(per_page=1)
        
        content['status']='OK'
        content['status_code']='200'
        content['error_msg']=''
    except Exception as e:
        content['status']='KO'
        content['status_code']='500'
        content['error_msg']=str(e)
    
    # Add application time
    content['start_time'] = strStartTime
    uptime = time.time() - startTime
    content['uptime_hours'] = str(uptime/3600)

    json_data = json.dumps(content, indent=2)
    return Response(json_data, mimetype='application/json')
