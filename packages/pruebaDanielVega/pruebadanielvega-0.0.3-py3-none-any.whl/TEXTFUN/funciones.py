def invertir(numero):
    "numero invertido"
    a= ""+numero
    numero=a[::-1] 
    "[::-1] toma la cadena del string al reves"
    return numero
def palindromo(numero):
    a=""+numero
    if a==a[::-1]:
        return "Es palindromo"
    else:
        return "No es palindromo"
def pasarBinario(numero):
    numeroA=""
    while(numero!=0):
        numeroA+=numero%2
        numero=numero/2
    return int(numeroA)
