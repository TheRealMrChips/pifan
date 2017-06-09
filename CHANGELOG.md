# pifan - Change Log

## V2.1 - 7/23/2016
* Added `--timestamp` parameter to allow the user to choose between formats: `ISO8601`, tab-separated `datetime`, and `none` at all.
* Fixed highly fluctuating temperature values by averaging multiple readings across a short (250ms) timespan.
* Removed some stray mentions of the old `cool` action that were still in the code comments.

## V2.0 - 7/21/2016

* Replaced `--action` parameter with `--mode` parameter for clarity/consistency.
* Replaced `cool` mode with two new modes: `cron` and `daemon`.
* The new `cron` mode makes the app friendly for people who want to automate it using a cron-script.  It simply sets the fan state based on the current temperature rules as provided in the `--tempOn` and `--tempOff` values on the command line.  It then exits.
* The new `daemon` mode behaves the same as the old `cool` mode, running continuously until terminated.  This is the mode to use if you want to automate this tool using init scripts at startup, to wrap it as a service, or to simply kick it off to run in a separate shell.
* Temperatures are now managed to the tenth of a degree.  This affects the `--tempOn`, `--tempOff` parameters as well as command output.
* Status reporting has been cleaned-up and is now consistently formatted across modes.
* Removed `--verbose` parameter in favor of consistent verbosity across all modes.
* 
## v1.0 - 7/19/2016

* First official release.
* All basic functionality and actions available: `run` fan, `stop` fan, `temp` check, and continuous `cool` actions are working.
