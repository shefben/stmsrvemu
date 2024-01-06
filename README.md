# Stm Server Emulator  for python 3.9

You will be required to install sqlalchemy in python usin the following command:
```
python -m pip install -r requirements.txt
```

Code is there for beta1 but is not fully integrated so will not work (if you know python you can try it out yourself, but i havnt tested it yet)

Source code for the server emulator for clients 2002-2010

Compile on Python 3.9.13 64-bit if you want to run/build from source using:

python.exe -m PyInstaller -F -i source-content.ico emulator.py

> *Please note the code is constant work-in-progress and might not compile or operate correctly after some comits*

### Current Change Log
+ fully updated to pmeins latest code changes as of 12/14/2023
+ converted from python 2.7 to 3.9
+ Refactored code to be easier to read and more modular
+ Implemented full cser server packet parsing and collected information saving
+ auto-create ALL required folders
+ Integrated Beta 1 (2002) steam
+ Added color coded console text
+ Added exception/error catcher to improve readabilty of errors
+ created a new masterserver to replace the old 3 masterservers
+ dynamic serverlists for the directoryserver and content directory server
+ created harvest server for bugreport files and other memory dump files
+ added missing packets to auth server and directory server (not operational, just for collecting packet data)
+ added ini option to automatically retrieve public ip address
+ removed http_name
+ changed http_ip to be used ONLY for neutering.  This is because people may want to host their website somewhere other than where the stmserver is hosted
    also because apache should only ever listen on a local IP unless there are multiple interfaces with lan/wan access or if you use an external ip for internet access
+ added simultaneous lan/wan game/client validation
+ fixed simultaneous lan/wan neutering
+ added name suggestor and name suggestion dialog
+ fixed overwriting user accounts that already exist
+ added email functions
+ added email templates
+ added authserver email code (validation code, new user email etc..)
+ added valve anti cheat server 1 for beta 1 hl engine to mid 2005 hl engine
+ consolidated alot of repeated code
+ added auto internal ip
+ added auto external ip
+ added white/black lists
+ added configurable contentserver cellid
+ added configurable contentserver region codes
+ added location information for emails (country/state) for users own security (to check against who requested something such as changing passwords)
+ added functionality for users who's external IP shows up for lan connections. they now are handled as lan users if their IP matches the servers external IP
+ added optional built-in name suggestions
+ added optional name suggestion additions (prepended and append additions)
+ added option to completely disable cddb (firstblob) database


### Credits
+ pmein1 - Developer and support
+ cystface-man - Developer and provided descriptions of CCDB records and service packet information
+ Dormine - Original python poc emulator code and updates
+ Tane - Original app update code
+ steamCooker - Help with some of the intricacies of the Steam services
+ GenoKirby - Provided description of section 5 of the SADB


### shefben/cystfaceman fork info:
I am using this fork to integrate all packets and services that have been found through reverse engineering.
The point is to hopefully one day have a complete steam network for the 2004-2008 clients that allow game authentication
game registration, and other things.

some other changes i hope to make are as followed:
  
- [ ] Replaced user's .py file with a mysql database
- [ ] Create a php script to query the database and also add/remove users and also add / remove subscriptions
- [ ] Get tracker/friends server working for all steam versions
- [x] Get steam v2 (2003) working properly
- [x] Add Packets to allow for outside server's to be added to directoryserver list (like having multiple content servers that can automatically add to the directoryserver list)
