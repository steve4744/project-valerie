# project-valerie

This is a quick fix to keep Project Valerie working a bit longer on my Vu+ Duo.

The update website http://val.duckbox.info is no longer online which causes the STB to crash when you try to open Project Valerie.
The web interface will also not load as it tries to check if there is a new version available from the defunct website.

Both fixes can be done by logging on the the receiver (using putty) and changing the following 2 files, then restarting Enigma2.

STB fix:  /usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/\_\_init\_\_.py

Web fix:  /usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/DMC_Plugins/DMC_WebInterfaceExtras/core/WebMainActions.py

The actual code changes can be seen by clicking "Compare" above (ignore any changes to other files shown).


@steve4744  - 5th June 2017

