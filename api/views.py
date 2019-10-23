##########################################
#__author__ = "Brian Valenzi"
#__credit__= ["Brian Valenzi"]
#__email__="bv457@uowmail.edu.au"
#__status__="Production"
##########################################
from rest_framework.views import APIView, Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from django.views.generic.edit import CreateView
from django.db import connection
from django.http import JsonResponse
from django.conf import settings
from datetime import date
import gnupg
import sys, subprocess, shlex, os, stat, django
import json

@permission_classes((permissions.AllowAny,))

#This is the API request handler class for GET and POST requests
class CustomView(APIView):
	def get(self, request, format=json):
		#This returns all deployed surveys and their date from the SQL database
		if request.path.strip('/') == 'get-deployed':
			return JsonResponse(DBCommunicator().return_deployed(), safe=False)
		else:
			#This Queries the database for the survey associated with the HASH passed in the URL path
			#If successful match, returns the form JSON object to be rendered by Angular Web Interface
			return Response(DBCommunicator().return_form(str(request.path)))

	def post(self, request, format=None):
		#This handles POST request of patient form data by encrypting and writing to a file
		if request.path.strip('/') == 'form-data':
			return Response(FormDataHandler().handle_form_data(request))
		else:
			#This handles POST requests from formbuilder and inserts the forms JSON object with the associated
			#patient hash into the SQL database
			return Response(DBCommunicator().store_form(request))

class DBCommunicator():
	GET_FORM_QUERY = "SELECT Uncompleted_Survey.data_dump FROM Uncompleted_Survey JOIN Permitted_Patient_Hash ON Permitted_Patient_Hash.id = Uncompleted_Survey.id WHERE Permitted_Patient_Hash.hash = %s"
	GET_DEPLOYED_FORMS = "SELECT form_name, id, deploy_date FROM Uncompleted_Survey;"
	GET_IF_FORM_ID_EXISTS = "SELECT id FROM Uncompleted_Survey WHERE id = %s;"
	GET_IF_PATIENT_HASH_EXISTS = "SELECT hash FROM Permitted_Patient_Hash WHERE hash = %s;"

	POST_FORM_QUERY = "INSERT INTO Uncompleted_Survey (id, form_name, version, valid, data_dump, deploy_date) VALUES(%s, %s, %s, %s, %s, %s)"
	POST_HASH_QUERY = "INSERT INTO Permitted_Patient_Hash (hash, id) VALUES(%s, %s)"

	UPDATE_SURVEY = "UPDATE Uncompleted_Survey SET data_dump = %s, form_name = %s, deploy_date = %s WHERE id = %s"
	UPDATE_PATIENT_ASSOCIATED_SURVEY = "UPDATE Permitted_Patient_Hash SET id = %s WHERE hash = %s"

	#Queries SQL database to check if form exists
	def does_form_exist(self, formId, cursor):
		cursor.execute(self.GET_IF_FORM_ID_EXISTS, [formId])
		count = cursor.fetchone()
		if count is not None:
			return True
		else:
			return False

	#Checks if a patients hash already is associated with a survey
	def does_patient_hash_exist(self, patientHash, cursor):
		cursor.execute(self.GET_IF_PATIENT_HASH_EXISTS, [patientHash])
		count = cursor.fetchone()
		if count is not None:
			return True
		else:
			return False
	#Qeuries SQL db and returns survey JSON object to be rendered by Angular formserver web app if it exists
	def return_form(self, patienthash):
		with connection.cursor() as cursor:
			cursor.execute(self.GET_FORM_QUERY, [patienthash.strip('/')])
			record = cursor.fetchall()
			if cursor.rowcount == 0:
				return 'form not found'
		for row in record:
			form_data = row[0]
		return form_data
	#Stores deployed forms from the formbuilder Angular web app
	def store_form(self, request):
		formId = json.loads(request.body)['tabViewId']
		formName = json.loads(request.body)['tabViewLabel']
		formData = request.body
		patientHash = str(request.path).strip('/')
		currentDate = date.today().strftime("%y%m%d")

		cursor = connection.cursor()
		try:
			if self.does_form_exist(formId, cursor):
				cursor.execute(self.UPDATE_SURVEY, [formData, formName, currentDate, formId])
			else:
				cursor.execute(self.POST_FORM_QUERY, [formId, formName, int(1), int(1), formData, currentDate])
				if self.does_patient_hash_exist(patientHash, cursor):
					cursor.execute(self.UPDATE_PATIENT_ASSOCIATED_SURVEY, [formId, patientHash])
				else:
					cursor.execute(self.POST_HASH_QUERY, [patientHash, formId])
		finally:
			cursor.close();
		return formData
	#Queries SQL db and retrieves all deployed forms and returns them in a JSON object format for the Formbuilder
	def return_deployed(self):
		with connection.cursor() as cursor:
			cursor.execute(self.GET_DEPLOYED_FORMS)
			record = cursor.fetchall()
			myDict = {}
			mylist = []
			if cursor.rowcount == 0:
				return 'No deployed forms'
			for row in record:
				name = row[0]
				formId = row[1]
				deploy_date = row[2]
				record = {"name":name, "id":formId, "deploy_date": str(deploy_date)}
				mylist.append(record)
			myDict["Deployed_Forms"]=mylist
			return json.dumps(myDict)


class FormDataHandler():

	FILE_TYPE = ".txt"
	#Function handles sensitive form data and calls other functions to encrypt and write to file
	def handle_form_data(self, request):
		requestData = request.body
		formName = "test"
		fileDir = str(os.path.join(settings.BASE_DIR, formName)+self.FILE_TYPE)
		self.encrypt_file(fileDir, requestData)
	#This function encrypts form data under RSA public key from GPG keyring
	#(All encryption is done within application memory)
	#RSA Private key requires the passphrase to be used to decrypt data 
	#THIS SHOULD BE A VERY VERY SECURE PASSPHRASE THAT IS RESISTENT TO PASSWORD ATTACKS!
	def encrypt_file(self, fileDir, requestData):

		gpg = gnupg.GPG(gnupghome=settings.BASE_DIR+'/gpghome')
		gpg.encoding = 'utf-8'
		encrypted_data = gpg.encrypt(requestData, 'AF812D71B7163C9C', always_trust=True)
		self.write_file(encrypted_data.data, fileDir+".gpg")
	#This function handles writing data to a file
	def write_file(self, data, filename):
		with open(filename, 'wb') as file:
			file.write(data)
			file.close()	
