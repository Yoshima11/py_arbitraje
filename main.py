import threading
from datetime import date
from datetime import timedelta
from datetime import datetime
from math import sqrt
import flet as ft
import flet.canvas as cv
from iol import ApiIOL

iol = ApiIOL()

simbolos = [
    ['AL30', 'GD30'],
    ['AL35', 'GD35'],
    ['AE38', 'GD38'],
    ['TX26', 'TX28'],
    ['DICP', 'DIP0'],
    ['PARP', 'PAP0'],
]


class ratio_indicador(ft.Row):
    def __init__(self,
                 simbolo_1: str = None,
                 simbolo_2: str = None,
                 des_min: float = None,
                 des_max: float = None,
                 v_ratio: float = None):
        super().__init__()
        self.marg_x = 2
        self.marg_y = 2
        self.ancho = 50
        self.alto = 30
        self.sim_1 = ft.Text(simbolo_1)
        self.sim_2 = ft.Text(simbolo_2)
        self.num_ratio = self.ajustar_valores(des_min, des_max, v_ratio)
        self.ratio = ft.Text(value=str(self.num_ratio))
        self.barra = cv.Canvas(
            [
                cv.Rect(0, 0, self.ancho * 3 + 4, self.alto + 4, paint=ft.Paint(ft.colors.WHITE)),
                cv.Rect(self.marg_x, self.marg_y, self.ancho, self.alto, paint=ft.Paint(ft.colors.GREEN_50)),
                cv.Rect(self.ancho + self.marg_x, self.marg_y, self.ancho, self.alto,
                        paint=ft.Paint(ft.colors.AMBER_50)),
                cv.Rect(self.ancho * 2 + self.marg_x, self.marg_y, self.ancho, self.alto,
                        paint=ft.Paint(ft.colors.GREEN_50)),
                cv.Text(self.ancho / 2 + self.marg_x, self.marg_y, simbolo_1, alignment=ft.alignment.top_center),
                cv.Text((self.ancho * 2) + (self.ancho / 2) + self.marg_x, self.marg_y, simbolo_2,
                        alignment=ft.alignment.top_center),
                cv.Rect(self.num_ratio + self.ancho + self.marg_x, self.marg_y, 3, self.alto,
                        paint=ft.Paint(ft.colors.RED)),
            ],
            width=self.ancho + 4,
            height=self.alto + 4,
        )
        self.controls = [
            #self.sim_1,
            #self.ratio,
            self.barra,
            #self.sim_2,
        ]

    def ajustar_valores(self,
                        v_min: float,
                        v_max: float,
                        v_ratio: float):
        res = v_max - v_min
        por = (v_ratio - v_min) / res * self.ancho
        if por >= self.ancho*2:
            por = self.ancho*2
        if por <= -self.ancho:
            por = -self.ancho
        return por


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
            hora_actual.value = f'Ultima actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}'
            for i in range(0, len(datos)):
                precio_1 = iol.get_price(simbolo=datos[i]['simbolo_1'], plazo='t1')
                precio_2 = iol.get_price(simbolo=datos[i]['simbolo_2'], plazo='t1')
                ratio_actual = float(precio_1['ultimoPrecio']) / float(precio_2['ultimoPrecio'])
                datos[i]['sim_1'] = precio_1
                datos[i]['sim_2'] = precio_2
                datos[i]['ratio_actual'] = ratio_actual
                print(datos[i])
            page.update(hora_actual)
            agregar_fila(datos)
            event.wait(60)
            if event.is_set():
                break
            else:
                pass

    def ratios_hist(simbolos: list):
        h_cot = []
        ratios = []
        for i in range(0, len(simbolos)):
            h_cot.append([iol.get_historical_price(mercado='bCBA', simbolo=simbolos[i][0],
                                                   fecha_desde=date.today() - timedelta(days=365),
                                                   fecha_hasta=date.today() - timedelta(days=1),
                                                   ajustada='sinAjustar'),
                          iol.get_historical_price(mercado='bCBA', simbolo=simbolos[i][1],
                                                   fecha_desde=date.today() - timedelta(days=365),
                                                   fecha_hasta=date.today() - timedelta(days=1),
                                                   ajustada='sinAjustar'),
                          ])
        for i in range(0, len(simbolos)):
            ratios.append({'simbolo_1': simbolos[i][0],
                           'simbolo_2': simbolos[i][1],
                           'nombre': f'{simbolos[i][0]}/{simbolos[i][1]}',
                           'prom_200': calc_promedio(calc_ratio_hist(h_cot[i][0][0:200],
                                                                     h_cot[i][1][0:200])),
                           'desv_est_200': desviacion_estandar(calc_ratio_hist(h_cot[i][0][0:200],
                                                                               h_cot[i][1][0:200])),
                           'prom_20': calc_promedio(calc_ratio_hist(h_cot[i][0][0:20],
                                                                    h_cot[i][1][0:20])),
                           'desv_est_20': desviacion_estandar(calc_ratio_hist(h_cot[i][0][0:20],
                                                                              h_cot[i][1][0:20])),
                           'prom_5': calc_promedio(calc_ratio_hist(h_cot[i][0][0:5],
                                                                   h_cot[i][1][0:5])),
                           'desv_est_5': desviacion_estandar(calc_ratio_hist(h_cot[i][0][0:5],
                                                                             h_cot[i][1][0:5])),
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

    def agregar_fila(datos: list):
        lista_table.rows.clear()
        page.update(lista_table)
        for i in range(0, len(datos)):
            lista_table.rows.append(
                ft.DataRow([
                    ft.DataCell(ft.Text(datos[i]['nombre'])),
                    ft.DataCell(ratio_indicador(simbolo_1=datos[i]['sim_1']['simbolo'],
                                                simbolo_2=datos[i]['sim_2']['simbolo'],
                                                des_min=datos[i]['prom_5'] - datos[i]['desv_est_5'],
                                                des_max=datos[i]['prom_5'] + datos[i]['desv_est_5'],
                                                v_ratio=datos[i]['ratio_actual'])),
                    ft.DataCell(ratio_indicador(simbolo_1=datos[i]['sim_1']['simbolo'],
                                                simbolo_2=datos[i]['sim_2']['simbolo'],
                                                des_min=datos[i]['prom_20'] - datos[i]['desv_est_20'],
                                                des_max=datos[i]['prom_20'] + datos[i]['desv_est_20'],
                                                v_ratio=datos[i]['ratio_actual'])),
                    ft.DataCell(ratio_indicador(simbolo_1=datos[i]['sim_1']['simbolo'],
                                                simbolo_2=datos[i]['sim_2']['simbolo'],
                                                des_min=datos[i]['prom_200'] - datos[i]['desv_est_200'],
                                                des_max=datos[i]['prom_200'] + datos[i]['desv_est_200'],
                                                v_ratio=datos[i]['ratio_actual'])),
                    ft.DataCell(ft.Text(datos[i]['ratio_actual'])),
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
            ft.DataColumn(ft.Text('Indicador 5')),
            ft.DataColumn(ft.Text('Indicador 20')),
            ft.DataColumn(ft.Text('Indicador 200')),
            ft.DataColumn(ft.Text('Ratio'), numeric=True),
        ],
        border=ft.border.all(2, 'grey'),
        border_radius=0,
        heading_row_color=ft.colors.GREY_200,
        data_text_style=ft.TextStyle(size=12),
        heading_text_style=ft.TextStyle(size=15),
        width=1300,
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
