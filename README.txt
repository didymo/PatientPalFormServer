#Name
FormServer
#Description
This project was created for a Final year project at UOW as the backend for a Survey Toolkit.
Sole purpose is availability to patients to retrieve their personalised forms in a public domain.
The main design features include:
	-Restful API to accept POST and GET requests
	-Patient hash tokenized system, which stores which patient hash is associated to a survey
	-Return survey JSON data to an Angular Web app interface to render patients requested forms
	-Handle patient returned form data over HTTPS and performs application level encryption and writes to a file
	-Manage any newly deployed surveys or newly associated patient forms
	-Patients request forms by sending their personal hash in a GET request via Angular web interface
#Technologies
Django framework
Restful API framework
MySQL Database manager
GPG cryptographic tool software
Apache2 web server
Apache2 WSGI module
#Security
Apache2 HTTPS -> SSL/TLS
Patient anonymity tokenized system(No identifying patient data is stored on the server)
GPG cryptographic software to encrypt returned patient data
#Authors
Brian Valenzi
bv457@uowmail.edu.au
#Status
Production V1

