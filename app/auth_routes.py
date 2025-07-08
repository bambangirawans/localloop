# app/auth_routes.py

from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        password = request.form["password"]

        db = get_db()
        existing_user = db.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()

        if existing_user:
            flash("Phone number already registered.", "error")
            return redirect("/register")

        db.execute(
            "INSERT INTO users (full_name, phone, password_hash) VALUES (?, ?, ?)",
            (full_name, phone, generate_password_hash(password))
        )
        db.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["phone"] = user["phone"]
            flash("Welcome back!", "success")
            return redirect("/")

        flash("Invalid phone number or password.", "error")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")
