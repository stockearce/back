from rest_framework import serializers
from .models import Producto, ImagenProducto, TipoProducto

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'ruta']

class ProductoSerializer(serializers.ModelSerializer):
    # Incluir las imágenes relacionadas
    imagenes = ImagenProductoSerializer(many=True, read_only=True, source='imagenproducto_set')
    
    # Incluir el nombre del tipo de producto
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    
    # URL completa de la primera imagen (si existe)
    imagen_principal = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'tipo',
            'tipo_nombre',
            'cantidad',
            'valor',
            'umbral_alerta',
            'fecha_modificacion',
            'imagenes',
            'imagen_principal'
        ]
    
    def get_imagen_principal(self, obj):
        """Retorna la URL completa de la primera imagen del producto"""
        primera_imagen = obj.imagenproducto_set.first()
        if primera_imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{primera_imagen.ruta}')
            return f'/media/{primera_imagen.ruta}'
        return None

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = ['id', 'nombre']
