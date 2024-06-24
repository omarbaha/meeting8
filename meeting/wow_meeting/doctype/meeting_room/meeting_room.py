# Copyright (c) 2023, Omar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
import json

class MeetingRoom(Document):
	def after_insert(self):
		createMeeting(self)


def createMeeting(self):
	try:
		user = frappe.get_doc("User", frappe.session.user)
		company = self.company

		meeting_settings = frappe.get_list(
			"Meeting Settings",
			filters={"company": company},
			fields=["name", "token"]
		)
		if len(meeting_settings) > 0:
			token = meeting_settings[0].token
		else:
			frappe.throw("Could not find your token")
	except frappe.DoesNotExistError:
		return 0

	parts = []
	for p in self.participants:
		parts.append(p.email)

	url = "https://meet.wowdigital.sa/api/method/meeting.meeting.meetingApi.createroomApi"
	body = {
		"token": token,
		"title": self.title,
		"subject" : self.description,
		"startdate": f"{self.start_date} {self.start_time}",
		"moderator": self.moderator,
		"members": parts,
	}

	response = requests.post(url, json=body)

	if response.status_code == 200:
		data = json.loads(response.text)["message"]
		if data["success"] == 200:
			room = frappe.get_doc("Meeting Room", self.name)
			room.room_code = data["roomcode"]
			room.room_id = data["roomid"]
			room.save()
		else:
			frappe.throw(str(data["msg"]))
	else:
		frappe.throw(str(data["msg"]))


@frappe.whitelist()
def meetingLogin(user, company):
	# frappe.throw(user)
	try:
		user = frappe.get_doc("User", frappe.session.user)

		meeting_settings = frappe.get_list(
			"Meeting Settings",
			filters={"company": company},
			fields=["name", "token"]
		)
		if len(meeting_settings) > 0:
			token = meeting_settings[0].token
		else:
			frappe.throw("Could not find your token")
	except frappe.DoesNotExistError:
		return 0

	url = "https://meet.wowdigital.sa/api/method/meeting.meeting.meetingApi.LoginUserApi"
	body = {
		"token": token,
		"usr": user,
	}

	response = requests.post(url, json=body)
	if response.status_code == 200:
		data = json.loads(response.text)["message"]
		return {"response_code": 200, "data": data}
	
	return {"response_code": 500}

