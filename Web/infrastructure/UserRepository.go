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
	rows, err := r.db.Query(`
	SELECT u.*, COUNT(g.id) AS games_count
	FROM users u LEFT JOIN games g ON u.id = g.user_id
	GROUP BY u.id, u.username, u.telegram_id, u.register_date, u.last_active
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var result []DTO.User

	for rows.Next() {
		var user DTO.User
		err := rows.Scan(&user.Id, &user.Username, &user.Telegram_id, &user.Register_date, &user.Last_active, &user.Games_count)
		if err != nil {
			return nil, err
		}
		result = append(result, user)
	}

	return result, nil
}

func (r *UserRepository) GetUserInfo(userId int) (DTO.User, error) {
	var user DTO.User
	err := r.db.QueryRow(`SELECT * FROM users WHERE id = $1`, userId).Scan(
		&user.Id,
		&user.Username,
		&user.Telegram_id,
		&user.Register_date,
		&user.Last_active,
	)

	return user, err
}

func (r *UserRepository) GetUserGames(userId int) ([]DTO.Game, error) {
	rows, err := r.db.Query(`
	SELECT
    id,
    user_id,
    COALESCE(external_game_id, 0),
    game_name,
    game_status,
    COALESCE(user_rating, 0),
    COALESCE(note, ''),
    date_added,
	COALESCE(completion_date, '0001-01-01')
	FROM Games 
	WHERE user_id = $1`, userId)
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
