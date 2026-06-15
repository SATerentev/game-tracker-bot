package TemplatesData

import "web-app/DTO"

type UsersPageData struct {
	Users []DTO.User
}

type UserInfoPageData struct {
	User  DTO.User
	Games []DTO.Game
}

type ErrorPageData struct {
	Error string
}
