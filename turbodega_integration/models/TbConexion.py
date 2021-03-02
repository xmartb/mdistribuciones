import json
import logging

import requests

_logger = logging.getLogger(__name__)


class TBClient(object):
    def __init__(self, timeout=30):

        self._product_url = "https://dashboard.turbodega.com/api/dc/products"
        self._partner_url = "https://dashboard.turbodega.com/api/dc/stores"
        self._resourceId  = "https://dashboard.turbodega.com/api/dc"
        self._method = "POST"
        self._timeout = timeout

    def _call_api(self, url, data, token=None, method=None):

        ##############################################
        # ENVIAR DATOS AL API (PUSH DATA)
        ##############################################
        headers = {
            "Content-type": "application/json",
            # "x-token": "tokenSecurityDPE100028",
            "x-token": token,
        }

        try:
            if method:
                self._method = method

            if self._method == "GET":
                json_data = json.dumps(data)
                _logger.info("url---GET-------------->")
                _logger.info(url)
                _logger.info(headers)
                _logger.info(json_data)
                r = requests.get(
                    url, headers=headers, params=json_data, timeout=self._timeout
                )

            elif self._method == "POST":
                json_data = json.dumps(data)
                _logger.info("----------POST")
                _logger.info(url)
                _logger.info(headers)
                _logger.info(json_data)

                r = requests.post(
                    url,
                    headers=headers,
                    json=json.loads(json_data),
                    timeout=self._timeout,
                )
            elif self._method == "PUT":
                json_data = json.dumps(data)
                _logger.info("----------PUT")

                _logger.info(url)
                _logger.info(headers)
                _logger.info(json_data)
                r = requests.put(
                    url,
                    headers=headers,
                    json=json.loads(json_data),
                    timeout=self._timeout,
                )
                # print("r>>>>>>>>>>>>>>>>>>>>>>>>>>>>><", r)

            if r.status_code == 200:
                return True, r.text, url

            else:
                # ERROR EN LA CONEXION
                # print("r.status_code", r.status_code)
                return (
                    False,
                    {
                        "faultcode": r.status_code,
                        "faultstring": r.text,
                    },
                    url,
                )

        except Exception as e:
            return False, {"faultcode": "000", "faultstring": e}, url

    def api_get_resourceid(self, tb_data, token):
        return self._call_api(self._resourceId, data=tb_data, token=token, method="GET")

    def _tb_send_product(self, tb_data, token):
        return self._call_api(self._product_url, tb_data, token, method="POST")

    def _tb_put_product(self, tb_data, token):
        url = self._product_url + "/" + str(tb_data["distributorSKU"])
        return self._call_api(url, data=tb_data, token=token, method="PUT")

    def _tb_send_partner(self, tb_data, token):
        return self._call_api(self._partner_url, tb_data, token)

    def _tb_put_partner(self, tb_data, token):
        url = self._partner_url + "/" + str(tb_data["code"])
        return self._call_api(url, data=tb_data, token=token, method="PUT")

    def _tb_send_so(self, tb_data, token):
        return self._call_api(self._product_url, tb_data)


def api_send_product(tb_data, token):

    client = TBClient()

    return client._tb_send_product(tb_data, token=token)


def api_update_product(tb_data, token):
    client = TBClient()

    return client._tb_put_product(tb_data, token=token)


def api_get_resourceid(tb_data, token):

    client = TBClient()

    return client.api_get_resourceid(tb_data, token=token)


def api_send_partner(tb_data, token):

    client = TBClient()

    return client._tb_send_partner(tb_data, token=token)


def api_update_partner(tb_data, token):
    client = TBClient()

    return client._tb_put_partner(tb_data, token=token)


def api_send_so(tb_data, token):

    client = TBClient()

    return client._tb_send_so(tb_data, token=token)
