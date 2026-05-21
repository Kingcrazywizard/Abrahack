### 🏎️ ¿Por qué Nativo es superior para Ollama en tu setup?

- **Cero fricción con CUDA:** De forma nativa, Ollama detecta tu GTX 1060 y las librerías de CUDA en el milisegundo en que arranca el sistema. En Docker, tendrías que instalar el `nvidia-container-toolkit`, mapear los _sockets_ de la GPU hacia el contenedor, configurar los _runtimes_ en el archivo `daemon.json` y lidiar con permisos adicionales.
    
- **Consumo mínimo de recursos:** Al correr nativo mediante un servicio de `systemd`, Ollama se apaga o entra en reposo absoluto consumiendo casi 0% de CPU y RAM cuando no le estás haciendo peticiones, liberando toda la potencia para cuando lances Unity.
    
- **Integración limpia con tus herramientas:** Al estar expuesto directamente en el puerto local (`localhost:11434`), cualquier script de automatización en Bash, aplicación de Python o tu futuro backend en Docker para los agentes cognitivos se conectará a Ollama de forma directa sin configurar redes virtuales bridge de Docker.
    

## Despliegue de Ollama + Phi-3-mini (Modo Nativo)

Abre tu terminal Kitty y ejecuta los siguientes pasos:

### Paso 1: Instalar Ollama desde los repositorios oficiales

En Arch, Ollama está mantenido de forma impecable en los repositorios oficiales de la comunidad:

Bash

```
sudo pacman -S ollama
```

### Paso 2: Habilitar y arrancar el servicio con Systemd

En lugar de ejecutarlo manualmente en primer plano, vamos a dejarlo como un demonio del sistema que se administre solo:

Bash

```
sudo systemctl enable --now ollama
```

_(Para verificar que esté corriendo fino y escuchando en tu sistema, puedes ejecutar `systemctl status ollama`)._

### Paso 3: Descargar y correr Phi-3-mini en tu GPU

Ahora viene el momento mágico. Vamos a pedirle a Ollama que descargue el modelo de Microsoft cuantizado e inicialice un chat directo en tu consola. Ejecuta:

Bash

```
ollama run phi3:mini
```

### ¿Qué verás ahora?

Ollama comenzará a descargar los aproximadamente 2.2 GB que pesa el modelo. Al terminar la descarga, la terminal cambiará y te mostrará un prompt de entrada (`>>>`).

Hazle una pregunta de código compleja o pídele que actúe como un experto en etología canina para tu app _MyDoggy_. Notarás cómo tu GTX 1060 despierta (los ventiladores podrían acelerar un poco) y verás la velocidad absurda a la que imprime los caracteres en pantalla gracias a que está alojado por completo en tu VRAM.

¡Escribe `ollama run phi3:mini` y dime qué tal se siente la velocidad de tu primera IA ejecutada de forma 100% soberana en tu máquina!