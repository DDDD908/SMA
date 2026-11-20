# Descripción: Define una aspiradora reactiva que limpia su celda o intenta moverse en una de las ocho direcciones en cada turno.
# Autores: Alexa Sarahí Castillo Portillo A01803450 - Daniela Gil González A01752908 
# Fecha: 16/11/2026
from mesa.discrete_space import CellAgent


DIRECCIONES = (
	(-1, -1), (0, -1), (1, -1),
	(-1, 0),           (1, 0),
	(-1, 1),  (0, 1),  (1, 1),
)


class Aspiradora(CellAgent):

	# Coloca la aspiradora en la celda inicial que le asigna el modelo.
	# self: Aspiradora actual. modelo: Simulación a la que pertenece.
	# celda: Celda de inicio. Retorno: ninguno.
	def __init__(self, modelo, celda):
		super().__init__(modelo)
		self.cell = celda

	# Ejecuta una acción según lo que la aspiradora percibe en su celda.
	# self: Aspiradora que toma el turno. Retorno: ninguno.
	def actuar(self):
		posicion = self.cell.coordinate
		basura = self.model.basuraPorPosicion.get(posicion)

		if basura is not None:
			basura.remove()
			del self.model.basuraPorPosicion[posicion]
		else:
			self.intentarMovimiento()

	# Sortea una dirección. Si apunta fuera de la habitación, termina
	# el turno en la misma celda sin sumar un movimiento.
	# self: Aspiradora que intenta moverse. Retorno: ninguno.
	def intentarMovimiento(self):
		actualX, actualY = self.cell.coordinate
		cambioX, cambioY = self.random.choice(DIRECCIONES)
		destinoX = actualX + cambioX
		destinoY = actualY + cambioY

		if 0 <= destinoX < self.model.ancho and 0 <= destinoY < self.model.alto:
			self.cell = self.model.grid[destinoX, destinoY]
			self.model.movimientosTotales += 1