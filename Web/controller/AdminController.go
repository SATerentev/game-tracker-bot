package controller

import (
	"html/template"
	"net/http"
	"web-app/service"
)

const indexTemplagePath = "templates/index.html"

type AdminController struct {
	adminService  service.AdminService
	indexTemplate template.Template
}

type IndexPageData struct {
	Test string
}

func NewAdminController(service service.AdminService) AdminController {
	indexTemplate, err := template.ParseFiles(indexTemplagePath)
	if err != nil {
		panic("Somethin went wrong " + err.Error())
	}
	return AdminController{adminService: service, indexTemplate: *indexTemplate}
}

func (c *AdminController) AdminHandler(w http.ResponseWriter, r *http.Request) {
	data := IndexPageData{Test: "asd"}
	c.indexTemplate.Execute(w, data)
}
