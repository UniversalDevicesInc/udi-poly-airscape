"""
Work on makeing this a generic session handler for all Polyglot's
"""

import requests,json,re,xmltodict,unicodedata

def remove_control_characters(s):
    res = "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
    return re.sub(r"\\", "", res)

class pgSession():

    def __init__(self,parent,l_name,logger,host,port=None,debug_level=-1):
        self.parent = parent
        self.l_name = l_name
        self.logger = logger
        self.host   = host
        self.port   = port
        self.debug_level = debug_level
        if port is None:
            self.port_s = ""
        else:
            self.port_s = ':{}'.format(port)
        self.session = requests.Session()

    def get(self,path,payload,auth=None,parse="json"):
        url = "http://{}{}/{}".format(self.host,self.port_s,path)
        self.l_debug('get',0,"Sending: url={0} payload={1}".format(url,payload))
        # No speical headers?
        headers = {
        }
        #"Content-Type": "application/json"
        if auth is not None:
            headers['Authorization'] = auth
        self.l_debug('get', 1, "headers={}".format(headers))
        #self.session.headers.update(headers)
        try:
            response = self.session.get(
                url,
                params=payload,
                headers=headers,
                timeout=10,
            )
            self.l_debug('get', 1, "url={}".format(response.url))
        # This is supposed to catch all request excpetions.
        except requests.exceptions.RequestException as e:
            self.l_error('get',"Connection error for %s: %s" % (url, e))
            return False
        return(self.response(response,'get',parse=parse))

    def response(self,response,name,parse="json"):
        fname = 'reponse:'+name
        self.l_debug(fname,0,' Got: code=%s' % (response.status_code))
        self.l_debug(fname,2,'      text=%s' % (response.text))
        rdata = False
        if response.status_code == 200:
            self.l_debug(fname,0,' All good!')
        elif response.status_code == 400:
            self.l_error(fname,"Bad request: %s: text: %s" % (response.url,response.text) )
        elif response.status_code == 404:
            self.l_error(fname,"Not Found: %s: text: %s" % (response.url,response.text) )
        elif response.status_code == 401:
            # Authentication error
            self.l_error(fname,"Unauthorized: %s: text: %s" % (response.url,response.text) )
        else:
            self.l_error(fname,"Unknown response %s: %s %s" % (response.status_code, response.url, response.text) )
        # No matter what, return the code and error
        if parse == "xml":
            # It's xml
            try:
                rtxt = remove_control_characters(response.text)
                rdata = xmltodict.parse(rtxt)
            except (Exception) as err:
                self.l_error(fname,'Failed to convert xml {0}: {1}'.format(rtxt,err), exc_info=True)
                rdata = False
        elif parse == "json":
            # It's json
            try:
                rtxt = remove_control_characters(response.text)
                rdata = json.loads(rtxt)
            except (Exception) as err:
                self.l_error(fname,'Failed to convert json {0}: {1}'.format(rtxt,err), exc_info=True)
                rdata = False
        elif parse == "axml":
            # Weird xml from airscape
            try:
                rtxt = remove_control_characters(response.text)
                pattern = r'.*?<(.*?)>(.*?)</.*?>'
                regex   = re.compile(pattern)
                it = regex.finditer(rtxt)
                rdata = {}
                for match in it:
                    rdata[match.group(1)] = match.group(2)
            except (Exception) as err:
                self.l_error(fname,'Failed to convert axml {0}: {1}'.format(rtxt,err), exc_info=True)
                rdata = False
        else:
            # return the exact reponse
            rdata = response.text
        return { 'code': response.status_code, 'data': rdata }

    def post(self,path,payload={},params={},dump=True,auth=None):
        url = "https://{}{}/{}".format(self.host,self.port_s,path)
        if dump:
            payload = json.dumps(payload)
        self.l_debug('post',0,"Sending: url={0} payload={1}".format(url,payload))
        headers = {
            'Content-Length': str(len(payload))
        }
        if 'json' in params and ( params['json'] or params['json'] == 'true'):
            headers['Content-Type'] = 'application/json'
        if auth is not None:
            headers['Authorization'] = auth
        self.l_debug('post', 1, "headers={}".format(headers))
        #self.session.headers.update(headers)
        try:
            response = self.session.post(
                url,
                params=params,
                data=payload,
                headers=headers,
                timeout=60
            )
            self.l_debug('post', 1, "url={}".format(response.url))
        # This is supposed to catch all request excpetions.
        except requests.exceptions.RequestException as e:
            self.l_error('post',"Connection error for %s: %s" % (url, e))
            return False
        return(self.response(response,'post'))


    def l_info(self, name, string):
        self.logger.info("%s:%s: %s" %  (self.l_name,name,string))

    def l_error(self, name, string, exc_info=False):
        self.logger.error("%s:%s: %s" % (self.l_name,name,string), exc_info=exc_info)

    def l_warning(self, name, string):
        self.logger.warning("%s:%s: %s" % (self.l_name,name,string))

    def l_debug(self, name, debug_level, string):
        if self.debug_level >= debug_level:
            self.logger.debug("%s:%s: %s" % (self.l_name,name,string))
