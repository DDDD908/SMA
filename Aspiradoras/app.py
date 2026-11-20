# Visualiza la habitación y la evolución de la limpieza con Solara.
# Autores: [Daniela Gil González A01752908 Alexa Sarahí Castillo Portillo A01803450]
# Fecha: 16/11/2026

import solara
from matplotlib.figure import Figure
from mesa.visualization import Slider, SolaraViz
from mesa.visualization.utils import update_counter
from aspiradora import Aspiradora
from basura import Basura
from model import AspiradoraModel


# model: simulación actual. Retorna la figura del piso y su gráfica de limpieza.
def dibujarSimulacion(model):
	figura = Figure(figsize=(9, 4), constrained_layout=True)
	tablero, grafica = figura.subplots(1, 2)
	for tipo, color, marca, etiqueta in (
		(Basura, "sienna", "s", "Basura"), (Aspiradora, "royalblue", "o", "Robot")
	):
		posiciones = [agente.cell.coordinate for agente in model.agents_by_type.get(tipo, ())]
		tablero.scatter([x for x, y in posiciones], [y for x, y in posiciones],
						c=color, marker=marca, label=etiqueta, s=42)
	tablero.set(xlim=(-0.5, model.width - 0.5), ylim=(-0.5, model.height - 0.5),
				aspect="equal", title="Habitación")
	tablero.legend(loc="upper left", bbox_to_anchor=(0, -0.04), ncol=2)
	grafica.plot(range(model.paso + 1), model.historial, color="seagreen", marker=".")
	grafica.set(xlim=(0, max(1, model.tiempoMaximo)), ylim=(-2, 102),
				xlabel="Paso", ylabel="Celdas limpias (%)", title="Avance de limpieza")
	grafica.grid(alpha=0.25)
	return figura


parametros = {
	"rng": Slider("Semilla", 42, 1, 100),
	"width": Slider("Ancho", 22, 2, 60),
	"height": Slider("Alto", 22, 2, 60),
	"numAgentes": Slider("Número de aspiradoras", 3, 1, 50),
	"porcentajeBasura": Slider("Suciedad inicial (%)", 40, 0, 100),
	"tiempoMaximo": Slider("Tiempo máximo (pasos)", 60, 1, 600),
}


# model: simulación actual. Presenta las figuras y las tres métricas. Retorno: ninguno.
@solara.component
def panelInformacion(model):
	update_counter.get()
	datos = model.obtenerEstadisticas()
	solara.FigureMatplotlib(dibujarSimulacion(model), format="png")
	estado = "Completa" if model.tiempoLimpieza is not None else "Incompleta"
	solara.Markdown(
		f"**Limpieza {estado.lower()}** · Paso {model.paso} de {model.tiempoMaximo}  \n"
		f"Tiempo observado: **{datos['tiempoObservado']} pasos** · "
		f"Celdas limpias: **{datos['porcentajeLimpias']:.2f}%** · "
		f"Movimientos totales: **{datos['movimientos']}**"
	)


# Abre la simulación en el navegador. Sin parámetros ni retorno.
@solara.component
def page():
	modelo = solara.use_reactive(solara.use_memo(AspiradoraModel, []))
	SolaraViz(modelo, components=[], model_params=parametros, name="Aspiradoras")
	panelInformacion(modelo.value)
