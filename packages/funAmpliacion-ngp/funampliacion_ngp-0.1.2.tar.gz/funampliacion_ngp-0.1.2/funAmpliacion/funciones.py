def sumatorio(n):
    sumaImpares = 0
    sumaPares = 0
    for i in range(1,n):
        if i%2==0:
            sumaPares+=i
        else:
            sumaImpares+=i
    print(f"La suma de pares es: {sumaPares}")
    print(f"La suma de impares es: {sumaImpares}")

def divisibles(n):
    for i in range(1,n):
        if i%5==0 ^ i%3==0:
            print(i,end="-")
    
def factorial(f):
    suma = 1
    for i in range(1,f+1):
        suma*=i
    print(f"El factorial es: {suma}")

def contarDigitosParesImpares(num):
    sumaPares = 0
    sumaImpares = 0
    for i in num:
        if int(i)%2==0:
            sumaPares+=1
            continue
        sumaImpares+=1
    print(f"Numeros pares: {sumaPares}")
    print(f"Numeros impares: {sumaImpares}")

def sumaAritmetica(a1,d,n):
    if n <= 0:
        print("El número de términos debe ser positivo.")
    else:
        Sn = n / 2 * (2 * a1 + (n-1) * d)
        print(f"La suma de los {n} primeros términos es: {Sn}")
        
def fibonacci(num):
    a,b=0,1
    for _ in range(num):
        print(a,end=",")
        a,b=b,b+a   

def numeroPerfecto(num):
    suma = 0
    for i in range(1,num):
        if num == i:
            continue
        if num%i==0:
            suma+=i
    if num == suma :
        print("Es perfecto")
    else:
        print("No es perfecto")

def potencias(base,exp):
    resultado = 1
    for _ in range(exp):
        resultado*=base
    print(resultado)

def inversion(num):
    invertido = ""
    for i in num:
        invertido=i+invertido
    print(invertido)

def palindromo(num):
    invertido = ""
    for i in num:
        invertido=i+invertido
    if num==invertido:
        print("Es palindromo")
    else:
        print("No es palindromo")

def conversionDecimalToBinario(numDecimal):
    numBinario = ""
    while numDecimal>0:
        resto=numDecimal%2
        numBinario=str(resto)+numBinario
        numDecimal=numDecimal//2
    print(numBinario)

def mcd(a,b):
    while b != 0:
        a, b = b, a % b
    print("El MCD es:", a)

def trianguloPascal(n):
    for i in range(n):
        num = 1
        print(" " * (n - i), end="")  # espacios para centrar
        for j in range(i + 1):
            print(num, end=" ")
            num = num * (i - j) // (j + 1)
        print()

def numPrimos(a,b):
    primos =[]
    for i in range(a,b+1):
        for j in range(2,i):
            if(i%j==0):
                break
        else:
            primos.append(i)
    print(primos) 

def descomposicionPrimos(a):
    factores = []
    i=2
    while i<=a:
        if a % i == 0:
            factores.append(i)
            a =a//i  # dividimos y seguimos con el cociente
        else:
            i += 1
    print(factores)

def digitosRepetidos(num):
    while num>=9:
        suma = 0
        for i in str(num):
            suma+=int(i)
        num=suma
    print(num)

def armstrong(num):
    suma=0
    for i in num:
        suma+=int(i)**3
    if int(num) == suma:
        print("Es Armstrong")
    else:
        print("No es Armstrong")
    
def ordenCreciente(num):
    alm = 0
    creciente = True

    for i in str(num):
        if int(i)>alm:
            alm=int(i)
        else:
            creciente=False
            break
    if(creciente==True):
        print("Orden creciente")
    else:
        print("No creciente")

def primosGemelos():
    primos=[]
    primosGemelos=[]
    for i in range(2,100):
        for j in range(2,i):
            if(i%j==0):
                break
        else:
            primos.append(i)

    for i in range(len(primos)-1):
        if primos[i+1]-primos[i]==2:
            primosGemelos.append(f"{primos[i]},{primos[i+1]}")
    print(primosGemelos)

def secuenciaCollatz(num):
    while num!=1:
        if num%2==0:
            pri = num
            num=num/2
            print(f"{pri}/2={num}")
        else:
            pri=num
            num=num*3+1
            print(f"{pri}*3+1={num}")

def hola():
    print("hola")