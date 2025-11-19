# Servidor IA - Puerto 7060

Scripts específicos para ejecutar el backend de IA en el servidor dedicado (10.0.218.101).

## Conexión al servidor

```bash
ssh -p 101 grupo6@jb.dcc.uchile.cl
```

**Credenciales:**
- Host: jb.dcc.uchile.cl
- Puerto: 101
- Usuario: grupo6
- Password: g6xdXhfkUEqHYLhLpfV
- IP local: 10.0.218.101

## Instalación rápida

```bash
# 1. Clonar el repositorio
cd ~
mkdir -p sources
cd sources
git clone https://github.com/M4rb4r0/Proyecto-de-IA-safecab.git
cd Proyecto-de-IA-safecab
git checkout ai/video-processing

# 2. Instalar Miniforge si no está
cd ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b
~/miniforge3/bin/conda init bash
source ~/.bashrc

# 3. Instalar el servidor IA
cd ~/sources/Proyecto-de-IA-safecab/release/ia-server
chmod +x *.sh
bash INSTALL.sh

# 4. (Opcional) Configurar como servicio
bash INSTALL-service.sh
```

## Características

- ✅ **Sin Apache**: Usa Gunicorn (servidor WSGI puro)
- ✅ **Sin sudo**: No requiere permisos de administrador
- ✅ **Puerto 7060**: Accesible desde la red local
- ✅ **Auto-reinicio**: Con systemd (opcional)
- ✅ **GPU**: Compatible con PyTorch y CUDA

## Estructura de directorios

```
~/safecab-ia-server/
├── app1-ia/           # Código de la aplicación
│   ├── app.py
│   ├── main.py
│   ├── utils.py
│   └── server.pid
├── logs/              # Logs del servidor
│   ├── access.log
│   └── error.log
├── subir.sh          # Script para iniciar
└── bajar.sh          # Script para detener
```

## Comandos

### Control manual

```bash
# Iniciar servidor
bash ~/safecab-ia-server/subir.sh

# Detener servidor
bash ~/safecab-ia-server/bajar.sh

# Ver logs en tiempo real
tail -f ~/safecab-ia-server/logs/error.log

# Ver procesos
ps aux | grep gunicorn
```

### Control con systemd (si está configurado)

```bash
# Ver estado
systemctl --user status safecab-ia-server

# Iniciar
systemctl --user start safecab-ia-server

# Detener
systemctl --user stop safecab-ia-server

# Reiniciar
systemctl --user restart safecab-ia-server

# Ver logs
journalctl --user -u safecab-ia-server -f
```

## Verificación

```bash
# Ver si el puerto está escuchando
netstat -tlnp | grep 7060

# Ver procesos de Gunicorn
ps aux | grep gunicorn

# Probar endpoint (desde otro servidor con curl)
curl http://10.0.218.101:7060/safecab/app1-ia/predict
```

## Actualizar código

```bash
cd ~/sources/Proyecto-de-IA-safecab
git pull
git checkout ai/video-processing

# Reinstalar
cd release/ia-server
bash INSTALL.sh

# O reiniciar manualmente
bash ~/safecab-ia-server/bajar.sh
cp -r ../../app1-ia/* ~/safecab-ia-server/app1-ia/
bash ~/safecab-ia-server/subir.sh
```

## Troubleshooting

### Puerto ocupado

```bash
# Matar procesos
pkill -9 -f "gunicorn.*7060"

# Verificar que esté libre
netstat -tlnp | grep 7060
```

### Ver logs detallados

```bash
# Logs de error
tail -50 ~/safecab-ia-server/logs/error.log

# Logs de acceso
tail -50 ~/safecab-ia-server/logs/access.log
```

### Reinstalar ambiente

```bash
conda remove -n safecab-ia --all -y
conda create -n safecab-ia python=3.11 -y
source ~/miniforge3/bin/activate safecab-ia
pip install gunicorn flask torch torchvision pillow ultralytics opencv-python
```

## Endpoints

- `POST /safecab/app1-ia/predict` - Detección en imágenes
- `POST /safecab/app1-ia/predict-video` - Detección en videos

## Configuración del Frontend

El frontend debe configurar la variable de entorno:

```bash
export IA_SERVER=http://10.0.218.101:7060
```

O editar `app1-front/app.py`:

```python
IA_SERVER = 'http://10.0.218.101:7060'
```
