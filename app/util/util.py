import math
# calculos de Índice de Masa Corporal (IMC) y Tasa Metabólica Basal (TMB) para determinar las calorías diarias necesarias para mantener el peso actual, adelgazar o aumentar de peso. Además, se proporcionará una distribución de macronutrientes (proteínas, grasas y carbohidratos) basada en los objetivos de salud y preferencias personales. También se incluirá una función para generar combinaciones de alimentos basadas en las necesidades calóricas y macronutricas.
def calcular_tmb(peso, altura, edad, genero):
    if genero == 0:
        return 9.99 * peso + 6.25 * altura - 4.92 * edad + 5
    else:
        return 9.99 * peso + 6.25 * altura - 4.92 * edad - 161

def calcular_calorias_totales(tmb, nivel_actividad):
    factores_actividad = [1.2, 1.375, 1.55, 1.725, 1.9]
    return tmb * factores_actividad[nivel_actividad]

def calcular_macronutrientes(calorias_totales):
    proteinas = calorias_totales * 0.3 / 4
    grasas = calorias_totales * 0.3 / 9
    carbohidratos = calorias_totales * 0.4 / 4
    return [proteinas, grasas, carbohidratos]

def get_combination_at_index(n, index):
    combination = []
    k = 0
    remaining_index = index
    while remaining_index >= math.comb(n, k):
        remaining_index -= math.comb(n, k)
        k += 1
    current_n = n
    while k > 0:
        if remaining_index < math.comb(current_n - 1, k - 1):
            combination.append(n - current_n)
            k -= 1
        else:
            remaining_index -= math.comb(current_n - 1, k - 1)
        current_n -= 1
    return combination


def calcular_imc(peso, altura):
    if altura > 3:
        altura = altura / 100 
    imc = peso / (altura ** 2)
    return imc