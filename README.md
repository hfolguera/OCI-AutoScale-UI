# OCI-AutoScale-UI

This is the code repository for the OCI-AutoScale-UI tool which allows visualizing all the configured resources for OCI-AutoScale.

OCI-AutoScale is a tool based on the OCI-AutoScale project by Richard Garsthagen (AnykeyNL).

OCI-AutoScale-UI provides a user interface to XX and perform basic commands such as XXX.

## Features

## Installation

### Python
```
sudo pip3 install -r requirements.txt
```

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

## Next steps
- Logging
- Historico
- Creación de budgets/notifications/...
- Edit schedule
- 404
- Dockerize app
- Login
- Monitoring? Metrics?
- Filter resources by instance_type, compartment, status...

## Issues
- Copy OCID
- Fix command-line parameters parser
- Fix Schedule values alignment
- Fix table column width
- Fix pagination: Empty last page, disable previous on first page (after going forward)