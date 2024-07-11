from server.db import init_db
from server.doc.doc_config import swagger
from server.src.log_config import server_log
from server.src.routes import app

if __name__ == "__main__":
    init_db()
    server_log.debug("База данных подключилась")
    swagger()
    server_log.debug("Документация подключилась")
    app.run(host="0.0.0.0", port=8000)
    server_log.debug("Сервер запустился")
