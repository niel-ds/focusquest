import flet as ft
from pages.login_page import LoginPage
from pages.home_page import HomePage
from services.supabase_service import SupabaseService


def main(page: ft.Page):
    page.title = "FocusQuest"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0D0D1A"
    page.padding = 0
    page.window.width = 400
    page.window.height = 800

    try:
        supabase = SupabaseService()
    except ValueError as e:
        page.add(ft.Text(str(e), color="red", size=16))
        return

    def route_change(e):
        page.views.clear()
        if page.route in ("/", "/login"):
            page.views.append(LoginPage(page, supabase, go_home))
        elif page.route == "/home":
            page.views.append(HomePage(page, supabase, go_login))
        page.update()

    def go_home(user_data):
        page.session.set("user", user_data)
        page.go("/home")

    def go_login():
        supabase.sign_out()
        page.session.remove("user")
        page.go("/login")

    page.on_route_change = route_change
    page.go("/login")


ft.app(target=main)
