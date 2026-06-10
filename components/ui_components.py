import flet as ft

BG      = "#0D0D1A"
SURFACE = "#16162A"
CARD    = "#1E1E35"
PURPLE  = "#7C3AED"
CYAN    = "#06B6D4"
GOLD    = "#F59E0B"
GREEN   = "#10B981"
RED     = "#F87171"
TEXT    = "#E2E8F0"
SUBTEXT = "#94A3B8"

PRIORITY_CONFIG = {
    "low":    {"label": "Fácil",   "color": GREEN,  "icon": "🟢", "xp": 10,  "coins": 2},
    "medium": {"label": "Médio",   "color": CYAN,   "icon": "🔵", "xp": 20,  "coins": 5},
    "high":   {"label": "Difícil", "color": PURPLE, "icon": "🟣", "xp": 40,  "coins": 10},
    "epic":   {"label": "ÉPICO",   "color": GOLD,   "icon": "⭐", "xp": 80,  "coins": 20},
}


def xp_bar(current_xp: int, max_xp: int, level: int):
    pct = min(current_xp / max(max_xp, 1), 1.0)
    return ft.Column([
        ft.Row([
            ft.Text(f"Nível {level}", color=GOLD, size=13, weight=ft.FontWeight.BOLD),
            ft.Text(f"{current_xp}/{max_xp} XP", color=SUBTEXT, size=12),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(
            content=ft.Container(
                bgcolor=PURPLE,
                border_radius=4,
                height=8,
                expand=pct,
            ),
            bgcolor=CARD,
            border_radius=4,
            height=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        ),
    ], spacing=4)


def stat_chip(icon: str, value, label: str, color: str = CYAN):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(icon, size=16),
                ft.Text(str(value), color=color, size=16, weight=ft.FontWeight.BOLD),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(label, color=SUBTEXT, size=11),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=CARD,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
    )


def task_card(task: dict, on_complete, on_delete):
    priority = task.get("priority", "medium")
    cfg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["medium"])
    status = task.get("status", "pending")
    done = status == "done"

    # Formatar horário
    sched = task.get("scheduled_at", "")
    time_str = ""
    if sched:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(sched.replace("Z", "+00:00"))
            time_str = dt.strftime("%d/%m %H:%M")
        except:
            time_str = sched[:16]

    title_style = ft.TextStyle(
        decoration=ft.TextDecoration.LINE_THROUGH if done else None,
        color=SUBTEXT if done else TEXT,
    )

    complete_btn = ft.IconButton(
        icon=ft.icons.CHECK_CIRCLE if done else ft.icons.RADIO_BUTTON_UNCHECKED,
        icon_color=GREEN if done else cfg["color"],
        icon_size=26,
        tooltip="Completar missão",
        disabled=done,
        on_click=lambda e: on_complete(task),
    )

    delete_btn = ft.IconButton(
        icon=ft.icons.DELETE_OUTLINE,
        icon_color=RED,
        icon_size=20,
        tooltip="Deletar",
        on_click=lambda e: on_delete(task["id"]),
    )

    left_bar = ft.Container(
        width=4,
        bgcolor=cfg["color"] if not done else SUBTEXT,
        border_radius=ft.border_radius.only(top_left=12, bottom_left=12),
    )

    body = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(cfg["icon"] + " " + cfg["label"],
                        color=cfg["color"], size=11, weight=ft.FontWeight.BOLD),
                ft.Text(f"+{cfg['xp']} XP  +{cfg['coins']}🪙",
                        color=GOLD, size=11),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(task["title"], style=title_style, size=15, weight=ft.FontWeight.W_600,
                    max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Row([
                ft.Icon(ft.icons.ACCESS_TIME, size=13, color=SUBTEXT),
                ft.Text(time_str, color=SUBTEXT, size=12),
            ], spacing=4) if time_str else ft.Container(height=0),
        ], spacing=4),
        expand=True,
        padding=ft.padding.symmetric(vertical=10, horizontal=8),
    )

    return ft.Container(
        content=ft.Row([
            left_bar,
            complete_btn,
            body,
            delete_btn,
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=SURFACE if not done else ft.colors.with_opacity(0.5, SURFACE),
        border_radius=12,
        margin=ft.margin.only(bottom=10),
        shadow=ft.BoxShadow(
            blur_radius=10, color=ft.colors.with_opacity(0.2, "#000000"), offset=ft.Offset(0, 3)
        ),
    )


def reward_toast(page: ft.Page, xp: int, coins: int, leveled_up: bool):
    msg = f"🎉 +{xp} XP  +{coins}🪙"
    if leveled_up:
        msg = "🌟 LEVEL UP! " + msg

    snack = ft.SnackBar(
        content=ft.Text(msg, color=BG, weight=ft.FontWeight.BOLD, size=15),
        bgcolor=GOLD if leveled_up else GREEN,
        duration=3000,
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()


def badge_dialog(page: ft.Page, badge_name: str, badge_icon: str):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("🏆 Conquista Desbloqueada!", text_align=ft.TextAlign.CENTER,
                       color=GOLD, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            ft.Text(badge_icon, size=52, text_align=ft.TextAlign.CENTER),
            ft.Text(badge_name, color=TEXT, size=18, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        actions=[ft.TextButton("Incrível!", on_click=lambda e: close_dlg())],
        bgcolor=SURFACE,
        shape=ft.RoundedRectangleBorder(radius=20),
    )

    def close_dlg():
        dlg.open = False
        page.update()

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
