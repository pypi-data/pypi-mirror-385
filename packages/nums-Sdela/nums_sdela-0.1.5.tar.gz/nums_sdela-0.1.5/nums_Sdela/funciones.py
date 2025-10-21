#Ejercicio 1 Suma de números pares e impares. Pide un número n y calcula por separado la suma de los números pares y de los impares entre 1 y n.

def sumaPareImpar(n):
    np = 0
    ni = 0
    for i in range(n+1):
        if(i%2 == 0):
            np = np + i
        else:
            ni = ni + i

    return np, ni

#Ejercicio 2 Números divisibles por 3 y 5. Muestra todos los números del 1 al 100 que sean divisibles por 3 o por 5, pero no por ambos.

def div3y5():
    for i in range(101):
        if (i%3 == 0) ^ (i%5 == 0):
            print(i)

#Ejercicio 3 Factorial de un número. Pide un número entero positivo y calcula su factorial (n!). (Usar un bucle for o while)
    
def factorial(n):
    f = 1;
    for i in range(1, n+1):
        f = f * i
    return f

#Ejercicio 4 Contar de dígitos pares e impares. Pide un número y determina cuántos de sus dígitos son pares y cuántos impares.

def parImpar(n):
    for i in range(0, len(n)):
        if(int(n[i]) % 2 == 0):
            return "par"
        else:
            return "impar"

#Ejercicio 5 Suma de una serie aritmética. Calcula la suma de los n primeros términos de una serie aritmética,
#sabiendo el primer término a1 y la diferencia d. Fórmula: Sn = n/2 * (2*a1 + (n-1)*d). (Pide los datos y verifica que n sea positivo).

def serieAritmetica(a1, d, n):
    n = -1
    Sn = 0
    for i in range(0, n):
        Sn = Sn + i/2 * (2*a1 + (n-1)*d)
    return Sn

#6 Serie de Fibonacci. Pide un número n y muestra los primeros n términos de la serie de Fibonacci.

def fibonacci(n):
    a = 1
    b = 0
    s = ""
    for i in range(n):
        s = s + str(b)
        a, b = b, a+b
    return s

#7 Números perfectos. Un número es perfecto si es igual a la suma de sus divisores (excepto él mismo). Pide un número y determina si es perfecto.

def numPerfecto(n):
    t = 0
    for i in range(1, n-1):
        if n%i == 0:
            t = t + i
    if t == n:
        return "Es perfecto"
    else:
        return "No es perfecto"

#8 Potencias sin usar operador **. Pide una base y un exponente, y calcula la potencia mediante multiplicaciones sucesivas.

def potenciaSin(b, e):
    n = 1

    for i in range(e):
        n = n*b
    return n

#9 Inversión de número. Pide un número entero y muestra su valor invertido (por ejemplo, 1234 → 4321).
def numInverso(n):
    n = str(n)
    inv = ""
    for i in range(len(n)-1, -1, -1):
        inv = inv + n[i]
    return inv

#10 Palíndromo numérico. Determina si un número leído por teclado es palíndromo (se lee igual al derecho y al revés).
def numPalindromo():
    n = str(n)
    inv = ""
    for i in range(len(n)-1, -1, -1):
        inv = inv + n[i]
    if inv == n:
        return("es palindromo")
    else:
        return("no lo es")


#11 Conversión decimal → binario. Pide un número entero positivo y convierte a binario sin usar bin(). (Usar divisiones sucesivas entre 2 y guardar los restos.)

def aBin(n):
    s = ""
    while n//2 != 0:
        s = str(n%2) + s
        n = n//2
    s = str(n%2) + s
    return(s)

#12 Máximo común divisor (MCD). Calcula el MCD de dos números usando el algoritmo de Euclides.

def mcd(n1, n2):

    if n2>n1:
        n3 = n2
        n2 = n1
        n1 = n2

    while n2 != 0:
        print(n1)
        print("-----")
        print(n2)
        n1, n2 = n2, n1%n2

    return(f"M.C.D = {n1}")

#13 Triángulo de Pascal. Pide un número de filas n y muestra el triángulo de Pascal con bucles anidados.

def triPascal(n1):

    for i in range(n1):
        v = 1
        for j in range(i+1):
            print(v, end = " ")
            v = v * (i - j)//(j+1)
        print('\n')


#14 Números primos en un rango. Pide dos números a y b y muestra todos los primos entre a y b.

def primosRango(n1, n2):

    for i in range(n1, n2+1):
        pr = True
        for j in range(2, i):
            if i%j == 0:
                pr = False
        if pr == True:
            print(i)

#15 Descomposición en factores primos. Pide un número y muestra su descomposición en factores primos.

def descPrimo(n1):
    i = 2
    while n1 > 1:
        if n1%i == 0:
            print(i)
            n1 = n1//i
        else:
            i = i + 1

#16 Suma de dígitos repetida. Pide un número y suma sus dígitos repetidamente hasta obtener una sola cifra (número digital).

def sumaRepe(n1):
    sum = 0
    while len(str(n1)) > 1:
        for i in range(len(str(n1))):
            sum = sum + int(str(n1)[i])
        n1 = sum
        sum = 0
    return n1


#17 Detectar número Armstrong. Un número de 3 cifras es Armstrong si la suma de sus dígitos elevados al cubo es igual al propio número. (Ejemplo: 153 → 1³ + 5³ + 3³ = 153)
def numArmstrong(n1):

    d1 = int(str(n1)[0])
    d2 = int(str(n1)[1])
    d3 = int(str(n1)[2])

    if((pow(d1, 3) + pow(d2, 3) + pow(d3, 3)) == n1):
        return True
    else:
        return False

#18 Cifras crecientes. Pide un número y determina si sus cifras están en orden creciente (ejemplo: 1359 ✅, 1324 ❌).

def cifraCreciente(n1):
    check = True
    for i in range(len(str(n1))-1):
        if str(n1)[i]>str(n1)[i+1]:
            check = False
    if check == True:
        return True
    else:
        return False

#19 Números primos gemelos. Muestra todos los pares de números primos menores de 100 que difieren en 2 unidades.
def primosGemelos():
    ge = 2
    for i in range(2, 100):
        pr = True
        for j in range(2, i):
            if i%j == 0:
                pr = False
        if pr == True:
            if i == ge+2:
                print(f"{ge}, {i}")
                ge = i
            else:
                ge = i
        

#20 Secuencia de Collatz (o conjetura del 3n+1). Pide un número y genera la secuencia hasta llegar a 1: Si es par, se divide entre 2. Si es impar, se multiplica por 3 y se suma 1. (Mostrar la secuencia completa.)

def secuenciaCollatz(n1):
    while n1>1:
        if n1%2 == 0:
            n1 = n1//2
        else:
            n1 = n1*3 + 1
        print(n1)