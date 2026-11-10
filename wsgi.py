"""WSGI 入口：gunicorn / uWSGI / flask run 都从这里加载。

    flask --app wsgi run --debug
    gunicorn -b 0.0.0.0:8000 wsgi:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":  # 直接 python wsgi.py 也能起一个开发服务器
    app.run(host="127.0.0.1", port=5000, debug=True)
