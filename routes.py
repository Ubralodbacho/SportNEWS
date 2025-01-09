from flask import render_template, redirect, flash, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from uuid import uuid4

from forms import NewsForm, RegisterForm, LoginForm, CommentForm
from models import News, User, Comment
from ext import app, db


@app.route("/")
def main():
    latest_news = News.query.order_by(News.created_at.desc()).limit(3).all()
    return render_template("web-main.html", latest_news = latest_news)


@app.route("/web_login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        else:
            flash("Invalid username or password", "error")
    return render_template("web-login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/registration", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        
        if existing_user:
            flash("ამ სახელით მომხმარებელი უკვე არსებობს. გთხოვთ, აირჩიოთ სხვა სახელი.", "error")
            return redirect("/registration") 

        new_user = User(username=form.username.data,
                        password=form.password.data,
                        role="Guest")
        db.session.add(new_user)
        db.session.commit()
        return redirect("/web_login")
    
    return render_template("web-reg.html", form=form)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get('query') 
    if query:
        results = News.query.filter(News.name.ilike(f'%{query}%')).all()  # სვაში `name`-ში შესაბამისი სიტყვა
        return render_template("search_results.html", results=results, query=query)
    return render_template("search_results.html", results=[], query=query)


@app.route("/<category>")
def category(category):
    news = News.query.filter(News.category == category).order_by(News.id.desc()).all()
    return render_template(f"category.html", news=news, category=category)

@app.route("/add_news", methods=["GET", "POST"])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        file = form.img.data
        filename, filetype = path.splitext(file.filename)
        filename = f"{uuid4()}{filetype}"
        filepath = path.join(app.root_path, "static", filename)
        file.save(filepath)

        new_news = News(name=form.name.data,
                           descrip=form.descrip.data,
                           category = form.category.data,
                           img=filename)

        db.session.add(new_news)
        db.session.commit()

        return redirect("/")

    if form.errors:
        flash(f"Form errors: {form.errors}", "danger")
    return render_template("add-news.html", form=form)



@app.route("/news_detail/<int:news_id>", methods=["GET", "POST"])
def news_detail(news_id):
    news_item = News.query.get_or_404(news_id)
    form = CommentForm()

    if not current_user.is_authenticated:
        flash("კომენატრის დასატოვებლად აუცილებელია ავტორიზაციის გავლა", "warning")

    # კომენტარის დამატება ( მხოლოდ ავტორიზებულისთვის )
    if current_user.is_authenticated and form.validate_on_submit():
        comment = Comment(content=form.content.data, news_id=news_id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash("კომენტარი წარმატებით დაემატა!", "success")
        return redirect(url_for("news_detail", news_id=news_id))

    comments = Comment.query.filter_by(news_id=news_id).all()  # ყველა კომენტარი
    return render_template("news_detail.html", news=news_item, form=form, comments=comments)


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.user.id and current_user.role != 'Admin':
        flash("თქვენ არ გაქვთ უფლება ამ კომენტარის რედაქტირებაზე!", "danger")
        return redirect(url_for("news_detail", news_id=comment.news_id))

    form = CommentForm(obj=comment)
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash("კომენტარი წარმატებით განახლდა!", "success")
        return redirect(url_for("news_detail", news_id=comment.news_id))

    return render_template("edit_comment.html", form=form, comment=comment)

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.user.id and current_user.role != 'Admin':
        flash("თქვენ არ გაქვთ უფლება ამ კომენტარის წაშლაზე!", "danger")
        return redirect(url_for("news_detail", news_id=comment.news_id))

    db.session.delete(comment)
    db.session.commit()
    flash("კომენტარი წარმატებით წაიშალა!", "success")
    return redirect(url_for("news_detail", news_id=comment.news_id))




@app.route("/edit_news/<int:news_id>", methods=["GET", "POST"])
@login_required
def edit_news(news_id):
    
    if current_user.role != 'Admin':
        flash("თქვენ არ გაქვთ უფლება ამ გვერდზე წვდომისათვის!", "danger")
        return redirect("/")  

    news_item = News.query.get_or_404(news_id)  
    form = NewsForm(obj=news_item)  

    if form.validate_on_submit():
        
        news_item.name = form.name.data
        news_item.descrip = form.descrip.data
        news_item.category = form.category.data

        
        if form.img.data:
            file = form.img.data
            filename, filetype = path.splitext(file.filename)
            filename = f"{uuid4()}{filetype}"
            filepath = path.join(app.root_path, "static", filename)
            file.save(filepath)
            news_item.img = filename

        db.session.commit()
        flash("მონაცემები წარმატებით განახლდა!", "success")
        return redirect(f"/{news_item.category}")  

    return render_template("edit-news.html", form=form, news=news_item)

@app.route("/delete_news/<int:news_id>", methods=["POST"])
@login_required
def delete_news(news_id):
    if current_user.role != 'Admin':
        flash("თქვენ არ გაქვთ უფლება ამ გვერდზე წვდომისათვის!", "danger")
        return redirect("/") 

    news_item = News.query.get_or_404(news_id)


    return redirect(f"/{news_item.category}")