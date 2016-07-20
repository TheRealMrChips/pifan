# pifan
pifan - A python command-line tool to control a cooling fan attached to a Raspberry Pi

##Background:

This app came about because I was building a Raspberry-Pi based webcam.  The webcam was to be mounted in an enclosure in a sunny location here in SoCal.  I was not sure if the heat inside the enclosure would cause problems with my Pi, so I decided to add a small cooling fan to it.  The only problem was that, for longevity, I didn't want the fan to be running unless it was truly needed.  So I built a small controller board that allowed the fan to be turned on and off via a GPIO pin on the Pi.  Since the fan was small, 5-volts, and drew only ~100ma current, I was also able to simplify the circuit by having it powered by the Pi itself.  The only thing missing was a way to automatically control the fan based on the temperature of the Pi itself.

Enter "__pifan__".  This little ~200-line Python script is a full-blown command-line utility for managing a fan connected to one of the GPIO pins on a Pi.  It has options for manually starting and stopping the fan, determining what the internal CPU temperature is, and running in a continuous "cooling" mode where the fan is turned on when the internal temp reaches a threshold, and is turned off again once a lower threshold is achieved after cooling down.  It also has ancillary options for logging events and determining what state the fan should be left in when the app shuts down.

##The Fan Control Circuit:

If you want to use this app, you will first need a fan attached to a pin on your Pi to control it.  This can be achieved using a simple circuit like the following:

![pifan-basic-5v-100ma-fan-control-module](https://github.com/TheRealMrChips/pifan/blob/master/pifan-basic-5v-100ma-fan-control-module.png "Pifan - Basic 5v-100ma Fan Control Module")


