# Discord Chat AI
## Usage
This discord bot allows you to assign personalities to different text channels, the bot will then respond with its best response it can find. After it sends a message three reactions will be added, a green, blue and red circle. The green circle will positively reinforce the response, the blue will not encourage nor discourage the response and the red will prompt the user for a better response.
This requires an SQL database to store the learning.
## Config
All of the config can be done in the `config.json` file.

| Flag                  | Usage                                                                                                  | Default              |
|-----------------------|--------------------------------------------------------------------------------------------------------|----------------------|
| BOT_TOKEN             | The discord token for your bot.                                                                        | -                    |
| BOT_PREFIX            | The prefix used for chat commands.                                                                     | ">"                  |
| BOT_STATUS            | The playing status your bot will display.                                                              | "Train me to speak!" |
| RESPONSE_TIMEOUT      | How long the bot will wait for responses.                                                              | 30                   |
| MINIMUM_CONFIDENCE    | The minimum confidence for a response to be considered.                                                | 0.4                  |
| MAXIMUM_CONFIDENCE    | The maximum confidence for a response to be considered.                                                | 1                    |
| DB_PROTOCOL           | The protocol used to access the database.                                                              | "mysql+pymysql"      |
| DB_USERNAME           | The username for the database.                                                                         | "username"           |
| DB_PASSWORD           | The password to the database.                                                                          | "password"           |
| DB_IP                 | The IP for the database host.                                                                          | "localhost"          |
| DB_NAME               | The name of the database.                                                                              | "chatbotDB"          |
| CHANNEL_PERSONALITIES | A key value pair with the key as a discord channel ID as a string and the value as a personality name. | {}                   |
## Database Structure
### statement
| Field          | Type         | Nullable | Primary Key | Default |
|----------------|--------------|----------|-------------|---------|
| id             | int          | no       | yes         | -       |
| text           | varchar(255) | no       | no          | -       |
| in_response_to | varchar(255) | no       | no          | -       |
| personality    | varchar(64)  | no       | no          | normal  |

MySQL
```sql
CREATE TABLE `statement` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`text` VARCHAR(255) NOT NULL,
	`in_response_to` VARCHAR(255) NOT NULL,
	`personality` VARCHAR(64) NOT NULL DEFAULT 'normal',
	PRIMARY KEY (`id`)
);
```