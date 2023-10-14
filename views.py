# by Amir Hossein Navazi

from django.http import HttpResponse , JsonResponse
from django.conf import settings
import requests
import json

from django.shortcuts import redirect

ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"

# Optional Data
metadata = {
	"mobile": "09123456789",  # Buyer phone number Must start with 09
	"email": "example@example.com",  # Buyer Email
	"order_id": "1234",  # Order Id
}
currency = "IRR"  # or "IRT"

# کد مرچنت خود را در فایل settings وارد کنید

# Required Data
amount = 2000  # Based on your currency
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
CallbackURL = 'http://127.0.0.1:8000/verify/'


# Important: need to edit for a real server.


def send_request(request):
	data = {
		"merchant_id": settings.MERCHANT,
		"amount": amount,
		"currency": currency,
		"description": description,
		"callback_url": CallbackURL,
		"metadata": metadata
	}
	data = json.dumps(data)
	# set content length by data
	headers = {'content-type': 'application/json', 'accept': 'application/json'}
	try:
		response = requests.post(
			ZP_API_REQUEST, data=data, headers=headers, timeout=10)
		response = response.json()
		err = response["errors"]
		if err:
			return JsonResponse(err, content_type="application/json",safe=False)
		if response['data']['code'] == 100:
			url = ZP_API_STARTPAY + str(response['data']['authority'])
			return redirect(url)
		else:
			return JsonResponse(json.dumps({'status': False, 'code': str(response['data']['code'])}), safe=False)
		return JsonResponse(response)

	except requests.exceptions.Timeout:
		data = json.dumps({'status': False, 'code': 'timeout'})
		return HttpResponse(data)
	except requests.exceptions.ConnectionError:
		data = json.dumps({'status': False, 'code': 'اتصال برقرار نشد'})
		return HttpResponse(data)


def verify(request):
	authority = request.GET.get('Authority')
	status = request.GET.get('Status')
	if status == "NOK":
		return HttpResponse(json.dumps({'status': "پرداخت ناموفق"}))
	data = {
		"merchant_id": settings.MERCHANT,
		"amount": amount,
		"authority": authority,
	}
	data = json.dumps(data)
	headers = {'content-type': 'application/json', 'accept': 'application/json'}
	try:
		response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
		response = response.json()
		err = response["errors"]
		if err:
			return JsonResponse(err, content_type="application/json",safe=False)
		if response['data']['code'] == 100:
			data = json.dumps({'status': True, 'first_time_verify': True, 'ref_id': response['data']['ref_id']})
		else:
			data = json.dumps({'status': False, 'data': response})
		return JsonResponse(data, safe=False)

	except requests.exceptions.ConnectionError:
		data = json.dumps({'status': False, 'code': 'اتصال برقرار نشد'})
		return HttpResponse(data)
