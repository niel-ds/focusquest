-- =============================================
-- FOCUSQUEST - Schema do Banco de Dados
-- Execute este SQL no Supabase SQL Editor
-- =============================================

-- Tabela de perfis de usuário (estende auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    avatar_url TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    xp_to_next_level INTEGER DEFAULT 100,
    coins INTEGER DEFAULT 0,
    total_tasks_done INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de tarefas
CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'epic')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'done', 'failed')),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    xp_reward INTEGER DEFAULT 20,
    coin_reward INTEGER DEFAULT 5,
    recurrence TEXT DEFAULT 'none' CHECK (recurrence IN ('none', 'daily', 'weekly')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de badges/conquistas
CREATE TABLE IF NOT EXISTS public.badges (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT NOT NULL,
    condition_type TEXT NOT NULL,
    condition_value INTEGER NOT NULL,
    xp_bonus INTEGER DEFAULT 50
);

-- Tabela de badges conquistados pelo usuário
CREATE TABLE IF NOT EXISTS public.user_badges (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    badge_id UUID REFERENCES public.badges(id) ON DELETE CASCADE NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- Tabela de recompensas de tempo (ex: 5min de Instagram)
CREATE TABLE IF NOT EXISTS public.rewards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    reward_type TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ,
    earned_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Inserir badges padrão
-- =============================================
INSERT INTO public.badges (name, description, icon, condition_type, condition_value, xp_bonus) VALUES
('Iniciante', 'Complete sua primeira tarefa', '⚡', 'tasks_done', 1, 50),
('Guerreiro', 'Complete 10 tarefas', '⚔️', 'tasks_done', 10, 100),
('Lendário', 'Complete 50 tarefas', '👑', 'tasks_done', 50, 300),
('Inabalável', 'Mantenha um streak de 7 dias', '🔥', 'streak', 7, 150),
('Mestre do Foco', 'Mantenha um streak de 30 dias', '🧠', 'streak', 30, 500),
('Nível 5', 'Alcance o nível 5', '🌟', 'level', 5, 100),
('Nível 10', 'Alcance o nível 10', '💎', 'level', 10, 250)
ON CONFLICT DO NOTHING;

-- =============================================
-- Row Level Security (RLS)
-- =============================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rewards ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso
CREATE POLICY "Usuários veem só seu perfil" ON public.profiles FOR ALL USING (auth.uid() = id);
CREATE POLICY "Usuários veem só suas tarefas" ON public.tasks FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Usuários veem só seus badges" ON public.user_badges FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Usuários veem só suas recompensas" ON public.rewards FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Badges são públicos para leitura" ON public.badges FOR SELECT USING (true);

-- =============================================
-- Função para criar perfil ao registrar
-- =============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username)
    VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
