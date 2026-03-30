import uvicorn

from ps.apps import app
from ps.conf import WEBAPP_HOST, WEBAPP_PORT


def main():
    uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    main()
