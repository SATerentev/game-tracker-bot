CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    telegram_id BIGINT UNIQUE NOT NULL,
    register_date DATE DEFAULT CURRENT_DATE,
    last_active DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Games (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(id) ON DELETE CASCADE,
    external_game_id BIGINT,
    game_name VARCHAR(255) NOT NULL,
    game_status INT NOT NULL,
    user_rating INT,
    note TEXT,
    date_added DATE NOT NULL,
    completion_date DATE
);