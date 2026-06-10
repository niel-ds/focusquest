import flet as ft

BG       = "#0D0D1A"
SURFACE  = "#16162A"
CARD     = "#1E1E35"
PURPLE   = "#7C3AED"
CYAN     = "#06B6D4"
GOLD     = "#F59E0B"
TEXT     = "#E2E8F0"
SUBTEXT  = "#94A3B8"
ERROR    = "#F87171"


def LoginPage(page: ft.Page, supabase, on_success):
    is_login = [True]
    error_text = ft.Text("", color=ERROR, size=13, text_align=ft.TextAlign.CENTER)

    email_field = ft.TextField(
        hint_text="E-mail",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        border_color=PURPLE,
        focused_border_color=CYAN,
        color=TEXT,
        bgcolor=CARD,
        border_radius=12,
        height=52,
    )
    password_field = ft.TextField(
        hint_text="Senha",
        prefix_icon=ft.icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_color=PURPLE,
        focused_border_color=CYAN,
        color=TEXT,
        bgcolor=CARD,
        border_radius=12,
        height=52,
    )
    username_field = ft.TextField(
        hint_text="Nome de usuário",
        prefix_icon=ft.icons.PERSON_OUTLINE,
        border_color=PURPLE,
        focused_border_color=CYAN,
        color=TEXT,
        bgcolor=CARD,
        border_radius=12,
        height=52,
        visible=False,
    )

    btn_text = ft.Text("ENTRAR", size=16, weight=ft.FontWeight.BOLD, color=BG)
    loading = ft.ProgressRing(width=22, height=22, color=BG, visible=False)
    action_btn = ft.ElevatedButton(
        content=ft.Row(
            [loading, btn_text],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        style=ft.ButtonStyle(
            bgcolor=PURPLE,
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation=0,
        ),
        height=52,
        width=340,
    )

    toggle_text = ft.Text("Não tem conta? ", color=SUBTEXT, size=14)
    toggle_link = ft.TextButton(
        "Criar conta",
        style=ft.ButtonStyle(color=CYAN),
    )

    title_label = ft.Text(
        "FOCUSQUEST",
        size=30,
        weight=ft.FontWeight.W_900,
        color=PURPLE,
    )
    subtitle = ft.Text(
        "Transforme suas metas em missões",
        color=SUBTEXT,
        size=14,
        text_align=ft.TextAlign.CENTER,
    )

    def set_loading(val: bool):
        loading.visible = val
        btn_text.visible = not val
        action_btn.disabled = val
        page.update()

    def do_action(e):
        error_text.value = ""
        em = email_field.value.strip()
        pw = password_field.value.strip()
        if not em or not pw:
            error_text.value = "Preencha e-mail e senha."
            page.update()
            return
        set_loading(True)
        try:
            if is_login[0]:
                res = supabase.sign_in(em, pw)
                if res.user:
                    profile = supabase.get_profile(res.user.id)
                    on_success({"user": res.user, "profile": profile})
                else:
                    error_text.value = "E-mail ou senha inválidos."
            else:
                un = username_field.value.strip()
                if not un:
                    error_text.value = "Preencha o nome de usuário."
                    set_loading(False)
                    return
                res = supabase.sign_up(em, pw, un)
                if res.user:
                    profile = supabase.get_profile(res.user.id)
                    on_success({"user": res.user, "profile": profile})
                else:
                    error_text.value = "Erro ao criar conta. Tente outro e-mail."
        except Exception as ex:
            error_text.value = f"Erro: {str(ex)[:60]}"
        set_loading(False)

    action_btn.on_click = do_action

    def toggle_mode(e):
        is_login[0] = not is_login[0]
        if is_login[0]:
            btn_text.value = "ENTRAR"
            toggle_text.value = "Não tem conta? "
            toggle_link.text = "Criar conta"
            username_field.visible = False
        else:
            btn_text.value = "CRIAR CONTA"
            toggle_text.value = "Já tem conta? "
            toggle_link.text = "Fazer login"
            username_field.visible = True
        error_text.value = ""
        page.update()

    toggle_link.on_click = toggle_mode

    content = ft.Column(
        [
            ft.Container(height=60),
            ft.Row(
                [
                    ft.Icon(ft.icons.BOLT, color=GOLD, size=36),
                    title_label,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
            ),
            ft.Container(height=4),
            subtitle,
            ft.Container(height=36),
            ft.Container(
                content=ft.Column(
                    [
                        username_field,
                        email_field,
                        password_field,
                        ft.Container(height=4),
                        error_text,
                        ft.Container(height=4),
                        action_btn,
                        ft.Container(height=8),
                        ft.Row(
                            [toggle_text, toggle_link],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=SURFACE,
                border_radius=24,
                padding=ft.padding.symmetric(horizontal=24, vertical=28),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    return ft.View(
        "/login",
        [ft.Container(content=content, bgcolor=BG, expand=True, padding=20)],
        bgcolor=BG,
        padding=0,
    )
