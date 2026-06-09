package service

import (
	"web-app/DTO"
	"web-app/infrastructure"
)

type AdminService struct {
	userRepository *infrastructure.UserRepository
}

func NewAdminService(repository *infrastructure.UserRepository) AdminService {
	return AdminService{userRepository: repository}
}

func (s *AdminService) GetAllUsers() ([]DTO.User, error) {
	result, err := s.userRepository.GetUsers()
	if err != nil {
		return nil, err
	}
	return result, nil
}

func (s *AdminService) GetUserInfo(userId int) (DTO.User, error) {
	user, err := s.userRepository.GetUserInfo(userId)
	if err != nil {
		return DTO.User{}, err
	}
	return user, nil
}

func (s *AdminService) GetAllUserGames(userId int) ([]DTO.Game, error) {
	result, err := s.userRepository.GetUserGames(userId)
	if err != nil {
		return nil, err
	}
	return result, nil
}
