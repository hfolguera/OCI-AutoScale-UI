import oci
import time
import argparse
import json
import requests
import pandas as pd
from flask import Flask, request, render_template, url_for, flash, redirect, Response
from prometheus_flask_exporter import PrometheusMetrics
import StartStopFunctions
import TagFunctions
import MonitoringFunctions

# Global variables
ScheduleKeys = ['AnyDay', 'WeekDay', 'WeekEnd', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

app = Flask(__name__)
app.config.from_pyfile('config.py')

metrics = PrometheusMetrics(app)

strStartTime = time.strftime("%m/%d/%Y, %H:%M:%S")
startTime = time.time()

# Load configuration variables from config.py
PredefinedTag = app.config["PREDEFINED_TAG"]
AllowStartStopResources = app.config["ALLOW_START_STOP_RESOURCES"]

RestUrl = app.config["REST_URL"]

UseInstancePrincipal = app.config["USE_INSTANCE_PRINCIPAL"]

# Load OCI-Cli configuration
if UseInstancePrincipal:
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    config = {'region': signer.region, 'tenancy': signer.tenancy_id}
else:
    config = oci.config.from_file()
    oci.config.validate_config(config)
    
    signer = oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config.get("key_file"),
        pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
        private_key_content=config.get("key_content")
    )

# Global functions
def getResources(page=None, per_page='10', DisplayNameFilter="", ResouceTypeFilter="", CompartmentFilter="", StatusFilter=""):
    # Initialize variables
    limit = '9999'
    if per_page == 'All':
        per_page = limit

    # Get all resources with Autoscale tags
    search_client = oci.resource_search.ResourceSearchClient(config=config,signer=signer)
    searchDetails = oci.resource_search.models.StructuredSearchDetails()
    searchDetails.query = "query "+ResouceTypeFilter+" resources where (definedTags.namespace = '"+PredefinedTag+"')" if ResouceTypeFilter else "query all resources where (definedTags.namespace = '"+PredefinedTag+"')"
    searchDetails.query += " && displayName  = '" + DisplayNameFilter + "'" if DisplayNameFilter else ""
    searchDetails.query += " && compartmentId  = '" + CompartmentFilter + "'" if CompartmentFilter else ""
    searchDetails.query += " && lifecycleState  = '" + StatusFilter + "'" if StatusFilter else ""

    if page == None:
        response = oci.pagination.list_call_get_up_to_limit(search_client.search_resources,int(per_page),int(limit),searchDetails)
    else:
        response = oci.pagination.list_call_get_up_to_limit(search_client.search_resources,int(per_page),int(limit),searchDetails, page=page)

    return response

# UI Endpoints (Routes)
@app.route('/', methods=('GET', 'POST'))
def index():
    resources = None
    page = None
    per_page = '10'
    next_page_token = None
    previous_page_token = None

    DisplayNameFilter = ""
    ResouceTypeFilter = ""
    CompartmentFilter = ""
    StatusFilter = ""

    if request.method == 'GET':
        # Get Method: Homepage has been called
        # Call OCI to search resources
        resources = getResources()

        if resources.status != 200:
            flash("ERROR retrieving resource results!", "danger")

    else:
        # POST Method
        ## Filter parameters
        if 'DisplayNameFilter' in request.form:
            DisplayNameFilter = request.form['DisplayNameFilter']
        if 'ResouceTypeFilter' in request.form:
            ResouceTypeFilter = request.form['ResouceTypeFilter']
        if 'CompartmentFilter' in request.form:
            CompartmentFilter = request.form['CompartmentFilter']
        if 'StatusFilter' in request.form:
            StatusFilter = request.form['StatusFilter']

        ## Pagination parameters
        if 'page' in request.form:
            page = request.form['page']
        if 'per_page' in request.form:
            per_page = request.form['per_page']

        # Call OCI to search resources
        resources = getResources(page=page, per_page=per_page, DisplayNameFilter=DisplayNameFilter, ResouceTypeFilter=ResouceTypeFilter, CompartmentFilter=CompartmentFilter, StatusFilter=StatusFilter)

    ## Pagination parameters
    if 'opc-next-page' in resources.headers:
        next_page_token = resources.headers['opc-next-page']

    if 'opc-previous-page' in resources.headers:
        previous_page_token = resources.headers['opc-previous-page']

    return render_template('index.html', resources=resources.data, PredefinedTag=PredefinedTag, next_page_token=next_page_token, per_page=per_page, previous_page_token=previous_page_token, DisplayNameFilter=DisplayNameFilter, ResouceTypeFilter=ResouceTypeFilter, CompartmentFilter=CompartmentFilter, StatusFilter=StatusFilter)

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
                    id = key[12:]
                    ScheduleTags[request.form[key]] = request.form['Schedule-'+id]

        Action = request.form['Action']

        if Action == 'Update':
            # Redirect to setResource.html passing arguments from index.html update icon
            return render_template('setResource.html', ScheduleKeys=ScheduleKeys, OCID=OCID, ScheduleTags=ScheduleTags, Action=Action)
        
        else:
            response = TagFunctions.tagResource(config=config, signer=signer, PredefinedTag=PredefinedTag, OCID=OCID, ScheduleTags=ScheduleTags)

            # Handle response
            if response.status == 200:
                flash('Resource '+OCID+' set successfully!', 'success')
            else:
                flash('Error adding the resource '+OCID+'!', 'danger')
            
            return redirect(url_for('index'))

    return render_template('setResource.html', ScheduleKeys=ScheduleKeys, Action="Add")

@app.route('/startResource', methods=('GET', 'POST'))
def startResource():
    if AllowStartStopResources != True:
        flash('START operation is not allowed!!', 'danger')
        return redirect(url_for('index'))
    else:
        OCID = request.form['OCID']
        ResourceType = request.form["ResourceType"]
        CompartmentId = request.form["CompartmentId"]
        response = ""

        if ResourceType == "Instance":
            response = StartStopFunctions.startInstance(config=config, signer=signer, OCID=OCID)

        elif ResourceType == "DbSystem":
            response = StartStopFunctions.startDbSystem(config=config, signer=signer, OCID=OCID, CompartmentId=CompartmentId)

        # elif ResourceType == "VmCluster":
        #     # TODO

        elif ResourceType == "AutonomousDatabase":
            response = StartStopFunctions.startAutonomousDatabase(config=config, signer=signer, OCID=OCID)

        # elif ResourceType == "InstancePool":
        #     # TODO

        else:
            # Resource type not supported!
            flash('Resource type '+ResourceType+' not supported!', 'danger')

        if response.status == 200:
            flash('Resource '+OCID+' started!', 'success')
        else:
            flash('Error starting resource '+OCID+'!!', 'danger')
        return redirect(url_for('index'))

@app.route('/stopResource', methods=('GET', 'POST'))
def stopResource():
    if AllowStartStopResources != True:
        flash('STOP operation is not allowed!!', 'danger')
        return redirect(url_for('index'))
    else:
        OCID = request.form['OCID']
        ResourceType = request.form["ResourceType"]
        CompartmentId = request.form["CompartmentId"]
        response = ""

        if ResourceType == "Instance":
            response = StartStopFunctions.stopInstance(config=config, signer=signer, OCID=OCID)

        elif ResourceType == "DbSystem":
            response = StartStopFunctions.stopDbSystem(config=config, signer=signer, OCID=OCID, CompartmentId=CompartmentId)

        # elif ResourceType == "VmCluster":
        #     # TODO

        elif ResourceType == "AutonomousDatabase":
            response = StartStopFunctions.stopAutonomousDatabase(config=config, signer=signer, OCID=OCID)

        # elif ResourceType == "InstancePool":
        #     # TODO

        else:
            # Resource type not supported!
            flash('Resource type '+ResourceType+' not supported!', 'danger')

        if response.status == 200:
            flash('Resource '+OCID+' stopped!', 'success')
        else:
            flash('Error stopping resource '+OCID+'!!', 'danger')
        return redirect(url_for('index'))

@app.route('/viewMetrics', methods=('GET', 'POST'))
def viewMetrics():
    OCID = request.form['OCID']
    DisplayName = request.form['DisplayName']
    ResourceType = request.form['ResourceType']
    CompartmentId = request.form['CompartmentId']
    
    ScheduleTags = request.form['ScheduleTags']
    ScheduleTags = ScheduleTags.replace("\'", "\"")
    ScheduleTags = json.loads(ScheduleTags)

    # Get monitoring data
    ## Build metric parameters by Resource Type
    if ResourceType == "Instance":
        monitoringData = MonitoringFunctions.getInstanceStatusMetrics(config=config, signer=signer, OCID=OCID, CompartmentId=CompartmentId, ScheduleTags=ScheduleTags)
       
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
        flash('Resource type '+ResourceType+' not supported!', 'danger')
        return redirect(url_for('index'))

    return render_template('viewMetrics.html', OCID=OCID, DisplayName=DisplayName, labels=monitoringData["labels"], status_data=monitoringData["status_data"], schedule_data=monitoringData["schedule_data"])

@app.route('/exportJSON')
def exportJSON():
    resources = getResources(per_page='All')

    items = []
    for item in resources.data:
        row = {}
        row['display_name'] = item.display_name
        row['identifier'] = item.identifier
        row['compartment_id'] = item.compartment_id
        row['defined_tags'] = {PredefinedTag: {}}
        row['defined_tags'][PredefinedTag] = item.defined_tags[PredefinedTag]
        row['lifecycle_state'] = item.lifecycle_state
        items.append(row)
    
    data = {}
    data['items'] = items

    json_data = json.dumps(data, indent=4)

    return Response(json_data, mimetype='application/json', headers={'Content-Disposition':'attachment;filename=AutoScale_Config.json'})

@app.route('/exportCSV')
def exportCSV():
    resources = getResources(per_page='All')

    csv_data = "display_name; identifier; compartment_id; defined_tags; lifecycle_state\n"
    for item in resources.data:
        csv_data = csv_data + item.display_name+"; "+item.identifier+"; "+item.compartment_id+"; "+str({PredefinedTag: item.defined_tags[PredefinedTag]})+"; "+item.lifecycle_state+";\n"

    return Response(csv_data, mimetype='application/csv', headers={'Content-Disposition':'attachment;filename=AutoScale_Config.csv'})

@app.route('/exportREST', methods=('GET', 'POST'))
def exportREST():
    if request.method == 'POST':
        if 'URL' in request.form:
            URL = request.form["URL"]

            # Get the resources
            resources = getResources(per_page='All')

            error_count = 0
            for item in resources.data:
                row = {}
                row["ocid"] = item.identifier
                row["display_name"] = item.display_name
                row["resource_type"] = item.resource_type
                row["schedule"] = str(item.defined_tags[PredefinedTag])

                json_row = json.dumps(row)

                # Execute the PUT command
                response = requests.post(URL, data=json_row, headers={"Content-Type": "application/json"})

                if response.status_code == 201:
                    flash('Resource '+item.identifier+' exported successfully!', 'success')
                else:
                    flash('Error adding the resource '+item.identifier+'!', 'danger')
                    error_count+=1

            if error_count == 0:
                flash('REST resources exported successfully!!', 'success')
            else:
                flash('REST resources exported with errors!!', 'danger')

            return redirect(url_for('index'))
    
    else:
        return render_template('exportREST.html', RestUrl=RestUrl)

@app.route('/importJSON', methods=('GET', 'POST'))
def importJSON():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            
            # TODO: Verify file is JSON format
            json_object = json.loads(file.read())
            error_count = 0
            for item in json_object['items']:
                response = TagFunctions.tagResource(config=config, signer=signer, PredefinedTag=PredefinedTag, OCID=item['identifier'], ScheduleTags=item['defined_tags'][PredefinedTag])
                
                # Handle response
                if response.status == 200:
                    flash('Resource '+item['identifier']+' set successfully!', 'success')
                else:
                    flash('Error adding the resource '+item['identifier']+'!', 'danger')
                    error_count+=1
            
            if error_count == 0:
                flash('JSON file imported successfully!!', 'success')
            else:
                flash('JSON file imported with errors!!', 'danger')
            return redirect(url_for('index'))

    else:
        return render_template('importFile.html')

@app.route('/importCSV', methods=('GET', 'POST'))
def importCSV():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']

            # TODO: Verify file is CSV format
            csv_object = pd.read_csv(file, delimiter=';', header=0, index_col=False)
            error_count = 0
            for index,row in csv_object.iterrows():
                OCID = row[1].lstrip()
                json_ScheduleTags = row[3]
                json_ScheduleTags = json_ScheduleTags.replace("\'", "\"")
                json_ScheduleTags = json.loads(json_ScheduleTags)

                response = TagFunctions.tagResource(config=config, signer=signer, PredefinedTag=PredefinedTag, OCID=OCID, ScheduleTags=json_ScheduleTags[PredefinedTag])

                # Handle response
                if response.status == 200:
                    flash('Resource '+OCID+' set successfully!', 'success')
                else:
                    flash('Error adding the resource '+OCID+'!', 'danger')
                    error_count+=1
                
            if error_count == 0:
                flash('CSV file imported successfully!!', 'success')
            else:
                flash('CSV file imported with errors!!', 'danger')
            return redirect(url_for('index'))
    
    else:
        return render_template('importFile.html')

@app.route('/importREST', methods=('GET', 'POST'))
def importREST():
    if request.method == 'POST':
        if 'URL' in request.form:
            URL = request.form["URL"]

            # Execute the GET command
            response = requests.get(URL).json()

            # Configure resources
            error_count = 0
            for item in response["items"]:
                json_ScheduleTags = json.loads(item["schedule"])
                response = TagFunctions.tagResource(config=config, signer=signer, PredefinedTag=PredefinedTag, OCID=item["ocid"], ScheduleTags=json_ScheduleTags)

                # Handle response
                if response.status == 200:
                    flash('Resource '+item["ocid"]+' set successfully!', 'success')
                else:
                    flash('Error adding the resource '+item["ocid"]+'!', 'danger')
                    error_count+=1

            if error_count == 0:
                flash('REST resources imported successfully!!', 'success')
            else:
                flash('REST resources imported with errors!!', 'danger')

            return redirect(url_for('index'))

    else:
        return render_template('importREST.html', RestUrl=RestUrl)

@app.route('/log')
def Log():
    return render_template('log.html')

@app.route('/getLog')
def getLog():
    def generate():
        # TODO: Point to OCI-AutoScale log file
        with open('../OCI-AutoScale/automation.log') as f:
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
