# HTTP Health Check Script

The `health_check.py` script performs a HTTP health check on given URLs and outputs the health status in JSON format. It checks the URLs using a multi-threaded approach and supports both full and simple reporting.

## Requirements
This script was tested with the following software and system

- Python 3
- Ubuntu 22.04

## Software Packages to be Installed
- nginx
- uwsgi-plugin-python3
- uwsgi
- uwsgi-emperor

## Usage
The script accepts the following arguments:

- `--report`: Output full status in JSON format.
- `--simple`: Output simple status in JSON format.
  (Note: If no argument is specified, the default behaviour is to output a Healthy or Unhealthy status in plain text.)

## Configuration

The URLs to be checked and other configurations are specified in the `config.json` file. The configuration options are as follows:

- `urls`: A list of URLs to be checked.
- `timeout`: The timeout (in seconds) for each HTTP request.
- `success_codes`: A list of HTTP status codes considered as successful responses.
- `verify_tls`: A boolean value indicating whether TLS verification should be enabled or disabled.

Example `config.json`:

```json
{
    "urls": [
        "https://google.com",
        "https://apple.com"
    ],
    "timeout": 5,
    "success_codes": [200, 301, 401, 404, 502],
    "verify_tls": true
}
```

## Install Software
```
sudo apt-get update
sudo apt-get install nginx uwsgi uwsgi-plugin-python3 uwsgi-emperor
```

## Installation of Script
1. Create the `/opt/healthcheck` directory
   ```
   mkdir /opt/healthcheck
   ```

2. Copy the script and example configuration
   ```
   cp health_check.py /opt/healthcheck
   cp config.json /opt/healthcheck
   ```
   
3. Set up permissions
   ```
   chown -R www-data:www-data /opt/healthcheck
   chmod 755 /opt/healthcheck/health_check.py
   chmod 644 /opt/healthcheck/config.json
   ```

## Running the Script (Command Line)
To run the script with its default behaviour:
```
/opt/healthcheck/health_check.py
```

To get the full status in JSON format:
```
/opt/healthcheck/health_check.py --report
```

To get the simple status in JSON format:
```
/opt/healthcheck/health_check.py --simple
```

## Configure uWSGI Emperor
1. Copy the `health_check.ini` uWSGI app configuration
   ```
   cp health_check.ini /etc/uwsgi-emperor/vassals
   ```
   
2. Set up permissions
   ```
   chown root:root /etc/uwsgi-emperor/vassals/health_check.ini
   chmod 644 /etc/uwsgi-emperor/vassals/health_check.ini
   ```

## NGINX Configuration
Below is an NGINX proxy configuration to the uWSGI app:
```
server {
    listen 80 default_server;

    server_name _;

    location / {
        return 200 '';
        add_header Content-Type text/html;
    }

    location /healthcheck {
        include uwsgi_params;
        uwsgi_pass unix:/opt/healthcheck/health_check.sock;
    }
}
```
