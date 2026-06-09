package service

import (
	"web-app/infrastructure"
)

type AdminService struct {
	userRepository infrastructure.UserRepository
}

func NewAdminService(repository infrastructure.UserRepository) AdminService {
	return AdminService{userRepository: repository}
}
