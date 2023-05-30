# OCI-AutoScale-UI

This is the code repository for the OCI-AutoScale-UI tool which allows visualizing all the configured resources for OCI-AutoScale.

OCI-AutoScale is a tool based on the OCI-AutoScale project by Richard Garsthagen (AnykeyNL).

OCI-AutoScale-UI provides a user interface to XX and perform basic commands such as XXX.

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

## Running the application

### Start in DEBUG mode
```
. ./setenv.sh
flask run
```

### Python
```
. ./setenv.sh
flask run --host 0.0.0.0
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
ExecStart=/usr/local/bin/flask run
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

## Next steps
- Historico
- Creación de budgets/notifications/...
- 404
- Dockerize app
- Login
- Filter resources by instance_type, compartment, status...
- App versioning
- Include "Add Schedule" button to dynamically add schedule rows on setResource
- Include import JSON/CSV resources
- Include start and stop option

## Issues
- Copy OCID
- Fix command-line parameters parser
- Fix pagination: Empty last page, disable previous on first page (after going forward)