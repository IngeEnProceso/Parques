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
            
            turnoCompleto = False
            while not turnoCompleto:
                turnoCompleto = tirarDados(color, fichas, jugadores)
                        
            if verificarVictoria(fichas):
                print(f"\n¡{color} ha ganado!")
                return

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

def esSalida(pos, color=None):
    if color:
        return pos == salidas[color]
    
    return pos in salidas.values()

def hayBloqueo(pos, jugadores, color_actual):
    count, fichas_en_casilla = fichasEnCasilla(pos, jugadores)
    
    if count < 2:
        return False
    
    if count == 2:
        colores_en_casilla = set([color for color, _ in fichas_en_casilla])
        
        if len(colores_en_casilla) == 1:
            return True
        
        elif len(colores_en_casilla) == 2:
            if esCasillaSegura(pos):
                return True
            elif esSalida(pos):
                return True
            else:
                return False
    
    return True

def calcularRecorrido(pos_actual, pos_destino):
    if pos_destino >= pos_actual:
        return pos_destino - pos_actual
    else:
        return (68 - pos_actual) + pos_destino
    
def puedeAtravesarBloqueo(ficha_pos, destino_pos, jugadores, color_actual):
    if ficha_pos > destino_pos:
        for pos in range(ficha_pos + 1, 69):
            if hayBloqueo(pos, jugadores, color_actual):
                return False
        for pos in range(1, destino_pos):
            if hayBloqueo(pos, jugadores, color_actual):
                return False
    else:
        for pos in range(ficha_pos + 1, destino_pos):
            if hayBloqueo(pos, jugadores, color_actual):
                return False
    
    return True

def moverFicha(ficha, movimientos, color, jugadores):
    if ficha["estado"] == "carcel":
        return False
    
    if ficha["estado"] == "tablero":
        pos_actual = ficha["pos"]
        entrada_llegada = entradas_llegada[color]
        
        pasa_por_entrada, exceso = pasaPorEntrada(pos_actual, movimientos, entrada_llegada)
        
        if pasa_por_entrada:
            if exceso <= 8: 
                if not puedeAtravesarBloqueoHastaEntrada(pos_actual, movimientos, entrada_llegada, jugadores, color):
                    return False
                
                # Mover a la zona de llegada
                ficha["estado"] = "llegada"
                ficha["pos"] = exceso
                
                if exceso == 8:
                    ficha["estado"] = "meta"
                    return "meta"
                return "llegada"
            else:
                return False
        else:
            nueva_pos = pos_actual + movimientos
            if nueva_pos > 68:
                nueva_pos = nueva_pos - 68
            
            if not puedeAtravesarBloqueo(pos_actual, nueva_pos, jugadores, color):
                return False
            
            if hayBloqueo(nueva_pos, jugadores, color):
                return False
            
            count, fichas_en_casilla = fichasEnCasilla(nueva_pos, jugadores, color)
            
            if count > 0:
                if esCasillaSegura(nueva_pos):
                    total_fichas = count + 1
                    if total_fichas > 2:
                        return False
                    ficha["pos"] = nueva_pos
                    return True
                
                elif esSalida(nueva_pos):
                    if esSalida(nueva_pos, color):
                        for color_enemigo, ficha_enemiga in fichas_en_casilla:
                            ficha_enemiga["estado"] = "carcel"
                            ficha_enemiga["pos"] = 0
                        ficha["pos"] = nueva_pos
                        return "captura"
                    else:
                        total_fichas = count + 1
                        if total_fichas > 2:
                            return False
                        ficha["pos"] = nueva_pos
                        return True
                
                else:
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

def puedeAtravesarBloqueoHastaEntrada(pos_actual, movimientos, entrada_llegada, jugadores, color):
    recorrido = []
    for i in range(1, movimientos + 1):
        pos_temp = pos_actual + i
        if pos_temp > 68:
            pos_temp = pos_temp - 68
        recorrido.append(pos_temp)
        
        if pos_temp == entrada_llegada:
            break
    
    for pos in recorrido:
        if hayBloqueo(pos, jugadores, color):
            return False
    
    return True

def usarMovimientosExtra(color, fichas, jugadores, movimientos_extra, razon):
    print(f"\n🎉 ¡{razon}! Tienes {movimientos_extra} movimientos extra.")
    
    fichas_movibles = []
    for i, ficha in enumerate(fichas):
        if ficha["estado"] == "tablero":
            if puedeRealizarMovimiento(ficha, movimientos_extra, color, jugadores):
                fichas_movibles.append((i, ficha))
        elif ficha["estado"] == "llegada":
            nueva_pos_llegada = ficha["pos"] + movimientos_extra
            if nueva_pos_llegada <= 8:
                fichas_movibles.append((i, ficha))
    
    if not fichas_movibles:
        print("No tienes fichas disponibles para usar estos movimientos extra.")
        return

    print("Fichas disponibles para usar los movimientos extra:")
    for j, (i, ficha) in enumerate(fichas_movibles):
        estado_str = "tablero" if ficha["estado"] == "tablero" else "llegada"
        print(f"{j+1}. Ficha {i+1} (en {estado_str}, posición {ficha['pos']})")
    
    eleccion = get_int("Elige qué ficha mover: ", 1, len(fichas_movibles))
    i, ficha = fichas_movibles[eleccion-1]
    
    resultado = moverFicha(ficha, movimientos_extra, color, jugadores)
    
    if resultado:
        print(f"Ficha {i+1} se mueve {movimientos_extra} casillas de una vez")
        
        if resultado == "captura":
            print("¡Captura realizada con movimientos extra! Obtienes 20 movimientos adicionales")
            usarMovimientosExtra(color, fichas, jugadores, 20, "Captura con movimientos extra")
        elif resultado == "meta":
            print("¡Ficha llegó a la meta con movimientos extra! Obtienes 10 movimientos adicionales")
            usarMovimientosExtra(color, fichas, jugadores, 10, "Meta con movimientos extra")
        elif resultado == "llegada":
            print("¡Ficha llegó a zona de llegada!")
    else:
        print("Error: No se pudo aplicar el movimiento extra.")

def sacarFicha(color, fichas, jugadores, dados_disponibles=None, tipo_saque=None):
    fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
    if not fichas_en_carcel:
        return {"exito": False, "dados_usados": [], "mensaje": "No hay fichas en la cárcel"}
    
    salida_pos = salidas[color]
    count, fichas_en_casilla = fichasEnCasilla(salida_pos, jugadores)
    dados_usados = []
    
    if count >= 2:
        fichasEnemigas = [f for f in fichas_en_casilla if f[0] != color]
        fichasAmigas = [f for f in fichas_en_casilla if f[0] == color]
        
        if len(fichasEnemigas) == 2:
            for color_enemigo, ficha_enemiga in fichasEnemigas:
                ficha_enemiga["estado"] = "carcel"
                ficha_enemiga["pos"] = 0
        elif len(fichasEnemigas) == 1:
            color_enemigo, ficha_enemiga = fichasEnemigas[0]
            ficha_enemiga["estado"] = "carcel"
            ficha_enemiga["pos"] = 0    
        elif len(fichasEnemigas) == 0 and len(fichasAmigas) == 2:
            if tipo_saque == "suma":
                pass
            else:
                if not dados_disponibles:
                    return {"exito": False, "dados_usados": [], 
                           "mensaje": "No se pueden mover las fichas amigas sin dados disponibles"}
                
                fichas_movibles = []
                for color_amigo, ficha_amiga in fichasAmigas:
                    for dado in dados_disponibles:
                        ficha_temp = ficha_amiga.copy()
                        if moverFicha(ficha_temp, dado, color, jugadores):
                            fichas_movibles.append((ficha_amiga, dado))
                            break
                
                if not fichas_movibles:
                    return {"exito": False, "dados_usados": [], 
                           "mensaje": "No se puede mover ninguna ficha amiga de la salida"}
                
                ficha_a_mover, dado_a_usar = fichas_movibles[0]
                resultado = moverFicha(ficha_a_mover, dado_a_usar, color, jugadores)
                
                if resultado:
                    dados_usados.append(dado_a_usar)
                    print(f"Se movió una ficha amiga {dado_a_usar} casillas para liberar la salida")
                    if resultado == "captura":
                        print("¡Captura realizada!")
                        usarMovimientosExtra(color, fichas, jugadores, 20, "Captura realizada")
                    elif resultado == "llegada":
                        print("¡Ficha llegó a su destino!")
                    elif resultado == "meta":
                        print("¡Ficha llegó a la meta!")
                        usarMovimientosExtra(color, fichas, jugadores, 10, "Ficha en la meta")
                else:
                    return {"exito": False, "dados_usados": [], 
                           "mensaje": "No se pudo mover la ficha amiga"}
    
    elif count == 1:
        color_enemigo, ficha_enemiga = fichas_en_casilla[0]
        if color_enemigo != color:
            ficha_enemiga["estado"] = "carcel"
            ficha_enemiga["pos"] = 0
    
    fichas_en_carcel[0]["estado"] = "tablero"
    fichas_en_carcel[0]["pos"] = salida_pos
    
    return {"exito": True, "dados_usados": dados_usados, 
           "mensaje": f"Ficha de {color} sale de la cárcel"}

def obtenerMovimientosPosibles(fichas, color, jugadores, movimientos):
    movimientos_posibles = []
    
    for i, ficha in enumerate(fichas):
        if ficha["estado"] == "carcel" or ficha["estado"] == "meta":
            continue
        
        if puedeRealizarMovimiento(ficha, movimientos, color, jugadores):
            movimientos_posibles.append((i, ficha))
    
    return movimientos_posibles

def puedeRealizarMovimiento(ficha, movimientos, color, jugadores):
    if ficha["estado"] == "carcel":
        return False
    
    if ficha["estado"] == "tablero":
        pos_actual = ficha["pos"]
        entrada_llegada = entradas_llegada[color]
        
        pasa_por_entrada, exceso = pasaPorEntrada(pos_actual, movimientos, entrada_llegada)
        
        if pasa_por_entrada:
            if exceso <= 8:
                return puedeAtravesarBloqueoHastaEntrada(pos_actual, movimientos, entrada_llegada, jugadores, color)
            else:
                return False
        else:
            nueva_pos = pos_actual + movimientos
            if nueva_pos > 68:
                nueva_pos = nueva_pos - 68
            
            if not puedeAtravesarBloqueo(pos_actual, nueva_pos, jugadores, color):
                return False
            
            if hayBloqueo(nueva_pos, jugadores, color):
                return False
            
            count, fichas_en_casilla = fichasEnCasilla(nueva_pos, jugadores, color)
            
            if count > 0:
                if esCasillaSegura(nueva_pos):
                    total_fichas = count + 1
                    return total_fichas <= 2
                elif esSalida(nueva_pos):
                    if not esSalida(nueva_pos, color):
                        total_fichas = count + 1
                        return total_fichas <= 2
            
            return True
    
    elif ficha["estado"] == "llegada":
        nueva_pos = ficha["pos"] + movimientos
        return 0 <= nueva_pos <= 8
    
    return False

def obtenerFichasEnSalida(fichas, color):
    salida_pos = salidas[color]
    fichas_en_salida = []
    
    for i, ficha in enumerate(fichas):
        if ficha["estado"] == "tablero" and ficha["pos"] == salida_pos:
            fichas_en_salida.append((i, ficha))
    
    return fichas_en_salida

def verificarVictoria(fichas):
    return all(f["estado"] == "meta" for f in fichas)

def pasaPorEntrada(pos_actual, movimientos, entrada_llegada):
    posiciones_recorridas = []
    for i in range(1, movimientos + 1):
        pos_temp = pos_actual + i
        if pos_temp > 68:
            pos_temp = pos_temp - 68
        posiciones_recorridas.append(pos_temp)
    
    if entrada_llegada in posiciones_recorridas:
        for i, pos in enumerate(posiciones_recorridas):
            if pos == entrada_llegada:
                exceso = movimientos - (i + 1) 
                return True, exceso
    
    return False, 0

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
    
    if puede_sacar == "suma" and len(fichas_en_salida) >= 2:
        print("Tienes 2 fichas en salida. Con suma de 5, no puedes sacar. Los dados se usan como movimientos normales.")
        puede_sacar = False
    elif puede_sacar == "doble":
        fichas_por_sacar = min(len(fichas_en_carcel), 2)
    elif puede_sacar in ["simple", "suma"]:
        fichas_por_sacar = min(len(fichas_en_carcel), 1)
    
    if puede_sacar and fichas_por_sacar > 0:
        if puede_sacar == "doble":
            fichas_en_salida = obtenerFichasEnSalida(fichas, color)
            
            if len(fichas_en_salida) >= 2:
                print("Tienes 2 fichas en salida y doble 5. Debes mover una con un 5 antes de sacar.")
                
                print("\nFichas en salida:")
                for j, (i, ficha) in enumerate(fichas_en_salida):
                    print(f"{j+1}. Ficha {i+1}")
                
                eleccion = get_int("Elige qué ficha mover: ", 1, len(fichas_en_salida))
                i, ficha = fichas_en_salida[eleccion-1]
                
                resultado = moverFicha(ficha, 5, color, jugadores)
                if resultado:
                    print(f"Ficha {i+1} se mueve 5 casillas")
                    dados_disponibles.remove(5)
                    if resultado == "captura":
                        print("¡Captura realizada!")
                        usarMovimientosExtra(color, fichas, jugadores, 20, "Captura realizada")
                    elif resultado == "llegada":
                        print("¡Ficha llegó a su destino!")
                    elif resultado == "meta":
                        print("¡Ficha llegó a la meta!")
                        usarMovimientosExtra(color, fichas, jugadores, 10, "Ficha en la meta")
            
            elif len(fichas_en_salida) == 1:
                print("Tienes 1 ficha en salida. Con doble 5 puedes sacar una y mover la de salida.")
                
               
                fichas_sacadas = 0
                
                dados_para_sacar = dados_disponibles.copy()
                resultado = sacarFicha(color, fichas, jugadores, dados_para_sacar, puede_sacar)
                
                if resultado["exito"]:
                    print(resultado["mensaje"])
                    fichas_sacadas += 1
                    fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
                    
                    for dado_usado in resultado["dados_usados"]:
                        if dado_usado in dados_disponibles:
                            dados_disponibles.remove(dado_usado)
                
                dados_disponibles = [5] * (2 - fichas_sacadas)
            
            else:
                fichas_sacadas = 0
                while fichas_sacadas < fichas_por_sacar and len(fichas_en_carcel) > 0:
                    dados_para_sacar = dados_disponibles.copy()
                    resultado = sacarFicha(color, fichas, jugadores, dados_para_sacar, puede_sacar)
                    
                    if resultado["exito"]:
                        print(resultado["mensaje"])
                        fichas_sacadas += 1
                        fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
                        
                        for dado_usado in resultado["dados_usados"]:
                            if dado_usado in dados_disponibles:
                                dados_disponibles.remove(dado_usado)
                    else:
                        print(f"No se pudo sacar la ficha: {resultado['mensaje']}")
                        break
                
                dados_disponibles = [5] * (2 - fichas_sacadas)
        
        else:  
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
                                print("¡Captura realizada!")
                                usarMovimientosExtra(color, fichas, jugadores, 20, "Captura realizada")
                            elif resultado == "llegada":
                                print("¡Ficha llegó a su destino!")
                            elif resultado == "meta":
                                print("¡Ficha llegó a la meta!")
                                usarMovimientosExtra(color, fichas, jugadores, 10, "Ficha en la meta")
            
            fichas_sacadas = 0
            while fichas_sacadas < fichas_por_sacar and len(fichas_en_carcel) > 0:
                dados_para_sacar = dados_disponibles.copy()
                resultado = sacarFicha(color, fichas, jugadores, dados_para_sacar, puede_sacar)
                
                if resultado["exito"]:
                    print(resultado["mensaje"])
                    fichas_sacadas += 1
                    fichas_en_carcel = [f for f in fichas if f["estado"] == "carcel"]
                    
                    for dado_usado in resultado["dados_usados"]:
                        if dado_usado in dados_disponibles:
                            dados_disponibles.remove(dado_usado)
                else:
                    print(f"No se pudo sacar la ficha: {resultado['mensaje']}")
                    break
        
        if puede_sacar == "suma":
            dados_disponibles = []
        elif puede_sacar == "simple":
            dados_disponibles = [d for d in dados_disponibles if d != 5]
    
    
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
                    print("¡Captura realizada!")
                    usarMovimientosExtra(color, fichas, jugadores, 20, "Captura realizada")
                elif resultado == "llegada":
                    print("¡Ficha llegó a su destino!")
                elif resultado == "meta":
                    print("¡Ficha llegó a la meta!")
                    usarMovimientosExtra(color, fichas, jugadores, 10, "Ficha en la meta")
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
                    print("¡Captura realizada!")
                    usarMovimientosExtra(color, fichas, jugadores, 20, "Captura realizada")
                elif resultado == "llegada":
                    print("¡Ficha llegó a su destino!")
                elif resultado == "meta":
                    print("¡Ficha llegó a la meta!")
                    usarMovimientosExtra(color, fichas, jugadores, 10, "Ficha en la meta")
    
    if es_par and paresConsecutivos[color] < 3:
        print("Como sacaste par, juegas de nuevo!")
        return False
    
    return True

if __name__ == "__main__":
    empezarJuego()
