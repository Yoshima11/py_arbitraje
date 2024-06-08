import threading
import time
import requests
from datetime import date

import constantes


class ApiIOL:
    """Api Invertir Online"""
    access_token = ''
    refresh_token = ''
    token_error = True
    token_error_code = 0
    get_error = True
    get_error_code = 0

    def __init__(self):
        self.head_token = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def verifier_token(self, response, refresh):
        try:
            response.raise_for_status()
            self.token_error = False
            self.token_error_code = response.status_code
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            if refresh:  # Si es verdadero crea un thread que actualiza el token cada 15 minutos.
                thread = threading.Thread(target=self.ref_token, daemon=True)
                thread.start()
        except requests.exceptions.HTTPError as error:
            self.token_error = True
            self.token_error_code = error

    def head_req(self):  # headers para requests de la api
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        return headers

    def ref_token(self):
        while True:
            time.sleep(900)
            body = {
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
            }
            self.req_token(body, False)

    def req_token(self, body, refresh=True):
        """ Función para solicitar el token"""
        try:
            response = requests.post(
                url='https://api.invertironline.com/token',
                data=body,
                headers=self.head_token,
                timeout=10,
            )
            self.verifier_token(response, refresh)
        except requests.exceptions.ConnectionError as error:
            self.token_error = True
            self.token_error_code = error

    def get(self, url):
        """ Función para realizar consultas. En https://api.invertironline.com/ consultar operaciones disponibles"""
        try:
            response = requests.get(
                url=url,
                headers=self.head_req(),
            )
            try:
                response.raise_for_status()
                self.get_error = False
                self.get_error_code = response.status_code
                return response.json()
            except requests.exceptions.HTTPError as error:
                self.get_error = True
                self.get_error_code = error
        except requests.exceptions.ConnectionError as error:
            self.get_error = True
            self.get_error_code = error

    def get_price(self, mercado='bCBA', simbolo=None, plazo='t1'):
        url = f'https://api.invertironline.com//api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalleMobile/{plazo}'
        return self.get(url=url)

    def get_historical_price(self, mercado=constantes.Mercado.BCBA, simbolo='AL30',
                             fecha_desde: date = date(1970, 1, 1),
                             fecha_hasta: date = date.today(),
                             ajustada='sinAjustar'):
        url = f'https://api.invertironline.com//api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/\
              {fecha_desde.strftime('%Y-%m-%d')}/{fecha_hasta.strftime('%Y-%m-%d')}/{ajustada}'
        return self.get(url=url)

    def operar(self, url, data):
        """Falta función para poder operar"""
        pass
