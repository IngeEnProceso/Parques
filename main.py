import random

casillasGenerales = list(range(1, 69))
casillasSeguras = [12, 17, 29, 34, 46, 51, 63, 68]
salidas = {
    "Rojo": 5,
    "Azul": 22,
    "Verde": 39,
    "Amarillo": 56
}

entradas_llegada = {
    "Rojo": 68,
    "Azul": 17,
    "Verde": 34,
    "Amarillo": 51
}

casillasLlegada = {
    "Rojo": list(range(69, 77)),
    "Azul": list(range(77, 85)),
    "Verde": list(range(85, 93)),
    "Amarillo": list(range(93, 101))
}

paresConsecutivos = {}
modoDesarrollador = False

def get_int(prompt, min_val=None, max_val=None, alert="Ingrese un valor válido."):
    while True:
        try:
            value = int(input(prompt))
            if (min_val is None or value >= min_val) and (max_val is None or value <= max_val):
                return value
            print(alert)
        except ValueError:
            print(alert)

def mostrarTablero(jugadores):
    print("\n" + "="*50)
    print("ESTADO DEL TABLERO")
    print("="*50)
    
    for jugador in jugadores:
        color, fichas = jugador
        print(f"\n{color}:")
        for i, ficha in enumerate(fichas):
            if ficha["estado"] == "carcel":
                print(f"  Ficha {i+1}: En cárcel")
            elif ficha["estado"] == "tablero":
                print(f"  Ficha {i+1}: Casilla {ficha['pos']}")
            elif ficha["estado"] == "llegada":
                print(f"  Ficha {i+1}: En llegada (posición {ficha['pos']})")
            elif ficha["estado"] == "meta":
                print(f"  Ficha {i+1}: En meta")

def empezarJuego():
    global paresConsecutivos, modoDesarrollador
    
    print("Bienvenido al parqués de programadores.")
    
    modo = get_int("Seleccione modo:\n1. Modo real\n2. Modo desarrollador\nOpción: ", 1, 2)
    modoDesarrollador = (modo == 2)
    
    Njugadores = get_int("Elige un número de jugadores, máximo de 4: ", 2, 4)
    colores = ["Rojo", "Azul", "Verde", "Amarillo"]
    jugadores = []
    
    for i in range(Njugadores):
        color = colores[i]
        paresConsecutivos[color] = 0
        jugadores.append([
            color, 
            [
                {"estado": "carcel", "pos": 0, "id": j} for j in range(4)
            ]
        ])
    
    print("Que gane el mejor.")
    
    while True:
        for i in range(Njugadores):
            color, fichas = jugadores[i]
            mostrarTablero(jugadores)
            
            if verificarVictoria(fichas):
                print(f"\n¡{color} ha ganado!")
                return
            
            turnoCompleto = False
            while not turnoCompleto:
                turnoCompleto = tirarDados(color, fichas, jugadores)

def SePuedeSacarFicha(dado1, dado2):
    if dado1 + dado2 == 5:
        return "suma"
    if dado1 == 5 and dado2 == 5:
        return "doble"
    if dado1 == 5 or dado2 == 5:
        return "simple"
    return False

def obtenerDados():
    global modoDesarrollador
    
    if modoDesarrollador:
        opcion = get_int("1. Lanzamiento real\n2. Escoger números\nOpción: ", 1, 2)
        if opcion == 1:
            dado1 = random.randint(1, 6)
            dado2 = random.randint(1, 6)
        else:
            dado1 = get_int("Primer dado: ", 1, 6)
            dado2 = get_int("Segundo dado: ", 1, 6)
    else:
        dado1 = random.randint(1, 6)
        dado2 = random.randint(1, 6)
    
    return dado1, dado2

def fichasEnCasilla(pos, jugadores, excluir_color=None):
    count = 0
    fichas_en_casilla = []
    
    for jugador in jugadores:
        color, fichas = jugador
        if excluir_color and color == excluir_color:
            continue
            
        for ficha in fichas:
            if ficha["estado"] == "tablero" and ficha["pos"] == pos:
                count += 1
                fichas_en_casilla.append((color, ficha))
    
    return count, fichas_en_casilla

def esCasillaSegura(pos):
    return pos in casillasSeguras

def esSalida(pos, color):
    return pos == salidas[color]

def hayBloqueo(pos, jugadores, color_actual):
    count, fichas_en_casilla = fichasEnCasilla(pos, jugadores)
    
    if count >= 2:
        colores_en_casilla = set([color for color, _ in fichas_en_casilla])
        
        if len(colores_en_casilla) == 1:
            return True
        elif esCasillaSegura(pos) or any(esSalida(pos, c) for c in colores_en_casilla):
            return True
    
    return False

def calcularRecorrido(pos_actual, pos_destino):
    if pos_destino >= pos_actual:
        return pos_destino - pos_actual
    else:
        return (68 - pos_actual) + pos_destino

def moverFicha(ficha, movimientos, color, jugadores):
    if ficha["estado"] == "carcel":
        return False
    
    if ficha["estado"] == "tablero":
        pos_actual = ficha["pos"]
        entrada_llegada = entradas_llegada[color]
        nueva_pos = pos_actual + movimientos
        
        if nueva_pos > 68:
            nueva_pos = nueva_pos - 68
        
        if pos_actual < entrada_llegada and nueva_pos >= entrada_llegada:
            exceso = nueva_pos - entrada_llegada
            if exceso <= 8:
                ficha["estado"] = "llegada"
                ficha["pos"] = exceso
                if exceso == 8:
                    ficha["estado"] = "meta"
                    return "meta"
                return "llegada"
            else:
                return False
        elif pos_actual == entrada_llegada and movimientos <= 8:
            ficha["estado"] = "llegada"
            ficha["pos"] = movimientos
            if movimientos == 8:
                ficha["estado"] = "meta"
                return "meta"
            return "llegada"
        
        if hayBloqueo(nueva_pos, jugadores, color):
            return False
        
        count, fichas_en_casilla = fichasEnCasilla(nueva_pos, jugadores, color)
        if count > 0 and not esCasillaSegura(nueva_pos) and not esSalida(nueva_pos, color):
            for color_enemigo, ficha_enemiga in fichas_en_casilla:
                ficha_enemiga["estado"] = "carcel"
                ficha_enemiga["pos"] = 0
            
            ficha["pos"] = nueva_pos
            return "captura"
        
        ficha["pos"] = nueva_pos
        return True
    
    elif ficha["estado"] == "llegada":
        nueva_pos = ficha["pos"] + movimientos
        if nueva_pos == 8:
            ficha["pos"] = nueva_pos
            ficha["estado"] = "meta"
            return "meta"
        elif nueva_pos < 8:
            ficha["pos"] = nueva_pos
            return True
        else:
            return False
    
    return False

def sacarFicha(color, fichas, jugadores):
    fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
    if not fichas_en_carcel:
        return False
    
    salida_pos = salidas[color]
    count, fichas_en_casilla = fichasEnCasilla(salida_pos, jugadores)
    
    if count >= 2:
        return False
    
    if count == 1:
        color_enemigo, ficha_enemiga = fichas_en_casilla[0]
        if color_enemigo != color:
            ficha_enemiga["estado"] = "carcel"
            ficha_enemiga["pos"] = 0
    
    fichas_en_carcel[0]["estado"] = "tablero"
    fichas_en_carcel[0]["pos"] = salida_pos
    return True

def obtenerMovimientosPosibles(fichas, color, jugadores, movimientos):
    movimientos_posibles = []
    
    for i, ficha in enumerate(fichas):
        if ficha["estado"] == "carcel" or ficha["estado"] == "meta":
            continue
        
        ficha_temp = ficha.copy()
        resultado = moverFicha(ficha_temp, movimientos, color, jugadores)
        if resultado:
            movimientos_posibles.append((i, ficha))
    
    return movimientos_posibles

def obtenerFichasEnSalida(fichas, color):
    salida_pos = salidas[color]
    fichas_en_salida = []
    
    for i, ficha in enumerate(fichas):
        if ficha["estado"] == "tablero" and ficha["pos"] == salida_pos:
            fichas_en_salida.append((i, ficha))
    
    return fichas_en_salida

def verificarVictoria(fichas):
    return all(f["estado"] == "meta" for f in fichas)

def tirarDados(color, fichas, jugadores):
    global paresConsecutivos
    
    print(f"\n--- Turno de {color} ---")
    input("Presiona Enter para lanzar los dados...")
    
    dado1, dado2 = obtenerDados()
    print(f"Dados obtenidos: {dado1} y {dado2}")
    
    es_par = (dado1 == dado2)
    if es_par:
        paresConsecutivos[color] += 1
        print(f"¡Par! Pares consecutivos: {paresConsecutivos[color]}")
        
        if paresConsecutivos[color] == 3:
            print("¡Tres pares consecutivos! La última ficha movida va a la cárcel.")
            fichas_en_juego = [f for f in fichas if f["estado"] not in ["carcel", "meta"]]
            if fichas_en_juego:
                fichas_en_juego[-1]["estado"] = "carcel"
                fichas_en_juego[-1]["pos"] = 0
            paresConsecutivos[color] = 0
            return True
    else:
        paresConsecutivos[color] = 0
    
    puede_sacar = SePuedeSacarFicha(dado1, dado2)
    fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
    fichas_en_salida = obtenerFichasEnSalida(fichas, color)
    
    dados_disponibles = [dado1, dado2]
    fichas_por_sacar = 0
    
    if puede_sacar == "doble":
        fichas_por_sacar = min(len(fichas_en_carcel), 2)
    elif puede_sacar in ["simple", "suma"]:
        fichas_por_sacar = min(len(fichas_en_carcel), 1)
    
    if puede_sacar and fichas_por_sacar > 0:
        if len(fichas_en_salida) >= 2:
            dados_no_cinco = [d for d in dados_disponibles if d != 5]
            
            if dados_no_cinco:
                print("Tienes fichas en tu salida y debes mover alguna antes de sacar.")
                
                print("\nFichas en salida que deben moverse:")
                for j, (i, ficha) in enumerate(fichas_en_salida):
                    print(f"{j+1}. Ficha {i+1}")
                
                while len(fichas_en_salida) >= 2 and dados_no_cinco:
                    eleccion = get_int("Elige qué ficha de la salida mover: ", 1, len(fichas_en_salida))
                    i, ficha = fichas_en_salida[eleccion-1]
                    
                    dado_a_usar = dados_no_cinco[0]
                    if len(dados_no_cinco) > 1:
                        print(f"Dados disponibles (sin contar el 5): {dados_no_cinco}")
                        dado_a_usar = get_int("¿Con qué dado mover?: ", min(dados_no_cinco), max(dados_no_cinco))
                        while dado_a_usar not in dados_no_cinco:
                            print("Debes usar un dado que no sea 5.")
                            dado_a_usar = get_int("¿Con qué dado mover?: ", min(dados_no_cinco), max(dados_no_cinco))
                    
                    resultado = moverFicha(ficha, dado_a_usar, color, jugadores)
                    if resultado:
                        print(f"Ficha {i+1} se mueve {dado_a_usar} casillas")
                        dados_disponibles.remove(dado_a_usar)
                        dados_no_cinco.remove(dado_a_usar)
                        fichas_en_salida = obtenerFichasEnSalida(fichas, color)
                        if resultado == "captura":
                            print("¡Captura realizada! 20 movimientos extra")
                        elif resultado == "llegada":
                            print("¡Ficha llegó a su destino! 10 movimientos extra")
                        elif resultado == "meta":
                            print("¡Ficha llegó a la meta!")
        
        fichas_sacadas = 0
        while fichas_sacadas < fichas_por_sacar and len(fichas_en_carcel) > 0:
            if sacarFicha(color, fichas, jugadores):
                print(f"Ficha de {color} sale de la cárcel!")
                fichas_sacadas += 1
                fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
        
        if puede_sacar == "suma":
            dados_disponibles = []
        elif puede_sacar == "simple":
            dados_disponibles = [d for d in dados_disponibles if d != 5]
        elif puede_sacar == "doble":
            dados_restantes = 2 - fichas_sacadas
            dados_disponibles = [5] * dados_restantes
    
    for dado in dados_disponibles:
        movimientos_posibles = obtenerMovimientosPosibles(fichas, color, jugadores, dado)
        
        if not movimientos_posibles:
            print(f"No hay movimientos posibles con el dado {dado}")
            continue
        
        if len(movimientos_posibles) == 1:
            i, ficha = movimientos_posibles[0]
            resultado = moverFicha(ficha, dado, color, jugadores)
            if resultado:
                print(f"Ficha {i+1} se mueve {dado} casillas automáticamente")
                if resultado == "captura":
                    print("¡Captura realizada! 20 movimientos extra")
                elif resultado == "llegada":
                    print("¡Ficha llegó a su destino! 10 movimientos extra")
                elif resultado == "meta":
                    print("¡Ficha llegó a la meta!")
        else:
            print(f"\nFichas que pueden moverse con {dado}:")
            for j, (i, ficha) in enumerate(movimientos_posibles):
                estado_actual = "tablero" if ficha["estado"] == "tablero" else "llegada"
                print(f"{j+1}. Ficha {i+1} (en {estado_actual}, posición {ficha['pos']})")
            
            eleccion = get_int("Elige qué ficha mover: ", 1, len(movimientos_posibles))
            
            i, ficha = movimientos_posibles[eleccion-1]
            resultado = moverFicha(ficha, dado, color, jugadores)
            if resultado:
                print(f"Ficha {i+1} se mueve {dado} casillas")
                if resultado == "captura":
                    print("¡Captura realizada! 20 movimientos extra")
                elif resultado == "llegada":
                    print("¡Ficha llegó a su destino! 10 movimientos extra")
                elif resultado == "meta":
                    print("¡Ficha llegó a la meta!")
    
    if es_par and paresConsecutivos[color] < 3:
        print("Como sacaste par, juegas de nuevo!")
        return False
    
    return True

if __name__ == "__main__":
    empezarJuego()
