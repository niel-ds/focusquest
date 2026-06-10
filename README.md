# ⚡ FocusQuest — App de Produtividade Gamificado

App mobile Android criado com **Python + Flet + Supabase**.  
Transforme suas metas em missões, ganhe XP, moedas e desbloqueie conquistas!

---

## 🗂️ Estrutura do Projeto

```
focus_quest/
├── main.py                        # Ponto de entrada
├── requirements.txt               # Dependências
├── schema.sql                     # SQL para configurar o Supabase
├── .env.example                   # Template das variáveis de ambiente
├── pages/
│   ├── login_page.py              # Tela de Login / Cadastro
│   └── home_page.py               # Tela principal (missões, foco, badges, perfil)
├── components/
│   └── ui_components.py           # Componentes reutilizáveis
└── services/
    └── supabase_service.py        # Toda a lógica com o banco de dados
```

---

## 🚀 Como Configurar

### 1. Configurar o Supabase

1. Acesse [supabase.com](https://supabase.com) e crie um projeto gratuito
2. No menu lateral, vá em **SQL Editor**
3. Cole o conteúdo de `schema.sql` e clique em **Run**
4. Vá em **Settings → API** e copie:
   - `Project URL`
   - `anon public` key

### 2. Criar o arquivo `.env`

```bash
cp .env.example .env
```

Edite o `.env` e preencha com suas credenciais:

```env
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_ANON_KEY=SUA_CHAVE_ANONIMA_AQUI
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar no computador (para testar)

```bash
python main.py
```

### 5. Gerar APK para Android

```bash
# Instalar o flet CLI (se ainda não tiver)
pip install flet

# Empacotar para Android
flet build apk
```

O APK ficará na pasta `build/apk/`.

---

## 🎮 Funcionalidades

### ⚡ Missões (Tarefas)
- Criar tarefas com **título, descrição, dificuldade e horário agendado**
- Dificuldades: 🟢 Fácil · 🔵 Médio · 🟣 Difícil · ⭐ Épico
- Recorrência: Sem · Diária · Semanal
- Completar tarefa ganha **XP + moedas + tempo livre**

### 🏆 Sistema de Recompensas
- **XP** → sobe de nível (com barra de progresso)
- **Moedas** → coletáveis por missão
- **Badges** → conquistas desbloqueadas por marcos
- **Tempo livre** → cada tarefa concluída gera 5 min de recompensa

### ⏱️ Modo Foco (Anti-distração)
- Timer Pomodoro: 25, 50 ou 90 minutos
- Tela de foco que toma conta do app com countdown
- Mensagem de bloqueio para Instagram / TikTok
- *(No Android, para bloqueio real de apps é necessário usar o Digital Wellbeing nativo do sistema)*

### 🏅 Badges disponíveis
| Badge | Condição |
|-------|----------|
| ⚡ Iniciante | 1 tarefa concluída |
| ⚔️ Guerreiro | 10 tarefas concluídas |
| 👑 Lendário | 50 tarefas concluídas |
| 🔥 Inabalável | Streak de 7 dias |
| 🧠 Mestre do Foco | Streak de 30 dias |
| 🌟 Nível 5 | Alcançar nível 5 |
| 💎 Nível 10 | Alcançar nível 10 |

---

## 🔧 Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| **Python 3.10+** | Linguagem principal |
| **Flet 0.24** | UI multiplataforma (Flutter via Python) |
| **Supabase** | Banco de dados, autenticação, RLS |
| **python-dotenv** | Variáveis de ambiente |

---

## 📱 Notas sobre o Bloqueio de Apps no Android

O Android **não permite** que apps de terceiros bloqueiem outros apps diretamente por razões de segurança. As alternativas nativas são:

1. **Digital Wellbeing** (Settings → Digital Wellbeing → App Timers)  
   → Configure limites diários para Instagram e TikTok manualmente

2. **Modo Foco nativo** (Android 9+)  
   → Ative o Focus Mode e adicione apps de distração

3. **O FocusQuest** implementa o bloqueio *dentro do app* via timer de foco com tela modal que ocupa o dispositivo enquanto o timer está ativo.

---

## 🧩 Possíveis Melhorias Futuras

- [ ] Notificações push (lembretes de tarefas agendadas)
- [ ] Modo offline com sincronização posterior
- [ ] Perfil com foto de avatar customizável
- [ ] Sistema de amigos e ranking de XP
- [ ] Sons e efeitos de vitória ao completar tarefa
- [ ] Widget na tela inicial do Android
