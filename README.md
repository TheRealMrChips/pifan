# pifan
pifan - A python command-line tool to control a cooling fan attached to a Raspberry Pi

##Background:

This app came about because I was building a Raspberry-Pi based webcam.  The webcam was to be mounted in an enclosure in a sunny location here in SoCal.  I was not sure if the heat inside the enclosure would cause problems with my Pi, so I decided to add a small cooling fan to it.  The only problem was that, for longevity, I didn't want the fan to be running unless it was truly needed.  So I built a small controller board that allowed the fan to be turned on and off via a GPIO pin on the Pi.  Since the fan was small, 5-volts, and drew only ~100ma current, I was also able to simplify the circuit by having it powered by the Pi itself.  The only thing missing was a way to automatically control the fan based on the temperature of the Pi itself.

Enter "__pifan__".  This little ~200-line Python script is a full-blown command-line utility for managing a fan connected to one of the GPIO pins on a Pi.  It has options for manually starting and stopping the fan, determining what the internal CPU temperature is, and running in a continuous "cooling" mode where the fan is turned on when the internal temp reaches a threshold, and is turned off again once a lower threshold is achieved after cooling down.  It also has ancillary options for logging events and determining what state the fan should be left in when the app shuts down.

##The Fan Control Circuit:

If you want to use this app, you will first need a fan attached to a pin on your Pi to control it.  This can be achieved using a simple circuit like the following:

![pifan-basic-5v-100ma-fan-control-module](https://github.com/TheRealMrChips/pifan/blob/master/pifan-basic-5v-100ma-fan-control-module.png "Pifan - Basic 5v-100ma Fan Control Module")

Once you have the basic circuit working in a breadboard format, you can then move it to a smaller prototype board which can then be attached across pins 2,4,6 and 8 of the Pi.  Here a a couple shots of the final setup that I ended up with after my experimentation. The soldering is a bit sloppy because I was in a hurry, but it works, and it's __small__!

For 5-volt fans I have found at least two that work well in this configuration: The [SEPA SF25A 5V 0.09A](https://www.google.com/#q=sepa+sf25a) (pictured) is a great little 25mm fan for situations where you need something really small.  It's only drawback is that it tends to be a bit noisy for such a small fan.  If noise is a concern, and you don't mind a slightly bigger fan, I __highly__ recommend the [Noctua NF-A4x10 5V 0.05A] (https://www.google.com/#q=noctua+nf-a4x10) fan.  At 40mm it's small enough for most needs, and it is by far the quietest 40mm fan I've ever worked with.  Additionally, the Noctua has a 3rd speed sensor wire that I intend to use to improve pifan by allowing it to detect the current fan-speed with each iteration. No more guessing whether the fan is on or off!

![pifan-controller-image-1](https://github.com/TheRealMrChips/pifan/blob/master/pifan-controller-1.jpg "Pifan - Example Controller")

![pifan-controller-image-2](https://github.com/TheRealMrChips/pifan/blob/master/pifan-controller-2.jpg "Pifan - Example Controller")





