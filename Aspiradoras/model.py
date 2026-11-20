# Inicializa la habitación y mide la limpieza por paso.
# Autores: [Daniela Gil González A01752908 Alexa Sarahí Castillo Portillo A01803450]
# Fecha: 16/11/2026
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from aspiradora import Aspiradora
from basura import Basura


class AspiradoraModel(Model):
	# Crea el modelo. self: habitación; width, height: dimensiones; numAgentes: robots;
	# porcentajeBasura: suciedad inicial; tiempoMaximo: límite de pasos; rng: semilla.
	# Retorno: ninguno. Se usan índices desde cero y la posición literal (1, 1).
	def __init__(self, width=20, height=20, numAgentes=3, porcentajeBasura=40,
				 tiempoMaximo=60, rng=42):
		super().__init__(rng=None if rng is None else int(rng))
		if min(width, height) < 2 or numAgentes < 1 or tiempoMaximo < 0:
			raise ValueError("Revisa las dimensiones, el número de agentes y el tiempo.")
		if not 0 <= porcentajeBasura <= 100:
			raise ValueError("La suciedad debe estar entre 0 y 100.")
		self.width = width
		self.height = height
		self.totalCeldas = width * height
		self.tiempoMaximo = tiempoMaximo
		self.paso = 0
		self.movimientos = 0
		self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
		self.basuraRestante = int(self.totalCeldas * porcentajeBasura / 100)
		for celda in self.random.sample(list(self.grid.all_cells), self.basuraRestante):
			basura = Basura(self)
			basura.cell = celda
		for _ in range(numAgentes):
			robot = Aspiradora(self)
			robot.cell = self.grid[(1, 1)]
		self.tiempoLimpieza = 0 if self.basuraRestante == 0 else None
		self.running = tiempoMaximo > 0
		self.historial = [self.obtenerEstadisticas()["porcentajeLimpias"]]

	# self: habitación. Ejecuta un turno por robot y registra el paso. Retorno: ninguno.
	def step(self):
		if self.running:
			self.agents_by_type[Aspiradora].do("step")
			self.paso += 1
			if self.basuraRestante == 0 and self.tiempoLimpieza is None:
				self.tiempoLimpieza = self.paso
			self.historial.append(self.obtenerEstadisticas()["porcentajeLimpias"])
			self.running = self.paso < self.tiempoMaximo

	# self: habitación. Retorna un diccionario con tiempo, limpieza y movimientos.
	def obtenerEstadisticas(self):
		limpias = self.totalCeldas - self.basuraRestante
		return {
			"pasos": self.paso,
			"tiempoObservado": self.paso if self.tiempoLimpieza is None else self.tiempoLimpieza,
			"movimientos": self.movimientos,
			"celdasLimpias": limpias,
			"porcentajeLimpias": 100 * limpias / self.totalCeldas,
		}
