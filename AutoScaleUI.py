import oci
import time
import argparse
import json
from flask import Flask, request, render_template, url_for, flash, redirect, Response
from flask_paginate import Pagination, get_page_args

# Arguments parser
## Parse command-line arguments
# parser = argparse.ArgumentParser()
# parser.add_argument('-t', default="", dest='config_profile', help='Config file section to use (tenancy profile)')
# parser.add_argument('-tag', default="Schedule", dest='tag', help='Tag to examine, Default=Schedule')
# parser.add_argument('-topic', default="", dest='topic', help='Topic OCID to send summary in home region')
# parser.add_argument('-log', default="", dest='log', help='Log OCID to send log output to')
# parser.add_argument('-loglevel', default="ERRORS", dest='log_level', help='Log level [ALL | ERRORS] ')

# args = parser.parse_args()

## Assign variables
#PredefinedTag = args.tag
PredefinedTag = 'Schedule'


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

@app.route('/addResource', methods=('GET', 'POST'))
def addResource():
    if request.method == 'POST':
        print('Test')
        OCID = request.form['OCID']
        print(OCID)
        #ScheduleKey = request.form['ScheduleKey']
        #print(ScheduleKey)
        #Schedule = request.form['Schedule']
        #print(Schedule)
        
        # Lookup resource type
        # query: query all resources where identifier = 'ocid1.compartment.oc1..<unique_ID>'

        # Tag the OCI resource
        print('Tag!')
        return redirect(url_for('index'))

    return render_template('addResource.html')

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

# @app.route('/log')
# def streamLog():
#     return render_template('log.html')

@app.route('/health')
def health():
    content = {}
    try:
        res = getResources(per_page=1)
        
        content['status']='OK'
        content['status_code']='200'
        content['error_msg']=''
    except Exception as e:
        content['status']='KO'
        content['status_code']='500'
        content['error_msg']=str(e)
    
    json_data = json.dumps(content, indent=2)
    return Response(json_data, mimetype='application/json')
