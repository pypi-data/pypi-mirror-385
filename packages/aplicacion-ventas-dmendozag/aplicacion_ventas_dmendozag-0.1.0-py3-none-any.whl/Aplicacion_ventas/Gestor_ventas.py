from .Descuentos import descuento
from .Impuestos import impuestos
from .Precios import precios

class GestorVentas:
    def __init__(self,precio_base,impuesto_porcentaje,descuento_porcentaje):
        self.precio_base = precio_base
        self.impuesto = impuestos(impuesto_porcentaje)
        self.descuento = descuento(descuento_porcentaje)
    
    def calcular_precio_final(self):
        impuesto_aplicado = self.impuesto.aplicar_impuesto(self.precio_base)
        descuento_aplicado = self.descuento.aplicar_descuento(self.precio_base)
        precio_final = precios.calcular_precio_final(self.precio_base,impuesto_aplicado,descuento_aplicado)
        return round(precio_final,2)
    
        