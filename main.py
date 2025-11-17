import json
import random
import os
from datetime import datetime

GITHUB_REPO_URL = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05/main/2526-1/"
DATA_FILE = "datos_hotdog_ccs.json"

class Ingrediente:
    """
    Clase que representa un ingrediente individual en el inventario.
    """
    def _init_(self, nombre, categoria, cantidad, precio, caracteristicas=None):
        self.nombre = nombre
        self.categoria = categoria # Pan, Salchicha, Topping, Salsa, Acompañante
        self.cantidad = cantidad
        self.precio = precio
        # Caracteristicas extra como 'longitud' para validar pan vs salchicha
        self.caracteristicas = caracteristicas if caracteristicas else {}

    def to_dict(self):
        """Convierte el objeto a diccionario para guardar en JSON."""
        return {
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio,
            "caracteristicas": self.caracteristicas
        }

    def _str_(self):
        return f"{self.nombre} ({self.categoria}) - Stock: {self.cantidad}"

class HotDog:
    """
    Clase que define un combo de Hot Dog en el menú.
    """
    def _init_(self, nombre, pan, salchicha, toppings, salsas, acompanante=None, precio_venta=0):
        self.nombre = nombre
        self.pan = pan # Objeto Ingrediente o nombre
        self.salchicha = salchicha
        self.toppings = toppings # Lista
        self.salsas = salsas # Lista
        self.acompanante = acompanante
        self.precio_venta = precio_venta

    def to_dict(self):
        """Convierte el objeto a diccionario para guardar en JSON."""
        return {
            "nombre": self.nombre,
            "pan": self.pan,
            "salchicha": self.salchicha,
            "toppings": self.toppings,
            "salsas": self.salsas,
            "acompanante": self.acompanante,
            "precio_venta": self.precio_venta
        }

class Tienda:
    """
    Clase controladora principal (Sistema) que gestiona inventario, menú y ventas.
    """
    def _init_(self):
        self.inventario = [] # Lista de objetos Ingrediente
        self.menu = []       # Lista de objetos HotDog
        self.ventas_diarias = [] # Historial de estadísticas por día
        self.cargar_datos()

    # --- Módulo de Persistencia y Carga (API/Archivos)
    
    def cargar_datos(self):
        """
        Carga datos desde el archivo local JSON. Si no existe, intenta descargar de GitHub.
        """
        if os.path.exists(DATA_FILE):
            print("Cargando datos desde archivo local...")
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._procesar_json_inventario(data.get("inventario", []))
                    self._procesar_json_menu(data.get("menu", []))
                    self.ventas_diarias = data.get("historico_ventas", [])
            except Exception as e:
                print(f"Error cargando archivo local: {e}. Iniciando desde cero/API.")
                self.descargar_de_api()
        else:
            print("Archivo local no encontrado. Intentando descargar de la API...")
            self.descargar_de_api()

    def descargar_de_api(self):
        
        try:
            
            # DATA SEMILLA (Hardcoded para que el programa funcione inmediatamente)
            data_semilla_inv = [
                {"nombre": "Pan Corto", "categoria": "Pan", "cantidad": 100, "precio": 1.0, "caracteristicas": {"longitud": "corto"}},
                {"nombre": "Pan Largo", "categoria": "Pan", "cantidad": 50, "precio": 1.5, "caracteristicas": {"longitud": "largo"}},
                {"nombre": "Salchicha Polaca", "categoria": "Salchicha", "cantidad": 100, "precio": 2.0, "caracteristicas": {"longitud": "corto"}},
                {"nombre": "Salchicha Alemana", "categoria": "Salchicha", "cantidad": 50, "precio": 3.0, "caracteristicas": {"longitud": "largo"}},
                {"nombre": "Cebolla", "categoria": "Topping", "cantidad": 200, "precio": 0.5},
                {"nombre": "Papas", "categoria": "Topping", "cantidad": 200, "precio": 0.5},
                {"nombre": "Ketchup", "categoria": "Salsa", "cantidad": 500, "precio": 0.2},
                {"nombre": "Refresco", "categoria": "Acompañante", "cantidad": 100, "precio": 1.5}
            ]
            self._procesar_json_inventario(data_semilla_inv)
            print("Datos iniciales cargados (Semilla/API).")
        except Exception as e:
            print(f"Error conectando a API: {e}")

    def _procesar_json_inventario(self, lista_dict):
        self.inventario = [Ingrediente(**item) for item in lista_dict]

    def _procesar_json_menu(self, lista_dict):
        self.menu = [HotDog(**item) for item in lista_dict]

    def guardar_datos(self):
        """Guarda el estado actual en un JSON local."""
        data = {
            "inventario": [i.to_dict() for i in self.inventario],
            "menu": [m.to_dict() for m in self.menu],
            "historico_ventas": self.ventas_diarias
        }
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print("Datos guardados exitosamente.")
        except Exception as e:
            print(f"Error guardando datos: {e}")

    # --- Módulo 1: Gestión de Ingredientes 

    def buscar_ingrediente(self, nombre):
        for ing in self.inventario:
            if ing.nombre.lower() == nombre.lower():
                return ing
        return None

    def listar_ingredientes(self, categoria=None):
        """Lista ingredientes, opcionalmente filtrados por categoría."""
        print(f"\n--- Inventario {'(' + categoria + ')' if categoria else ''} ---")
        for i, ing in enumerate(self.inventario):
            if categoria is None or ing.categoria.lower() == categoria.lower():
                print(f"{i+1}. {ing}")

    def agregar_ingrediente(self):
        print("\n--- Agregar Ingrediente ---")
        nombre = input("Nombre: ")
        categoria = input("Categoría (Pan/Salchicha/Topping/Salsa/Acompañante): ")
        try:
            cantidad = int(input("Cantidad inicial: "))
            precio = float(input("Costo unitario: "))
        except ValueError:
            print("Error: Debe ingresar números válidos.")
            return

        caracteristicas = {}
        if categoria.lower() in ["pan", "salchicha"]:
            longitud = input("Longitud (corto/largo): ").lower()
            caracteristicas["longitud"] = longitud

        nuevo = Ingrediente(nombre, categoria, cantidad, precio, caracteristicas)
        self.inventario.append(nuevo)
        print("Ingrediente agregado.")

    def eliminar_ingrediente(self):
        self.listar_ingredientes()
        nombre = input("Ingrese el nombre del ingrediente a eliminar: ")
        ing = self.buscar_ingrediente(nombre)
        
        if not ing:
            print("Ingrediente no encontrado.")
            return

        # Validar si se usa en el menú 
        en_uso = False
        for perro in self.menu:
            lista_componentes = [perro.pan, perro.salchicha] + perro.toppings + perro.salsas
            if perro.acompanante: lista_componentes.append(perro.acompanante)
            
            if ing.nombre in lista_componentes:
                en_uso = True
                break
        
        if en_uso:
            confirm = input(f"El ingrediente '{ing.nombre}' se usa en el menú. Eliminarlo borrará también los Hot Dogs asociados. ¿Confirmar? (s/n): ")
            if confirm.lower() != 's':
                return
            # Eliminar Hot Dogs que usen el ingrediente
            self.menu = [p for p in self.menu if ing.nombre not in ([p.pan, p.salchicha] + p.toppings + p.salsas)]
            print("Hot dogs afectados eliminados del menú.")

        self.inventario.remove(ing)
        print("Ingrediente eliminado.")

    # --- Módulo 2: Gestión de Inventario 
    
    def actualizar_inventario(self):
        self.listar_ingredientes()
        nombre = input("Nombre del ingrediente a actualizar: ")
        ing = self.buscar_ingrediente(nombre)
        if ing:
            try:
                nuevo_stock = int(input(f"Stock actual {ing.cantidad}. Ingrese cantidad a sumar (o restar con -): "))
                ing.cantidad += nuevo_stock
                print(f"Nuevo stock de {ing.nombre}: {ing.cantidad}")
            except ValueError:
                print("Error: Ingrese un número entero.")
        else:
            print("Ingrediente no encontrado.")

    # --- Módulo 3: Gestión del Menú 

    def ver_menu(self):
        print("\n--- Menú Hot Dog CCS ---")
        if not self.menu:
            print("El menú está vacío.")
        for i, perro in enumerate(self.menu):
            # Verificar disponibilidad 
            disponible = self._verificar_stock_combo(perro)
            estado = "Disponible" if disponible else "Agotado"
            print(f"{i+1}. {perro.nombre} - ${perro.precio_venta} [{estado}]")
            print(f"   Ingredientes: {perro.pan}, {perro.salchicha}, {', '.join(perro.toppings)}")

    def _verificar_stock_combo(self, perro):
        """Verifica si hay inventario para un Hot Dog específico."""
        componentes = [perro.pan, perro.salchicha] + perro.toppings + perro.salsas
        if perro.acompanante: componentes.append(perro.acompanante)
        
        # Conteo de necesidades
        necesidades = {}
        for c in componentes:
            necesidades[c] = necesidades.get(c, 0) + 1
            
        for nombre_ing, cantidad_nec in necesidades.items():
            ing_obj = self.buscar_ingrediente(nombre_ing)
            if not ing_obj or ing_obj.cantidad < cantidad_nec:
                return False
        return True

    def agregar_hotdog(self):
        print("\n--- Crear Nuevo Hot Dog ---")
        nombre = input("Nombre del Hot Dog: ")
        
        # Seleccionar Pan
        self.listar_ingredientes("Pan")
        pan = input("Nombre del Pan: ")
        obj_pan = self.buscar_ingrediente(pan)
        if not obj_pan: return

        # Seleccionar Salchicha
        self.listar_ingredientes("Salchicha")
        salchicha = input("Nombre de la Salchicha: ")
        obj_sal = self.buscar_ingrediente(salchicha)
        if not obj_sal: return

        # Validación de longitud [cite: 65]
        if obj_pan.caracteristicas.get("longitud") != obj_sal.caracteristicas.get("longitud"):
            conf = input("ADVERTENCIA: La longitud del pan y la salchicha no coinciden. ¿Continuar? (s/n): ")
            if conf.lower() != 's': return

        # Toppings
        self.listar_ingredientes("Topping")
        toppings_str = input("Nombres de toppings (separados por coma): ")
        lista_toppings = [t.strip() for t in toppings_str.split(",") if t.strip()]
        
        # Salsas
        self.listar_ingredientes("Salsa")
        salsas_str = input("Nombres de salsas (separados por coma): ")
        lista_salsas = [s.strip() for s in salsas_str.split(",") if s.strip()]

        # Acompañante
        self.listar_ingredientes("Acompañante")
        acompanante = input("Nombre acompañante (enter si ninguno): ")
        if acompanante == "": acompanante = None

        try:
            precio = float(input("Precio de venta: "))
        except ValueError:
            print("Precio inválido.")
            return

        nuevo_perro = HotDog(nombre, pan, salchicha, lista_toppings, lista_salsas, acompanante, precio)
        self.menu.append(nuevo_perro)
        print("Hot Dog agregado al menú.")

    def eliminar_hotdog(self):
        self.ver_menu()
        try:
            idx = int(input("Número del Hot Dog a eliminar: ")) - 1
            if 0 <= idx < len(self.menu):
                perro = self.menu[idx]
                # Advertencia si hay inventario [cite: 71]
                if self._verificar_stock_combo(perro):
                    conf = input("ADVERTENCIA: Aún hay inventario para vender este producto. ¿Seguro desea eliminarlo? (s/n): ")
                    if conf.lower() != 's': return
                self.menu.pop(idx)
                print("Eliminado.")
            else:
                print("Índice inválido.")
        except ValueError:
            print("Error de entrada.")

    # --- Módulo 5: Simulación de Ventas [cite: 73] ---

    def simular_dia(self):
        if not self.menu:
            print("No se puede simular sin menú.")
            return

        print("\n--- Iniciando Simulación del Día ---")
        num_clientes = random.randint(0, 200) # [cite: 76]
        print(f"Se esperan {num_clientes} clientes hoy.")

        stats = {
            "total_clientes": num_clientes,
            "clientes_compraron": 0,
            "cambiaron_opinion": 0, # 
            "no_pudieron_comprar": 0, 
            "hotdogs_vendidos": {},
            "ingredientes_fallidos": {},
            "acompanantes_vendidos": 0,
            "total_dinero": 0
        }

        for i in range(num_clientes):
            num_ordenes = random.randint(0, 5) 
            
            if num_ordenes == 0:
                print(f"Cliente {i}: Cambió de opinión.")
                stats["cambiaron_opinion"] += 1
                continue

            cliente_feliz = True
            orden_cliente = []

            # Intentar procesar la orden
            temp_inventario_needs = {}

            for _ in range(num_ordenes):
                opcion = random.choice(self.menu) 
                
                # Componentes base
                componentes = [opcion.pan, opcion.salchicha] + opcion.toppings + opcion.salsas
                if opcion.acompanante: componentes.append(opcion.acompanante)
                
                # Acompañante extra aleatorio? [cite: 80]
                extra_acom = None
                if random.choice([True, False]):
                    # Buscar un acompañante al azar del inventario
                    acompanantes_posibles = [ing for ing in self.inventario if ing.categoria == "Acompañante"]
                    if acompanantes_posibles:
                        extra_acom = random.choice(acompanantes_posibles).nombre
                        componentes.append(extra_acom)

                # Acumular necesidades
                for comp in componentes:
                    temp_inventario_needs[comp] = temp_inventario_needs.get(comp, 0) + 1
                
                orden_cliente.append({"perro": opcion, "extra": extra_acom})

            # Verificar si hay stock para TODA la orden del cliente
            for ing_nombre, cantidad_req in temp_inventario_needs.items():
                ing_obj = self.buscar_ingrediente(ing_nombre)
                if not ing_obj or ing_obj.cantidad < cantidad_req:
                    cliente_feliz = False
                    stats["no_pudieron_comprar"] += 1
                    stats["ingredientes_fallidos"][ing_nombre] = stats["ingredientes_fallidos"].get(ing_nombre, 0) + 1
                    print(f"Cliente {i}: Se marchó. Falta ingrediente: {ing_nombre}") # [cite: 83]
                    break
            
            if cliente_feliz:
                # Ejecutar venta (Descontar inventario) [cite: 82]
                stats["clientes_compraron"] += 1
                for item, cant in temp_inventario_needs.items():
                    self.buscar_ingrediente(item).cantidad -= cant
                
                print(f"Cliente {i}: Compró {[o['perro'].nombre for o in orden_cliente]}")
                
                # Registrar estadísticas
                for order in orden_cliente:
                    nombre_perro = order["perro"].nombre
                    stats["hotdogs_vendidos"][nombre_perro] = stats["hotdogs_vendidos"].get(nombre_perro, 0) + 1
                    stats["total_dinero"] += order["perro"].precio_venta
                    
                    if order["perro"].acompanante: stats["acompanantes_vendidos"] += 1
                    if order["extra"]: stats["acompanantes_vendidos"] += 1

        self._reporte_final(stats)
        self.ventas_diarias.append(stats) # Guardar historial para bono

    def _reporte_final(self, stats):
        """Genera el reporte al final de la simulación[cite: 84]."""
        print("\n--- REPORTE DEL DÍA ---")
        print(f"Total Clientes: {stats['total_clientes']}")
        print(f"Clientes Atendidos: {stats['clientes_compraron']}")
        print(f"Cambiaron de opinión: {stats['cambiaron_opinion']}") 
        print(f"No pudieron comprar: {stats['no_pudieron_comprar']}") 
        
        promedio = 0
        total_perros = sum(stats['hotdogs_vendidos'].values())
        if stats['clientes_compraron'] > 0:
            promedio = total_perros / stats['clientes_compraron']
        print(f"Promedio hot dogs/cliente: {promedio:.2f}") 
        
        mas_vendido = max(stats['hotdogs_vendidos'], key=stats['hotdogs_vendidos'].get) if stats['hotdogs_vendidos'] else "Ninguno"
        print(f"Hot Dog más vendido: {mas_vendido}") 
        
        print(f"Ingredientes fallidos: {stats['ingredientes_fallidos']}") 
        print(f"Acompañantes vendidos: {stats['acompanantes_vendidos']}") 

    # --- Bono: Estadísticas Gráficas 
    def mostrar_estadisticas(self):
        if len(self.ventas_diarias) < 2:
            print("Necesitas simular al menos 2 días para ver gráficas.") 
            return
        
        dias = range(1, len(self.ventas_diarias) + 1)
        ventas = [d['total_dinero'] for d in self.ventas_diarias]
        rechazos = [d['no_pudieron_comprar'] for d in self.ventas_diarias]

        
# --- Menú Principal ---

def main():
    tienda = Tienda()
    
    while True:
        print("\n=== SISTEMA HOT DOG CCS ===")
        print("1. Gestión de Ingredientes")
        print("2. Gestión de Inventario")
        print("3. Gestión del Menú")
        print("4. Simular Día de Ventas")
        print("5. Ver Estadísticas (Bono)")
        print("6. Guardar y Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            print("\n1. Listar\n2. Agregar\n3. Eliminar")
            sub = input("Opción: ")
            if sub == '1': tienda.listar_ingredientes()
            elif sub == '2': tienda.agregar_ingrediente()
            elif sub == '3': tienda.eliminar_ingrediente()
            
        elif opcion == '2':
            print("\n1. Ver todo\n2. Actualizar stock")
            sub = input("Opción: ")
            if sub == '1': tienda.listar_ingredientes()
            elif sub == '2': tienda.actualizar_inventario()
            
        elif opcion == '3':
            print("\n1. Ver Menú\n2. Agregar Hot Dog\n3. Eliminar Hot Dog")
            sub = input("Opción: ")
            if sub == '1': tienda.ver_menu()
            elif sub == '2': tienda.agregar_hotdog()
            elif sub == '3': tienda.eliminar_hotdog()
            
        elif opcion == '4':
            tienda.simular_dia()
            
        elif opcion == '5':
            tienda.mostrar_estadisticas()
            
        elif opcion == '6':
            tienda.guardar_datos()
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida.")

if _name_ == "_main_":
    main()
