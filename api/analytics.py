from django.db import connection
import json

class Analytics():

	INSERT_FORM_RECORD = "INSERT INTO Analytics (one, two, three, four) VALUES(%s, %s, %s, %s)"
	GET_FORM_STATS = "SELECT one, two, three, four FROM Analytics ORDER BY one"
	GET_TOTAL_FORMS = "SELECT server FROM Counter"
	GET_SYNC_TOTAL = "SELECT * FROM Counter"
	SYNC_TOTAL_FORMS = "UPDATE Counter SET local = server"
	COUNT_AGES = "SELECT COUNT(one) FROM Analytics GROUP BY one;"

	def sync_total(self):
		cursor = connection.cursor()
		cursor.execute(self.SYNC_TOTAL_FORMS)

	def get_sync_total(self):
		cursor = connection.cursor()
		cursor.execute(self.GET_SYNC_TOTAL)
		record = cursor.fetchone()
		if record[0] != record[1]:
			return True
		#else:
			return False 

	def get_analytics_data(self):
		if self.get_sync_total():
			self.sync_total()
			cursor = connection.cursor()
			cursor.execute(self.GET_FORM_STATS)
			record = cursor.fetchall()
			listt =[]
			mylist =[]
			myDict = {}
			myDict["Distance"] = {}
			myDict["Knowledge"] = {}
			myDict["Rating"] = {}
			mylist1 = [0]*4
			mylist2 = [0]*4
			mylist3 = [0]*4
			mylist4 = [0]*4
			mylist5 = [0]*4
			mylist6 = [0]*4
			i = 1
			while i <= 3:
				for row in record:
					#return row
					age = row[0]
					distance = row[1]
					know = row[2]
					rating = row[3]
					if row[i] is not None:
						if age == 1:
							mylist1[row[i]-1] += 1
						elif age == 2:
							mylist2[row[i]-1] += 1
						elif age == 3:
							mylist3[row[i]-1] += 1
						elif age == 4:
							mylist4[row[i]-1] += 1
						elif age == 5:
							mylist5[row[i]-1] += 1
						elif age == 6:
							mylist6[row[i]-1] += 1
					#record = {"name":name, "id":formId, "deploy_date": str(deploy_date)}
					#mylist.append(record)
				if i == 1:
					myDict["Distance"]["_1"]=mylist1
					myDict["Distance"]["_2"]=mylist2
					myDict["Distance"]["_3"]=mylist3
					myDict["Distance"]["_4"]=mylist4
					myDict["Distance"]["_5"]=mylist5
					myDict["Distance"]["_6"]=mylist6
				elif i == 2:
					myDict["Knowledge"]["_1"]=mylist1
					myDict["Knowledge"]["_2"]=mylist2
					myDict["Knowledge"]["_3"]=mylist3
					myDict["Knowledge"]["_4"]=mylist4
					myDict["Knowledge"]["_5"]=mylist5
					myDict["Knowledge"]["_6"]=mylist6
				elif i == 3:
					myDict["Rating"]["_1"]=mylist1
					myDict["Rating"]["_2"]=mylist2
					myDict["Rating"]["_3"]=mylist3
					myDict["Rating"]["_4"]=mylist4
					myDict["Rating"]["_5"]=mylist5
					myDict["Rating"]["_6"]=mylist6
				mylist1 = [0]*3
				mylist2 = [0]*3
				mylist3 = [0]*3
				mylist4 = [0]*3
				mylist5 = [0]*3
				mylist6 = [0]*3
				i+=1

			cursor.execute(self.GET_TOTAL_FORMS)
			record = cursor.fetchall()
			#tempList = []
			#tempList = {"sum":record[0]}
			for result in record:
				mylist = result
				myDict["total"] = mylist

			cursor.execute(self.COUNT_AGES)
			record = cursor.fetchall()
			for result in record:
				listt.append(result[0])
			myDict["ages"] = listt
			return myDict
		else:
			return None

	def store_analytics_data(self, request):
		jsonObj = json.loads(request.body)
		try:
			age = self.age_switch(jsonObj['4424'])
			distance = self.distance_switch(jsonObj['4425'])
			know = self.know_switch(jsonObj['4426'])
			rating = self.rate_switch(jsonObj['4427'])

			cursor = connection.cursor()
			cursor.execute(self.INSERT_FORM_RECORD, [age, distance, know, rating])
			cursor.execute("UPDATE "+" Counter "+" SET server = server" +"+ 1")
		except:
			return False
		return True

	def age_switch(self, age):
		switcher = {
			"18 or below": 1, 
			"19-24": 2,
			"25-34": 3,
			"35-44": 4,
			"45-54": 5,
			"55 or above": 6
		}
		return switcher.get(age, None)

	def distance_switch(self, distance):
		switcher = {
			"Less than 15 minutes": 1, 
			"15-30 minutes ": 2,
			"30 minutes": 3,
			"Longer than 60 minutes": 4
		}
		return switcher.get(distance, None)

	def know_switch(self, know):
		switcher = {
			"Yes": 1, 
			"No": 2,
			"I would prefer not to answer": 3
		}
		return switcher.get(know, None)

	def rate_switch(self, rate):
		switcher = {
			"Yes": 1, 
			"Yeah": 2,
			"I'm not sure...yes?": 3
		}
		return switcher.get(rate, None)
