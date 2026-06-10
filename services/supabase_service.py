import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import math

load_dotenv()

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_ANON_KEY", "")
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar no arquivo .env")
        self.client: Client = create_client(url, key)
        self.current_user = None

    # ─── AUTH ────────────────────────────────────────────────────────────────

    def sign_up(self, email: str, password: str, username: str):
        res = self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}}
        })
        if res.user:
            self.current_user = res.user
        return res

    def sign_in(self, email: str, password: str):
        res = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            self.current_user = res.user
        return res

    def sign_out(self):
        self.client.auth.sign_out()
        self.current_user = None

    def get_user(self):
        return self.client.auth.get_user()

    # ─── PROFILE ─────────────────────────────────────────────────────────────

    def get_profile(self, user_id: str):
        res = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
        return res.data

    def update_profile(self, user_id: str, data: dict):
        self.client.table("profiles").update(data).eq("id", user_id).execute()

    # ─── TASKS ───────────────────────────────────────────────────────────────

    def get_tasks(self, user_id: str):
        res = (self.client.table("tasks")
               .select("*")
               .eq("user_id", user_id)
               .order("scheduled_at", desc=False)
               .execute())
        return res.data or []

    def create_task(self, user_id: str, title: str, description: str,
                    priority: str, scheduled_at: str, recurrence: str = "none"):
        xp_map = {"low": 10, "medium": 20, "high": 40, "epic": 80}
        coin_map = {"low": 2, "medium": 5, "high": 10, "epic": 20}
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "priority": priority,
            "scheduled_at": scheduled_at,
            "recurrence": recurrence,
            "xp_reward": xp_map.get(priority, 20),
            "coin_reward": coin_map.get(priority, 5),
        }
        res = self.client.table("tasks").insert(data).execute()
        return res.data[0] if res.data else None

    def complete_task(self, task_id: str, user_id: str):
        # Busca a tarefa
        task_res = self.client.table("tasks").select("*").eq("id", task_id).single().execute()
        task = task_res.data
        if not task:
            return None

        # Atualiza status da tarefa
        self.client.table("tasks").update({
            "status": "done",
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", task_id).execute()

        # Busca perfil
        profile = self.get_profile(user_id)
        xp_gain = task["xp_reward"]
        coin_gain = task["coin_reward"]
        new_xp = profile["xp"] + xp_gain
        new_coins = profile["coins"] + coin_gain
        new_total = profile["total_tasks_done"] + 1

        # Calcular nível
        new_level = profile["level"]
        xp_needed = profile["xp_to_next_level"]
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = math.floor(100 * (1.3 ** (new_level - 1)))

        # Calcular streak
        today = date.today()
        last_date = profile.get("last_activity_date")
        streak = profile["current_streak"]
        if last_date:
            last = date.fromisoformat(str(last_date))
            if last == today - timedelta(days=1):
                streak += 1
            elif last < today - timedelta(days=1):
                streak = 1
        else:
            streak = 1

        longest = max(profile["longest_streak"], streak)

        # Criar recompensa de tempo livre (5 min de Instagram)
        expires = datetime.utcnow() + timedelta(hours=24)
        self.client.table("rewards").insert({
            "user_id": user_id,
            "reward_type": "free_time",
            "minutes": 5,
            "expires_at": expires.isoformat()
        }).execute()

        # Atualizar perfil
        self.client.table("profiles").update({
            "xp": new_xp,
            "coins": new_coins,
            "level": new_level,
            "xp_to_next_level": xp_needed,
            "total_tasks_done": new_total,
            "current_streak": streak,
            "longest_streak": longest,
            "last_activity_date": today.isoformat()
        }).eq("id", user_id).execute()

        # Verificar badges
        self._check_badges(user_id, new_total, streak, new_level)

        return {
            "xp_gain": task["xp_reward"],
            "coin_gain": task["coin_reward"],
            "new_level": new_level,
            "leveled_up": new_level > profile["level"],
        }

    def delete_task(self, task_id: str):
        self.client.table("tasks").delete().eq("id", task_id).execute()

    def update_task_status(self, task_id: str, status: str):
        self.client.table("tasks").update({"status": status}).eq("id", task_id).execute()

    # ─── BADGES ──────────────────────────────────────────────────────────────

    def get_all_badges(self):
        res = self.client.table("badges").select("*").execute()
        return res.data or []

    def get_user_badges(self, user_id: str):
        res = (self.client.table("user_badges")
               .select("*, badges(*)")
               .eq("user_id", user_id)
               .execute())
        return res.data or []

    def _check_badges(self, user_id: str, tasks_done: int, streak: int, level: int):
        all_badges = self.get_all_badges()
        earned_res = self.client.table("user_badges").select("badge_id").eq("user_id", user_id).execute()
        earned_ids = {b["badge_id"] for b in (earned_res.data or [])}

        for badge in all_badges:
            if badge["id"] in earned_ids:
                continue
            ct = badge["condition_type"]
            cv = badge["condition_value"]
            unlocked = False
            if ct == "tasks_done" and tasks_done >= cv:
                unlocked = True
            elif ct == "streak" and streak >= cv:
                unlocked = True
            elif ct == "level" and level >= cv:
                unlocked = True

            if unlocked:
                self.client.table("user_badges").insert({
                    "user_id": user_id,
                    "badge_id": badge["id"]
                }).execute()
                # Bônus de XP pelo badge
                profile = self.get_profile(user_id)
                self.client.table("profiles").update({
                    "xp": profile["xp"] + badge["xp_bonus"],
                    "coins": profile["coins"] + 10,
                }).eq("id", user_id).execute()

    # ─── REWARDS ─────────────────────────────────────────────────────────────

    def get_available_rewards(self, user_id: str):
        now = datetime.utcnow().isoformat()
        res = (self.client.table("rewards")
               .select("*")
               .eq("user_id", user_id)
               .eq("used", False)
               .gte("expires_at", now)
               .execute())
        return res.data or []

    def use_reward(self, reward_id: str):
        self.client.table("rewards").update({"used": True}).eq("id", reward_id).execute()
