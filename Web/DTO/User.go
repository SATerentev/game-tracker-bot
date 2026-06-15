package DTO

import (
	"time"
)

type User struct {
	Id            int
	Username      string
	Telegram_id   int
	Register_date time.Time
	Last_active   time.Time
	Games_count   int
}

func (u User) Formatted_register_date() string {
	return u.Register_date.Format("2006-01-02")
}

func (u User) Formatted_last_active_date() string {
	return u.Last_active.Format("2006-01-02")
}
