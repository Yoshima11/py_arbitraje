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


class ratio_indicador(ft.Row):
    def __init__(self,
                 simbolo_1: str = None,
                 simbolo_2: str = None,
                 v_min: float = None,
                 v_max: float = None,
                 valor: float = None):
        super().__init__()
        self.sim_1 = ft.Text(simbolo_1)
        self.sim_2 = ft.Text(simbolo_2)
        self.minimo = ft.Text(v_min)
        self.ratio = ft.Text(valor)
        self.maximo = ft.Text(v_max)
        self.controls = [
            self.sim_1,
            self.minimo,
            self.ratio,
            self.maximo,
            self.sim_2,
        ]


def main(page: ft.Page):
    event = threading.Event()
    page.title = "py_arbitrador"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.scroll = 'adaptive'

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
        while True:
            for i in range(0, len(datos)):
                precio_1 = iol.get_price(simbolo=datos[i]['simbolo_1'], plazo='t1')
                precio_2 = iol.get_price(simbolo=datos[i]['simbolo_2'], plazo='t1')
                ratio_actual = float(precio_1['ultimoPrecio']) / float(precio_2['ultimoPrecio'])
                datos[i]['simbolo_1'] = precio_1
                datos[i]['simbolo_2'] = precio_2
                datos[i]['ratio_actual'] = ratio_actual
                print(datos[i])
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
            ratios.append({'simbolo_1': simbolos[i],
                           'simbolo_2': simbolos[i + 1],
                           'nombre': f'{simbolos[i]}/{simbolos[i + 1]}',
                           'prom_200': calc_promedio(calc_ratio_hist(h_cot[simbolos[i]][0:200],
                                                                     h_cot[simbolos[i + 1]][0:200])),
                           'desv_est_200': desviacion_estandar(calc_ratio_hist(h_cot[simbolos[i]][0:200],
                                                                               h_cot[simbolos[i + 1]][0:200])),
                           'prom_20': calc_promedio(calc_ratio_hist(h_cot[simbolos[i]][0:20],
                                                                    h_cot[simbolos[i + 1]][0:20])),
                           'desv_est_20': desviacion_estandar(calc_ratio_hist(h_cot[simbolos[i]][0:20],
                                                                              h_cot[simbolos[i + 1]][0:20])),
                           'prom_5': calc_promedio(calc_ratio_hist(h_cot[simbolos[i]][0:5],
                                                                   h_cot[simbolos[i + 1]][0:5])),
                           'desv_est_5': desviacion_estandar(calc_ratio_hist(h_cot[simbolos[i]][0:5],
                                                                             h_cot[simbolos[i + 1]][0:5])),
                           })
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
                    ft.DataCell(ratio_indicador(simbolo_1=datos[i]['simbolo_1']['simbolo'],
                                                simbolo_2=datos[i]['simbolo_2']['simbolo'],
                                                v_min=datos[i]['prom_5'] - datos[i]['desv_est_5'],
                                                v_max=datos[i]['prom_5'] + datos[i]['desv_est_5'],
                                                valor=datos[i]['ratio_actual'])),
                    ft.DataCell(ft.Text(datos[i]['ratio_actual'])),
                    ft.DataCell(ft.Text(datos[i]['prom_5'] + datos[i]['desv_est_5'])),
                    ft.DataCell(ft.Text(datos[i]['prom_5'] - datos[i]['desv_est_5'])),
                    ft.DataCell(ft.Text(datos[i]['prom_200'])),
                    ft.DataCell(ft.Text(datos[i]['desv_est_200'])),
                    ft.DataCell(ft.Text(datos[i]['prom_20'])),
                    ft.DataCell(ft.Text(datos[i]['desv_est_20'])),
                    ft.DataCell(ft.Text(datos[i]['prom_5'])),
                    ft.DataCell(ft.Text(datos[i]['desv_est_5'])),
                ])
            )
        page.update()

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
            ft.DataColumn(ft.Text('Indicador')),
            ft.DataColumn(ft.Text('Ratio'), numeric=True),
            ft.DataColumn(ft.Text('prom5 + desv'), numeric=True),
            ft.DataColumn(ft.Text('prom5 - desv'), numeric=True),
            ft.DataColumn(ft.Text('Media 200'), numeric=True),
            ft.DataColumn(ft.Text('STD 200'), numeric=True),
            ft.DataColumn(ft.Text('Media 20'), numeric=True),
            ft.DataColumn(ft.Text('STD 20'), numeric=True),
            ft.DataColumn(ft.Text('Media 5'), numeric=True),
            ft.DataColumn(ft.Text('STD 5'), numeric=True),
        ],
        border=ft.border.all(2, 'grey'),
        border_radius=0,
        heading_row_color=ft.colors.GREY_200,
        data_text_style=ft.TextStyle(size=12),
        heading_text_style=ft.TextStyle(size=15),
    )
    table_column = ft.Column(controls=[lista_table], height=650, scroll=ft.ScrollMode.ALWAYS)
    page.add(
        ft.Row(
            controls=[
                inicio_column,
                ft.Image(src='principal.jpg', width=200, border_radius=ft.border_radius.all(10)),
            ],
            spacing=100
        ),
        table_column,
        hora_actual,
        ft.ElevatedButton('agregar celda', on_click=agregar_fila),
        ft.ElevatedButton('Salir', on_click=salir),
    )


ft.app(main)
