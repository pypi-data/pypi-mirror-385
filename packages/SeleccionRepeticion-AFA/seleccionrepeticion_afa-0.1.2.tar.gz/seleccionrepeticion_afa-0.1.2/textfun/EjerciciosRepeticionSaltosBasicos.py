# 1. Mostrar los números del 1 al 10 usando un while.
a = 1
while a <= 10:
    print(a)
    a += 1

# 2. Mostrar los números del 1 al 10 usando un for y range().

for i in range (10):
    print(i +1)

# 3. Pedir un número al usuario y mostrar la cuenta atrás hasta 0.

num = int(input("Introduce un numero: "))

while num >= 0:
    print(num)
    num -= 1

# 4. Mostrar los números pares del 1 al 20.

for i in range (0,21,2):
    print(i)

# 5. Calcular y mostrar la suma de los números del 1 al 10.
suma = 0
for i in range (1,11):
    suma += i
print(suma)

# 6. Pedir un número y mostrar su tabla de multiplicar del 1 al 10.

numero = int(input("Introduce un numero: "))

for i in range (1,11):
    print(numero * i)

# 7. Pedir al usuario números hasta que introduzca un 0, y mostrar la suma total.

numero1 = int(input("Introduce un numero: "))
suma1 = 0
while numero1 != 0:
    suma1 += numero1
    numero1 = int(input("Introduce un numero: "))

print(suma1)

# 8. Dada la lista ["manzana", "pera", "uva"], mostrar cada elemento.

fruta = ["manzana", "pera", "uva"]

for i in fruta:
    print(i)

# 9. Pedir al usuario una palabra y mostrar cada letra en una línea.

palabra = input("Introduce una palabra: ")

for i in palabra:
    print(i)

# 10. Pedir una palabra y contar cuántas letras tiene usando un bucle.

palabra2 = input("Introduce una palabra: ")
letras = 0

for i in palabra2:
    letras +=1
print(letras)

# 11. Mostrar los impares entre 1 y 50 usando continue.

for i in range (1,51):
    if i % 2== 0:
        continue
    print(i)


# 12. Pedir números al usuario hasta que introduzca uno que sea múltiplo de 7.

numero2 = int(input("Introduce un numero: "))

while numero2 % 7 != 0:
    numero2 = int(input("Introduce un numero: "))
print("Numero multiplo de 7:",numero2)


# 13. El ordenador tiene un número secreto (ej. 15) y el usuario debe adivinarlo.

numSecreto = 15

adivina = int(input("Introduce cual crees que es el numero secreto: "))

while adivina != numSecreto:
    adivina = int(input("Introduce cual crees que es el numero secreto: "))
print("Has acertado el numero secreto", adivina)


# 14. Repetir un menú con opciones (1. Saludar, 2. Despedir, 3. Salir) hasta que el usuario elija salir.

numMenu = int(input("Introduce una opcion:  1. Saludar, 2. Despedir, 3. Salir: "))

while numMenu != 3:
    if numMenu == 1:
        print("Hola")
    else:
        print("Adios")
    numMenu = int(input("Introduce una opcion:  1. Saludar, 2. Despedir, 3. Salir: "))
print("SALIENDO DEL PROGRAMA")


# 15. Pedir notas hasta que el usuario introduzca -1. Mostrar la media de todas.

num5 = int(input("Introduce notas, salir(-1): "))
suma11 = 0
contador = 0

while num5 != -1:
    suma11 +=num5
    contador += 1
    num5 = int(input("Introduce notas, salir(-1): "))
print(suma11/contador)


# 16. Pedir un número n y mostrar los n primeros números de la serie de Fibonacci.
n = int(input("Cuantos numeros de la serie Fibonacci quieres ver? "))

a, b = 0, 1
contador = 0

print("Serie de Fibonacci:")

while contador < n:
    print(a)
    a, b = b, a + b
    contador += 1


# 17. Pedir un número y mostrar si es primo comprobando sus divisores con un bucle.

num6 = int(input("Introduce un numero: "))
es_primo = True

if num6 <= 1:
    es_primo = False

for i in range(2, int(num6**0.5) + 1):
    if num6 % i == 0:
        es_primo = False
        break

if es_primo:
    print(num6, "es un numero primo")
else:
    print(num6, "no es un numero primo")


# 18. Simular un login de usuario - contraseña con 3 posibles intentos.

usuario = "admin"
contraseña = "1234"
intentosRestantes = 3

while intentosRestantes > 0:
    usuarioInput = input("Introduce el usuario: ")
    contraseñaInput = input("Introduce la contraseña: ")

    if usuarioInput == usuario and contraseñaInput == contraseña:
        print("Login exitoso")
        break
    else:
        intentosRestantes -= 1
        print(f"Credenciales incorrectas. Te quedan {intentosRestantes} intentos.")
if intentosRestantes == 0:
    print("Has agotado todos los intentos. Acceso bloqueado.")
