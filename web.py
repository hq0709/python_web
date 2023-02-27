from flask import Flask, render_template

# Flask 是一个类
app = Flask(__name__)


# 创建了网址 /show/info 和函数 index 的对应关系
# 以后在浏览器上访问网址 /show/info 网站自动执行index
@app.route("/show/info")
def index():
    # return "jhqyyds"
    return render_template("index.html")


@app.route("/get/news")
def get_news():
    return render_template("get_news.html")


if __name__ == "__main__":
    app.run()
