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

class CustomView(APIView):
	def get(self, request, format=json):
		if request.path.strip('/') == 'get-deployed':
			return JsonResponse(DBCommunicator().return_deployed(), safe=False)
		else:
			return Response(DBCommunicator().return_form(str(request.path)))

	def post(self, request, format=None):
		if request.path.strip('/') == 'form-data':
			return Response(FormDataHandler().handle_form_data(request))
		else:
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

	def does_form_exist(self, formId, cursor):
		cursor.execute(self.GET_IF_FORM_ID_EXISTS, [formId])
		count = cursor.fetchone()
		if count is not None:
			return True
		else:
			return False

	def does_patient_hash_exist(self, patientHash, cursor):
		cursor.execute(self.GET_IF_PATIENT_HASH_EXISTS, [patientHash])
		count = cursor.fetchone()
		if count is not None:
			return True
		else:
			return False

	def return_form(self, patienthash):
		with connection.cursor() as cursor:
			cursor.execute(self.GET_FORM_QUERY, [patienthash.strip('/')])
			record = cursor.fetchall()
			if cursor.rowcount == 0:
				return 'form not found'
		for row in record:
			form_data = row[0]
		return form_data

	def store_form(self, request):
		formId = json.loads(request.body)['tabId']
		formName = json.loads(request.body)['tabDesc']
		formData = json.loads(request.body)
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

	def handle_form_data(self, request):
		requestData = request.body
		formName = "test"
		fileDir = str(os.path.join(settings.BASE_DIR, formName)+self.FILE_TYPE)

		#test purposes write data to read before encryption
		#self.write_file(requestData, fileDir)
		self.encrypt_file(fileDir, requestData)

	def encrypt_file(self, fileDir, requestData):

		gpg = gnupg.GPG(gnupghome=settings.BASE_DIR+'/gpghome')
		gpg.encoding = 'utf-8'
		encrypted_data = gpg.encrypt(requestData, 'AF812D71B7163C9C', always_trust=True)
		self.write_file(encrypted_data.data, fileDir+".gpg")

		#THIS IS FOR DECRYPTION
		#decrypted_data = gpg.decrypt(encrypted_data.data, passphrase="formserver", always_trust=True)
		#self.write_file(decrypted_data.data, fileDir)

	def write_file(self, data, filename):
		with open(filename, 'wb') as file:
			file.write(data)
			file.close()	
