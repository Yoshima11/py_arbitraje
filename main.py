import threading
from datetime import date
from datetime import timedelta
from datetime import datetime
from math import sqrt
import flet as ft
from iol import ApiIOL

iol = ApiIOL()

simbolos = [
    'AL30', 'GD30', 'AL35', 'GD35', 'AE38', 'GD38', 'TX26', 'TX28', 'DICP', 'DIP0', 'PARP', 'PAP0'
]


def main(page: ft.Page):
    event = threading.Event()
    page.title = "py_arbitrador"
    page.vertical_alignment = ft.MainAxisAlignment.START

    def conectar_iol(e):
        login_error.color = 'black'
        login_error.value = 'Iniciando sesión ...'
        page.update(login_error)
        body = {
            'username': user.value,
            'password': password.value,
            'grant_type': "password",
        }
        iol.req_token(body, True)
        if iol.token_error:
            login_error.color = 'red'
            login_error.value = iol.token_error_code
            page.update(login_error)
        else:
            print(iol.access_token)
            login_off()
            datos = ratios_hist(simbolos)
            auto_refrescar(datos)

    def login_off():
        user.disabled = True
        password.disabled = True
        password.value = ''
        login_error.color = 'green'
        login_error.value = 'Sesión iniciada correctamente.'
        iniciar_sesion.disabled = True
        page.update(user, password, login_error, iniciar_sesion)

    def auto_refrescar(datos: list):
        datos_2 = datos
        while True:
            for i in range(0, len(datos)):
                #ratio_actual = (iol.get_price(simbolo=datos[i]['simbolo_1'], plazo='t0')['ultimoPrecio'] /
                #                iol.get_price(simbolo=datos[i]['simbolo_2'], plazo='t0')['ultimoPrecio'])
                #precio_1 = iol.get_price(simbolo=datos[i]['simbolo_1'], plazo='t0')['ultimoPrecio']
                #precio_2 = iol.get_price(simbolo=datos[i]['simbolo_2'], plazo='t0')['ultimoPrecio']
                #ratio_actual = precio_1 / precio_2
                precio_1 = iol.get_price(simbolo=datos[i]['simbolo_1'], plazo='t0')
                precio_2 = iol.get_price(simbolo=datos[i]['simbolo_2'], plazo='t0')
                ratio_actual = precio_1['ultimoPrecio'] / precio_2['ultimoPrecio']

                datos_2[i]['simbolo_1'] = precio_1
                datos_2[i]['simbolo_2'] = precio_2
                datos_2[i]['ratio_actual'] = ratio_actual

                datos[i]['precio_1'] = precio_1['ultimoPrecio']
                datos[i]['precio_2'] = precio_2['ultimoPrecio']
                datos[i]['ratio_actual'] = ratio_actual

            print(datos_2)
            hora_actual.value = f'Ultima actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}'
            page.update(hora_actual)
            agregar_fila(datos)
            event.wait(60)
            if event.is_set():
                break
            else:
                pass

    def ratios_hist(simbolos: list):
        h_cot = {}
        ratios = []
        for i in simbolos:
            h_cot[i] = iol.get_historical_price(mercado='bCBA', simbolo=i,
                                                fecha_desde=date.today() - timedelta(days=365),
                                                fecha_hasta=date.today() - timedelta(days=5),
                                                ajustada='sinAjustar')
        for i in range(0, len(simbolos), 2):
            valor_1_200 = h_cot[simbolos[i]][0:200]
            valor_2_200 = h_cot[simbolos[i + 1]][0:200]
            ratios_200 = calc_ratio_hist(valor_1_200, valor_2_200)
            valor_1_20 = h_cot[simbolos[i]][0:20]
            valor_2_20 = h_cot[simbolos[i + 1]][0:20]
            ratios_20 = calc_ratio_hist(valor_1_20, valor_2_20)
            ratios.append({'simbolo_1': simbolos[i],
                           'simbolo_2': simbolos[i+1],
                           'nombre': f'{simbolos[i]}/{simbolos[i + 1]}',
                           'prom_200': calc_promedio(ratios_200),
                           'desv_est_200': desviacion_estandar(ratios_200),
                           'prom_20': calc_promedio(ratios_20),
                           'desv_est_20': desviacion_estandar(ratios_20),
                           })
        for i in range(0, len(ratios)):
            print(ratios[i])
        return ratios

    def calc_promedio(valores: list):
        suma = 0
        for valor in valores:
            suma += valor
        return suma / len(valores)

    def calc_ratio_hist(valores_1: list, valores_2: list):
        ratios = []
        for i in range(0, len(valores_1)):
            try:
                ratios.append(valores_1[i]['ultimoPrecio'] / valores_2[i]['ultimoPrecio'])
            except IndexError:
                pass
        return ratios

    def desviacion_estandar(valores: list):
        suma = 0
        media = calc_promedio(valores)
        for valor in valores:
            suma += (valor - media) ** 2
        radicando = suma / (len(valores) - 1)
        return sqrt(radicando)

    def obtener_simbolos():
        pass

    def agregar_fila(datos: list):
        lista_table.rows.clear()
        page.update(lista_table)
        for i in range(0, len(datos)):
            lista_table.rows.append(
                ft.DataRow([
                    ft.DataCell(ft.Text(datos[i]['nombre'])),
                    ft.DataCell(ft.Text(datos[i]['nombre'])),
                    ft.DataCell(ft.Text(datos[i]['ratio_actual'])),
                    ft.DataCell(ft.Text(datos[i]['prom_200'])),
                    ft.DataCell(ft.Text(datos[i]['desv_est_200'])),
                    ft.DataCell(ft.Text(datos[i]['prom_20'])),
                    ft.DataCell(ft.Text(datos[i]['desv_est_20'])),
                ])
            )
        page.update(lista_table)

    def salir(e):
        page.window_destroy()
        event.set()

    titulo = ft.Text('Inicio sesión API Invertir Online', size=18, text_align=ft.TextAlign.START, width=500)
    user = ft.TextField(label='Nombre de Usuario', value='', )
    password = ft.TextField(label='Contraseña', value='', password=True, can_reveal_password=True)
    login_error = ft.Text('')
    iniciar_sesion = ft.ElevatedButton('Iniciar Sesión', on_click=conectar_iol, )
    inicio_column = ft.Column(width=500, controls=[titulo, user, password, login_error, iniciar_sesion])
    hora_actual = ft.Text('')
    lista_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('Nombre')),
            ft.DataColumn(ft.Text('Ratio')),
            ft.DataColumn(ft.Text('Media 200'), numeric=True),
            ft.DataColumn(ft.Text('STD 200'), numeric=True),
            ft.DataColumn(ft.Text('Media 20'), numeric=True),
            ft.DataColumn(ft.Text('STD 20'), numeric=True),
        ],
    )
    page.add(
        ft.Row(
            controls=[
                inicio_column,
                ft.Image(src='principal.jpg', width=200, border_radius=ft.border_radius.all(10), )],
            spacing=100
        ),
        lista_table,
        hora_actual,
        ft.ElevatedButton('agregar celda', on_click=agregar_fila),
        ft.ElevatedButton('Salir', on_click=salir),
    )


ft.app(main)
