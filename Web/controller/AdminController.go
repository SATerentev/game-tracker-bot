package controller

import (
	"html/template"
	"net/http"
	"strconv"
	"web-app/DTO"
	"web-app/service"
)

const usersTemplatePath = "templates/Users.html"
const userInfoTemplatePath = "templates/UserInfo.html"
const errorTemplatePath = "templates/Error.html"

type AdminController struct {
	adminService     service.AdminService
	usersTemplate    template.Template
	userInfoTemplate template.Template
	errorTemplate    template.Template
}

type UsersPageData struct {
	Users []DTO.User
}

type UserInfoPageData struct {
	User  DTO.User
	Games []DTO.Game
}

func NewAdminController(service service.AdminService) AdminController {
	usersTemplate, err := template.ParseFiles(usersTemplatePath)
	if err != nil {
		panic(err)
	}
	userInfoTemplate, err := template.ParseFiles(userInfoTemplatePath)
	if err != nil {
		panic(err)
	}
	errorTemplate, err := template.ParseFiles(errorTemplatePath)
	if err != nil {
		panic(err)
	}
	return AdminController{
		adminService:     service,
		usersTemplate:    *usersTemplate,
		userInfoTemplate: *userInfoTemplate,
		errorTemplate:    *errorTemplate,
	}
}

func (c *AdminController) UsersHandler(w http.ResponseWriter, r *http.Request) {
	users, err := c.adminService.GetAllUsers()
	if err != nil {
		panic(err)
	}
	data := UsersPageData{Users: users}
	c.usersTemplate.Execute(w, data)
}

func (c *AdminController) UserInfoHandler(w http.ResponseWriter, r *http.Request) {
	userId, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		c.errorTemplate.Execute(w, err)
	}

	userGames, err := c.adminService.GetAllUserGames(userId)
	if err != nil {
		c.errorTemplate.Execute(w, err)
	}
	user, err := c.adminService.GetUserInfo(userId)
	data := UserInfoPageData{
		User:  user,
		Games: userGames,
	}

	c.userInfoTemplate.Execute(w, data)
}
