from ext import app
from routes import main, logout, login, register, search, add_news, news_detail, edit_comment, delete_comment, edit_news, delete_news, category


app.run(debug=True, host= "0.0.0.0")
