from website import create_app

app = create_app()

if app.config["FLASK_ENV"] == 'development':
    if __name__ == "__main__":
        app.run(debug=True)