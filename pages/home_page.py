import flet as ft
from datetime import datetime, date, timedelta
from components.ui_components import (
    task_card, stat_chip, xp_bar,
    reward_toast, badge_dialog,
    BG, SURFACE, CARD, PURPLE, CYAN, GOLD, GREEN, RED, TEXT, SUBTEXT
)


def HomePage(page: ft.Page, supabase, on_logout):
    user_data = page.session.get("user")
    user = user_data["user"]
    profile_ref = [user_data.get("profile") or {}]
    tasks_ref = [supabase.get_tasks(user.id)]

    tasks_list  = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)
    profile_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
    rewards_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
    badges_col  = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)

    focus_visible = [False]
    focus_content = ft.Container(visible=False, expand=True, bgcolor=BG)

    # ── FOCUS MODE ────────────────────────────────────────────────────────────
    def open_focus(minutes):
        remaining = [minutes * 60]
        timer_text = ft.Text(
            f"{minutes:02d}:00",
            size=64,
            weight=ft.FontWeight.W_900,
            color=CYAN,
        )
        stop_btn = ft.ElevatedButton(
            "Encerrar Foco",
            style=ft.ButtonStyle(
                bgcolor=RED,
                color=BG,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            height=48,
        )

        import threading
        running = [True]

        def tick():
            import time
            while running[0] and remaining[0] > 0:
                time.sleep(1)
                remaining[0] -= 1
                m, s = divmod(remaining[0], 60)
                timer_text.value = f"{m:02d}:{s:02d}"
                try:
                    page.update()
                except Exception:
                    break
            if remaining[0] == 0 and running[0]:
                stop(None)

        def stop(e):
            running[0] = False
            focus_content.visible = False
            focus_visible[0] = False
            page.update()

        stop_btn.on_click = stop
        threading.Thread(target=tick, daemon=True).start()

        focus_content.content = ft.Column(
            [
                ft.Container(height=80),
                ft.Icon(ft.icons.BOLT, size=60, color=GOLD),
                ft.Text("MODO FOCO ATIVADO", size=18, color=PURPLE,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                timer_text,
                ft.Container(height=16),
                ft.Text(
                    "Instagram e TikTok bloqueados\nFoque na sua missao!",
                    color=SUBTEXT, size=14, text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text(
                        "Sem Instagram  Sem TikTok  Sem YouTube",
                        color=RED, size=13, text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor="#2a1a1a",
                    border_radius=10,
                    padding=10,
                ),
                ft.Container(height=30),
                stop_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        focus_content.visible = True
        focus_visible[0] = True
        page.update()

    # ── ADD TASK DIALOG ───────────────────────────────────────────────────────
    def open_add_task():
        title_f = ft.TextField(
            label="Titulo da missao",
            border_color=PURPLE,
            focused_border_color=CYAN,
            color=TEXT,
            bgcolor=CARD,
            border_radius=10,
        )
        desc_f = ft.TextField(
            label="Descricao (opcional)",
            border_color=PURPLE,
            focused_border_color=CYAN,
            color=TEXT,
            bgcolor=CARD,
            border_radius=10,
            multiline=True,
            max_lines=3,
        )
        priority_dd = ft.Dropdown(
            label="Dificuldade",
            options=[
                ft.dropdown.Option("low",    "Facil   (+10 XP)"),
                ft.dropdown.Option("medium", "Medio   (+20 XP)"),
                ft.dropdown.Option("high",   "Dificil (+40 XP)"),
                ft.dropdown.Option("epic",   "EPICO   (+80 XP)"),
            ],
            value="medium",
            border_color=PURPLE,
            focused_border_color=CYAN,
            color=TEXT,
            bgcolor=CARD,
            border_radius=10,
        )
        recurrence_dd = ft.Dropdown(
            label="Recorrencia",
            options=[
                ft.dropdown.Option("none",   "Sem recorrencia"),
                ft.dropdown.Option("daily",  "Diaria"),
                ft.dropdown.Option("weekly", "Semanal"),
            ],
            value="none",
            border_color=PURPLE,
            focused_border_color=CYAN,
            color=TEXT,
            bgcolor=CARD,
            border_radius=10,
        )

        now = datetime.now()
        sel_date = [now.date()]
        sel_time = [now.time()]
        datetime_label = ft.Text(
            f"Data: {now.strftime('%d/%m/%Y')}  Hora: {now.strftime('%H:%M')}",
            color=CYAN,
            size=13,
        )

        def on_date_change(e):
            if e.control.value:
                v = e.control.value
                sel_date[0] = v.date() if hasattr(v, "date") else v
                update_dt_label()

        def on_time_change(e):
            if e.control.value:
                sel_time[0] = e.control.value
                update_dt_label()

        def update_dt_label():
            d = sel_date[0]
            t = sel_time[0]
            try:
                datetime_label.value = f"Data: {d.strftime('%d/%m/%Y')}  Hora: {t.strftime('%H:%M')}"
            except Exception:
                pass
            page.update()

        date_picker = ft.DatePicker(on_change=on_date_change)
        time_picker = ft.TimePicker(on_change=on_time_change)
        page.overlay.extend([date_picker, time_picker])
        page.update()

        err = ft.Text("", color=RED, size=12)

        save_btn = ft.ElevatedButton(
            "CRIAR MISSAO",
            style=ft.ButtonStyle(
                bgcolor=PURPLE,
                color=BG,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            height=48,
        )

        def save_task(e):
            if not title_f.value.strip():
                err.value = "De um titulo para a missao!"
                page.update()
                return
            try:
                d = sel_date[0]
                t = sel_time[0]
                dt = datetime(d.year, d.month, d.day, t.hour, t.minute)
                iso = dt.isoformat()
            except Exception:
                iso = datetime.now().isoformat()

            task = supabase.create_task(
                user_id=user.id,
                title=title_f.value.strip(),
                description=desc_f.value.strip(),
                priority=priority_dd.value,
                scheduled_at=iso,
                recurrence=recurrence_dd.value,
            )
            if task:
                tasks_ref[0].insert(0, task)
                dlg.open = False
                refresh_tasks()
            else:
                err.value = "Erro ao criar. Tente novamente."
            page.update()

        save_btn.on_click = save_task

        def close_dlg():
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova Missao", color=GOLD, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=380,
                content=ft.Column(
                    [
                        title_f,
                        desc_f,
                        priority_dd,
                        recurrence_dd,
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Escolher Data",
                                    style=ft.ButtonStyle(
                                        color=CYAN,
                                        side=ft.BorderSide(1, CYAN),
                                    ),
                                    on_click=lambda e: date_picker.pick_date(),
                                ),
                                ft.OutlinedButton(
                                    "Escolher Hora",
                                    style=ft.ButtonStyle(
                                        color=PURPLE,
                                        side=ft.BorderSide(1, PURPLE),
                                    ),
                                    on_click=lambda e: time_picker.pick_time(),
                                ),
                            ],
                            spacing=10,
                        ),
                        datetime_label,
                        err,
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    style=ft.ButtonStyle(color=SUBTEXT),
                    on_click=lambda e: close_dlg(),
                ),
                save_btn,
            ],
            bgcolor=SURFACE,
            shape=ft.RoundedRectangleBorder(radius=20),
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # ── COMPLETE / DELETE TASK ────────────────────────────────────────────────
    def complete_task(task):
        result = supabase.complete_task(task["id"], user.id)
        if result:
            profile_ref[0] = supabase.get_profile(user.id)
            tasks_ref[0] = supabase.get_tasks(user.id)
            reward_toast(page, result["xp_gain"], result["coin_gain"], result["leveled_up"])
            refresh_tasks()
            refresh_profile()
            refresh_rewards()

    def delete_task(task_id):
        supabase.delete_task(task_id)
        tasks_ref[0] = [t for t in tasks_ref[0] if t["id"] != task_id]
        refresh_tasks()

    # ── REFRESH TASKS ─────────────────────────────────────────────────────────
    def refresh_tasks():
        tasks_list.controls.clear()
        pending = [t for t in tasks_ref[0] if t["status"] != "done"]
        done    = [t for t in tasks_ref[0] if t["status"] == "done"]

        if not tasks_ref[0]:
            tasks_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Nenhuma missao ainda!", color=SUBTEXT, size=16,
                                    text_align=ft.TextAlign.CENTER),
                            ft.Text("Toque em + para criar sua primeira missao",
                                    color=SUBTEXT, size=13, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=40,
                )
            )
        else:
            if pending:
                tasks_list.controls.append(
                    ft.Text("MISSOES ATIVAS", color=PURPLE, size=12,
                            weight=ft.FontWeight.BOLD)
                )
                tasks_list.controls.append(ft.Container(height=8))
                for t in pending:
                    tasks_list.controls.append(task_card(t, complete_task, delete_task))
            if done:
                tasks_list.controls.append(ft.Container(height=12))
                tasks_list.controls.append(
                    ft.Text("CONCLUIDAS", color=GREEN, size=12, weight=ft.FontWeight.BOLD)
                )
                tasks_list.controls.append(ft.Container(height=8))
                for t in done:
                    tasks_list.controls.append(task_card(t, complete_task, delete_task))
        page.update()

    # ── REFRESH PROFILE ───────────────────────────────────────────────────────
    def refresh_profile():
        p = profile_ref[0]
        profile_col.controls.clear()
        xp      = p.get("xp", 0)
        max_xp  = p.get("xp_to_next_level", 100)
        level   = p.get("level", 1)
        coins   = p.get("coins", 0)
        streak  = p.get("current_streak", 0)
        longest = p.get("longest_streak", 0)
        total   = p.get("total_tasks_done", 0)
        username = p.get("username", "Heroi")

        avatar_icons = ["🌱","⚡","🔥","💎","👑","🌟","🧠","⚔️","🏹","🐉"]
        av = avatar_icons[min(level - 1, len(avatar_icons) - 1)]

        profile_col.controls += [
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(av, size=56, text_align=ft.TextAlign.CENTER),
                        ft.Text(username, color=TEXT, size=20,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                        xp_bar(xp, max_xp, level),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                bgcolor=SURFACE,
                border_radius=20,
                padding=24,
            ),
            ft.Container(height=16),
            ft.Row(
                [
                    stat_chip("Moedas", coins, "Moedas", GOLD),
                    stat_chip("Streak", streak, "Streak", RED),
                    stat_chip("Feitas", total, "Feitas", GREEN),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("ESTATISTICAS", color=SUBTEXT, size=12,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        _stat_row("Maior streak", f"{longest} dias"),
                        _stat_row("Missoes completadas", str(total)),
                        _stat_row("Nivel atual", str(level)),
                    ],
                    spacing=10,
                ),
                bgcolor=SURFACE,
                border_radius=16,
                padding=20,
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                "Sair da conta",
                style=ft.ButtonStyle(
                    bgcolor=SURFACE,
                    color=RED,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    side=ft.BorderSide(1, RED),
                ),
                height=46,
                width=200,
                on_click=lambda e: on_logout(),
            ),
        ]
        page.update()

    def _stat_row(label, value):
        return ft.Row(
            [
                ft.Text(label, color=SUBTEXT, size=14),
                ft.Text(value, color=TEXT, size=14, weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    # ── REFRESH REWARDS ───────────────────────────────────────────────────────
    def refresh_rewards():
        rewards = supabase.get_available_rewards(user.id)
        rewards_col.controls.clear()
        rewards_col.controls += [
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("MODO FOCO", color=GOLD, size=16,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Ative um timer e bloqueie as distracoes",
                            color=SUBTEXT, size=13,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                _focus_btn("25 min", 25, PURPLE),
                                _focus_btn("50 min", 50, CYAN),
                                _focus_btn("90 min", 90, GOLD),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                bgcolor=SURFACE,
                border_radius=20,
                padding=24,
            ),
            ft.Container(height=20),
            ft.Text("RECOMPENSAS DISPONIVEIS", color=SUBTEXT, size=12,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
        ]

        if not rewards:
            rewards_col.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhuma recompensa ainda.\nComplete missoes para ganhar tempo livre!",
                        color=SUBTEXT, size=14, text_align=ft.TextAlign.CENTER,
                    ),
                    padding=30,
                )
            )
        else:
            for r in rewards:
                rewards_col.controls.append(_reward_card(r))
        page.update()

    def _focus_btn(label, minutes, color):
        return ft.ElevatedButton(
            label,
            style=ft.ButtonStyle(
                bgcolor=SURFACE,
                color=color,
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, color),
            ),
            height=40,
            on_click=lambda e, m=minutes: open_focus(m),
        )

    def _reward_card(r):
        def use_it(e):
            supabase.use_reward(r["id"])
            refresh_rewards()
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Voce ganhou {r['minutes']} min de tempo livre!",
                        color=BG, weight=ft.FontWeight.BOLD),
                bgcolor=GREEN,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

        try:
            exp = datetime.fromisoformat(r["expires_at"].replace("Z", "+00:00"))
            exp_str = exp.strftime("Expira %d/%m as %H:%M")
        except Exception:
            exp_str = ""

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"{r['minutes']} min de tempo livre",
                                    color=TEXT, size=15, weight=ft.FontWeight.W_600),
                            ft.Text(exp_str, color=SUBTEXT, size=12),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        "Usar",
                        style=ft.ButtonStyle(
                            bgcolor=GREEN,
                            color=BG,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        height=36,
                        on_click=use_it,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=SURFACE,
            border_radius=14,
            padding=14,
            margin=ft.margin.only(bottom=10),
        )

    # ── REFRESH BADGES ────────────────────────────────────────────────────────
    def refresh_badges():
        all_badges  = supabase.get_all_badges()
        user_badges = supabase.get_user_badges(user.id)
        earned_ids  = {b["badge_id"] for b in user_badges}

        badges_col.controls.clear()
        badges_col.controls += [
            ft.Container(height=8),
            ft.Text(
                f"Conquistas: {len(earned_ids)}/{len(all_badges)}",
                color=GOLD, size=16, weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=12),
        ]

        rows = []
        row = []
        for b in all_badges:
            earned = b["id"] in earned_ids
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(b["icon"], size=34, text_align=ft.TextAlign.CENTER),
                        ft.Text(
                            b["name"],
                            color=TEXT if earned else SUBTEXT,
                            size=12,
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            f"+{b['xp_bonus']} XP",
                            color=GOLD if earned else SUBTEXT,
                            size=11,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                bgcolor=SURFACE if earned else "#1a1a2e",
                border_radius=14,
                padding=12,
                width=100,
                border=ft.border.all(1, GOLD if earned else CARD),
                opacity=1.0 if earned else 0.4,
                tooltip=b["description"],
            )
            row.append(card)
            if len(row) == 3:
                rows.append(ft.Row(row, spacing=10, alignment=ft.MainAxisAlignment.CENTER))
                row = []
        if row:
            rows.append(ft.Row(row, spacing=10, alignment=ft.MainAxisAlignment.CENTER))

        badges_col.controls += rows
        page.update()

    # ── INITIAL LOAD ──────────────────────────────────────────────────────────
    refresh_tasks()
    refresh_profile()
    refresh_rewards()
    refresh_badges()

    # ── TAB CONTENT ───────────────────────────────────────────────────────────
    def build_tab(index):
        if index == 0:
            return ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("MISSOES", color=TEXT, size=20,
                                        weight=ft.FontWeight.W_900),
                                ft.IconButton(
                                    icon=ft.icons.ADD_CIRCLE,
                                    icon_color=GOLD,
                                    icon_size=30,
                                    tooltip="Nova missao",
                                    on_click=lambda e: open_add_task(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    ),
                    ft.Container(
                        content=tasks_list,
                        padding=ft.padding.symmetric(horizontal=16),
                        expand=True,
                    ),
                ],
                expand=True,
            )
        elif index == 1:
            return ft.Container(
                content=rewards_col,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                expand=True,
            )
        elif index == 2:
            return ft.Container(
                content=badges_col,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                expand=True,
            )
        elif index == 3:
            return ft.Container(
                content=profile_col,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                expand=True,
            )

    current_tab = [0]
    content_area = ft.Container(expand=True, content=build_tab(0))

    def on_nav_change(e):
        current_tab[0] = e.control.selected_index
        content_area.content = build_tab(current_tab[0])
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.icons.BOLT_OUTLINED,
                selected_icon=ft.icons.BOLT,
                label="Missoes",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.TIMER_OUTLINED,
                selected_icon=ft.icons.TIMER,
                label="Foco",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.EMOJI_EVENTS_OUTLINED,
                selected_icon=ft.icons.EMOJI_EVENTS,
                label="Badges",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.PERSON_OUTLINE,
                selected_icon=ft.icons.PERSON,
                label="Perfil",
            ),
        ],
        bgcolor=SURFACE,
        selected_index=0,
        on_change=on_nav_change,
        height=70,
    )

    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("FocusQuest", color=PURPLE, size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Text("Streak: ", color=SUBTEXT, size=13),
                        ft.Text(
                            str(profile_ref[0].get("current_streak", 0)),
                            color=GOLD, size=14, weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(width=12),
                        ft.Text("Nivel: ", color=SUBTEXT, size=13),
                        ft.Text(
                            str(profile_ref[0].get("level", 1)),
                            color=CYAN, size=14, weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=SURFACE,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
    )

    main_stack = ft.Stack(
        [
            ft.Column(
                [header, content_area, nav_bar],
                spacing=0,
                expand=True,
            ),
            focus_content,
        ],
    )

    return ft.View(
        "/home",
        [ft.Container(content=main_stack, bgcolor=BG, expand=True)],
        bgcolor=BG,
        padding=0,
    )
