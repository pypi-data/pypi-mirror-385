# 1. Suma de números pares e impares. Pide un número n y calcula por separado la suma de los números pares y de los impares entre 1 y n.
def ejercicio1():
    suma_pares = 0
    suma_impares = 0
    num = int(input("Dime un número y te digo la suma por separado de los pares e impares: "))
    for i in range(1,num):
        if i % 2 == 0:
            suma_pares += i
        else:
            suma_impares += i
    print(f"La suma de los pares es {suma_pares} y la de los impares es {suma_impares}")

# 2. Números divisibles por 3 y 5. Muestra todos los números del 1 al 100 que sean divisibles por 3 o por 5, pero no por ambos.
def ejercicio2():
    for i in range(1,101):
        if(i % 3 == 0) ^ (i % 5 == 0):
            print(f"El número {i} es divisible por 3 o 5 pero no por ambos")

# 3. Factorial de un número. Pide un número entero positivo y calcula su factorial (n!). (Usar un bucle for o while)
def ejercicio3():
    num = int(input("Dime un numero entero y te doy su factorial: "))
    factorial = num
    while num > 1:
        num -= 1
        factorial *= num
    print(f"El factorial es: {factorial}")

# 4. Contar de dígitos pares e impares. Pide un número y determina cuántos de sus dígitos son pares y cuántos impares.
def ejercicio4():
    num = int(input("Dime un número que sea largo: "))
    numero = str(num)
    cnt_pares = 0
    cnt_impares = 0
    for c in numero:
        if int(c) % 2 == 0:
            cnt_pares += 1
        else: cnt_impares += 1
    print(f"El número {num} tiene un total de {cnt_pares} digitos que son pares y {cnt_impares} impares")

# 5. Suma de una serie aritmética. Calcula la suma de los n primeros términos de una serie aritmética, sabiendo el primer término a1 y la diferencia d. Fórmula: Sn = n/2 * (2*a1 + (n-1)*d). (Pide los datos y verifica que n sea positivo).
def ejercicio5():
    a1 = float(input("Dime a1: "))
    d = float(input("Dime la diferencia: "))
    n = int(input("Dime la cantidad de términos: "))
    if(n > 0):
        sn = 0
        for i in range(n):
            sn += i/2 * (2*a1 + (i-1)*d)
        print(f"La serie queda como: {sn}")
    else: print("n debe ser positivo")

# 6. Serie de Fibonacci. Pide un número n y muestra los primeros n términos de la serie de Fibonacci.
def ejercicio6():
    num = int(input("Dime la cantidad de numeros de fibonacci que quieres ver: "))
    num1 = 0
    num2 = 1
    while num > 0:
        print(num1)
        num2 += num1
        num1 = num2-num1
        num -= 1

# 7. Números perfectos. Un número es perfecto si es igual a la suma de sus divisores (excepto él mismo). Pide un número y determina si es perfecto.
def ejercicio7():
    num = int(input("Dime un número y te diré si es perfecto o no: "))
    sum = 0
    for i in range(1, num):
        if i % 2 == 0:
            sum += i
    if sum == num:
        print(f"{num} es un número perfecto")
    else: print(f"{num} no es un número perfecto")

# 8. Potencias sin usar operador **. Pide una base y un exponente, y calcula la potencia mediante multiplicaciones sucesivas.
def ejercicio8():
    base = int(input("Dime la base: "))
    exponente = int(input("Dime la exponente: "))
    total = base
    for i in range(1, exponente):
        total *= base
    print(f"{base}**{exponente} = {total}")

# 9. Inversión de número. Pide un número entero y muestra su valor invertido (por ejemplo, 1234 → 4321).
def ejercicio9():
    num = int(input("Dime un número que sea largo: "))
    numero = str(num)
    invertido = ""
    for i in range(len(numero),0,-1):
        invertido += i
    print(f"{numero} invertido es: {invertido}")

# 10. Palíndromo numérico. Determina si un número leído por teclado es palíndromo (se lee igual al derecho y al revés).
def ejercicio10():
    num = int(input("Dime un número que sea largo: "))
    numero = str(num)
    invertido = ""
    for i in range(len(numero),0,-1):
        invertido += numero[i-1]
    if numero == invertido:
        print(f"{numero} es palíndromo")
    else: print(f"{num} NO es palíndromo")

# 11. Conversión decimal → binario. Pide un número entero positivo y convierte a binario sin usar bin(). (Usar divisiones sucesivas entre 2 y guardar los restos.)
def ejercicio11():
    num = int(input("Dime un número entero positivo y te lo convierto a binario: "))
    binario = ""
    while num > 0:
        resto = int(num % 2)
        binario = str(resto) + binario
        num = num//2
    print(f"Tu número en binario es: {binario}")

    num1 = int(input("Te voy a calcular el MCD, dime el primero numero: "))
    num2 = int(input("Te voy a calcular el MCD, dime el segundo numero: "))
    resto = num1 % num2
    while resto != 0:
        num1 = num2
        num2 = resto
        resto = num1 % num2
    print(f"El MCD es {num2}")

# 12. Máximo común divisor (MCD). Calcula el MCD de dos números usando el algoritmo de Euclides.
def ejercicio12():
    num1 = int(input("Te voy a calcular el MCD, dime el primero numero: "))
    num2 = int(input("Te voy a calcular el MCD, dime el segundo numero: "))
    resto = num1 % num2
    while resto != 0:
        num1 = num2
        num2 = resto
        resto = num1 % num2
    print(f"El MCD es {num2}")

# 13. Triángulo de Pascal. Pide un número de filas n y muestra el triángulo de Pascal con bucles anidados.
def ejercicio13():
    filas = int(input("Dime el total de filas y te imprimiré el triangulo de pascal: "))
    filaActual = 1
    for i in range(filas):
        for j in range(filas - i - 1):
            print(" ", end="")
        
        num = 1
        for j in range(i + 1):
            print(num, end=" ")
            num = num * (i - j) // (j + 1) if j < i else 1
        print()

# 14. Números primos en un rango. Pide dos números a y b y muestra todos los primos entre a y b.
def ejercicio14():
    num1 = int(input("Te voy a decir los primos en un rango, dime el primer numero: "))
    num2 = int(input("Te voy a decir los primos en un rango, dime el segundo numero: "))
    for i in range(num1, num2):
        esPrimo = True
        for j in range(2,i):
            if i % j == 0:
                esPrimo = False
        if esPrimo:
            print(f"Numero primo: {i}")

# 15. Descomposición en factores primos. Pide un número y muestra su descomposición en factores primos.
def ejercicio15():
    num = int(input("Dime un numero y te hago su descomposición en factores primos: "))
    i = 2
    while i < num:
        while num % i == 0:
            print(i, end=" ")
            num = num // i
        i += 1
    print()

# 16. Suma de dígitos repetida. Pide un número y suma sus dígitos repetidamente hasta obtener una sola cifra (número digital).
def ejercicio16():
    num = int(input("Dime un número y lo sumaré hasta que quede en solo un digito: "))
    while num >= 10:
        nuevoNum = 0
        numStr = str(num)
        for i in range(0,len(numStr)):
            nuevoNum = nuevoNum + int(numStr[i])
        num = nuevoNum
    print(f"El digito final es: {num}")

# 17. Detectar número Armstrong. Un número de 3 cifras es Armstrong si la suma de sus dígitos elevados al cubo es igual al propio número. (Ejemplo: 153 → 1³ + 5³ + 3³ = 153)
def ejercicio17():
    num = int(input("Dime un número y te diré si es un númemro Armstrong o no: "))
    if num < 100 or num > 999:
        print(f"Tu número no es Armstrong ya que tiene más de 3 cifras")
    else:
        numeroStr = str(num)
        nuevoNum = 0
        for i in range(0,len(numeroStr)):
            nuevoNum += int(numeroStr[i])**3
        print(f"El número {num} tras el cálculo es {nuevoNum}.",end=" ")
        print("Por que tu número","no es Armstrong." if nuevoNum != num else "es Armstrong.")

# 18. Cifras crecientes. Pide un número y determina si sus cifras están en orden creciente (ejemplo: 1359 ✅, 1324 ❌).
def ejercicio18():
    num = int(input("Dime un número y te diré si es está en orden creciente o no: "))
    esCreciente = True
    numeroStr = str(num)
    if num > 0 and len(numeroStr) > 2:
        for i in range(0,len(numeroStr)-1):
            if int(numeroStr[i]) > int(numeroStr[i+1]):
                esCreciente = False
    if esCreciente:
        print(f"{num} está en orden creciente.")
    else:
        print(f"{num} no está en orden creciente.")

# 19. Números primos gemelos. Muestra todos los pares de números primos menores de 100 que difieren en 2 unidades.
def ejercicio19():
    LIMITE = 100
    i = 3
    while i < 100:
        esPrimo = True
        for j in range(2,i-1):
            if i % j == 0:
                esPrimo = False
        if esPrimo:
            tambienEsPrimo = True
            for j in range(2,i+1):
                if (i+2) % j == 0:
                    tambienEsPrimo = False
            if tambienEsPrimo:
                print(f"{i} {i+2}")
        i += 1

# 20. Secuencia de Collatz (o conjetura del 3n+1). Pide un número y genera la secuencia hasta llegar a 1: Si es par, se divide entre 2. Si es impar, se multiplica por 3 y se suma 1. (Mostrar la secuencia completa.)
def ejercicio20():
    num = int(input("Dime un número y te diré la secuencia de Collatz: "))
    while num > 1:
        if num % 2 == 0:
            num //= 2
        else:
            num = num * 3 + 1
        print(f"{num}")