package DTO

import (
	"time"
)

type Game struct {
	Id               int
	User_id          int
	External_game_id int
	Game_name        string
	Game_status      int
	User_rating      int
	Note             string
	Date_added       time.Time
	Completion_date  time.Time
}

func (u Game) Formatted_date_added() string {
	return u.Date_added.Format("2006-01-02")
}

func (u Game) Formatted_completion_date() string {
	if u.Completion_date.IsZero() {
		return ""
	}
	return u.Completion_date.Format("2006-01-02")
}
