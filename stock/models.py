from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ------------------------------
#  MODELO: Producto
# ------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)

    cantidad = models.IntegerField(default=0)
    
    # PRECIO DE VENTA (ya existe)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    
    # 🆕 PRECIO DE COMPRA (NUEVO)
    valor_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio de Compra",
        default=0.00  # Valor por defecto
    )
    
    # 🆕 CALCULAR GANANCIA
    @property
    def ganancia_unitaria(self):
        return float(self.valor) - float(self.valor_compra)
    
    @property
    def margen_porcentaje(self):
        if float(self.valor_compra) > 0:
            return round((self.ganancia_unitaria / float(self.valor_compra)) * 100, 2)
        return 0
    
    umbral_alerta = models.PositiveIntegerField(
        default=5,
        verbose_name="Stock Mínimo de Alerta"
    )
    
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} unidades)"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ruta = models.CharField(max_length=500)
    
    def __str__(self):
        return f"Imagen {self.id} - {self.producto.nombre}"

class PresentacionProducto(models.Model):
    """
    Define las presentaciones disponibles para un producto.
    Ej: Unidad x1, Pack x6, Pack x8, Caja x24, etc.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='presentaciones'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de Presentación",
        help_text="Ej: Unidad, Pack x6, Pack x8, Caja x24"
    )
    cantidad_unidades = models.PositiveIntegerField(
        verbose_name="Cantidad de Unidades",
        help_text="Cuántas unidades de stock representa esta presentación"
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de Venta"
    )
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Precio de Compra"
    )
    activo = models.BooleanField(default=True)

    @property
    def ganancia_unitaria(self):
        return float(self.precio_venta) - float(self.precio_compra)

    @property
    def margen_porcentaje(self):
        if float(self.precio_compra) > 0:
            return round((self.ganancia_unitaria / float(self.precio_compra)) * 100, 2)
        return 0

    class Meta:
        verbose_name = "Presentación de Producto"
        verbose_name_plural = "Presentaciones de Producto"
        unique_together = ('producto', 'nombre')

    def __str__(self):
        return f"{self.producto.nombre} - {self.nombre} (x{self.cantidad_unidades}) ${self.precio_venta}"
# ------------------------------
#  MODELO: Cliente
# ------------------------------
class Cliente(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cliente'
    )

    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    nombre_local = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre del Local")

    cuil = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="CUIL/CUIT",
        unique=True
    )

    email = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_completo
from django.db import models

class Chofer(models.Model):
    """Modelo para gestionar choferes/conductores"""
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20)
    vehiculo = models.CharField(max_length=100, verbose_name="Vehículo/Patente")

    pin = models.CharField(
        max_length=6,
        verbose_name="PIN",
        help_text="PIN numérico del chofer"
    )

    activo = models.BooleanField(default=True, verbose_name="Activo")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas/Descripción")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} - {self.vehiculo}"

# ------------------------------
#  MODELO: Ventas (CON ESTADOS)
from django.db import models
from django.contrib.auth.models import User

class Ventas(models.Model):
    """
    Pedido/Venta creada por vendedores.
    NO descuenta stock hasta que estado = 'enviada'
    """

    # ==============================
    # ESTADOS
    # ==============================
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('enviada', 'Enviada'),      # Aquí se descuenta stock
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]

    # ==============================
    # MÉTODOS DE PAGO
    # ==============================
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('cuenta_corriente', 'Cuenta Corriente'),
    ]

    # ==============================
    # RELACIONES
    # ==============================

    # Usuario que creó la venta
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_creadas',
        verbose_name="Usuario creador"
    )

    # Cliente
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        verbose_name="Cliente"
    )

    # Chofer asignado
    chofer = models.ForeignKey(
        'Chofer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Chofer Asignado"
    )

    # ==============================
    # FECHAS
    # ==============================

    fecha_envio_programada = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha Programada de Envío"
    )

    hora_envio_programada = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Hora Programada de Envío"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    fecha_envio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha Real de Envío"
    )

    # ==============================
    # CAMPOS PRINCIPALES
    # ==============================

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )

    metodo_pago = models.CharField(
        max_length=30,
        choices=METODO_PAGO_CHOICES,
        default='efectivo',
        verbose_name="Método de Pago"
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total"
    )

    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas"
    )

    # ==============================
    # REGLAS DE NEGOCIO
    # ==============================

    def save(self, *args, **kwargs):
        # Una venta pendiente debe tener usuario creador
        if self.estado == 'pendiente' and not self.usuario_creador:
            raise ValueError(
                "Una venta en estado pendiente debe tener un usuario creador asignado"
            )

        super().save(*args, **kwargs)

    # ==============================
    # MÉTODOS
    # ==============================

    def calcular_total(self):
        """Calcula el total sumando todos los detalles"""
        return sum(detalle.subtotal for detalle in self.detalles.all())

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre_completo} - {self.get_estado_display()}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_creacion']

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    
    # 🆕 Presentación elegida al momento de vender
    presentacion = models.ForeignKey(
        PresentacionProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Presentación"
    )
    
    cantidad = models.PositiveIntegerField()  # Cantidad de esa presentación
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def unidades_totales_descontadas(self):
        """Cuántas unidades reales se descuentan del stock"""
        if self.presentacion:
            return self.cantidad * self.presentacion.cantidad_unidades
        return self.cantidad




from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    USUARIO_TIPOS = (
        ('ventas', 'Ventas'),
        ('administrativo', 'Administrativo'),
        ('camiones', 'Camiones'),
     
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=USUARIO_TIPOS, default='ventas')

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_display()}"
