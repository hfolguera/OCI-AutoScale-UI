import oci
import time
from flask import Flask, request, render_template, url_for, flash, redirect

# Load OCI-Cli configuration from $HOME/.oci
config = oci.config.from_file(profile_name='hfolguera')
oci.config.validate_config(config)

def getResources():
    # Get all resources with Autoscale tags
    search_client = oci.resource_search.ResourceSearchClient(config)
    searchDetails = oci.resource_search.models.StructuredSearchDetails()
    searchDetails.query = "query all resources where (definedTags.namespace = 'Autoscale')"

    response = search_client.search_resources(searchDetails, limit=1000).data

    return response.items

app = Flask(__name__)

@app.route('/')
def index():
    resources = getResources()
    return render_template('index.html', resources=resources)

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
        
        # Tag the OCI resource
        print('Tag!')
        return redirect(url_for('index'))

    return render_template('addResource.html')