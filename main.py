import os
import threading
from datetime import date
import flet as ft
from iol import ApiIOL

iol = ApiIOL()


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

    def login_off():
        user.disabled = True
        password.disabled = True
        password.value = ''
        login_error.color = 'green'
        login_error.value = 'Sesión iniciada correctamente.'
        iniciar_sesion.disabled = True
        page.update(user, password, login_error, iniciar_sesion)

    def auto_refrescar(e):
        cot_button.disabled = True
        page.update(cot_button)
        while True:
            print(iol.get_price(simbolo=inst_text.value))
            event.wait(60)
            if event.is_set():
                break
            else:
                pass

    def cot_hist(e):
        print(iol.get_historical_price(mercado='bCBA', simbolo='TX26',
                                       fecha_desde=date(2024, 5, 16),
                                       fecha_hasta=date.today(), ajustada='sinAjustar'))

    def calc_ratio(ticker1, ticker2, ):
        pass

    def obtener_simbolos():
        pass

    def agregar_fila(e):
        lista_table.rows.append(
            ft.DataRow([
                ft.DataCell(ft.Text('1')),
                ft.DataCell(ft.Text('2')),
                ft.DataCell(ft.Text('3')),
                ft.DataCell(ft.Text('4')),
                ft.DataCell(ft.Text('5')),
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
    lista_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text('Simbolo 1')),
                            ft.DataColumn(ft.Text('Simbolo 2')),
                            ft.DataColumn(ft.Text('ratio 200 ruedas'), numeric=True),
                            ft.DataColumn(ft.Text('ratio 20 ruedas'), numeric=True),
                            ft.DataColumn(ft.Text('ratio actual (1 min)'), numeric=True),
                        ],
    )
    page.add(
        ft.Row(
            controls=[
                inicio_column,
                ft.Image(src='principal4.jpg', width=200, border_radius=ft.border_radius.all(10), )],
            spacing=100
        ),
        lista_table,
        ft.ElevatedButton('agregar celda', on_click=agregar_fila),
        ft.ElevatedButton('Salir', on_click=salir),
    )


ft.app(main)
