from flask import Blueprint, render_template, request, redirect, url_for, session
from app.controllers.auth_controller import login_controller, register_controller, logout_controller

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        success, payload = login_controller(username, password)
        if success:
            session["user_id"] = payload["id"]
            session["username"] = payload["username"]
            session["role"] = payload.get("role", "user")
            session["plan"] = payload.get("plan", "Starter")
            session["organization_id"] = payload.get("organization_id")
            session["organization_name"] = payload.get("organization_name", "Personal")
            return redirect(url_for("scan.dashboard"))
        return render_template("login.html", error=payload)
    return render_template("login.html", error=None)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        organization_name = request.form.get("organization_name", "").strip()
        plan = request.form.get("plan", "Starter").strip() or "Starter"
        success, message = register_controller(username, email, password, organization_name, plan)
        if success:
            return redirect(url_for("auth.login"))
        return render_template("register.html", error=message)
    return render_template("register.html", error=None)

@auth_bp.route("/logout", methods=["GET"])
def logout():
    logout_controller()
    session.clear()
    return redirect(url_for("auth.login"))
