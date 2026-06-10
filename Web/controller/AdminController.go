package controller

import (
	"html/template"
	"net/http"
	"strconv"
	"web-app/TemplatesData"
	"web-app/service"
)

const baseTemplatePath = "templates/Base.html"
const usersTemplatePath = "templates/Users.html"
const userInfoTemplatePath = "templates/UserInfo.html"
const errorTemplatePath = "templates/Error.html"

const errorPage = "Error.html"
const usersPage = "Users.html"
const userInfoPage = "UserInfo.html"

type AdminController struct {
	adminService service.AdminService
	templates    *template.Template
}

func NewAdminController(service service.AdminService) AdminController {
	templates, err := template.ParseFiles(
		baseTemplatePath,
		usersTemplatePath,
		userInfoTemplatePath,
		errorTemplatePath,
	)
	if err != nil {
		panic(err)
	}

	return AdminController{
		adminService: service,
		templates:    templates,
	}
}

func (c *AdminController) UsersHandler(w http.ResponseWriter, r *http.Request) {
	users, err := c.adminService.GetAllUsers()
	if err != nil {
		c.templates.ExecuteTemplate(w, errorPage, TemplatesData.ErrorPageData{err.Error()})
		return
	}

	data := TemplatesData.UsersPageData{Users: users}
	c.templates.ExecuteTemplate(w, usersPage, data)
}

func (c *AdminController) UserInfoHandler(w http.ResponseWriter, r *http.Request) {
	userId, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		c.templates.ExecuteTemplate(w, errorPage, TemplatesData.ErrorPageData{err.Error()})
		return
	}

	user, err := c.adminService.GetUserInfo(userId)
	if err != nil {
		c.templates.ExecuteTemplate(w, errorPage, TemplatesData.ErrorPageData{err.Error()})
		return
	}

	userGames, err := c.adminService.GetAllUserGames(userId)
	if err != nil {
		c.templates.ExecuteTemplate(w, errorPage, TemplatesData.ErrorPageData{err.Error()})
		return
	}

	data := TemplatesData.UserInfoPageData{
		User:  user,
		Games: userGames,
	}

	c.templates.ExecuteTemplate(w, userInfoPage, data)
}
