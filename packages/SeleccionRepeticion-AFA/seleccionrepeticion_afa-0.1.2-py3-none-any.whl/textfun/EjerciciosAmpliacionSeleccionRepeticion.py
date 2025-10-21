#1. Suma de números pares e impares. Pide un número n y calcula por separado la suma de los números pares y de los impares entre 1 y n.

def suma_pares_impares(n):
    suma_pares = 0
    suma_impares = 0

    for i in range(1, n + 1):
        if i % 2 == 0:
            suma_pares += i
        else:
            suma_impares += i

    print("Pares:", suma_pares)
    print("Impares:", suma_impares)

#2. Números divisibles por 3 y 5. Muestra todos los números del 1 al 100 que sean divisibles por 3 o por 5, pero no por ambos.

def divisibles_3y5():
    for i in range (1,101):
        if i % 3 == 0 and i % 5 == 0:
            continue
        elif i % 3 == 0:
            print("Numero divisible por 3:",i)
        elif i % 5 == 0:
            print("Numero divisible por 5:",i)

# 3. Factorial de un número. Pide un número entero positivo y calcula su factorial (n!). (Usar un bucle for o while)

def factorialNum(n3):
    if n3 < 0:
        print("El número debe ser positivo.")
    else:
        factorial = 1

    for i in range(1, n3 + 1):
        factorial *= i  

    print(f"El factorial de {n3} es: {factorial}")


# 4. Contar de dígitos pares e impares. Pide un número y determina cuántos de sus dígitos son pares y cuántos impares.

def pares_impares(n4):
    pares = 0
    impares = 0

    for digito in n4:
        if digito.isdigit():
            if int(digito) % 2 == 0:
                pares += 1
            else:
                impares += 1

    print("Dígitos pares:", pares)
    print("Dígitos impares:", impares)


# 5. Suma de una serie aritmética. Calcula la suma de los n primeros términos de una serie aritmética, sabiendo el primer término a1 y la diferencia d. Fórmula: Sn = n/2 * (2*a1 + (n-1)*d). (Pide los datos y verifica que n sea positivo).

def serie_aritmetica(a1, d, n):
    if n <= 0:
        print("El número de términos debe ser positivo.")
    else:
        Sn = n / 2 * (2 * a1 + (n - 1) * d)
        print(f"La suma de los {n} primeros términos es: {Sn}")


# 6. Serie de Fibonacci. Pide un número n y muestra los primeros n términos de la serie de Fibonacci.

def fibonacci(n6):
    if n6 <= 0:
        print("Por favor, introduce un número positivo.")
    else:
        a, b = 0, 1
        print("Serie de Fibonacci:")
        for i in range(n6):
            print(a)
            a, b = b, a + b


# 7. Números perfectos. Un número es perfecto si es igual a la suma de sus divisores (excepto él mismo). Pide un número y determina si es perfecto.

def numeros_perfectos(n7):
    numPerfecto = 0

    for i in range(1, n7):
        if n7 % i == 0:
            numPerfecto += i

    if numPerfecto == n7:
        print(f"{n7} es un número perfecto.")
    else:
        print(f"{n7} no es un número perfecto.")


# 9. Inversión de número. Pide un número entero y muestra su valor invertido (por ejemplo, 1234 → 4321).

def inversion_numero(n9):
    invertido = n9[::-1]
    print(f"El número invertido es: {invertido}")

# 10. Palíndromo numérico. Determina si un número leído por teclado es palíndromo (se lee igual al derecho y al revés).

def Palindromo_numerico(n10):
    invertido = n10[::-1]

    if n10 == invertido:
        print(f"El número {n10} es palíndromo")
    else:
        print(f"El número {n10} no es palíndromo")

# 11. Conversión decimal → binario. Pide un número entero positivo y convierte a binario sin usar bin(). (Usar divisiones sucesivas entre 2 y guardar los restos.)

def conversion_decimalBinario(n11):
    if n11 < 0:
        print("¡Error! El número debe ser positivo.")
    else:
        if n11 == 0:
            binario = "0"
        else:
            binario = ""
            n = n11
            while n > 0:
                resto = n % 2
                binario = str(resto) + binario 
                n = n // 2
        print(f"El número {n11} en binario es: {binario}")

# 12. Máximo común divisor (MCD). Calcula el MCD de dos números usando el algoritmo de Euclides.

def MCD(a12, b12):
    x, y = a12, b12
    while y != 0:
        x, y = y, x % y

    print(f"El MCD de {a12} y {b12} es: {x}")

# 13. Triángulo de Pascal. Pide un número de filas n y muestra el triángulo de Pascal con bucles anidados.

def triangulo_pascal(n13):
    for i in range(n13):
        fila = [1]
        if i > 0:
            for j in range(1, i):
                fila.append(triangulo[i-1][j-1] + triangulo[i-1][j])
            fila.append(1)
        if i == 0:
            triangulo = [fila]
        else:
            triangulo.append(fila)
        print(' '*(n13-i), *fila)

# 14. Números primos en un rango. Pide dos números a y b y muestra todos los primos entre a y b.

def numeros_primos(inicioRango, finRango):
    for num in range(inicioRango, finRango+1):
        if num > 1:
            es_primo = True
            for i in range(2, int(num**0.5)+1):
                if num % i == 0:
                    es_primo = False
                    break
            if es_primo:
                print(num, end=' ')
    print()

# 15. Descomposición en factores primos. Pide un número y muestra su descomposición en factores primos.

def descomposicion_factoresPrimos(n15):
    n15 = n15
    factor8 = 2
    print(f"Descomposición en factores primos de {n15}: ", end='')
    while factor8 <= n15:
        if n15 % factor8 == 0:
            print(factor8, end=' ')
            n15 //= factor8
        else:
            factor8 += 1
    print()

# 16. Suma de dígitos repetida. Pide un número y suma sus dígitos repetidamente hasta obtener una sola cifra (número digital).

def suma_digitos_repetida(n16):
    num16 = n16
    while num16 >= 10:
        suma16 = 0
        for digito9 in str(num16):
            suma16 += int(digito9)
        num16 = suma16

    print(f"La suma de dígitos repetida de {n16} es: {num16}")

# 18. Cifras crecientes. Pide un número y determina si sus cifras están en orden creciente (ejemplo: 1359 ✅, 1324 ❌).

def cifras_crecientes(n18):
    creciente = all(n18[i] < n18[i+1] for i in range(len(n18)-1))

    if creciente:
        print(f"Las cifras de {n18} están en orden creciente")
    else:
        print(f"Las cifras de {n18} NO están en orden creciente")


# 19. Números primos gemelos. Muestra todos los pares de números primos menores de 100 que difieren en 2 unidades.

def primos_gemelos():
    def es_primo(num19):
        if num19 < 2:
            return False
        for i in range(2, int(num19 ** 0.5) + 1):
            if num19 % i == 0:
                return False
        return True

    print("Pares de números primos gemelos menores de 100:")

    for i in range(2, 100):
        if es_primo(i) and es_primo(i + 2):
            print(f"({i}, {i + 2})")

# 20. Secuencia de Collatz (o conjetura del 3n+1). Pide un número y genera la secuencia hasta llegar a 1: Si es par, se divide entre 2. Si es impar, se multiplica por 3 y se suma 1. (Mostrar la secuencia completa.)

def secuencia_collatz(n20):
    secuencia = [n20]  # Guardamos el número inicial
    while n20 != 1:
        if n20 % 2 == 0:
            n20 = n20 // 2  # Si es par, se divide entre 2
        else:
            n20 = 3 * n20 + 1  # Si es impar, se multiplica por 3 y se suma 1
        secuencia.append(n20)
    
    print("Secuencia de Collatz:")
    print(secuencia)