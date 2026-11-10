#!/usr/bin/env python3
"""Calculadora científica de linha de comando.

Uso:
    python calculadora.py

Digite uma expressão e pressione Enter. Exemplos:
    2 + 3 * 4
    sin(30) + cos(60)
    sqrt(81) / log(1000)
    fact(5) + 2^10
    3.5e-2 * 1e6

Digite "ajuda" para ver todos os comandos, funções e constantes.
"""

from __future__ import annotations

import ast
import math
import operator
import re
import sys
from dataclasses import dataclass, field


# ------------------------------------------------------------------ constantes

CONSTANTES: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "phi": (1 + math.sqrt(5)) / 2,
    "inf": math.inf,
}

_MODO_GRAUS = True  # global: True = graus, False = radianos


def usar_graus() -> None:
    """Faz as funções trigonométricas trabalharem em graus."""
    global _MODO_GRAUS
    _MODO_GRAUS = True


def usar_radianos() -> None:
    """Faz as funções trigonométricas trabalharem em radianos."""
    global _MODO_GRAUS
    _MODO_GRAUS = False


def em_graus() -> bool:
    """Diz se o modo de ângulo atual é graus."""
    return _MODO_GRAUS


_LIMITE_EXPRESSAO = 500
_LIMITE_HISTORICO = 100
_LIMITE_FATORIAL = 1000


# ---------------------------------------------------------------------- estado


@dataclass
class Estado:
    ans: float | int = 0
    memoria: float | int = 0
    historico: list[tuple[str, str]] = field(default_factory=list)


# ------------------------------------------------------------------ utilidades


def _configurar_saida() -> None:
    """Evita quebra de acento/símbolo em consoles com codificação limitada."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            try:
                fluxo.reconfigure(errors="replace")
            except Exception:
                pass


def _imprimir(texto: str = "") -> None:
    print(texto)


def mensagem(erro: Exception) -> str:
    if isinstance(erro, ZeroDivisionError):
        return "divisão por zero"
    if isinstance(erro, OverflowError):
        return "resultado grande demais"
    return str(erro) or erro.__class__.__name__


def formatar(valor: float | int) -> str:
    """Formata o resultado de forma legível, sem lixo de ponto flutuante."""
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return str(valor)

    valor = float(valor)
    if math.isnan(valor):
        return "NaN"
    if math.isinf(valor):
        return "inf" if valor > 0 else "-inf"
    if valor == 0:
        return "0"

    if abs(valor) >= 1e16 or abs(valor) < 1e-6:
        mantissa, expoente = f"{valor:.10e}".split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        return f"{mantissa}e{int(expoente)}"

    arredondado = round(valor, 12)
    if arredondado == int(arredondado):
        return str(int(arredondado))
    return f"{arredondado:.12g}"


def _snap(valor: float) -> float:
    """Zera resíduos minúsculos da trigonometria (ex.: sin(180°) ≈ 1e-16)."""
    return 0.0 if abs(valor) < 1e-12 else valor


# ------------------------------------------------------------------- funções


def _dominio(nome: str):
    """Converte erros do math em mensagens claras, em português."""

    def decorador(func):
        def envoltorio(*args):
            try:
                return func(*args)
            except ValueError as erro:
                raise ValueError(f"valor fora do domínio de {nome}()") from erro
            except OverflowError as erro:
                raise ValueError(f"resultado grande demais em {nome}()") from erro

        envoltorio.__name__ = getattr(func, "__name__", nome)
        return envoltorio

    return decorador


def _para_rad(x: float) -> float:
    return math.radians(x) if _MODO_GRAUS else x


def _de_rad(x: float) -> float:
    return math.degrees(x) if _MODO_GRAUS else x


def _sin(x: float) -> float:
    return _snap(math.sin(_para_rad(x)))


def _cos(x: float) -> float:
    return _snap(math.cos(_para_rad(x)))


def _tan(x: float) -> float:
    rad = _para_rad(x)
    if abs(math.cos(rad)) < 1e-12:
        raise ValueError("tangente indefinida nesse ângulo")
    return _snap(math.tan(rad))


@_dominio("asin")
def _asin(x: float) -> float:
    return _de_rad(math.asin(x))


@_dominio("acos")
def _acos(x: float) -> float:
    return _de_rad(math.acos(x))


@_dominio("atan")
def _atan(x: float) -> float:
    return _de_rad(math.atan(x))


def _raiz(x: float, n: float = 2) -> float:
    if n == 0:
        raise ValueError("o índice da raiz não pode ser zero")
    if x < 0:
        if float(n).is_integer() and int(n) % 2 == 1:
            return -((-x) ** (1.0 / n))
        raise ValueError("raiz de número negativo exige índice ímpar")
    return x ** (1.0 / n)


@_dominio("log")
def _log(x: float, base: float = 10) -> float:
    return math.log(x, base)


@_dominio("ln")
def _ln(x: float) -> float:
    return math.log(x)


@_dominio("log2")
def _log2(x: float) -> float:
    return math.log2(x)


def _fact(n: float | int) -> int:
    if isinstance(n, float):
        if not n.is_integer():
            raise ValueError("o fatorial exige um número inteiro")
        n = int(n)
    if n < 0:
        raise ValueError("o fatorial exige um inteiro não negativo")
    if n > _LIMITE_FATORIAL:
        raise ValueError(f"fatorial limitado a {_LIMITE_FATORIAL}")
    return math.factorial(n)


FUNCOES = {
    # trigonometria (respeita o modo graus/radianos)
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "asin": _asin,
    "acos": _acos,
    "atan": _atan,
    "sinh": _dominio("sinh")(math.sinh),
    "cosh": _dominio("cosh")(math.cosh),
    "tanh": _dominio("tanh")(math.tanh),
    # raízes e potência
    "sqrt": _dominio("sqrt")(math.sqrt),
    "cbrt": lambda x: _raiz(x, 3),
    "raiz": _raiz,
    # logaritmos e exponencial
    "log": _log,
    "ln": _ln,
    "log2": _log2,
    "exp": _dominio("exp")(math.exp),
    # arredondamento e afins
    "abs": abs,
    "round": round,
    "floor": lambda x: float(math.floor(x)),
    "ceil": lambda x: float(math.ceil(x)),
    "hypot": math.hypot,
    # fatorial e conversão de ângulo
    "fact": _fact,
    "deg": math.degrees,
    "rad": math.radians,
}


# ------------------------------------------------------------------ avaliação

_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def normalizar(texto: str) -> str:
    """Aceita símbolos comuns de calculadora e converte para Python."""
    trocas = str.maketrans(
        {
            "×": "*",
            "·": "*",
            "÷": "/",
            "−": "-",
            "π": "pi",
            "√": "sqrt",
        }
    )
    texto = texto.translate(trocas)
    texto = texto.replace("^", "**")
    # 5! vira fact(5); evita mexer em "!=" e em nomes.
    texto = re.sub(r"(?<![\w.])(\d+(?:\.\d+)?)!", r"fact(\1)", texto)
    return texto


def _potencia(base, expoente):
    if isinstance(base, int) and isinstance(expoente, int):
        if abs(expoente) > 10000:
            raise ValueError("expoente grande demais")
        if abs(base) > 1 and abs(expoente) > 1000:
            raise ValueError("potência grande demais")
    return base ** expoente


def _visitar(no, estado: Estado):
    if isinstance(no, ast.Constant):
        if isinstance(no.value, bool) or not isinstance(no.value, (int, float)):
            raise ValueError("apenas números são permitidos")
        return no.value

    if isinstance(no, ast.BinOp):
        operador = _OPERADORES.get(type(no.op))
        if operador is None:
            if isinstance(no.op, ast.Pow):
                return _potencia(_visitar(no.left, estado), _visitar(no.right, estado))
            raise ValueError("operador não permitido")
        return operador(_visitar(no.left, estado), _visitar(no.right, estado))

    if isinstance(no, ast.UnaryOp):
        operador = _UNARIOS.get(type(no.op))
        if operador is None:
            raise ValueError("operador não permitido")
        return operador(_visitar(no.operand, estado))

    if isinstance(no, ast.Name):
        if no.id in CONSTANTES:
            return CONSTANTES[no.id]
        if no.id == "ans":
            return estado.ans
        if no.id in ("mem", "m"):
            return estado.memoria
        raise ValueError(f"nome desconhecido: {no.id}")

    if isinstance(no, ast.Call):
        if not isinstance(no.func, ast.Name) or no.func.id not in FUNCOES:
            raise ValueError("função desconhecida")
        if no.keywords:
            raise ValueError("argumentos nomeados não são permitidos")
        argumentos = [_visitar(arg, estado) for arg in no.args]
        nome = no.func.id
        try:
            return FUNCOES[nome](*argumentos)
        except TypeError as erro:
            raise ValueError(f"número de argumentos inválido para {nome}()") from erro

    raise ValueError("expressão não permitida")


def avaliar(expressao: str, estado: Estado) -> float | int:
    texto = normalizar(expressao)
    if len(texto) > _LIMITE_EXPRESSAO:
        raise ValueError("expressão longa demais")
    try:
        arvore = ast.parse(texto, mode="eval")
    except SyntaxError as erro:
        raise ValueError(
            "expressão inválida — confira parênteses e operadores"
        ) from erro
    return _visitar(arvore.body, estado)


# ------------------------------------------------------------------ comandos

AJUDA = """\
COMANDOS
  ajuda              mostra esta ajuda
  modo               mostra o modo de ângulo atual
  graus / deg        trigonometria em graus (padrão)
  rad / radianos     trigonometria em radianos
  historico / hist   últimas expressões calculadas
  limpar / clear     apaga o histórico
  m+ [valor]         soma à memória (sem valor, usa o último resultado)
  m- [valor]         subtrai da memória
  mr                 mostra a memória
  mc                 zera a memória
  sair / exit        encerra

FUNÇÕES
  sin cos tan        trigonometria (respeita graus/radianos)
  asin acos atan     inversas (resultado no modo atual)
  sinh cosh tanh     hiperbólicas
  sqrt cbrt raiz     raiz quadrada, cúbica e enésima: raiz(x, n)
  log ln log2 exp    log base 10, natural, base 2 e e^x
  abs round floor ceil
  fact               fatorial: fact(5) ou 5!
  hypot              hipotenusa: hypot(a, b)
  deg rad            converte radianos->graus e graus->radianos

CONSTANTES
  pi  e  tau  phi  inf
  ans                último resultado
  mem                valor da memória

OPERADORES
  + - * / // % ^ (ou **) e parênteses
"""

COMANDOS = {
    "ajuda",
    "help",
    "?",
    "modo",
    "graus",
    "deg",
    "rad",
    "radianos",
    "historico",
    "hist",
    "limpar",
    "clear",
    "mc",
    "m+",
    "m-",
    "mr",
    "sair",
    "exit",
    "quit",
    "q",
}


def _prompt(estado: Estado) -> str:
    modo = "graus" if em_graus() else "rad"
    return f"  [{modo}] > "


def _mostrar_memoria(estado: Estado) -> None:
    _imprimir(f"  memória = {formatar(estado.memoria)}")


def _valor_memoria(argumento: str, estado: Estado) -> float | int:
    if argumento:
        return avaliar(argumento, estado)
    return estado.ans


def executar_comando(entrada: str, estado: Estado) -> bool:
    """Executa um comando. Retorna False quando o usuário pede para sair."""
    partes = entrada.split(maxsplit=1)
    nome = partes[0].lower()
    argumento = partes[1].strip() if len(partes) > 1 else ""

    if nome in {"sair", "exit", "quit", "q"}:
        return False

    if nome in {"ajuda", "help", "?"}:
        _imprimir(AJUDA)
    elif nome == "modo":
        _imprimir(f"  modo de ângulo: {'graus' if em_graus() else 'radianos'}")
    elif nome in {"graus", "deg"}:
        usar_graus()
        _imprimir("  trigonometria em graus")
    elif nome in {"rad", "radianos"}:
        usar_radianos()
        _imprimir("  trigonometria em radianos")
    elif nome in {"historico", "hist"}:
        if not estado.historico:
            _imprimir("  (histórico vazio)")
        else:
            for indice, (expressao, resultado) in enumerate(
                estado.historico[-20:], start=1
            ):
                _imprimir(f"  {indice:>3}. {expressao} = {resultado}")
    elif nome in {"limpar", "clear"}:
        estado.historico.clear()
        _imprimir("  histórico apagado")
    elif nome == "m+":
        try:
            estado.memoria += _valor_memoria(argumento, estado)
        except (ValueError, ZeroDivisionError, OverflowError) as erro:
            _imprimir(f"  erro: {mensagem(erro)}")
            return True
        _mostrar_memoria(estado)
    elif nome == "m-":
        try:
            estado.memoria -= _valor_memoria(argumento, estado)
        except (ValueError, ZeroDivisionError, OverflowError) as erro:
            _imprimir(f"  erro: {mensagem(erro)}")
            return True
        _mostrar_memoria(estado)
    elif nome == "mr":
        _mostrar_memoria(estado)
    elif nome == "mc":
        estado.memoria = 0
        _imprimir("  memória zerada")

    return True


# ----------------------------------------------------------------------- main

BANNER = """\
==========================================
        CALCULADORA CIENTÍFICA
==========================================
Digite uma expressão, por exemplo:  sin(30) + sqrt(2)
Comandos: ajuda | sair
"""


def main() -> None:
    _configurar_saida()
    estado = Estado()
    _imprimir(BANNER)

    while True:
        try:
            entrada = input(_prompt(estado)).strip()
        except (EOFError, KeyboardInterrupt):
            _imprimir("\nAté a próxima!")
            return

        if not entrada:
            continue

        primeira = entrada.split(maxsplit=1)[0].lower()
        if primeira in COMANDOS:
            if not executar_comando(entrada, estado):
                _imprimir("Até a próxima!")
                return
            continue

        try:
            resultado = avaliar(entrada, estado)
        except (ValueError, ZeroDivisionError, OverflowError) as erro:
            _imprimir(f"  erro: {mensagem(erro)}")
            continue

        estado.ans = resultado
        formatado = formatar(resultado)
        estado.historico.append((entrada, formatado))
        del estado.historico[:-_LIMITE_HISTORICO]
        _imprimir(f"  = {formatado}")


if __name__ == "__main__":
    main()
