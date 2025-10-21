# 1. Pedir un número y mostrar si es positivo o negativo.

num1 = int(input("Introduce un número: "))

if num1 < 0:
    print(f"El número {num1} es negativo")
else:
    print(f"El número {num1} es positivo")

# 2. Pedir un número y mostrar si es par o impar.

num2 = int(input("Introduce un numero: "))

if num2 % 2 == 0:
    print(f"El número {num2} es par")
else:
    print(f"El número {num2} es impar")

# 3. Pedir la edad y mostrar si la persona es mayor de edad (≥18) o no.

edad = int(input("Introduce tu edad: "))

if edad < 18:
    print("Eres menor de edad")
else:
    print("Eres mayor de edad")

# 4. Pedir una contraseña y comprobar si coincide con la guardada en una variable.

contraseña = "abc123"

contraseñaUser = str(input("Introduce la contraseña: "))

if contraseñaUser == contraseña:
    print("Contraseña correcta")
else:
    print("Contraseña incorrecta")

#5. Pedir una nota numérica y mostrar si el alumno aprueba (≥5) o suspende (<5).

nota = float(input("Introduce una nota: "))

if nota >= 5:
    print("El alumno ha aprobado")
else:
    print("El alumno ha suspendido.")

#6. Pedir un número y mostrar si es múltiplo de 3.

num3 = int(input("Introduce un numero: "))

if num3 % 3 == 0:
    print("Numero multiplo de 3")
else:
    print("Numero no multiplo de 3")

# 7. Pedir dos números y mostrar cuál es mayor (o si son iguales).

num4 = int(input("Introduce un numero: "))
num5 = int(input("Introduce otro numero: "))

if num4 > num5:
    print("El numero mayor es:", num4)
elif num5 > num4:
    print("El numero mayor es:", num5)
else:
    print("Los dos numeros son iguales")

# 8. Nota 0–4 → suspenso, 5–6 → aprobado, 7–8 → notable, 9–10 → sobresaliente.

nota2 = int(input("Introduce una nota: "))


match nota:
    case 0 | 1 | 2 | 3 | 4:
        print("Suspenso")
    case 5 | 6:
        print("Aprobado")
    case 7 | 8:
        print("Notable")
    case 9 | 10:
        print("Sobresaliente")
    case _:
        print("Numero no valido")

# 9. Pedir un número del 1 al 7 y mostrar qué día corresponde (1 = lunes…).

num6 = int(input("Introduce un numero del 1 al 7: "))

match num6:
    case 1:
        print("Lunes")
    case 2:
        print("Martes")
    case 3:
        print("Miércoles")
    case 4:
        print("Jueves")
    case 5:
        print("Viernes")
    case 6:
        print("Sábado")
    case 7:
        print("Domingo")
    case _:
        print("Número no válido")

# 10. Pedir dos números y una operación (+, -, *, /) y mostrar el resultado.

num7 = int(input("Introduce un numero: "))
num8 = int(input("Introduce otro numero: "))
operacion = str(input("Introduce una operacion (+, -, *, /): "))

match operacion:
    case "+":
        print(num7 + num8)
    case "-":
        print(num7 - num8)
    case "*":
        print(num7 * num8)
    case "/":
        print(num7 / num8)
    case _:
        print("Operacion invalida")

# 11. Pedir edad y si tiene carnet (True/False) y mostrar si puede conducir.

edad2 = int(input("Introduce tu edad: "))
carnet = bool(input("¿Tienes carnet?"))

if edad2 >= 18 and carnet:
    print("Puedes conducir")
else:
    print("No puedes conducir")

# 12. Pedir un número y mostrar si está entre 1 y 100.

num9 = int(input("Introduce un numero: "))

if 1 <= num9 <= 100:
    print("El numero esta entre 1 y 100")
else:
    print("El numero no esta entre 1 y 100")

# 13. Pedir tres notas y mostrar si el alumno aprueba (media ≥5 y ninguna <3).

nota3 = int(input("Introduce una nota: "))
nota4 = int(input("Introduce una nota: "))
nota5 = int(input("Introduce una nota: "))

media = (nota3 + nota4 + nota5) / 3

if media >= 5 and nota3 >= 3 and nota4 >= 3 and nota5 >= 3:
    print("El alumno ha aprobado")
else:
    print("El alumno ha suspendido")

# 14. Pedir tres lados y mostrar si el triángulo es equilátero, isósceles o escaleno.

lado1 = float(input("Introduce un lado: "))
lado2 = float(input("Introduce otro lado: "))
lado3 = float(input("Introduce otro lado: "))

if lado1 == lado2 == lado3:
    print("El triangulo es equilatero")
elif lado1 == lado2 or lado1 == lado3 or lado2 == lado3:
    print("El triangulo es isosceles")
else:
    print("El triangulo es escaleno")

# 15. Pedir un año y determinar si es bisiesto.

año = int(input("Introduce un año: "))

if (año % 4 == 0 and año % 100 != 0) or (año % 400 == 0):
    print(f"El año {año} es bisiesto")
else:
    print(f"El año {año} no es bisiesto")

# 16. El usuario elige una opción, el ordenador otra (usar random) y se indica quién gana.

import random
opciones = ["piedra", "papel", "tijeras"]

usuario = str(input("Elige piedra, papel o tijeras: ")).lower()
ordenador = random.choice(opciones)

print(f"El ordenador ha elegido: {ordenador}")
if usuario == ordenador:
    print("Empate")
elif (usuario == "piedra" and ordenador == "tijeras") or (usuario == "papel" and ordenador == "piedra") or (usuario == "tijeras" and ordenador == "papel"):
    print("Has ganado al ordenador!!!")
elif usuario not in opciones:
    print("Opción no válida")
else:
    print("Gana el ordenador")

'''
17. Pide al usuario el precio de un producto y su edad. Si el usuario es menor de 18 años → 10% de descuento. Si es mayor o igual a 65 años → 20% de descuento. 
En otro caso, no hay descuento. Muestra el precio final.
'''

precio = float(input("Introduce el precio del producto: "))
edad3 = int(input("Introduce tu edad: "))

match edad3:
    case edad3 if edad3 < 18:
        precioFinal = precio - (precio * 0.10)
        print(f"El precio final es: {precioFinal}")
    case edad3 if edad3 >= 65:
        precioFinal = precio - (precio * 0.20)
        print(f"El precio final es: {precioFinal}")
    case _:
        print(f"El precio final es: {precio}")

'''
18.Pide al usuario una temperatura y la unidad (C o F). Si la unidad es C, conviértela a Fahrenheit con la fórmula: F = C * 9/5 + 32. Si la unidad es F, 
conviértela a Celsius con la fórmula: C = (F - 32) * 5/9. Si la unidad no es válida, mostrar un mensaje de error.
'''

temperatura = float(input("Introduce una temperatura: "))
unidad = str(input("Introduce la unidad (C o F): "))

if unidad == "C":
    temperatura = temperatura * 9/5 +32
    print(f"Temperatura en Fahrenheit: {temperatura}")
elif unidad == "F":
    temperatura = (temperatura - 32) * 5/9
    print(f"Temperatura en grados: {temperatura}")
else:
    print("Unidad no valida")