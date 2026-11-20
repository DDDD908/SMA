# Descripción: Simula la limpieza de una habitación y compara el tiempo y los movimientos de equipos con distintas cantidades de aspiradoras.
# Autores: Alexa Sarahí Castillo Portillo A01803450 - Daniela Gil González A01752908 
# Fecha: 16/11/2026

from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid

from aspiradora import Aspiradora
from basura import Basura


POSICION_INICIAL = (1, 1)
CANTIDADES_COMPARACION = (1, 2, 4, 8, 16)
REPETICIONES = 10


class ModeloLimpieza(Model):

	# Crea la habitación, distribuye la basura y coloca las aspiradoras.
	# self: Modelo actual.
	# ancho y alto: Dimensiones de la habitación en celdas.
	# cantidadAspiradoras: Número de robots que empiezan en [1, 1].
	# porcentajeSucio: Porcentaje de celdas inicialmente sucias, de 0 a 100.
	# tiempoMaximo: Número máximo de pasos permitidos.
	# semilla: Valor que permite reproducir la misma corrida.
	# Retorno: ninguno.
	def __init__(
		self,
		ancho=10,
		alto=10,
		cantidadAspiradoras=4,
		porcentajeSucio=40,
		tiempoMaximo=500,
		semilla=42,
	):
		super().__init__(rng=semilla)

		self.ancho = ancho
		self.alto = alto
		self.porcentajeSucio = porcentajeSucio
		self.tiempoMaximo = tiempoMaximo
		self.semilla = semilla

		self.pasosObservados = 0
		self.movimientosTotales = 0
		self.basuraPorPosicion = {}

		# Varias aspiradoras pueden compartir celda. Los bordes son paredes.
		self.grid = OrthogonalMooreGrid(
			(ancho, alto),
			capacity=None,
			random=self.random,
			torus=False,
		)

		# Sortear la basura primero permite usar la misma habitación inicial
		# al comparar equipos de distintos tamaños con una misma semilla.
		self.distribuirBasura()

		celdaInicial = self.grid[POSICION_INICIAL]
		for _ in range(cantidadAspiradoras):
			Aspiradora(self, celdaInicial)

		self.running = self.cantidadBasura > 0 and self.tiempoMaximo > 0

	# Distribuye la basura en celdas distintas, redondeando al entero más cercano.
	# self: Modelo que se está inicializando.
	# Retorno: ninguno.
	def distribuirBasura(self):
		totalCeldas = self.ancho * self.alto
		cantidadInicial = (totalCeldas * self.porcentajeSucio + 50) // 100
		celdas = list(self.grid.all_cells)
		celdasSucias = self.random.sample(celdas, cantidadInicial)

		for celda in celdasSucias:
			self.basuraPorPosicion[celda.coordinate] = Basura(self, celda)

	# Cuenta las celdas que todavía contienen basura.
	# self: Modelo actual. Retorna la cantidad de celdas sucias.
	@property
	def cantidadBasura(self):
		return len(self.basuraPorPosicion)

	# Calcula el porcentaje de limpieza que muestra app.py.
	# self: Modelo actual. Retorna un porcentaje entre 0 y 100.
	@property
	def porcentajeLimpio(self):
		totalCeldas = self.ancho * self.alto
		celdasLimpias = totalCeldas - self.cantidadBasura
		return 100 * celdasLimpias / totalCeldas

	# Da un turno a cada aspiradora y comprueba si terminó la simulación.
	# self: Modelo activo. Retorno: ninguno.
	def step(self):
		if self.running:
			# El orden cambia en cada paso. Si dos robots comparten celda,
			# el segundo percibe cómo quedó después de actuar el primero.
			self.agents_by_type[Aspiradora].shuffle_do("actuar")
			self.pasosObservados += 1

			self.running = (
				self.cantidadBasura > 0
				and self.pasosObservados < self.tiempoMaximo
			)


# Compara equipos usando las mismas diez semillas para cada cantidad de robots.
# ancho y alto: Dimensiones comunes a todas las corridas.
# porcentajeSucio: Porcentaje inicial de suciedad.
# tiempoMaximo: Límite de pasos por corrida.
# semilla: Primera semilla de la comparación.
# Retorna una lista de resultados por equipo para las gráficas de app.py.
def compararEquipos(ancho, alto, porcentajeSucio, tiempoMaximo, semilla):
	resultados = []

	for cantidad in CANTIDADES_COMPARACION:
		sumaPasos = 0
		sumaMovimientos = 0
		sumaLimpieza = 0.0
		corridasCompletas = 0

		for repeticion in range(REPETICIONES):
			modelo = ModeloLimpieza(
				ancho=ancho,
				alto=alto,
				cantidadAspiradoras=cantidad,
				porcentajeSucio=porcentajeSucio,
				tiempoMaximo=tiempoMaximo,
				semilla=semilla + repeticion,
			)

			while modelo.running:
				modelo.step()

			sumaPasos += modelo.pasosObservados
			sumaMovimientos += modelo.movimientosTotales
			sumaLimpieza += modelo.porcentajeLimpio

			if modelo.cantidadBasura == 0:
				corridasCompletas += 1

		resultados.append({
			"cantidad": cantidad,
			"pasos": sumaPasos / REPETICIONES,
			"movimientos": sumaMovimientos / REPETICIONES,
			"limpieza": sumaLimpieza / REPETICIONES,
			"completas": corridasCompletas,
		})

	return resultados