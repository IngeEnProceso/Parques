import random


casillasGenerales = []
for i in range(1,69):
    casillasGenerales.append(i)

casillasSeguras = [12,17,29,34,46,51,63,68]
salidas = {
    "Rojo": 5,
    "Azul": 22,
    "Verde": 39,
    "Amarillo": 56
}

casillasRojo = []
casillasAzul = []
casillasVerde = []
casillasAmarillo = []

for i in range(1, 9):
    casillasRojo.append(i)
    casillasAzul.append(i)
    casillasVerde.append(i)
    casillasAmarillo.append(i)


def empezarJuego():
    print("Bienvenido al parqués de programadores.")
    global Njugadores
    while True:
        try: 
            Njugadores = int(input("Elige un numero de jugadores, maximo de 4: "))
            if Njugadores <= 4 and Njugadores > 1:
                break
            else:
                print("Elige un numero de jugadores valido.")
        except:
            print("Elige un valor valido.")
    return

empezarJuego()

colores = ["Rojo", "Azul", "Verde", "Amarillo"]
jugadores = []
for i in range(Njugadores):
    jugadores.append([colores[i], [0, 0, 0, 0]])
print("Que gane el mejor. ")


def tirarDados(color,posiciones):
    print(f"El color {color} lanza los dados, los numeros obtenidos son:")
    dado1 = random.randint(1,6)
    print(dado1)
    dado2 = random.randint(1,6)
    print(dado2)
    if any(pos == 0 for pos in posiciones):
        if dado1 + dado2 == 5:
            while True:
                try: 
                    fichaASacar = int(input("Tus dados sumaron 5. Elige una ficha a sacar: "))
                    if fichaASacar <= 4 and fichaASacar >= 1:
                        fichaASacar -= 1
                        if posiciones[fichaASacar] == 0:
                            posiciones[fichaASacar] = salidas[color]
                            break
                        else:
                            print("Elija una ficha en este en la carcel.")
                    else:
                        print("Elija una de sus 4 fichas.")
                except:
                    print("Elige un valor valido.")


while True:
    for i in jugadores:
            tirarDados(i[0],i[1])