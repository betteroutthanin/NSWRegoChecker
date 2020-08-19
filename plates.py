import requests
import json
import http.cookiejar

def Plates(numberPlate):
    headers = {
            'authority': 'my.service.nsw.gov.au',
            'method': 'GET',
            'path': '/MyServiceNSW/index',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'if-modified-since': 'Wed, 19 Aug 2020 11:10:13 GMT',
            'referer': 'https://www.service.nsw.gov.au/transaction/check-vehicle-registration',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
        }

    session = requests.Session()    
    session.headers.update(headers)
    
    # step 1 - extract the vid and csrf
    response1 = session.get('https://my.service.nsw.gov.au/MyServiceNSW/index#/rms/freeRegoCheck/details')            
    vid = GetThis('"vid":"', '"', response1.content)
    csrf = GetThis('"csrf":"', '"', response1.content)

    # step 2 - create a RMS transaction ID
    bodyjson2 = {
        "action": "RMSWrapperCtrl",
	    "method": "createRMSTransaction",
	    "data": ["{\"ipAddress\":\"50e2df348c3b2181dfa788187e5d16f730a184a8835ef4b6d9bc3ac8b8095a82\",\"transactionName\":\"FREEREGCHK\",\"outletNumber\":\"\"}"],
	    "type": "rpc",
	    "tid": 6,
	    "ctx": {
		    "csrf": csrf,
		    "vid": vid,
		    "ns": "",
		    "ver": 34
	    }        
    }
    response2 = session.post('https://my.service.nsw.gov.au/MyServiceNSW/apexremote', json = bodyjson2)    
    transactionToken = GetThis('"statusObject":"', '"', response2.content)

    # Step 3 - get the jam
    bodyjson3 = {
        "action": "RMSWrapperCtrl",
	    "method": "postVehicleListForFreeRegoCheck",
	    "data": ['{\"transactionToken\":\"' + transactionToken + '\",\"plateNumber\":\"' + numberPlate + '\"}'],
	    "type": "rpc",
	    "tid": 7,
	    "ctx": {
		    "csrf": csrf,
		    "vid": vid,
		    "ns": "",
		    "ver": 34
	    }
    }

    # The final deed
    response3 = session.post('https://my.service.nsw.gov.au/MyServiceNSW/apexremote', json = bodyjson3)
    final = str(response3.content.decode("utf-8"))    
    obj = json.loads(final)    
    
    try:
        expires = obj[0]['result']['statusObject']['registrationExpiryDate']
        status = obj[0]['result']['statusObject']['registrationStatus']
    except:
        expires = "Error"
        status = "Error"

    return status, expires

def GetThis(neddle, endmarker, haystack):
    haystack = str(haystack)
    start = haystack.find(neddle)    
    if start == 1:
        return ""    
    start = start + len(neddle)
    end = haystack.find(endmarker, start)       
    return(haystack[start:end])