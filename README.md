# OCI-AutoScale-UI

This is the code repository for the OCI-AutoScale-UI tool which allows visualizing all the configured resources for OCI-AutoScale.

OCI-AutoScale is a tool based on the [OCI-AutoScale](https://github.com/AnykeyNL/OCI-AutoScale) project by Richard Garsthagen (AnykeyNL).

## Features

OCI-AutoScale-UI provides the following features:
- Explore resources with OCI-AutoScale tags
- Add OCI-AutoScale tags for new resources
- Edit OCI-AutoScale tags for existing resources
- Export and Import OCI-AutoScale configuration in JSON or CSV format or via REST
- Display OCI-AutoScale logs through the web interface
- Application /health endpoint for monitoring purposes
- Application /metrics endpoint with Prometheus Exporter format

## Installation

Install the app requirements depending on deployment method:

### Python (Online mode)
```
sudo pip3 install -r requirements.txt
```

### Python (Offline mode)
If the server does not have access to public internet, download the python libraries from a server with internet access with the following command:
```
pip3 download -r requirements.txt
```

Transfer all the *.whl files to the destination server and install them:
```
sudo pip3 install --no-index --find-links <destination folder> -r requirements.txt
```

### Docker
#TODO

### Firewall configuration
If firewalld service is running, add an exception for port 5000 (default) to allow requests:
```
sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## Configuration
#TODO: Explain configuration file and parameters purpose

## Running the application

### Start application in Development mode
```
FLASK_APP=AutoScaleUI FLASK_ENV=development DEBUG_METRICS=1 flask run
```

### Python (Production mode)
```
FLASK_APP=AutoScaleUI FLASK_ENV=production flask run --host 0.0.0.0
```

#### Start app on boot
Configure OCI-AutoScale-UI to start on boot as a linux service.

Create the file `/etc/systemd/system/OCI-AutoScale-UI.service` with the following contents:
```
[Unit]
Description=OCI-AutoScale-UI
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/OCI-AutoScale-UI
Environment=FLASK_APP=AutoScaleUI
Environment=FLASK_ENV=production
Environment=DEBUG_METRICS=1
ExecStart=/usr/local/bin/flask run --host=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload systemd configuration:
```
sudo systemctl daemon-reload
sudo systemctl enable OCI-AutoScale-UI
sudo systemctl start OCI-AutoScale-UI
```

### Docker
#TODO

#### Start app on boot
#TODO

## Export/Import REST configuration
Application allows to export and/or import resources configuration through a REST API. Code is adapted to interact with an Oracle APEX and ORDS instance publishing an Autonomous Database table.
An APEX application is included in this repository to deploy an User Interface to provide access to a table storing the values and presenting them through ORDS (REST).

Import endpoint expects an "application/json" format with a `items` attribute containing all the table rows.
Example:
```
{"items":[{"ocid":"ocid1.instance.oc1.eu-madrid-1.anwwcljrijaigyicrhuktcuusgrrl7hdgkoqc5uufvme2yb7qrbujpw3zc3a","resource_type":"Instance","schedule":"{'AnyDay': '0,0,0,0,0,0,0,0,*,*,*,*,*,*,*,*,0,0,0,0,0,0,0,0'}","display_name":"demoinstance","links":[{"rel":"self","href":"https://adbdemo-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/schedules/ocid1.instance.oc1.eu-madrid-1.anwwcljrijaigyicrhuktcuusgrrl7hdgkoqc5uufvme2yb7qrbujpw3zc3a"}]},"hasMore":false,"limit":25,"offset":0,"count":15,"links":[{"rel":"self","href":"https://adbdemo-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/schedules/"},{"rel":"edit","href":"https://adbdemo-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/schedules/"},{"rel":"describedby","href":"https://adbdemo-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/metadata-catalog/schedules/"},{"rel":"first","href":"https://adbdemo-auto.adb.eu-madrid-1.oraclecloudapps.com/ords/automation/schedules/"}]}
```

### APEX application deployment
#TODO

## Next steps
Next features to be implemented:
- Dockerize app
- Login
- App versioning
- Include "Add Schedule" button to dynamically add schedule rows on setResource
- Allow to export current filter or all resources
- Allow to read log from file or from logging service

## Issues
Known issues to be fixed:
- Fix pagination: Empty last page, disable previous on first page (after going forward)
- Fix: Keep pagination (per_page) parameter when filter is used
- Fix: Metrics are disabled when run in the Flask development server with reload enabled. ...them anyway
- When an schedule is added to an existing resource, previous tags are removed