package main

import (
	"fmt"
	"net/http"
	"web-app/controller"
	"web-app/infrastructure"
	"web-app/service"
)

const port = ":8080"

func main() {
	repository := infrastructure.NewUserRepository()
	adminService := service.NewAdminService(repository)
	adminController := controller.NewAdminController(adminService)
	http.HandleFunc("/", adminController.AdminHandler)

	fmt.Println("Сервер запущен на http://localhost" + port)
	http.ListenAndServe(port, nil)
}
