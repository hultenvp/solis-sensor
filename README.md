[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Solis sensor integration
HomeAssistant sensor for Solis portal platform V2 (m.ginlong.com) and SolisCloud portal. 

## Platform v2
The platform v2 support logs in to the platform and exposes the data retrieved as sensors.
Also confirmed to work with:
* Solarman (home.solarman.cn)
* Sofar solar (home.solarman.cn)

> Platform V2 backend is used by Ginlong and MyEvolveCloud and the same backend is also used for different PV inverter brand portals. I've only tested it in context of Solis with the Ginlong platform. Let me know if it works with for other inverter types as well and I'll add them to the list of confirmed portals.

## SolisCloud
>❗This feature is in beta. The server still has some issues. Join the discussion [here](https://github.com/hultenvp/solis-sensor/discussions/71) to find out about known limitations and to ask questions.

[SolisCloud](https://www.soliscloud.com/) is the next generation Portal for Solis branded PV systems from Ginlong. It's unknown to me if the other brands are also supported.

The new portal requires a key-id, secret and username to function.
Key and secret can be obtained via support: Look at https://www.ginlong.com/global/aftersales.html for the initial contact email address in your region.
:rotating_light: It seems it is now possible to also obtain key and secret via SolisCloud
* Go to https://www.soliscloud.com/#/apiManage
* Ativate API management and agree with the usage conditions.
* After activation, click on view key tot get a pop-up window asking for the verification code.
* First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.
* After that, you will receive an email with the verification code you need to enter (within 60 seconds).
* Once confirmed, you get the API ID, secret an API URL

## HACS installation

The use of HACS is supported and is the preferred means of installing this integration.

## Manual installation

Create a directory called `solis` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this component by copying the files in [`/custom_components/solis/`]

This is how your custom_components directory should be:
```bash
custom_components
├── solis
│   ├── __init__.py
│   ├── const.py
│   ├── ginlong_api.py
│   ├── ginlong_base.py
│   ├── ginlong_const.py
│   ├── manifest.json
│   ├── sensor.py
│   ├── service.py
│   └── soliscloud_api.py
```

## Configuration

### Ginlong platform v2
To enable this integration for Ginlong Solis platform v2 support, add the following lines to your configuration.yaml file:

``` YAML
sensor:
  - platform: solis
    name: "My Solis Inverter"
    portal_domain: "m.ginlong.com" (replace for Solarman, Sofar)
    portal_username: "portal_username"
    portal_password: "portal_password"
    portal_plant_id: "plantId"
```
### Soliscloud
To enable this integration for SolisCloud, add the following lines to your configuration.yaml file:

``` YAML
sensor:
  - platform: solis
    name: "My Solis Inverter"
    portal_domain: "www.soliscloud.com:13333"
    portal_username: "portal_username"
    portal_key_id: "portal_key_id"
    portal_secret: "portal_secret"
    portal_plant_id: "plantId/stationID as string"
```

Configuration variables:

* **name** (Optional): Let you overwrite the name of the device in the frontend. *Default value: Solis*
* **portal_domain** (Required): Portal domain name *Default value: m.ginlong.com*. 
* **portal_username** (Required): Username of your portal account.
* **portal_password** (Optional): Password of the portal account. 
> Note: The integration uses https to communicate with the portal, but the username and password are sent over in plain text!
* **portal_key_id** (Optional): Key ID needed for communication with SolisCloud (obtain via Ginlong support)
* **portal_secret** (Optional): Secret needed for communication with SolisCloud (obtain via Ginlong support)
* **portal_plant_id** (Required): PlantId (Ginlong v2 portal) or StationId (SolisCloud) on the platform the inverter belongs to. Can be found on the portal.
> Dutch: Tab installatie: Installatie ID. 

The integration will detect automatically which data is available at the backend and create the relevant sensors. Names are backward compatible with old manual configuaration.

# Energy dashboard
The Solis integration now supports the energy dashboard introduced in Release 2021.8. 
> Note: This integration requires Home Assistant version 2021.9 or higher

![dashboard integration](./image/energy_dashboard_integration.GIF)
![energy production](./image/solar_production_energy_dashboard.GIF)

# Thanks
Big thanks & kudo's to [@LucidityCrash](https://github.com/LucidityCrash) for all the work on getting the SolisCloud support working!
