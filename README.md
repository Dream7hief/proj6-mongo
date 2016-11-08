# proj6-mongo
Simple list of dated memos kept in MongoDB database

#Author:
Logan Poole, lpoole3@uoregon.edu

## What it does
This program is designed to take a date and some text and create in memo in a pre-determined database using the credentials contained in the secrets folder. 


#Running Application
**run mongodb on port 27333(change admin_secrets.py in secrets folder)**
mongod --port 27333

git clone https://github.com/Dream7hief/proj6-mongo InstallDirectory
cd InstallDirectory
bash ./configure
make run**(control_C to stop program)

#Notes:
Absence of date sets date to matoday
Error 404 Page Not Found

#Application Testing
I have included a test script that test the functionality of the store and remove functions for the database. It also tests the handling for a no entry date.

The tests can be ran with these commands

cd InstallDirectory
make test **or
nosetest