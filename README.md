### 📝 Anonymous Note Service

Anonymous Note Service is a modern web platform that allows users to create and share notes anonymously. Users can choose to make their notes temporary—with automatic expiration after a set time—or persistent, remaining available until manually deleted. Each note can optionally include an image, offering a flexible and expressive way to communicate.

The backend is built with FastAPI, ensuring high performance and scalability. Localization support is provided by fastapi-babel, making the service accessible to a global audience. User authentication is handled securely using fastapi-users and OAuth2, supporting both traditional and social logins.

The platform leverages PostgreSQL for robust relational data storage. For asynchronous and scheduled background tasks—such as note expiration—the APScheduler library is utilized, ensuring timely and efficient task execution. Administration is streamlined with a custom admin panel built using **SQLAdmin**, providing powerful tools to manage users and content.

Development and dependency management are optimized with Poetry, replacing pip for better reproducibility and convenience. The application is deployed with Gunicorn, delivering fast response times and efficient resource usage.

To ensure portability and ease of deployment, the entire application runs inside Docker containers, enabling consistent environments across development, testing, and production.

Overall, Anonymous Note Service offers a secure, scalable, and user-friendly environment for anonymous sharing, combining a thoughtful tech stack with modern best practices in Python web development.

## Stack:

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [FastApi](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/)

## Local Developing

All actions should be executed from the source directory of the project and only after installing all requirements.

1. Firstly, create and activate a new virtual environment and install dependencies with Poetry:
   ```bash
   poetry install
   ```

2. Run database migrations using Alembic:
   ```bash
   alembic upgrade head
   ```
   
## Docker
   ```bash
   docker build .
   
   docker-compose up
   ```

## License

This project uses the [MIT] license(https://github.com/Sauberr/gallery/blob/master/LICENSE)

## Contact 

To contact the author of the project, write to email 𝚍𝚖𝚒𝚝𝚛𝚒𝚢𝚋𝚒𝚛𝚒𝚕𝚔𝚘@𝚐𝚖𝚊𝚒𝚕.𝚌𝚘𝚖.
