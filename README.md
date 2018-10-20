# lazy-holiday-planner

## About

The lazy bastard's holiday planner. Creating account gains you access to the ability to just quickly generate a full holiday by just specifying some details including location and the dates you want to be there. You get the ability to share the trip with friends and add landmarks and scheduled events.

## Setup

To setup the application in a developer environment, you will need to install the pip requirements and then run the dev-run script:

```bash
bash scripts/requirements-install
bash dev-run
```

This will begin the server, however a lot of the functionality will not work if you don't expose the webhook correctly. You can use ```ngrok``` to expose the ```/api/typeform``` to the internet, which will make the system actually work. ```ngrok``` can generate you a public facing domain by running the following command:

```bash
sudo ngrok http 8000
```

Then, you will need to modify the domain on the typeform website so that it can properly reach the webhook. I'd recommend using typeform's built in method for checking that the webhook properly works.