# ZPlatform

Company Z provides essential online services for tens of thousands of users through their platform ZPlatform. Company Z is going through stages of growth and adding 1000’s of users daily - while still serving millions of transactions per month.

## Running the application

### Requirements

```
- git
- docker
- docker compose V3 (If you use V2, use docker-compose when running docker compose commands)
```

### Installation and Setup

- Clone the repository

```
git clone https://github.com/Paccy10/z-platform.git
```

- Environment variables

```
Create a .env file and copy variables from .env.sample to .env and fill them accordingly (Check the submitted document or email for some values for some of them)
```

- Build and run the app

```
docker compose up --build -d --remove-orphans
```

- Run the app

```
docker compose up -d
```

- Stop the app

```
docker compose down
```

- Check logs

```
docker compose logs
```

- Run tests

```
docker compose exec api pytest
```
