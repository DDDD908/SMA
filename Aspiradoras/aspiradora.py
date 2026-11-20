# Comportamiento reactivo del robot aspirador.
# Autores: [Daniela Gil González A01752908 Alexa Sarahí Castillo Portillo A01803450]
# Fecha: 16/11/2026

from mesa.discrete_space import CellAgent
from basura import Basura

DIRECCIONES = (
	(-1, -1), (0, -1), (1, -1),
	(-1, 0), (1, 0),
	(-1, 1), (0, 1), (1, 1),
)


class Aspiradora(CellAgent):
	# self: aspiradora en turno. Limpia o intenta moverse una vez. Retorno: ninguno.
	def step(self):
		basuraAqui = next((obj for obj in self.cell.agents if isinstance(obj, Basura)), None)
		if basuraAqui is not None:
			basuraAqui.remove()
			self.model.basuraRestante -= 1
		else:
			x, y = self.cell.coordinate
			dx, dy = self.random.choice(DIRECCIONES)
			destino = (x + dx, y + dy)
			if 0 <= destino[0] < self.model.width and 0 <= destino[1] < self.model.height:
				self.cell = self.model.grid[destino]
				self.model.movimientos += 1
