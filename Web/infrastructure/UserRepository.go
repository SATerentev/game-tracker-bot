package infrastructure

import (
	"database/sql"
	"web-app/DTO"

	_ "github.com/lib/pq"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(connectionString string) (*UserRepository, error) {
	db, err := sql.Open("postgres", connectionString)
	if err != nil {
		return nil, err
	}

	return &UserRepository{db: db}, nil
}

func (r *UserRepository) GetUsers() ([]DTO.User, error) {
	rows, err := r.db.Query(`SELECT * FROM Users`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var result []DTO.User

	for rows.Next() {
		var user DTO.User
		err := rows.Scan(&user.Id, &user.Username, &user.Telegram_id, &user.Register_date, &user.Last_active)
		if err != nil {
			return nil, err
		}
		result = append(result, user)
	}

	return result, nil
}

func (r *UserRepository) GetUserInfo(userId int) (DTO.User, error) {
	var user DTO.User
	err := r.db.QueryRow(`SELECT * FROM Users WHERE id = $1`, userId).Scan(
		&user.Id,
		&user.Username,
		&user.Telegram_id,
		&user.Register_date,
		&user.Last_active,
	)

	return user, err
}

func (r *UserRepository) GetUserGames(userId int) ([]DTO.Game, error) {
	rows, err := r.db.Query(`SELECT * FROM Games WHERE user_id = $1`, userId)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var result []DTO.Game

	for rows.Next() {
		var game DTO.Game
		err := rows.Scan(
			&game.Id,
			&game.User_id,
			&game.External_game_id,
			&game.Game_name,
			&game.Game_status,
			&game.User_rating,
			&game.Note,
			&game.Date_added,
			&game.Completion_date,
		)
		if err != nil {
			return nil, err
		}
		result = append(result, game)
	}

	return result, nil
}
