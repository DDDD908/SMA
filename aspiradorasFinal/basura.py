# Descripción: Representa una unidad de basura que permanece en su celda hasta que una aspiradora la recoge.
# Autores: Alexa Sarahí Castillo Portillo A01803450 - Daniela Gil González A01752908 
# Fecha: 16/11/2026
from mesa.discrete_space import FixedAgent


class Basura(FixedAgent):

	# Coloca la basura en la celda que el modelo eligió al iniciar la corrida.
	# self: Unidad de basura que se está creando.
	# modelo: Simulación a la que pertenece.
	# celda: Celda de la habitación donde se coloca.
	# Retorno: ninguno.
	def __init__(self, modelo, celda):
		super().__init__(modelo)
		self.cell = celda