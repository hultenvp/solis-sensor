[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Solis sensor integration
HomeAssistant sensor for Solis portal platform V2 (m.ginlong.com) and SolisCloud portal. 
Still questions after the readme? Read the [wiki](https://github.com/hultenvp/solis-sensor/wiki) or look at the [discussions page](https://github.com/hultenvp/solis-sensor/discussions)

## Platform v2
The platform v2 support logs in to the platform and exposes the data retrieved as sensors.
Also confirmed to work with:
* Solarman (home.solarman.cn)
* Sofar solar (home.solarman.cn)

> Platform V2 backend is used by Ginlong and MyEvolveCloud and the same backend is also used for different PV inverter brand portals. I've only tested it in context of Solis with the Ginlong platform. Let me know if it works with for other inverter types as well and I'll add them to the list of confirmed portals.

## SolisCloud
:warning: ***READ CAREFULLY: As of 27/9 Ginlong has suspended access to the Soliscloud API claiming GDPR issues. They have indicated they will re-open the API in a next release somewhere Q1 2023. For now you can NOT request new API key and secret. If you have an API key and secret then the integration still works. People with older logger sticks can use the m.ginlong.com portal in combination with this integration. People with a newer S3 stick will have to use one of the local solutions (e.g. RS485 ethernet bridge). See [issue 162](https://github.com/hultenvp/solis-sensor/issues/162) and HA forum for discussions about local solutions.***

>❗This feature is in beta. The server still has some issues. Join the discussion [here](https://github.com/hultenvp/solis-sensor/discussions/71) to find out about known limitations and to ask questions.

[SolisCloud](https://www.soliscloud.com/) is the next generation Portal for Solis branded PV systems from Ginlong. It's unknown to me if the other brands are also supported.

~~The new portal requires a key-id, secret and username to function.~~<br>
~~You can obtain key and secret via SolisCloud.~~<br>
* ~~Go to https://www.soliscloud.com/#/apiManage.~~<br>
* ~~Activate API management and agree with the usage conditions.~~<br>
* ~~After activation, click on view key tot get a pop-up window asking for the verification code.~~<br>
* ~~First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.~~<br>
* ~~After that, you will receive an email with the verification code you need to enter (within 60 seconds).~~<br>
* ~~Once confirmed, you get the API ID, secret an API URL~~<br>

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

The integration can be configured via the UI.

<img width="301" alt="image" src="https://user-images.githubusercontent.com/61835400/200194739-68444b7f-7144-4d84-abd0-2ac3bb82ecda.png">

Select the right platform and platform URL to use and click "Submit"

**Ginlong platform v2**   Provide username, password and plant id. If you want to add multiple plants just follow the configuration for each plant.
**Soliscloud**            Provide username, key id, secret and station id. If you want to add multiple stations just follow the configuration for each plant.


# Energy dashboard
The Solis integration now supports the energy dashboard introduced in Release 2021.8. 
> Note: This integration requires Home Assistant version 2021.9 or higher

![dashboard integration](./image/energy_dashboard_integration.GIF)
![energy production](./image/solar_production_energy_dashboard.GIF)

# Thanks
Big thanks & kudo's to [@LucidityCrash](https://github.com/LucidityCrash) for all the work on getting the SolisCloud support working!
