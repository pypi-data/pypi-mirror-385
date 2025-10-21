# QArk Behave

QArk Behave es un formatter personalizado para Behave, proporcionando resultados de pruebas personalizados para QArk

## Características

- 🎯 **Formatter personalizado**: Saca todo la información posible de tus tests en behave
- 📁 **Directorio por defecto**: Genera resultados en `qark-results` automáticamente
- 🚀 **Fácil de usar**: Invocación simple desde línea de comandos

## Instalación

### Desde el código fuente

```bash
# Clonar el repositorio
git clone https://github.com/PabloGibaja/qark-behave.git
cd qark-behave

# Instalar en modo desarrollo
pip install -e .
```

### Usando pip (cuando esté publicado)

```bash
pip install qark-behave
```

## Uso

### Uso básico

Ejecuta tus pruebas de Behave con el formatter QArk:

```bash
python -m behave -f qark_behave.formatter:QArkFormatter
```

Esto generará los resultados en el directorio `qark-results` por defecto.

### Especificar directorio de salida

Puedes especificar un directorio personalizado para los resultados:

```bash
python -m behave -f qark_behave.formatter:QArkFormatter -o ./mi-directorio-resultados
```

### Ejemplo completo

```bash
# Ejecutar todas las features con el formatter QArk
python -m behave -f qark_behave.formatter:QArkFormatter -o ./qark-results features/

# Ejecutar una feature específica
python -m behave -f qark_behave.formatter:QArkFormatter -o ./resultados features/login.feature
```

## Estructura del proyecto
