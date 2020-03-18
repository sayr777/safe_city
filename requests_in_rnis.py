# !/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import datetime
import logging
import time

#----------------------------------------------------------------------------------
# 1) Получить token
#----------------------------------------------------------------------------------
def get_token(LOGIN,PASSWORD,URL):
	URL = URL + '?com.rnis.auth.action.login'
	index=5
	token = None
	while True:
		# querystring = {"com.rnis.auth.action.login": ""}
		payload = {"headers": {"meta": {}}, "payload": {"login": LOGIN, "password": PASSWORD}}
		payload = json.dumps(payload)
		headers = {
            'Subject': "com.rnis.auth.action.login",
            'Content-Type': "application/json"
		}
		try:
			# print(payload)
			r = requests.post(URL, data=payload, headers=headers, timeout = 10)
			r = r.json()
			# print(r)
			if r.get('success') is True:
				token = str(r.get('payload').get('token'))
				break
			else:
				print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),' !!!!!! Пытаюcь повторно получить токен ....')
				logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+' !!!!!! Пытаюcь повторно получить токен ....')
		except:
			pass
		index = index -1
		if index==0:
			break
		time.sleep(1)

	return token


#--------------------------------------------------------------------------------------------
# 2) Получить по id предприятия его название
#----------------------------------------------------------------------------------------------
def get_org_name (uuid_unit,rnis_token,URL):
	URL = URL + "?com.rnis.organizational_units.action.unit.get"
	index = 5
	unit_name = None
	while True:
		payload = {
			'headers': {
				'meta': {},
				'token': rnis_token			},
			'payload': {
				"unit_uuid": uuid_unit
			}
		}
		payload = json.dumps(payload)
		querystring = {"com.rnis.organizational_units.action.unit.get":""}
		headers = {'subject': "com.rnis.organizational_units.action.unit.get"}


		try:
			response = requests.request("POST", URL, data=payload, headers=headers, params=querystring)
			response = response.json()
			if response.get('success') is True:
				unit_name = str(response.get('payload').get('name_full')) # Полное наименование предприятия - обязательное поле
				unit_inn = str(response.get('payload').get('inn')) # ИНН предприятия - необязательное поле

				break
			else:
				print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),' !!!!!! Пытаюсь повторно получить название организации.....')
				logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+' !!!!!! Пытаюсь повторно получить название организации.....')
		except:
			pass
		index = index - 1
		if index == 0:
			break
		time.sleep(1)
	return uuid_unit, unit_name, unit_inn



#---------------------------------------------------------------------------------
# 5) Получить список организаций
#---------------------------------------------------------------------------------
def get_orgs_list(token_rnis,URL):
	URL = URL + "?com.rnis.organizational_units.action.carriers"
	while True:
		request = {
					'headers': {
						'meta': {

							'order': {},
							'filters': {
								'withComponent': 'kiutr'
							}
							# 'column_search': [{
							# 		'value': reg_num,
							# 		'column': 'state_number'
							# 	}],
							# 'response_data': ['items/uuid']
						},
						'token': token_rnis
					},
						'payload': {}
				}

		payload = json.dumps(request)
		querystring = {"com.rnis.organizational_units.action.carriers":""}
		headers = {"subject": "com.rnis.organizational_units.action.carriers", "content-type":"application/json"}
		response = requests.request("POST", URL, data=payload, headers=headers, params=querystring)



	return response



#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 6) Получить список нарядов в статусе обработки ДЕЙСТВУЕТ, в статусе обеспечения НЕ ОБЕСПЕЧЕН или НЕ ПОЛНОСТЬЮ ОБЕСПЕЧЕН за дату, по предприятию, номеру выхода, номеру маршрута и рег.номеру маршрута
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_uuid_orders(order_date , uuid_unit, turn, route_number, reg_route_number, token_rnis,URL):
	URL = URL + "?com.rnis.geo.action.order.list"
	while True:
		data = {'headers': {'meta':
					   {
						   'order':{'column':'turn','direction':'asc'},
						   'filters': {
							   'withCarriers': [uuid_unit],
							   'withComponent': 'kiutr',
							   'short': True,
							   # Если раскоментировать эти области,  то будут занаряживаться только не обеспеченные наряды
							   # 'withProcessingStatuses': ['active'],
							   # 'withProvisionStatuses': ['none', 'partial'],
							   "withPeriod": [ order_date, order_date ]
							},
						   'column_search':[
								{'value':turn,'column':'turn'},
								{'value':route_number,'column':'route_number'},
								{'value':reg_route_number,'column':'route_registration_number'}
							],
							'response_data':['items/uuid','items/number','items/turn']
					   },
				'token': token_rnis},
				'payload':{}
		}
		payload = json.dumps(data)
		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),payload)
		querystring = {"com.rnis.geo.action.order.list" : ""}
		headers = {'subject': "com.rnis.geo.action.order.list"}

		try:
			response = requests.request("POST", URL, data=payload, headers=headers, params=querystring)
			try:
				response.json().get('success')
				if response.json().get('success'):
					break
				else:
					print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),' !!!!!! Пытаюсь получить uuid план-наряда повторно ......')
					logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+
						  ' !!!!!! Пытаюсь получить uuid план-наряда повторно ......')
			except:
				pass
		except:
			pass

	if len(response.json().get('payload').get('items'))==0:
		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Не найден план-наряд за %s, выход %s, маршрут %s, рег.номер маршрута %s' % (order_date,turn,route_number,reg_route_number))
		return None
	else:
		# Возвращаем первый выбранный item из списка, если будут ошибки то надо делать проверку перебором
		# Структура {'uuid': '4cc8dc18-9ca0-11e9-b7c0-022516b20f8c', 'number': '2019-103', 'turn': 13}
		return response.json().get('payload').get('items')[0].get('uuid')

#-----------------------------------------------------------------------------------------------------------------------
# 7) Получить план-наряд по его uuid
#-----------------------------------------------------------------------------------------------------------------------
def get_order_in_rnis(orders_uuid, rnis_token, URL):
	URL = URL + "?com.rnis.geo.action.order.get"
	while True:
		request = {
			"headers": {
				"meta": {},
				"token": rnis_token
			},
			"payload": {
				"uuid": orders_uuid
			}
		}
		payload = json.dumps(request)
		querystring = {'com.rnis.geo.action.order.get':''}
		headers = {'subject': 'com.rnis.geo.action.order.get'}

		try:
			response = requests.request('POST', URL, data=payload, headers=headers, params=querystring)
			try:
				response.json().get('success')
				if response.json().get('success'):
					break
				else:
					print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь получить план-наряд повторно........')
					logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+'Пытаюсь получить план-наряд повторно........')
			except:
				pass
		except:
			pass
	return response.json().get('payload')


#-----------------------------------------------------------------------------------------------------------------------
# 8) Обновить план-наряд
#-----------------------------------------------------------------------------------------------------------------------
def update_order_in_rnis(array,rnis_token,URL):
	URL = URL + "?com.rnis.geo.action.order.update"
	while True:
		payload = {
			"headers": {
				"meta": {},
				"token": rnis_token},
			"payload": array
		}

		payload_json = json.dumps(payload)
		querystring = {'com.rnis.geo.action.order.update':''}
		headers = {'subject': 'com.rnis.geo.action.order.update'}

		try:
			response = requests.request('POST', URL, data=payload_json, headers=headers, params=querystring)
			if response.json().get('success'):
				break
			else:
				print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь обновить план-наряд повторно........')
				logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")+'Пытаюсь обновить план-наряд повторно........')
		except:
			pass
	return response.json()

#-----------------------------------------------------------------------------------------------------------------------
# 9 ) Получить автоматический зачет по uuid план-наряда (get_order_execution_info - com.rnis.geo.action.order_execution.list)
#-------------------------------------------------------------------------------------------------------------------------
def get_order_execution_info(uuid_order, token_rnis,URL):
	URL = URL + "?com.rnis.geo.action.order_execution.list"
	while True:
		headers = {'meta': {}}
		headers.update({'token': token_rnis})
		headers.get('meta').update({'filters': {}})
		headers.get('meta').get('filters').update({'withOrders': [uuid_order]})
		headers.get('meta').update({"response_data": ['items']})
		request = {}
		request.update({'headers': headers})
		payload = {}
		request.update({'payload': payload})
		request = json.dumps(request)
		querystring = {"com.rnis.geo.action.order_execution.list": ""}
		headers_ = {'subject': "com.rnis.geo.action.order_execution.list", "content-type": "application/json"}

		try:
			response = requests.request("POST", URL, data=request, headers=headers_, params=querystring, timeout=40)
		except:
			print('!!!!!!!! Unterminated string starting at:%s '%(uuid_order))

			break
		if response.json().get('success'):

			break
		else:
			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь получить статусы выполнения повторно для order_uuid: ',uuid_order)
			logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + 'Пытаюсь получить статусы выполнения повторно для order_uuid: ',uuid_order)

	if response.json():
		return response.json()

	# token_rnis = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJSTklTIiwiYXVkIjoiaHR0cDpcL1wvcm5pcy5jb20iLCJpYXQiOjE1NjYyMjEwNTQsIm5iZiI6MTU2NjEzNDY1NCwiaW5mbyI6IntcInVzZXJcIjp7XCJ1dWlkXCI6XCI4MTY4ZmM0YS1iOWJiLTExZTktYTViZS0wMmY0MmIzNTQyNjNcIixcImxvZ2luXCI6XCJSTklTMUNcIixcImNvbXBvbmVudFwiOlwib3BlcmF0b3JcIixcImlzX3N5c3RlbVwiOmZhbHNlLFwiaXNfc3VwZXJ2aXNvclwiOmZhbHNlLFwiaXNfc2VtaV9jb25maXJtZWRcIjpmYWxzZSxcImluZm9cIjp7fX19In0.mskyrEWTMRnRw_2ugtpQR_6VDI-dazjlDgWtKgz3fUs'
# URL = 'https://api.rnis.mosreg.ru/ajax/request'
# print(get_order_execution_info('7da72736-bd4d-11e9-b312-02f42b341fa9', token_rnis,URL))

#--------------------------------------------------------------------------------------------
# 10) Получить ручной зачет по uuid план-наряда (get_order_info - com.rnis.geo.action.order.get )
#--------------------------------------------------------------------------------------------
def get_order_info(uuid_order, token_rnis, URL):
	URL = URL + "?com.rnis.geo.action.order.get"
	headers = {'meta': {}}
	headers.update({'token': token_rnis})
	# headers.get('meta').update({'response_data': ['order_recalc/shifts']})
	request = {}
	request.update({'headers': headers})
	payload = {'uuid': uuid_order }
	payload.update({'execution_status': 1})
	request.update({'payload': payload})
	request = json.dumps(request)
	querystring = {"com.rnis.geo.action.order.get": ""}
	headers_ = {'subject': "com.rnis.geo.action.order.get", "content-type": "application/json"}

	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
	if response.json().get('success'):
		response.json().get('payload')

		return response.json()
	else:
		print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ': Не удалось найти наряд - ' + uuid_order)
		logging.info(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ': Не удалось найти наряд - ' + uuid_order)


# token_rnis = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJSTklTIiwiYXVkIjoiaHR0cDpcL1wvcm5pcy5jb20iLCJpYXQiOjE1NjYyMjEwNTQsIm5iZiI6MTU2NjEzNDY1NCwiaW5mbyI6IntcInVzZXJcIjp7XCJ1dWlkXCI6XCI4MTY4ZmM0YS1iOWJiLTExZTktYTViZS0wMmY0MmIzNTQyNjNcIixcImxvZ2luXCI6XCJSTklTMUNcIixcImNvbXBvbmVudFwiOlwib3BlcmF0b3JcIixcImlzX3N5c3RlbVwiOmZhbHNlLFwiaXNfc3VwZXJ2aXNvclwiOmZhbHNlLFwiaXNfc2VtaV9jb25maXJtZWRcIjpmYWxzZSxcImluZm9cIjp7fX19In0.mskyrEWTMRnRw_2ugtpQR_6VDI-dazjlDgWtKgz3fUs'
# URL = 'https://api.rnis.mosreg.ru/ajax/request'
# print(get_order_info('7da72736-bd4d-11e9-b312-02f42b341fa9', token_rnis,URL))



# #---------------------------------------------------------------------------------
# # Получить id_пользователя и организацию по его табельному номеру
# #---------------------------------------------------------------------------------
# def get_id_driver (tabelnum, token_rnis, uuid_unit):
# 	headers = {"meta": {"filters":{"withComponent":"kiutr"},"response_data":["items/uuid","items/info/surname","items/info/name","items/info/second_name","items/info/personnel_number","items/info/unit_uuid"]}}
# 	uuid_units=[]
# 	uuid_units.append(uuid_unit)
# 	headers.get('meta').get('filters').update({"withUnits":uuid_units})
# 	headers.update({'token': token_rnis})
# 	per_number = {"column": "info.personnel_number"}
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),per_number)
# 	per_number.update({'value': tabelnum})
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),per_number)
# 	column_search = []
# 	column_search.append(per_number)
# 	headers.get('meta').update({'column_search': column_search})
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),headers)
# 	payload = {}
# 	request = {}
# 	request.update({'headers': headers, 'payload': payload})
# 	payload_1 = json.dumps(request)
# 	# print (payload_1)
# 	url = 'https://api.rnis.mosreg.ru/ajax/request'
# 	querystring = {"com.rnis.auth.action.user.list":""}
# 	headers = {"subject": "com.rnis.auth.action.user.list", "content-type":"application/json"}
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 	response = requests.request("POST", url, data=payload_1, headers=headers, params=querystring)
# 	return response.json()

# #---------------------------------------------------------------------------------
# # Получить uuid пользователя, организацию и ФИО по его табельному номеру
# #---------------------------------------------------------------------------------
# def get_driver_in_rnis(tabel_num, token_rnis):
# 	while True:
# 		request = {
# 					'headers': {
# 						'meta': {
#
# 							'order': {
# 								'column': 'info.position_type',
# 								'direction': 'asc'
# 							},
# 							'filters': {
# 								'withPositionTypes': ['driver'],
# 								'withComponent': 'kiutr'
# 							},
# 							'column_search': [{
# 									'value': tabel_num,
# 									'column': 'info.personnel_number'
# 								}, {
# 									'value': 'водитель',
# 									'column': 'info.position_name'
# 								}
# 							],
# 							'response_data': ['items/uuid', 'items/info/surname', 'items/info/name', 'items/info/second_name', 'items/info/personnel_number', 'items/info/unit_uuid']
# 						},
# 						'token': token_rnis
# 					},
# 						'payload': {}
# 				}
#
# 		payload = json.dumps(request)
# 		querystring = {"com.rnis.auth.action.user.list":""}
# 		headers = {"subject": "com.rnis.auth.action.user.list", "content-type":"application/json"}
# 		response = requests.request("POST", URL, data=payload, headers=headers, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь получить водителя повторно........')
#
# 	if len(response.json().get('payload').get('items')) == 0:
# 		print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Водитель с табельным номером <%s> не найден' % (tabel_num))
# 		return {'uuid': 'none', 'info': {'name': 'none','second_name': 'none', 'surname': 'none','unit_uuid': 'none','personnel_number': 'none'}}
# 	else:
# 		if 	len(response.json().get('payload').get('items')) > 1:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'В РНИС присутсвуют двойники водителя с табельным номером %s' % (tabel_num))
# 		# Возвращаем первый выбранный item из списка, если будут ошибки то надо делать проверку перебором
# 		# Структура 'uuid': '6e96cbce-0076-11e8-a1f8-02f42bfc2b03', 'info': {'name': 'Петр','second_name': 'Борисович',
# 		# 'surname': 'Муравьев','unit_uuid': 'f2e58840-9931-11e7-a67f-70182a388da1','personnel_number': '40403'}
# 		return response.json().get('payload').get('items')[0]
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_driver_in_rnis('0000_7498', get_token()))
# # get_driver_in_rnis('0000_7607',get_token())







# driver_org = get_id_driver('09232', get_token()).get('payload').get('items')[0].get('info').get('unit_uuid')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),driver.get('payload').get('items')[0].get('info').get('unit_uuid'))
# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),driver_org)
# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_name_org(driver_org, get_token()).get('payload').get('name_full'))

# # Получить по рег.номеру uuid ТС
# #----------------------------------------
# def get_uuid_vehicle (reg_number,token_rnis):
# 	headers = {'meta': {"filters": {"withComponent": "kiutr"},"response_data": ["items/uuid","items/unit_uuid","items/state_number", "items/garage_number"],  "column_search": [{"column": "state_number"}]}}
# 	headers.get('meta').get('column_search')[0].update({'value': reg_number})
# 	headers.update({'token': token_rnis})
# 	payload = {}
# 	request = {'payload': {}}
# 	request.update({'headers': headers})
# 	payload_2 = json.dumps(request)
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),payload_2)
# 	url = 'https://api.rnis.mosreg.ru/ajax/request'
# 	querystring = {"com.rnis.vehicles.action.vehicle.list":""}
# 	headers = {'subject': "com.rnis.vehicles.action.vehicle.list"}
# 	response = requests.request("POST", url, data=payload_2, headers=headers, params=querystring)
# 	return response.json().get('payload')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_uuid_vehicle('р562рм750',get_token()))
#
# # Получить наряд за сутки по организации номеру маршрута,  выходу, статусу обработки
# #-----------------------------------------------------------------------------------
#
# def get_uuid_order (order_date , uuid_unit, turn, route_number, token_rnis):
# 	headers = {'meta':
# 				   {'filters':
# 						{'withComponent': 'kiutr',
# 						 'short': True},
# 						 # 'withProcessingStatuses':['draft']},
# 					"response_data": ['items/uuid','items/number','items/date', 'items/turn','items/shifts/runs/route_number','items/shifts/runs/route_registration_number']}}
#
# 	uuid_org = []
# 	uuid_org.append(uuid_unit)
# 	headers.get('meta').get('filters').update({'withCarriers' : uuid_org} )
#
# 	today = datetime.datetime.strptime (order_date , "%Y-%m-%d")
# 	# tomorrow = today + datetime.timedelta(days=1)
# 	withPeriod = [today.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d')]
# 	headers.get('meta').get('filters').update({'withPeriod': withPeriod})
# 	column_search = []
# 	column_search.append({"value": str(int(turn)),"column": "turn"})
# 	column_search.append({"value": route_number, "column": "route_number"})
# 	headers.get('meta').update({'column_search' : column_search})
# 	headers.update({'token': token_rnis})
# 	request = {'payload': {}}
# 	request.update({'headers': headers})
# 	payload_2 = json.dumps(request)
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),payload_2)
# 	url = 'https://api.rnis.mosreg.ru/ajax/request'
# 	querystring = {"com.rnis.geo.action.order.list":""}
# 	headers = {'subject': "com.rnis.geo.action.order.list"}
# 	response = requests.request("POST", url, data=payload_2, headers=headers, params=querystring)
# 	return response.json().get('payload')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_uuid_order('2019-06-07', 'f2e58840-9931-11e7-a67f-70182a388da1', '007', '508', get_token()))
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_uuid_order('2019-06-07', '93387cc2-8f4f-11e7-b168-9e213aac5ff4', '001', '308', get_token()))

# #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# # Получить список нарядов в статусе обработки ДЕЙСТВУЕТ, в статусе обеспечения НЕ ОБЕСПЕЧЕН или НЕ ПОЛНОСТЬЮ ОБЕСПЕЧЕН за дату, по предприятию, номеру выхода, номеру маршрута и рег.номеру маршрута
# #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# def get_uuid_orders(order_date , uuid_unit, turn, route_number, reg_route_number, token_rnis):
# 	while True:
# 		data = {'headers': {'meta':
# 					   {
# 						   'order':{'column':'turn','direction':'asc'},
# 						   'filters': {
# 							   'withCarriers': [uuid_unit],
# 							   'withComponent': 'kiutr',
# 							   'short': True,
# 							   # 'withProcessingStatuses': ['active'],
# 							   # 'withProvisionStatuses': ['none', 'partial'],
# 							   "withPeriod": [ order_date, order_date ]
# 							},
# 						   'column_search':[
# 								{'value':turn,'column':'turn'},
# 								{'value':route_number,'column':'route_number'},
# 								{'value':reg_route_number,'column':'route_registration_number'}
# 							],
# 							'response_data':['items/uuid','items/number','items/turn']
# 					   },
# 				'token': token_rnis},
# 				'payload':{}
# 		}
# 		payload = json.dumps(data)
# 		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),payload)
# 		querystring = {"com.rnis.geo.action.order.list":""}
# 		headers = {'subject': "com.rnis.geo.action.order.list"}
# 		response = requests.request("POST", URL, data=payload, headers=headers, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else: print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь получить uuid план-наряда повторно........')
#
# 	if len(response.json().get('payload').get('items'))==0:
# 		print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Не найден план-наряд за %s, для предприятия %s, выход %s, маршрут %s, рег.номер маршрута %s' % (order_date,get_name_org(uuid_unit,token_rnis).get('payload').get('name'),turn,route_number,reg_route_number))
# 		return {'uuid': 'None', 'number': 'None', 'turn': 13}
# 	else:
# 		# Возвращаем первый выбранный item из списка, если будут ошибки то надо делать проверку перебором
# 		# Структура {'uuid': '4cc8dc18-9ca0-11e9-b7c0-022516b20f8c', 'number': '2019-103', 'turn': 13}
# 		return response.json().get('payload').get('items')[0]
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_uuid_orders('2019-07-02','64903f9c-992f-11e7-8df6-8d2c5d9e8a62',3,'003','169', get_token()))


# #-----------------------------------------------------------------------------------------------------------------------
# # Получить план-наряд по его uuid
# #-----------------------------------------------------------------------------------------------------------------------
# def get_order_in_rnis(orders_uuid, token_rnis):
# 	request = {
# 		"headers": {
# 			"meta": {},
# 			"token": token_rnis
# 		},
# 		"payload": {
# 			"uuid": orders_uuid
# 		}
# 	}
# 	payload = json.dumps(request)
# 	querystring = {'com.rnis.geo.action.order.get':''}
# 	headers = {'subject': 'com.rnis.geo.action.order.get'}
# 	response = requests.request('POST', URL, data=payload, headers=headers, params=querystring)
# 	return response.json().get('payload')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_order_in_rnis('81c996d2-9ca0-11e9-86cc-022516b20f8c',get_token()))




# # Получить по uuid_rnis перевозчика все его маршруты (статус "Утвержден")
# #----------------------------------------
# def get_uuid_routes_list (uuid_unit,token_rnis):
# 	headers = {'meta': {"filters": {"withComponent": "kiutr"}}}
# 	headers.get('meta').get('filters').update({'withStatus': ['1abd2f98-7845-11e7-be3f-3a4e0357cc4a']})  # Статус "Утвержден"
# 	headers.get('meta').get('filters').update({'withOriginalUnits': [uuid_unit]})
# 	headers.get('meta').get('filters').update({'withoutGeometry': True})
# 	headers.get('meta').update({'response_data': ["items/uuid"]})
# 	headers.update({'token': token_rnis})
# 	request = {}
# 	request.update({'headers': headers})
# 	request.update({'payload':{}})
# 	request = json.dumps(request)
# 	querystring = {"com.rnis.geo.action.route.list":""}
# 	headers_ = {'subject': "com.rnis.geo.action.route.list", "content-type":"application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	return response.json().get('payload').get('items')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_uuid_routes_list('b88e6e44-992e-11e7-89f1-23fc3f340f92',get_token()))


# # Получить по uuid_rnis маршрута получить расписания
# #----------------------------------------
# def get_schedules_list (uuid_unit,token_rnis):
# 	headers = {'meta': {}}
# 	headers.update({'token': token_rnis})
# 	headers.get('meta').update({'filters':{}})
# 	headers.get('meta').get('filters').update({'withRoute':uuid_unit})
# 	headers.get('meta').update({'response_data': [
# 		"items/uuid",
# 		"items/route_number",
# 		"items/route_registration_number",
# 		"items/date_from",
# 		"items/date_to",
# 		"items/created_at",
# 		"items/turns"
# 	]})
# 	request = {}
# 	request.update({'headers': headers})
# 	payload = {}
# 	request.update({'payload':payload})
# 	request = json.dumps(request)
# 	querystring = {"com.rnis.geo.action.schedule.list":""}
# 	headers_ = {'subject': "com.rnis.geo.action.schedule.list", "content-type":"application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	return response.json().get('payload').get('items')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_schedules_list ('d1626a9c-eb77-11e7-a52f-71bf2ff230d6',get_token()))


# # Получить по uuid_rnis расписания атрибуты расписания (дата начала действия расписания,
# # дата окончания действия расписания, идентификатор расписания в РНИС,
# # номер маршрута, регистрационный номер маршрута, )
# #----------------------------------------
# def get_schedule (uuid_schedule,token_rnis):
# 	headers = {'meta': {}}
# 	headers.update({'token': token_rnis})
# 	request = {}
# 	request.update({'headers': headers})
# 	payload = {'uuid':uuid_schedule }
# 	request.update({'payload':payload})
# 	request = json.dumps(request)
# 	querystring = {"com.rnis.geo.action.schedule.get":""}
# 	headers_ = {'subject': "com.rnis.geo.action.schedule.get", "content-type":"application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	return response.json().get('payload')
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_schedule('070f39b4-ec30-11e7-8988-d13e5c496226',get_token()))


# # Получить по uuid_rnis расписания получить вариант расписания
# #----------------------------------------
# def get_schedule_turn (uuid_schedule,token_rnis):
# 	headers = {'meta': {}}
# 	headers.update({'token': token_rnis})
# 	headers.get('meta').update({'filters':{}})
# 	headers.get('meta').get('filters').update({'withSchedule':uuid_schedule})
# 	# headers.get('meta').update({'response_data': [
# 	# 	"items/uuid",
# 	# 	"items/route_number",
# 	# 	"items/route_registration_number",
# 	# 	"items/date_from",
# 	# 	"items/date_to",
# 	# 	"items/created_at",
# 	# 	"items/turns"
# 	# ]})
# 	request = {}
# 	request.update({'headers': headers})
# 	payload = {}
# 	request.update({'payload':payload})
# 	request = json.dumps(request)
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 	querystring = {"com.rnis.geo.action.schedule_turn.list":""}
# 	headers_ = {'subject': "com.rnis.geo.action.schedule_turn.list", "content-type":"application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_schedule_turn ('1f1a9c2c-445c-11e8-94c9-02f42b21b63e',get_token()))

#-----------------------------------------------------------------------------------------
# Получить список всех закрытых план-нарядов по организации и за определенную дату
#----------------------------------------------------------------------------------------
def get_list_orders_close (uuid_unit, orders_date, token_rnis,URL):
	URL = URL + "?com.rnis.geo.action.order.list"
	while True:
		headers = {'meta': {}}
		headers.update({'token': token_rnis})
		headers.get('meta').update({'filters': {}})
		headers.get('meta').get('filters').update({'withComponent': "kiutr"})
		headers.get('meta').get('filters').update({'short': False})
		headers.get('meta').get('filters').update({'withPeriod': [orders_date, orders_date]})
		headers.get('meta').get('filters').update({'withProcessingStatuses': ['ended']})
		headers.get('meta').get('filters').update({'withCarriers': [uuid_unit]})
		headers.get('meta').update({'response_data': [
			"items/uuid",
			"items/route_number",
			"items/route_registration_number",
			"items/turn"
		]})
		headers.get('meta').update({'order': {}})
		headers.get('meta').get('order').update({'column':'route_number'})
		headers.get('meta').get('order').update({'direction': 'desc'})
		headers.get('meta').get('order').update({'column': 'turn'})
		headers.get('meta').get('order').update({'direction': 'desc'})
		request = {}
		request.update({'headers': headers})
		payload = {}
		request.update({'payload': payload})
		request = json.dumps(request)
		querystring = {"com.rnis.geo.action.order.list": ""}
		headers_ = {'subject': "com.rnis.geo.action.order.list", "content-type": "application/json"}

		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
		if response.json().get('success'):

			break
		else: print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь получить список выходов повторно')
	return response.json()
# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_list_orders ('b88e6e44-992e-11e7-89f1-23fc3f340f92','2019-06-21',get_token()))
# file = open("some.txt", "w")
# file.write(str(get_list_orders ('','2019-06-21',get_token())))
# file.close()
#

#
# # Получить информацию о водителях по uuid предприятия
# #---------------------------------------------------------
# def get_list_drivers (uuid_unit, token_rnis):
# 	while True:
# 		headers = {'meta': {}}
# 		# headers.get('meta').update({'response_data': ['items/uuid','items/info/name', 'items/info/second_name', 'items/info/surname','items/info/personnel_number']})
# 		headers.get('meta').update({'filters': {}})
# 		headers.get('meta').get('filters').update({'withUnits': [uuid_unit]})
# 		headers.get('meta').get('filters').update({'withComponent':'kiutr'})
# 		headers.update({'token': token_rnis})
# 		request = {}
# 		request.update({'headers': headers})
# 		request.update({'payload': {}})
# 		request = json.dumps(request)
# 		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 		querystring = {"com.rnis.auth.action.user.list": ""}
# 		headers_ = {'subject': "com.rnis.auth.action.user.list", "content-type": "application/json"}
# 		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else: print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно получить список водителей.....')
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_list_drivers ('1dac746a-992f-11e7-a876-64cf03141d88',get_token()))
# # file = open("some.txt", "w")
# # file.write(str(get_list_drivers ('1dac746a-992f-11e7-a876-64cf03141d88',get_token())))
# # file.close()

# # Получить гаражные и регистрационные номера ТС по uuid предприятия
# #------------------------------------------------------------------
# def get_list_vehicles (uuid_unit, token_rnis):
# 	headers = {'meta': {}}
# 	headers.get('meta').update({'response_data': [ "items/uuid", "items/state_number", "items/garage_number"]})
# 	headers.get('meta').update({'filters': {}})
# 	headers.get('meta').get('filters').update({'withUnit': [uuid_unit]})
# 	headers.get('meta').get('filters').update({'withComponent': 'kiutr'})
# 	headers.get('meta').update({'order':{'column':'state_number','direction':'asc'}})
# 	headers.update({'token': token_rnis})
#
# 	request = {}
# 	request.update({'headers': headers})
# 	request.update({'payload': {}})
# 	request = json.dumps(request)
# 	# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 	querystring = {"com.rnis.vehicles.action.vehicle.list": ""}
# 	headers_ = {'subject': "com.rnis.vehicles.action.vehicle.list", "content-type": "application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_list_vehicles('1dac746a-992f-11e7-a876-64cf03141d88',get_token()))







# # Обновить запись о водителе (update_driver_info - com.rnis.geo.action.order.get )
# #--------------------------------------------------------------------------------------------
# def update_driver_info(uuid_driver, tabelNum, surname, firstname, partname, token_rnis):
# 	headers = {'meta': {}}
# 	headers.update({'token': token_rnis})
# 	# headers.get('meta').update({'response_data': ['order_recalc/shifts']})
# 	request = {}
# 	request.update({'headers': headers})
# 	payload = {'uuid': uuid_order }
# 	payload.update({'execution_status': 1})
# 	request.update({'payload': payload})
# 	request = json.dumps(request)
# 	querystring = {"com.rnis.geo.action.order.get": ""}
# 	headers_ = {'subject': "com.rnis.geo.action.order.get", "content-type": "application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	if response.json().get('success'):
# 		response.json().get('payload')
#
# 		return response.json()
# 	else: print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),datetime.datetime.now(), ': Не удалось найти наряд - ',uuid_vehicles)
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_order_info('861303ea-93a4-11e9-b112-02f42bae1169', get_token()))


# # Сделать новую запись о водителе (create_driver_info - com.rnis.geo.action.order.get )
# #--------------------------------------------------------------------------------------------
# def create_driver_info(tabelNum, surname, firstname, partname, token_rnis):
# 	headers = {'meta': {}}
# 	headers.update({'token': token_rnis})
# 	# headers.get('meta').update({'response_data': ['order_recalc/shifts']})
# 	request = {}
# 	request.update({'headers': headers})
# 	payload = {'uuid': uuid_order }
# 	payload.update({'execution_status': 1})
# 	request.update({'payload': payload})
# 	request = json.dumps(request)
# 	querystring = {"com.rnis.geo.action.order.get": ""}
# 	headers_ = {'subject': "com.rnis.geo.action.order.get", "content-type": "application/json"}
# 	response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 	if response.json().get('success'):
# 		response.json().get('payload')
#
# 		return response.json()
# 	else: print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),datetime.datetime.now(), ': Не удалось найти наряд - ',uuid_vehicles)
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_order_info('861303ea-93a4-11e9-b112-02f42bae1169', get_token()))
#

# # Поиск водителя в РНИС по предприятию и табельному номеру
# #--------------------------------------------------------------------------------------------
# def find_driver_in_rnis(tabelNum, uuid_unit, token_rnis):
# 	while True:
# 		headers = {'meta': {}}
# 		headers.get('meta').update({'filters': {}})
# 		headers.get('meta').get('filters').update({'withUnits': [uuid_unit]})
# 		headers.get('meta').get('filters').update({'withComponent':'kiutr'})
# 		column_search =[{'value': tabelNum ,'column': 'info.personnel_number'}]
# 		headers.get('meta').update({'column_search':column_search})
#
# 		headers.update({'token': token_rnis})
# 		# headers.get('meta').update({'response_data': ['order_recalc/shifts']})
# 		request = {}
# 		request.update({'headers': headers})
# 		payload = {}
# 		request.update({'payload': payload})
# 		request = json.dumps(request)
# 		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 		querystring = {"com.rnis.auth.action.user.list": ""}
# 		headers_ = {'subject': "com.rnis.auth.action.user.list", "content-type": "application/json"}
# 		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),response.text)
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно водителя.....')
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),find_driver_in_rnis('2995','d138f210-3ccd-11e7-b9d9-b9169ef068b2', get_token()))


# # Поиск водителя в РНИС по предприятию, табельному номеру и фамилии
# #--------------------------------------------------------------------------------------------
# def find_name_driver_in_rnis(tabelNum, surname, uuid_unit, token_rnis):
# 	while True:
# 		headers = {'meta': {}}
# 		headers.get('meta').update({'filters': {}})
# 		headers.get('meta').get('filters').update({'withUnits': [uuid_unit]})
# 		headers.get('meta').get('filters').update({'withComponent':'kiutr'})
# 		column_search =[{'value': tabelNum ,'column': 'info.personnel_number'},{'value': surname ,'column': 'info.surname'},]
# 		headers.get('meta').update({'column_search':column_search})
#
# 		headers.update({'token': token_rnis})
# 		# headers.get('meta').update({'response_data': ['order_recalc/shifts']})
# 		request = {}
# 		request.update({'headers': headers})
# 		payload = {}
# 		request.update({'payload': payload})
# 		request = json.dumps(request)
# 		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 		querystring = {"com.rnis.auth.action.user.list": ""}
# 		headers_ = {'subject': "com.rnis.auth.action.user.list", "content-type": "application/json"}
# 		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),response.text)
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно водителя.....')
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),find_name_driver_in_rnis('00000388','Тангатаров','b7b3c774-366f-11e8-ac50-02f42b1db541', get_token()))


# # Получить секцию Учет (positions)  для карточки водителя по uuid водителя
# #--------------------------------------------------------------------------------------------
# def get_position_in_rnis(driver_uuid, token_rnis):
# 	while True:
# 		headers = {'meta': {}}
# 		headers.update({'token': token_rnis})
# 		request = {}
# 		request.update({'headers': headers})
# 		payload = {'user_id': driver_uuid}
# 		request.update({'payload': payload})
# 		request = json.dumps(request)
# 		# print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 		querystring = {"com.rnis.auth.action.user.positions": ""}
# 		headers_ = {'subject': "com.rnis.auth.action.user.positions", "content-type": "application/json"}
# 		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),response.text)
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно получить карточку водителя...')
# 	return response.json()
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),get_position_in_rnis('2c3de662-4898-11e8-9324-02f42b8c5316', get_token()))
#
# # Обновить карточку водителя по uuid водителя
# #--------------------------------------------------------------------------------------------
# def update_driver_in_rnis(payload_info, token_rnis):
# 	# payload_info = json.loads(payload_info)
# 	while True:
# 		headers = {'meta': {}}
# 		headers.update({'token': token_rnis})
# 		request = {}
# 		request.update({'headers': headers})
#
# 		request.update({'payload': payload_info})
# 		request = json.dumps(request)
# 		print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),request)
# 		querystring = {"com.rnis.auth.action.user.update": ""}
# 		headers_ = {'subject': "com.rnis.auth.action.user.update", "content-type": "application/json"}
# 		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
# 		if response.json().get('success'):
# 			break
# 		else:
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),response.text)
# 			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно обновить карточку водителя...')
# 	return response.json()
#
#
# string_3 = {
# 	'uuid': '700c8598-0076-11e8-b6c4-02f42bfc2b03',
# 	'component': 'kiutr',
# 	'is_system': False,
# 	'is_supervisor': False,
# 	'is_virtual': True,
# 	'is_semi_confirmed': False,
# 	'info': {
# 		'name': 'Владимир',
# 		'second_name': 'Алексеевич',
# 		'surname': 'Бахтов'
# 	},
# 	'driver_license': {},
# 	'dismissals': [],
# 	'roles': [],
# 	'created_at': '2018-01-23T22:48:52+03:00',
# 	'updated_at': '2018-01-23T22:48:52+03:00',
# 	'positions': [{
# 			'uuid': '700d18dc-0076-11e8-b1e5-02f42bfc2b03',
# 			'user_uuid': '700c8598-0076-11e8-b6c4-02f42bfc2b03',
# 			'unit_uuid': '64903f9c-992f-11e7-8df6-8d2c5d9e8a62',
# 			'position_uuid': '63e97398-0076-11e8-b7ee-02f42badd6cc',
# 			'position_type': 'driver',
# 			'position_name': 'Водитель',
# 			'personnel_number': '0000_028704',
# 			'is_main_position': True,
# 			'hired_at': '2018-01-23T00:00:00+03:00'
# 		}
# 	],
# 	'is_blocked': False,
# 	'blocked_at': None,
# 	'tachographs': []
# }
#
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),update_driver_in_rnis(string_3, get_token()))
#
#
# payload_string = """{
# 		"uuid": "2c3de662-4898-11e8-9324-02f42b8c5316",
# 		"component": "kiutr",
# 		"is_system": false,
# 		"is_supervisor": false,
# 		"is_virtual": true,
# 		"is_semi_confirmed": false,
# 		"info": {
# 			"name": "Водитель_update2",
# 			"surname": "007_update2"
# 		},
# 		"driver_license": {},
# 		"dismissals": [],
# 		"work_graphics": [],
# 		"roles": [],
# 		"created_at": "2018-04-25T17:51:44+03:00",
# 		"updated_at": "2019-02-27T11:12:27+03:00",
# 		"positions": [{
# 				"uuid": "2c5c3be4-4898-11e8-a997-02f42b8c5316",
# 				"user_uuid": "2c3de662-4898-11e8-9324-02f42b8c5316",
# 				"unit_uuid": "7c160ac0-04be-11e8-8ed3-02f42b9dd6bc",
# 				"position_uuid": "5fb91cec-4897-11e8-9c14-02f42ba20283",
# 				"position_type": "driver",
# 				"position_name": "Водитель",
# 				"personnel_number": "7_update",
# 				"is_main_position": true,
# 				"hired_at": "2018-04-25T00:00:00+03:00"
# 			}
# 		],
#
# 		"is_blocked": false,
# 		"tachographs": [],
# 		"blocked_at": null
# 	}"""
# # print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),update_driver_in_rnis(payload_string, get_token()))
#

#--------------------------------------------------------------------------------------------
# Создать карточку водителя
#--------------------------------------------------------------------------------------------
def create_driver_in_rnis(payload_info, token_rnis,URL):
	URL = URL + "?com.rnis.auth.action.user.create"
	while True:

		request = {"headers":{"meta":{},"token":token_rnis},"payload":payload_info}
		request = json.dumps(request)
		# print(request)
		querystring = {"com.rnis.auth.action.user.create":""}
		headers_ = {"subject":"com.rnis.auth.action.user.create", "content-type": "application/json",}
		response = requests.request("POST", URL, data=request, headers=headers_, params=querystring)
		if response.json().get('success'):
			break
		else:
			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),response.text)
			print(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),'Пытаюсь повторно создать карточку водителя ...')

	return response.json()