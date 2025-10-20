// src/yog_sothoth/yog.go

package main

import (
	"fmt"
	"runtime"

	// Importamos nuestra librería local 'src/hack_go'
	// go.work se encarga de que Go la encuentre
	"src/hack_go"
)

func main() {
	fmt.Println("--- INICIO: Entrypoint Yog-Sothoth (Go) ---")

	// 1. Tarea del propio Yog-Sothoth
	fmt.Printf(">> [yog_sothoth]: Ejecutando en Go Version: %s\n", runtime.Version())

	// 2. Llamada a la librería hack_go
	hack_message := hack_go.DoHackGoStuff() // Llamamos la func pública
	fmt.Println(hack_message)

	fmt.Println("--- FIN: Entrypoint Yog-Sothoth (Go) ---")
}
