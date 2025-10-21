def ej1(num):
    pares = 0
    impares = 0
    for i in range(num+1):
        if i % 2 == 0:
            pares += i
        else:
            impares += i
    print(f"Pares: {pares} Impares: {impares}")

def ej2():
    for i in range(101):
        if(i%5 == 0) ^ (i%3==0):
            if(i%5==0):
                print(f"Divisible emtre 5: {i}")
            if(i%3==0):
                print(f"Divisible emtre 3: {i}")

def ej3(num):
    fact = num
    for i in range(num):
        fact *= i
    print(fact)

def ej4(num):
    par = 0
    impar = 0
    for letra in num:
        letra = int(letra)
        if(letra % 2 == 0):
            par += 1
        else:
            impar += 1
    print(f"Pares: {par} Impares: {impar}") 

def ej5(a1,d,n):
    total = 0
    for i in range(n+1):
        total = i/2 * (2*a1 + ( i-1) * d)
        print(total)
        total = 0
    
def ej6(n):
    a,b = 0,1
    if n <= 0:
        print("Introduce numero positivo")
    elif n == 1:
        print(a)
    else:
        for _ in range(n):
            print(a)
            a,b = b,a + b
            print()

def ej7(num):
    div = 0
    if num <= 0:
        print("Debe ser postivo")
    else:
        for i in range (1,(num//2) +1):
            if num % i == 0:
                div += i
        if div == num:
            print("Es perfecto")
        else:
            print("No es perfecto")

def ej8(base,exponente):
    resul = 1

    for i in range(exponente):
        resul *= base
    print(resul)

def ej9(num_str):
    num=int(num_str)
    inv = 0
    while num > 0:
        digito = num % 10
        inv = (inv * 10) + digito
        num = num // 10
    print(inv)

def ej10(num):
    inv = 0
    while num > 0:
        digito = num % 10
        inv = (inv * 10) + digito
        num = num // 10
    if num == inv:
        print("Palindromo")
    else:
        print("No palindromo")

def ej11(num):
    bina = 0
    while num > 1:
        bina = (bina * 10) + num % 2
        num //= 2
    print(bina)

def ej12(num1,num2):
    while num2 != 0:
        num1,num2 = num2 , num1 % num2
    print(num1)

def ej13(filas):
    for i in range(filas):
        
        for esp in range(filas - i - 1):
            print(" ")
        coe = 1

        for j in range(i+1):
            if j == 0:
                coe = 1
            else:
                coe = coe * (i-j + 1)
            print(coe)
        print()

def ej14(num,num2):
    if a < 2:
        a = 2
    for i in range(num,num2 + 1):
        primo = True
        if(i == 1):
            primo = False
        else:
            for j in range(2,int(num**0.5)+1):
                if num % i == 0:
                    primo = False
                    break
        
        if primo:
            print(i)

def ej15(num):
    div = 2
    fact = True

    while div * div <= num:
        if num % div == 0:
            if not fact:
                print(" * ")
            print(div)
            fact = False
            num = num // div
        else:
            div += 1
    if num > 1:
        if not fact:
            print(" * ")
        print("num")
    print()



def ej16(lee):
    while int(lee) > 9:
        total = 0
        for num in str(lee):
            total += int(num)
            print(total)
        lee = total
        print(lee)
def ej17(num_Str):
    if len(num_Str) != 3:
        print("Mal")
        return
    
    num = int(num_Str)
    sum = 0

    for char in num_Str:
        digi = int(char)
        sum += (digi * digi * digi)
    
    if sum == num:
        print("Amstrong")
    else:
        print("No amstrong")

def ej18(num):
    max = 0
    bol = True
    for i in num:
        if int(i) < max:
            bol = False
            break
        max = int(i)
    if(bol):
        print("Ordenado")
    else:
        print("Desordenado")
def ej19(k):
    print("Por implementar")
def ej20(num):
    while num != 1:
        if num % 2 == 0:
            num /= 2
        else:
            num = num * 3 + 1
        print(num)