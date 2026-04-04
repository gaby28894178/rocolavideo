# FonolaGabySoft - Constructor

## Archivos Necesarios

Para que el programa exe funcione correctamente, asegúrate de que los siguientes archivos estén presentes en la carpeta `constructor`:

- `constructor/config.ini`
- `constructor/configteclas.ini`
- `constructor/FonolaGabySoft.spec`
- `constructor/README.md`
- `constructor/teclas_disponibles.json`
- `constructor/url.ini`

## Comando de Compilación

Para compilar el programa en un ejecutable, ejecuta el siguiente comando desde la carpeta `constructor`:

```
python -m PyInstaller --noconfirm --onedir --windowed --icon "icono_app.ico" --add-data "Interface;Interface" --add-data "Logic;Logic" --name "FonolaGabySoft" "main.py"
```

Este comando genera un directorio con el ejecutable en `dist/FonolaGabySoft/`.
