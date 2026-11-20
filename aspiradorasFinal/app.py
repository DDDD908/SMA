# Descripción: Muestra la habitación, los resultados de la corrida actual y dos gráficas que comparan el tiempo y los movimientos de distintos equipos
# Autores: Alexa Sarahí Castillo Portillo A01803450 - Daniela Gil González A01752908 
# Fecha: 16/11/2026

import solara
from matplotlib.figure import Figure
from mesa.visualization import SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.utils import update_counter

from aspiradora import Aspiradora
from model import ModeloLimpieza, compararEquipos


# Define cómo se dibuja un agente en la habitación.
# agente: Aspiradora o basura que se va a representar.
# Retorna el color, la forma, el tamaño y el orden de dibujo.
def representarAgente(agente):
	if isinstance(agente, Aspiradora):
		return AgentPortrayalStyle(
			color="royalblue",
			marker="o",
			size=55,
			zorder=3,
		)

	return AgentPortrayalStyle(
		color="sienna",
		marker="s",
		size=65,
		zorder=2,
	)


# Ajusta el mapa para que las celdas se vean cuadradas.
# eje: Eje de Matplotlib donde se dibuja la habitación.
# Retorno: ninguno.
def configurarHabitacion(eje):
	eje.set_title("Habitación")
	eje.set_aspect("equal")
	eje.set_xlabel("Círculo azul = aspiradora     Cuadro café = basura")


# Muestra las tres estadísticas solicitadas para la corrida visible.
# modelo: Simulación que el usuario controla con los botones de Solara.
# Retorno: ninguno.
@solara.component
def mostrarResumen(modelo):
	update_counter.get()

	if modelo.cantidadBasura == 0:
		estado = "Limpieza completa"
	elif modelo.pasosObservados >= modelo.tiempoMaximo:
		estado = "Tiempo máximo alcanzado"
	else:
		estado = "Limpieza en curso"

	solara.Markdown(
		f"**{estado}**  \n"
		f"Tiempo observado: **{modelo.pasosObservados} pasos**  \n"
		f"Celdas limpias: **{modelo.porcentajeLimpio:.2f} %**  \n"
		f"Movimientos totales: **{modelo.movimientosTotales}**"
	)


# Construye las dos gráficas a partir de las corridas de comparación.
# resultados: Una fila por equipo, con cantidad, pasos y movimientos promedio.
# Retorna una figura de Matplotlib con ambas gráficas.
def crearGraficas(resultados):
	cantidades = [fila["cantidad"] for fila in resultados]
	pasos = [fila["pasos"] for fila in resultados]
	movimientos = [fila["movimientos"] for fila in resultados]

	figura = Figure(figsize=(7, 6), constrained_layout=True)
	ejeTiempo, ejeMovimientos = figura.subplots(2, 1)

	ejeTiempo.scatter(cantidades, pasos, color="darkorange", s=55)
	ejeTiempo.set_title("Tiempo observado por cantidad de aspiradoras")
	ejeTiempo.set_xlabel("Número de aspiradoras")
	ejeTiempo.set_ylabel("Pasos promedio por corrida")
	ejeTiempo.set_xticks(cantidades)
	ejeTiempo.set_ylim(bottom=0)
	ejeTiempo.grid(axis="y", alpha=0.25)

	etiquetas = [str(cantidad) for cantidad in cantidades]
	ejeMovimientos.bar(etiquetas, movimientos, color="royalblue")
	ejeMovimientos.set_title("Movimientos totales del equipo")
	ejeMovimientos.set_xlabel("Número de aspiradoras")
	ejeMovimientos.set_ylabel("Movimientos promedio por corrida")
	ejeMovimientos.set_ylim(bottom=0)
	ejeMovimientos.grid(axis="y", alpha=0.25)

	return figura


# Presenta la comparación usando las condiciones iniciales del mapa.
# modelo: Modelo que proporciona dimensiones, suciedad, límite y semilla.
# Retorno: ninguno.
@solara.component
def mostrarComparacion(modelo):
	condiciones = (
		modelo.ancho,
		modelo.alto,
		modelo.porcentajeSucio,
		modelo.tiempoMaximo,
		modelo.semilla,
	)

	# Las 50 corridas se recalculan solo cuando cambian sus condiciones.
	# Avanzar un paso en el mapa reutiliza los resultados anteriores.
	resultados = solara.use_memo(
		lambda: compararEquipos(*condiciones),
		dependencies=list(condiciones),
	)
	figura = solara.use_memo(
		lambda: crearGraficas(resultados),
		dependencies=list(condiciones),
	)

	solara.FigureMatplotlib(figura)



# Configura un deslizador entero del panel lateral.
# etiqueta: Nombre visible. valor: Valor inicial.
# minimo y maximo: Límites del control. Retorna su configuración.
def crearDeslizador(etiqueta, valor, minimo, maximo):
	return {
		"type": "SliderInt",
		"value": valor,
		"label": etiqueta,
		"min": minimo,
		"max": maximo,
		"step": 1,
	}


parametrosModelo = {
	"semilla": crearDeslizador("Semilla", 42, 0, 100),
	"ancho": crearDeslizador("Ancho de la habitación", 10, 2, 40),
	"alto": crearDeslizador("Alto de la habitación", 10, 2, 40),
	"cantidadAspiradoras": crearDeslizador("Aspiradoras en el mapa", 4, 1, 32),
	"porcentajeSucio": crearDeslizador("Suciedad inicial (%)", 40, 0, 100),
	"tiempoMaximo": crearDeslizador("Tiempo máximo (pasos)", 500, 1, 2000),
}

valoresIniciales = {
	nombre: control["value"]
	for nombre, control in parametrosModelo.items()
}

# Dibuja la habitación con las posiciones del paso actual.
# modelo: Simulación activa. Retorno: ninguno.
@solara.component
def mostrarHabitacion(modelo):
	actualizacion = update_counter.get()

	figura = Figure(figsize=(5, 4), constrained_layout=True)
	eje = figura.subplots()

	for posiciones, color, marca, tamano in (
		(list(modelo.basuraPorPosicion), "sienna", "s", 65),
		(
			[robot.cell.coordinate for robot in modelo.agents_by_type[Aspiradora]],
			"royalblue",
			"o",
			55,
		),
	):
		if posiciones:
			columnas, filas = zip(*posiciones)
			eje.scatter(columnas, filas, c=color, marker=marca, s=tamano)

	eje.set_xlim(-0.5, modelo.ancho - 0.5)
	eje.set_ylim(-0.5, modelo.alto - 0.5)
	configurarHabitacion(eje)

	solara.FigureMatplotlib(
		figura,
		format="png",
		dependencies=[modelo, actualizacion],
	)


# Muestra el mapa, el resumen y las dos gráficas al abrir la aplicación.
# Parámetros: ninguno. Retorno: ninguno.
@solara.component
def paginaAspiradoras():
	modeloInicial = solara.use_memo(
		lambda: ModeloLimpieza(**valoresIniciales),
		dependencies=[],
	)
	modeloActivo = solara.use_reactive(modeloInicial)

	with solara.Column():
		SolaraViz(
			modeloActivo,
			components=[],
			model_params=parametrosModelo,
			name="Aspiradoras",
		)

		with solara.ColumnsResponsive(12, medium=6, large=6, xlarge=6):
			with solara.Column():
				mostrarHabitacion(modeloActivo.value)
				mostrarResumen(modeloActivo.value)

			with solara.Column():
				mostrarComparacion(modeloActivo.value)


page = paginaAspiradoras