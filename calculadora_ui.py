#!/usr/bin/env python3
"""Interface gráfica (Flet) da calculadora científica.

Reutiliza o motor de `calculadora.py` — toda a conta é feita lá.
Execute com:

    python calculadora_ui.py
"""

from __future__ import annotations

import re

import flet as ft

import calculadora

# --------------------------------------------------------------------- estilo

ESTILO = {
    "num": (ft.Colors.SURFACE_CONTAINER_HIGH, ft.Colors.ON_SURFACE),
    "op": (ft.Colors.SECONDARY_CONTAINER, ft.Colors.ON_SECONDARY_CONTAINER),
    "fn": (ft.Colors.SURFACE_CONTAINER, ft.Colors.ON_SURFACE_VARIANT),
    "mem": (ft.Colors.SURFACE_CONTAINER_LOW, ft.Colors.ON_SURFACE_VARIANT),
    "clear": (ft.Colors.ERROR_CONTAINER, ft.Colors.ON_ERROR_CONTAINER),
    "eq": (ft.Colors.PRIMARY, ft.Colors.ON_PRIMARY),
    "ativo": (ft.Colors.PRIMARY_CONTAINER, ft.Colors.ON_PRIMARY_CONTAINER),
}

OPERADORES = "+−×÷^%"


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.estado = calculadora.Estado()

        self.expr = ""
        self.resultado = ""
        self.ultimo = ""
        self.avaliado = False
        self.erro = ""
        self.segundo = False

        self.texto_aux = ft.Text(
            " ",
            size=15,
            color=ft.Colors.ON_SURFACE_VARIANT,
            text_align=ft.TextAlign.RIGHT,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
            width=float("inf"),
        )
        self.texto_principal = ft.Text(
            "0",
            size=42,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.RIGHT,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            width=float("inf"),
        )
        self.indicador_memoria = ft.Container(
            content=ft.Text(
                "M",
                size=11,
                weight=ft.FontWeight.W_700,
                color=ft.Colors.ON_TERTIARY_CONTAINER,
            ),
            bgcolor=ft.Colors.TERTIARY_CONTAINER,
            padding=ft.Padding.symmetric(horizontal=7, vertical=2),
            border_radius=8,
            visible=False,
            tooltip="",
        )
        self.botao_modo = ft.Container(
            content=ft.Text(
                "DEG",
                size=11,
                weight=ft.FontWeight.W_700,
                color=ft.Colors.ON_PRIMARY_CONTAINER,
            ),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            padding=ft.Padding.symmetric(horizontal=9, vertical=3),
            border_radius=10,
            on_click=self.alternar_modo,
            tooltip="Clique para alternar graus/radianos",
        )
        self.botao_historico = ft.Container(
            content=ft.Icon(
                ft.Icons.HISTORY,
                size=21,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            padding=ft.Padding.all(6),
            border_radius=20,
            on_click=self.abrir_historico,
            tooltip="Histórico",
        )

        self.tela = ft.Container(
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        controls=[
                            self.indicador_memoria,
                            ft.Container(expand=True),
                            self.botao_modo,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.texto_aux,
                    self.texto_principal,
                ],
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=20,
            padding=ft.Padding.only(left=18, right=18, top=10, bottom=12),
            height=150,
        )

        self.grade = ft.Column(spacing=6)
        self.acoes = self._montar_acoes()
        self.montar_teclado()
        self.renderizar()

    # ------------------------------------------------------------- montagem

    def construir(self) -> ft.View:
        cabecalho = ft.Row(
            controls=[
                ft.Icon(ft.Icons.SCIENCE, size=22, color=ft.Colors.PRIMARY),
                ft.Text(
                    "Científica",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(expand=True),
                self.botao_historico,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return ft.View(
            route="/",
            padding=14,
            spacing=10,
            controls=[cabecalho, self.tela, self.grade],
        )

    def montar_teclado(self) -> None:
        self.grade.controls = [
            ft.Row(
                spacing=6,
                controls=[
                    self.tecla(rotulo, acao, tipo, altura, tamanho)
                    for rotulo, acao, tipo, altura, tamanho in linha
                ],
            )
            for linha in self.linhas()
        ]

    def linhas(self) -> list[list[tuple]]:
        segundo = self.segundo
        return [
            [
                ("MC", "mem_mc", "mem", 36, 12),
                ("MR", "mem_mr", "mem", 36, 12),
                ("M+", "mem_mais", "mem", 36, 12),
                ("M−", "mem_menos", "mem", 36, 12),
                ("EXP", "exp_cientifico", "mem", 36, 12),
            ],
            [
                ("2nd", "segundo", "ativo" if segundo else "fn", 52, 14),
                ("π", "pi", "fn", 52, 20),
                ("e", "e", "fn", 52, 20),
                ("C", "limpar", "clear", 52, 18),
                ("⌫", "apagar", "clear", 52, 20),
            ],
            [
                (
                    "sin⁻¹" if segundo else "sin",
                    "asin" if segundo else "sin",
                    "fn",
                    52,
                    14,
                ),
                (
                    "cos⁻¹" if segundo else "cos",
                    "acos" if segundo else "cos",
                    "fn",
                    52,
                    14,
                ),
                (
                    "tan⁻¹" if segundo else "tan",
                    "atan" if segundo else "tan",
                    "fn",
                    52,
                    14,
                ),
                ("^", "pot", "fn", 52, 20),
                (
                    "∛" if segundo else "√",
                    "cbrt" if segundo else "raiz",
                    "fn",
                    52,
                    20,
                ),
            ],
            [
                (
                    "eˣ" if segundo else "ln",
                    "funcao_exp" if segundo else "ln",
                    "fn",
                    52,
                    14,
                ),
                (
                    "10ˣ" if segundo else "log",
                    "funcao_10x" if segundo else "log",
                    "fn",
                    52,
                    14,
                ),
                ("x!", "fatorial", "fn", 52, 16),
                ("(", "abre", "fn", 52, 20),
                (")", "fecha", "fn", 52, 20),
            ],
            [
                ("7", "7", "num", 52, 20),
                ("8", "8", "num", 52, 20),
                ("9", "9", "num", 52, 20),
                ("÷", "dividir", "op", 52, 22),
                ("mod", "mod", "op", 52, 14),
            ],
            [
                ("4", "4", "num", 52, 20),
                ("5", "5", "num", 52, 20),
                ("6", "6", "num", 52, 20),
                ("×", "multiplicar", "op", 52, 22),
                ("1/x", "reciproco", "op", 52, 16),
            ],
            [
                ("1", "1", "num", 52, 20),
                ("2", "2", "num", 52, 20),
                ("3", "3", "num", 52, 20),
                ("−", "subtrair", "op", 52, 22),
                ("ANS", "ans", "op", 52, 14),
            ],
            [
                ("0", "0", "num", 52, 20),
                (".", "ponto", "num", 52, 22),
                ("±", "sinal", "num", 52, 20),
                ("+", "somar", "op", 52, 22),
                ("=", "igual", "eq", 52, 22),
            ],
        ]

    def tecla(self, rotulo, acao, tipo="fn", altura=52, tamanho=18) -> ft.Container:
        fundo, frente = ESTILO[tipo]
        return ft.Container(
            content=ft.Text(
                rotulo,
                size=tamanho,
                weight=ft.FontWeight.W_500,
                color=frente,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=fundo,
            border_radius=12,
            height=altura,
            expand=True,
            ink=True,
            on_click=lambda e, a=acao: self.ao_clicar(a),
        )

    # -------------------------------------------------------------- estado

    def _montar_acoes(self) -> dict:
        acoes = {
            "ponto": lambda: self.digito("."),
            "pi": lambda: self.constante("π"),
            "e": lambda: self.constante("e"),
            "sin": lambda: self.funcao("sin"),
            "cos": lambda: self.funcao("cos"),
            "tan": lambda: self.funcao("tan"),
            "asin": lambda: self.funcao("asin"),
            "acos": lambda: self.funcao("acos"),
            "atan": lambda: self.funcao("atan"),
            "ln": lambda: self.funcao("ln"),
            "log": lambda: self.funcao("log"),
            "funcao_exp": lambda: self.funcao("exp"),
            "funcao_10x": lambda: self.funcao("10^"),
            "raiz": lambda: self.funcao("√"),
            "cbrt": lambda: self.funcao("cbrt"),
            "somar": lambda: self.operador("+"),
            "subtrair": lambda: self.operador("−"),
            "multiplicar": lambda: self.operador("×"),
            "dividir": lambda: self.operador("÷"),
            "pot": lambda: self.operador("^"),
            "mod": lambda: self.operador("%"),
            "abre": self.abre,
            "fecha": self.fecha,
            "exp_cientifico": self.exp_cientifico,
            "fatorial": self.fatorial,
            "reciproco": self.reciproco,
            "sinal": self.sinal,
            "igual": self.igual,
            "limpar": self.limpar,
            "apagar": self.apagar,
            "ans": lambda: self.valor("ans"),
            "mem_mc": self.mem_mc,
            "mem_mr": lambda: self.valor("mem"),
            "mem_mais": self.mem_mais,
            "mem_menos": self.mem_menos,
            "segundo": self.alternar_segundo,
        }
        for digito in "0123456789":
            acoes[digito] = lambda d=digito: self.digito(d)
        return acoes

    def ao_clicar(self, acao: str) -> None:
        funcao = self.acoes.get(acao)
        if funcao is None:
            return
        funcao()
        self._fim()

    def _fim(self) -> None:
        self.renderizar()
        self.page.update()

    def renderizar(self) -> None:
        if self.erro:
            aux = self.erro
            principal = self.expr or "Erro"
            cor_aux = ft.Colors.ERROR
            cor_principal = ft.Colors.ERROR
        elif self.avaliado:
            aux = f"{self.ultimo} =" if self.ultimo else " "
            principal = self.resultado or "0"
            cor_aux = ft.Colors.ON_SURFACE_VARIANT
            cor_principal = ft.Colors.ON_SURFACE
        else:
            principal = self.expr or "0"
            aux = self.previa() or " "
            cor_aux = ft.Colors.ON_SURFACE_VARIANT
            cor_principal = ft.Colors.ON_SURFACE

        self.texto_aux.value = aux
        self.texto_aux.color = cor_aux
        self.texto_principal.value = principal
        self.texto_principal.color = cor_principal
        self.texto_principal.size = self.tamanho_fonte(principal)

        self.botao_modo.content.value = "DEG" if calculadora.em_graus() else "RAD"
        memoria = self.estado.memoria
        self.indicador_memoria.visible = memoria != 0
        self.indicador_memoria.tooltip = f"M = {calculadora.formatar(memoria)}"

    def tamanho_fonte(self, texto: str) -> int:
        tamanho = len(texto)
        if tamanho <= 12:
            return 42
        if tamanho <= 18:
            return 34
        if tamanho <= 26:
            return 28
        return 22

    # --------------------------------------------------------- cálculos

    def calcular(self, expressao: str):
        texto = expressao.strip()
        while texto and texto[-1] in OPERADORES:
            texto = texto[:-1]
        if not texto:
            return None
        faltando = texto.count("(") - texto.count(")")
        if faltando > 0:
            texto += ")" * faltando
        return calculadora.avaliar(texto, self.estado)

    def previa(self) -> str:
        if not self.expr:
            return ""
        simples = self.expr.lstrip("−-")
        if simples.replace(".", "").isdigit():
            return ""
        try:
            valor = self.calcular(self.expr)
        except Exception:
            return ""
        if valor is None:
            return ""
        return f"= {calculadora.formatar(valor)}"

    def _preparar(self, tipo: str) -> None:
        if self.avaliado:
            if tipo in {"num", "funcao", "constante", "abre", "valor"}:
                self.expr = ""
            else:
                self.expr = self.resultado
            self.avaliado = False
            self.ultimo = ""
        self.erro = ""

    def _fator_implicito(self) -> None:
        if not self.expr:
            return
        ultimo = self.expr[-1]
        if ultimo.isdigit() or ultimo in ".).π":
            self.expr += "×"
        elif ultimo == "e" and not (
            len(self.expr) >= 2 and self.expr[-2].isdigit()
        ):
            self.expr += "×"

    def digito(self, token: str) -> None:
        self._preparar("num")
        if token == ".":
            achado = re.search(r"(\d*\.?\d*)$", self.expr)
            atual = achado.group(1) if achado else ""
            if "." in atual:
                return
            if not atual:
                if self.expr:
                    ultimo = self.expr[-1]
                    if ultimo in ")π":
                        self.expr += "×"
                    elif ultimo == "e" and not (
                        len(self.expr) >= 2 and self.expr[-2].isdigit()
                    ):
                        self.expr += "×"
                token = "0."
            self.expr += token
            return

        if self.expr:
            ultimo = self.expr[-1]
            if ultimo in ")π":
                self.expr += "×"
            elif ultimo == "e" and not (
                len(self.expr) >= 2 and self.expr[-2].isdigit()
            ):
                self.expr += "×"
        self.expr += token

    def constante(self, token: str) -> None:
        self._preparar("constante")
        self._fator_implicito()
        self.expr += token

    def funcao(self, nome: str) -> None:
        self._preparar("funcao")
        self._fator_implicito()
        self.expr += nome + "("

    def abre(self) -> None:
        self._preparar("abre")
        self._fator_implicito()
        self.expr += "("

    def fecha(self) -> None:
        self._preparar("fecha")
        if self.expr.count("(") > self.expr.count(")"):
            self.expr += ")"

    def operador(self, token: str) -> None:
        self._preparar("op")
        if not self.expr:
            if token == "−":
                self.expr = "−"
            return

        ultimo = self.expr[-1]
        if ultimo == "(" and token != "−":
            return
        if ultimo in OPERADORES:
            if token == "−" and ultimo in "×÷^%":
                self.expr += "−"
                return
            self.expr = self.expr[:-1] + token
            return
        self.expr += token

    def exp_cientifico(self) -> None:
        self._preparar("num")
        if self.expr and (self.expr[-1].isdigit() or self.expr[-1] == "."):
            self.expr += "e"
        else:
            self._fator_implicito()
            self.expr += "e"

    def fatorial(self) -> None:
        if self.avaliado:
            self.expr = self.resultado
            self.avaliado = False
            self.ultimo = ""
        self.erro = ""
        self.expr = f"fact({self.expr or 'ans'})"

    def reciproco(self) -> None:
        if self.avaliado:
            self.expr = self.resultado
            self.avaliado = False
            self.ultimo = ""
        self.erro = ""
        self.expr = f"1/({self.expr or 'ans'})"

    def sinal(self) -> None:
        self.erro = ""
        if self.avaliado:
            self.expr = self.resultado
            self.avaliado = False
            self.ultimo = ""
        if not self.expr:
            self.expr = "−"
            return
        if self.expr.startswith("−(") and self.expr.endswith(")"):
            self.expr = self.expr[2:-1]
        elif self.expr.startswith("−"):
            self.expr = self.expr[1:]
        elif any(caractere in self.expr for caractere in OPERADORES):
            self.expr = f"−({self.expr})"
        else:
            self.expr = "−" + self.expr

    def valor(self, token: str) -> None:
        self._preparar("valor")
        if self.expr and self.expr[-1] not in OPERADORES + "(":
            self.expr = token
        else:
            self.expr += token

    def igual(self) -> None:
        self.erro = ""
        if not self.expr:
            return
        try:
            valor = self.calcular(self.expr)
        except Exception as erro:
            self.erro = calculadora.mensagem(erro)
            return
        if valor is None:
            return

        texto = calculadora.formatar(valor)
        self.ultimo = self.expr
        self.resultado = texto
        self.estado.ans = valor
        self.estado.historico.append((self.expr, texto))
        del self.estado.historico[:-100]
        self.expr = texto
        self.avaliado = True

    def limpar(self) -> None:
        self.expr = ""
        self.resultado = ""
        self.ultimo = ""
        self.avaliado = False
        self.erro = ""

    def apagar(self) -> None:
        self.erro = ""
        if self.avaliado:
            self.limpar()
            return
        self.expr = self.expr[:-1]

    # ------------------------------------------------------------- memória

    def _valor_atual(self):
        if not self.expr:
            return self.estado.ans
        try:
            valor = self.calcular(self.expr)
        except Exception:
            return self.estado.ans
        return self.estado.ans if valor is None else valor

    def mem_mais(self) -> None:
        self.estado.memoria += self._valor_atual()

    def mem_menos(self) -> None:
        self.estado.memoria -= self._valor_atual()

    def mem_mc(self) -> None:
        self.estado.memoria = 0

    # -------------------------------------------------------------- modos

    def alternar_segundo(self) -> None:
        self.segundo = not self.segundo
        self.montar_teclado()

    def alternar_modo(self, e=None) -> None:
        if calculadora.em_graus():
            calculadora.usar_radianos()
        else:
            calculadora.usar_graus()
        self._fim()

    # ------------------------------------------------------------ histórico

    def abrir_historico(self, e=None) -> None:
        entradas = self.estado.historico
        if entradas:
            itens = [
                ft.ListTile(
                    title=ft.Text(
                        expressao,
                        size=13,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    subtitle=ft.Text(
                        f"= {resultado}",
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    on_click=lambda ev, r=resultado: self.usar_resultado(r),
                )
                for expressao, resultado in reversed(entradas)
            ]
        else:
            itens = [
                ft.Text(
                    "Nenhum cálculo ainda.",
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            ]

        dialogo = ft.AlertDialog(
            title=ft.Text("Histórico"),
            content=ft.Column(
                controls=itens,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                width=360,
                height=360,
            ),
            actions=[
                ft.TextButton(
                    "Limpar",
                    on_click=self.limpar_historico,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                ),
                ft.TextButton(
                    "Fechar",
                    on_click=lambda ev: self.page.pop_dialog(),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.page.show_dialog(dialogo)

    def limpar_historico(self, e=None) -> None:
        self.estado.historico.clear()
        self.page.pop_dialog()
        self._fim()

    def usar_resultado(self, resultado: str) -> None:
        self.expr = resultado
        self.avaliado = False
        self.ultimo = ""
        self.erro = ""
        self.page.pop_dialog()
        self._fim()

    # -------------------------------------------------------------- teclado

    def ao_teclar(self, e: ft.KeyboardEvent) -> None:
        if e.ctrl or e.alt or e.meta:
            return

        mapa = {
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            ".": "ponto",
            ",": "ponto",
            "Decimal": "ponto",
            "+": "somar",
            "Add": "somar",
            "-": "subtrair",
            "Subtract": "subtrair",
            "*": "multiplicar",
            "x": "multiplicar",
            "X": "multiplicar",
            "Multiply": "multiplicar",
            "/": "dividir",
            "Divide": "dividir",
            "^": "pot",
            "%": "mod",
            "(": "abre",
            ")": "fecha",
            "!": "fatorial",
            "=": "igual",
            "Enter": "igual",
            "Return": "igual",
            "NumpadEnter": "igual",
            "Backspace": "apagar",
            "Delete": "limpar",
            "Escape": "limpar",
            "F2": "segundo",
        }
        acao = mapa.get(e.key)
        if acao:
            self.ao_clicar(acao)


def main(page: ft.Page) -> None:
    page.title = "Calculadora Científica"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    page.window.width = 440
    page.window.height = 760
    page.window.min_width = 360
    page.window.min_height = 640
    page.window.resizable = True

    app = App(page)
    page.on_keyboard_event = app.ao_teclar
    page.views.append(app.construir())
    page.update()


if __name__ == "__main__":
    ft.run(main)
