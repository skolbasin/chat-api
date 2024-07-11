import os

from flasgger import Swagger  # type: ignore

from server.src.routes import app

# документация только по моделям
models_doc = os.path.join(os.path.dirname(__file__), "swagger_models.yml")
# документация только по API
api_doc = os.path.join(os.path.dirname(__file__), "swagger_api.json")
# общая документация
all_doc = os.path.join(os.path.dirname(__file__), "swagger_doc.yml")


def swagger():
    Swagger(app, template_file=all_doc)
