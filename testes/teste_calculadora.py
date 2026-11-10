"""Testes do motor de cálculo (`calculadora.py`).

Execute com:

    python -m unittest discover -s testes -v
"""

from __future__ import annotations

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import calculadora


class TesteOperacoes(unittest.TestCase):
    def setUp(self) -> None:
        self.estado = calculadora.Estado()
        calculadora.usar_graus()

    def calcular(self, expressao: str):
        return calculadora.avaliar(expressao, self.estado)

    def test_operacoes_basicas(self):
        self.assertEqual(self.calcular("2 + 3 * 4"), 14)
        self.assertEqual(self.calcular("(2 + 3) * 4"), 20)
        self.assertEqual(self.calcular("10 % 4"), 2)
        self.assertEqual(self.calcular("7 // 2"), 3)

    def test_simbolos_de_calculadora(self):
        self.assertEqual(self.calcular("10 × 2"), 20)
        self.assertEqual(self.calcular("10 ÷ 4"), 2.5)
        self.assertEqual(self.calcular("5 − 8"), -3)
        self.assertAlmostEqual(self.calcular("√(16)"), 4.0)
        self.assertAlmostEqual(self.calcular("π"), math.pi)

    def test_potencias(self):
        self.assertEqual(self.calcular("2^10"), 1024)
        self.assertAlmostEqual(self.calcular("9^0.5"), 3.0)

    def test_funcoes(self):
        self.assertEqual(self.calcular("fact(5)"), 120)
        self.assertEqual(self.calcular("5!"), 120)
        self.assertAlmostEqual(self.calcular("cbrt(27)"), 3.0)
        self.assertAlmostEqual(self.calcular("log(8, 2)"), 3.0)
        self.assertAlmostEqual(self.calcular("ln(e)"), 1.0)
        self.assertEqual(self.calcular("abs(-3)"), 3)

    def test_trigonometria_em_graus(self):
        self.assertTrue(calculadora.em_graus())
        self.assertAlmostEqual(self.calcular("sin(30)"), 0.5)
        self.assertAlmostEqual(self.calcular("cos(60)"), 0.5)
        self.assertAlmostEqual(self.calcular("tan(45)"), 1.0)

    def test_trigonometria_em_radianos(self):
        calculadora.usar_radianos()
        self.addCleanup(calculadora.usar_graus)
        self.assertFalse(calculadora.em_graus())
        self.assertAlmostEqual(self.calcular("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(self.calcular("asin(1)"), math.pi / 2)

    def test_ans_e_memoria(self):
        self.estado.ans = 42
        self.estado.memoria = 7
        self.assertEqual(self.calcular("ans + mem"), 49)

    def test_estado_padrao(self):
        estado = calculadora.Estado()
        self.assertEqual(estado.ans, 0)
        self.assertEqual(estado.memoria, 0)
        self.assertEqual(estado.historico, [])


class TesteSeguranca(unittest.TestCase):
    def setUp(self) -> None:
        self.estado = calculadora.Estado()

    def test_codigo_arbitrario_bloqueado(self):
        proibidas = [
            "__import__('os')",
            "open('arquivo')",
            "1 if 2 else 3",
            "[1, 2]",
            "f'{1}'",
        ]
        for expressao in proibidas:
            with self.subTest(expressao=expressao):
                with self.assertRaises(ValueError):
                    calculadora.avaliar(expressao, self.estado)

    def test_expressao_longa(self):
        with self.assertRaises(ValueError):
            calculadora.avaliar("1+" * 300 + "1", self.estado)


class TesteErros(unittest.TestCase):
    def setUp(self) -> None:
        self.estado = calculadora.Estado()
        calculadora.usar_graus()

    def test_divisao_por_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calculadora.avaliar("1 / 0", self.estado)
        self.assertEqual(
            calculadora.mensagem(ZeroDivisionError()), "divisão por zero"
        )

    def test_raiz_de_negativo(self):
        with self.assertRaises(ValueError):
            calculadora.avaliar("sqrt(-1)", self.estado)

    def test_fatorial_invalido(self):
        with self.assertRaises(ValueError):
            calculadora.avaliar("fact(-1)", self.estado)

    def test_sintaxe_invalida(self):
        with self.assertRaises(ValueError):
            calculadora.avaliar("2 +", self.estado)

    def test_nome_desconhecido(self):
        with self.assertRaises(ValueError):
            calculadora.avaliar("x + 1", self.estado)


class TesteFormatacao(unittest.TestCase):
    def test_formatar(self):
        self.assertEqual(calculadora.formatar(14), "14")
        self.assertEqual(calculadora.formatar(2.5), "2.5")
        self.assertEqual(calculadora.formatar(0), "0")
        self.assertEqual(calculadora.formatar(1 / 3), "0.333333333333")
        self.assertEqual(calculadora.formatar(1e20), "1e20")
        self.assertEqual(calculadora.formatar(math.pi), "3.14159265359")

    def test_formatar_especiais(self):
        self.assertEqual(calculadora.formatar(math.inf), "inf")
        self.assertEqual(calculadora.formatar(-math.inf), "-inf")
        self.assertEqual(calculadora.formatar(math.nan), "NaN")


if __name__ == "__main__":
    unittest.main()
