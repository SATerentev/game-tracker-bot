package main

import (
	"fmt"
	"net/http"
	"os"
	"web-app/controller"
	"web-app/infrastructure"
	"web-app/service"

	"github.com/joho/godotenv"
)

const port = ":8080"

func main() {
	err := godotenv.Load("../.env")
	if err != nil {
		panic(err)
	}
	repository, err := infrastructure.NewUserRepository(getConnectionString())
	if err != nil {
		panic(err)
	}
	adminService := service.NewAdminService(repository)
	adminController := controller.NewAdminController(adminService)
	http.HandleFunc("/users", adminController.UsersHandler)
	http.HandleFunc("/user/{id}", adminController.UserInfoHandler)

	fmt.Println("Сервер запущен на http://localhost" + port)
	http.ListenAndServe(port, nil)
}

func getConnectionString() string {
	var (
		DB_user          = os.Getenv("DB_USER")
		DB_password      = os.Getenv("DB_PASSWORD")
		DB_name          = os.Getenv("DB_NAME")
		DB_host          = os.Getenv("DB_HOST")
		DB_port          = os.Getenv("DB_PORT")
		connectionString = "user=" + DB_user + " password=" + DB_password + " database=" +
			DB_name + " host=" + DB_host + " port=" + DB_port + " sslmode=disable"
	)

	return connectionString
}
