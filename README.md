# OCI-AutoScale-UI

This is the code repository for the OCI-AutoScale-UI tool which allows visualizing all the configured resources for OCI-AutoScale.

OCI-AutoScale is a tool based on the [OCI-AutoScale](https://github.com/AnykeyNL/OCI-AutoScale) project by Richard Garsthagen (AnykeyNL).

## Features

OCI-AutoScale-UI provides the following features:
- Explore resources with OCI-AutoScale tags
- Add OCI-AutoScale tags for new resources
- Edit OCI-AutoScale tags for existing resources
- Export OCI-AutoScale configuration in JSON or CSV format
- Display OCI-AutoScale logs through the web interface
- Application /health endpoint for monitoring purposes
- Application /metrics endpoint with Prometheus Exporter format

## Installation

Install the app requirements depending on deployment method:

### Python
```
sudo pip3 install -r requirements.txt
```

### Docker
#TODO

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

## Next steps
Next features to be implemented:
- Historico
- Creación de budgets/notifications/...
- 404
- Dockerize app
- Login
- App versioning
- Include "Add Schedule" button to dynamically add schedule rows on setResource
- Include start and stop option
- Compliance view: Show the real state of the resources vs the expected. Include discrepancy summary?
- Include embeded resources metrics
- Allow to export current filter or all resources

## Issues
Known issues to be fixed:
- Fix pagination: Empty last page, disable previous on first page (after going forward)
- Fix: Keep pagination (per_page) parameter when filter is used
- Fix: Metrics are disabled when run in the Flask development server with reload enabled. ...them anyway
