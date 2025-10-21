# Suma de números pares e impares. Pide un número n y calcula por separado la suma de los números pares y de los impares entre 1 y n.

def suma_pares_impares(numero):
    suma_pares = 0
    suma_impares = 0

    for n in range(1, numero+1):
        if n % 2 == 0:
            suma_pares += n
        else:
            suma_impares +=n

    return suma_pares, suma_impares


# Números divisibles por 3 y 5. Muestra todos los números del 1 al 100 que sean divisibles por 3 o por 5, pero no por ambos.

def numeros_divisibles_3_o_5():
     divisible_numbers = []
     for numero in range(1, 101):
         if numero % 3 == 0  or numero % 5 == 0:
             if not (numero % 3 == 0 and numero % 5 == 0):
                 divisible_numbers.append(numero)
     return divisible_numbers


# Factorial de un número. Pide un número entero positivo y calcula su factorial (n!). (Usar un bucle for o while)

def calcular_factorial(numero):
     factorial = 1

     for n in range(1, numero+1):
         factorial *= n

     return factorial


# Contar de dígitos pares e impares. Pide un número y determina cuántos de sus dígitos son pares y cuántos impares.

def contar_digitos_pares_impares(numero):
     contador_pares = 0
     contador_impares = 0

     for digito in str(numero):
         if int(digito) % 2 == 0:
             contador_pares += 1
         else:
             contador_impares += 1

     return contador_pares, contador_impares


# Suma de una serie aritmética. Calcula la suma de los n primeros términos de una serie aritmética, sabiendo el primer término a1 y la diferencia d. Fórmula: Sn = n/2 * (2*a1 + (n-1)*d). (Pide los datos y verifica que n sea positivo).

def suma_serie_aritmetica(a1, d, n):
    if n > 0:
        Sn = n / 2 * (2 * a1 + (n - 1) * d)
        return Sn
    else:
        raise ValueError("El número de términos (n) debe ser positivo")
    

# Serie de Fibonacci. Pide un número n y muestra los primeros n términos de la serie de Fibonacci.

def fibonacci(numero):
    a, b = 0, 1
    terms = []
    for _ in range(numero):
        terms.append(a)
        a, b = b, a + b
    return terms

# Números perfectos. Un número es perfecto si es igual a la suma de sus divisores (excepto él mismo). Pide un número y determina si es perfecto.

def es_numero_perfecto(numero):
    suma_divisores = 0
    for i in range(1, numero):
        if numero % i == 0:
            suma_divisores += i
    return suma_divisores == numero


# Potencias sin usar operador **. Pide una base y un exponente, y calcula la potencia mediante multiplicaciones sucesivas.

def calcular_potencia(base, exponente):
    potencia = 1
    for _ in range(exponente):
        potencia *= base
    return potencia