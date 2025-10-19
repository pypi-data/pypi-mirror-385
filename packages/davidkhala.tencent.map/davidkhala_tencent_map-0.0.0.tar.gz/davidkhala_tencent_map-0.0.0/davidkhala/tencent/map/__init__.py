from davidkhala.utils.http_request import Request, default_on_response

class API(Request):

    def __init__(self, key):
        super().__init__(None)
        self.key = key
    def request(self, url, method: str, params=None, data=None, json=None) -> dict:
        params['key'] = self.key
        r = super().request(url, method, params, data, json)
        if r["status"] != 0:
            raise Exception(r["message"])
        return r
    def suggest(self, query):
        url = 'https://apis.map.qq.com/ws/place/v1/suggestion'

        r = self.request(url,'GET', {
            'keyword': query,
        })
        return r['data']
