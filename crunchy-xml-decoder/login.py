import sys
import re
import requests
from getpass import getpass
from ConfigParser import ConfigParser
import random
import string
import altfuncs

def getuserstatus(sess_id_renew = False,sess_id_usa=''):
    status = 'Guest'
    user1 = 'Guest'
    session = requests.session()
    cookies_ = ConfigParser()
    if sess_id_usa=='':
        cookies_.read('cookies')
        sess_id_usa = cookies_.get('COOKIES', 'sess_id_usa')
        sess_id_ = cookies_.get('COOKIES', 'sess_id')
        auth = cookies_.get('COOKIES', 'auth')
    if sess_id_renew:
        session.get('http://api.crunchyroll.com/end_session.0.json?session_id='+sess_id_usa).json()
        session.get('http://api.crunchyroll.com/end_session.0.json?session_id='+sess_id_).json()
    checkusaid = session.get('http://api.crunchyroll.com/start_session.0.json?session_id='+sess_id_usa).json()
    if checkusaid['code'] == 'ok':
        if checkusaid['data']['user'] != None:
            user1 = checkusaid['data']['user']['username']
            if checkusaid['data']['user']['premium'] == '':
                status = 'Free Member'
            else:  # later will add Premium+ status
                status = 'Premium'
    else:
        #print checkusaid['data']['user']
        payload = {'device_id': ''.join(random.sample(string.ascii_letters + string.digits, 32)),'api_ver': '1.0','device_type': 'com.crunchyroll.iphone','access_token': 'QWjz212GspMHH9h','version': '2313.8','locale': 'jaJP','duration': '9999999999', 'auth' : auth}
        payload_t = {'device_id': ''.join(random.sample(string.ascii_letters + string.digits, 32)),'api_ver': '1.0','device_type': 'com.crunchyroll.iphone','access_token': 'QWjz212GspMHH9h'}
        if altfuncs.config()[8] != '':
            proxies = {'http': altfuncs.config()[8]}
        else:
            proxies = {}
        #print session.get('http://api-manga.crunchyroll.com/cr_start_session', data=payload_t)
        checkusaid2 = session.post('http://api-manga.crunchyroll.com/cr_start_session', data=payload).json()
        sess_id_usa = checkusaid2['data']['session_id'].encode('ascii', 'ignore')
        try:
            sess_id_ = session.post('http://api.crunchyroll.com/start_session.0.json', proxies=proxies, data=payload).json()['data']['session_id'].encode('ascii', 'ignore')
        except requests.exceptions.ProxyError:
            sess_id_ = session.post('http://api.crunchyroll.com/start_session.0.json', data=payload).json()['data']['session_id'].encode('ascii', 'ignore')
        open("cookies", "w").write('[COOKIES]\nsess_id = '+sess_id_+'\nsess_id_usa = '+sess_id_usa+'\nauth = '+auth)
        if checkusaid2['data']['user'] != None:
            user1 = checkusaid2['data']['user']['username']
            if checkusaid2['data']['user']['premium'] == '':
                status = 'Free Member'
            else:  # later will add Premium+ status
                status = 'Premium'
    return [status,user1]

def login(username, password):
    session = requests.session()
    payload = {'device_id': ''.join(random.sample(string.ascii_letters + string.digits, 32)),'api_ver': '1.0','device_type': 'com.crunchyroll.iphone','access_token': 'QWjz212GspMHH9h','version': '2313.8','locale': 'jaJP','duration': '9999999999'}
    if altfuncs.config()[8] != '':
        proxies = {'http': altfuncs.config()[8]}
    else:
        proxies = {}
    sess_id_usa = session.post('http://api-manga.crunchyroll.com/cr_start_session', data=payload).json()['data']['session_id'].encode('ascii', 'ignore')
    try:
        sess_id_ = session.post('http://api.crunchyroll.com/start_session.0.json', proxies=proxies, data=payload).json()['data']['session_id'].encode('ascii', 'ignore')
    except requests.exceptions.ProxyError:
        sess_id_ = session.post('http://api.crunchyroll.com/start_session.0.json', data=payload).json()['data']['session_id'].encode('ascii', 'ignore')
#for now we dont need unblocker server
    '''
    try:
        session.cookies['usa_sess_id'] = requests.get('https://cr.onestay.moe/getid').json()['sessionId'].encode('ascii', 'ignore')
    except:
        sleep(10)  # sleep so we don't overload crunblocker
        session.cookies['usa_sess_id'] = requests.get('http://rssfeedfilter.netne.net/').json()['sessionId'].encode('ascii', 'ignore')
    '''
    auth = ''
    if username and password != '':
        payload = {'session_id' : sess_id_usa,'locale': 'jaJP','duration': '9999999999','account' : username, 'password' : password}
        try:
            auth = session.post('https://api.crunchyroll.com/login.0.json', data=payload).json()['data']['auth'].encode('ascii', 'ignore')
        except:
            pass
    userstatus = getuserstatus(False,sess_id_usa)
    if username != '' and userstatus[0] == 'Guest':
        print 'Login failed.'
        #sys.exit()
    else:
        print 'Login as '+userstatus[1]+' successfully.'
    open("cookies", "w").write('[COOKIES]\nsess_id = '+sess_id_+'\nsess_id_usa = '+sess_id_usa+'\nauth = '+auth)
		

if __name__ == '__main__':
    try:
        if sys.argv[1][0] == 'y':
            username = raw_input(u'Username: ')
            password = getpass('Password(don\'t worry the password are typing but hidden:')
    except IndexError:
        username = ''
        password = ''
    login(username, password)
