def do_something(test, x):
    test.logger.info('something')
    return []

def get_session():
    import requests
    import re
    import json
    BASE_URL = 'https://hercules.icecube.wisc.edu'

    def url(u):
        return BASE_URL + u

    def web_login(test=False, port=None):
        session = requests.session()

        AUTH_URL = BASE_URL + '/auth/'
        # get authtoken first
        r = session.get(AUTH_URL)
        m = re.findall("""csrfmiddlewaretoken' value='(.*)'""", r.text)
        if m:
            token = m[0]

        headers = dict(Referer=AUTH_URL)
        r = session.post(AUTH_URL, dict(
                username='icecube',
                password='skua',
                csrfmiddlewaretoken=token
                ), headers=headers)
        return session

    session = web_login()

    return session

    #response = session.get(url('/moni20_single_dom_detail/133255/19-60/'))
    #data = response.content

