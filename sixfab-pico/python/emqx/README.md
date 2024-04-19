# Systemd subscriber
The Python-based MQTT subscriber is running as a service via systemd.

# Setup
Create the config file `mqtt_subscriber.service` at `/etc/systemd/system/`. Then run

    sudo systemctl daemon-reload
    sudo systemctl enable mqtt_subscriber.service
    sudo systemctl start mqtt_subscriber.service

# Status

Check the status and see logs via

    sudo systemctl status mqtt_subscriber.service
    sudo journalctl -f -u mqtt_subscriber.service