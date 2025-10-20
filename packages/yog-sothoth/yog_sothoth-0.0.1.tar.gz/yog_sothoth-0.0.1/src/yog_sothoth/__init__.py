# def main() -> None:
#     print("Hello from yog-sothoth!")
# # 

# src/yog_sothoth/__init__.py
from hack_py.hack import do_hack_py_stuff

def main() -> None:
    """
    Entrypoint principal de Python (Yog-Sothoth).
    """
    print("--- INICIO: Entrypoint Yog-Sothoth (Python) ---")

    # 1. Tarea del propio Yog-Sothoth
    print(">> [yog_sothoth]: Ejecutando lógica principal.")

    # 2. Llamada a la librería hack_py
    hack_message = do_hack_py_stuff()
    print(hack_message)

    print("--- FIN: Entrypoint Yog-Sothoth (Python) ---")