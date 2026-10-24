-- Supabase Migration: 001_app_schema.sql
-- Application schema for MathQuest: profiles, sessions, answers, mastery, badges.
-- Includes foreign keys, unique constraints, user_id indexes, Row Level Security (RLS) policies,
-- and an automated trigger to create a profile when a new user signs up in Supabase Auth.

-- ==============================================================================
-- 1. TABLE: profiles
-- Stores student user metadata, preferences, grade, and aggregate points/XP.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    grade INT DEFAULT 5 CHECK (grade IN (5, 6)),
    curriculum_board TEXT DEFAULT 'georgia',
    total_score INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Index on user_id for profiles
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);


-- ==============================================================================
-- 2. TABLE: sessions
-- Tracks completed and in-progress math practice rounds / quiz attempts.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    board TEXT NOT NULL DEFAULT 'georgia',
    grade INT NOT NULL CHECK (grade IN (5, 6)),
    topic TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'medium',
    score INT NOT NULL DEFAULT 0,
    streak INT NOT NULL DEFAULT 0,
    best_streak INT NOT NULL DEFAULT 0,
    total_questions INT NOT NULL DEFAULT 0,
    correct_count INT NOT NULL DEFAULT 0,
    accuracy_percent NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    completed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indexes on user_id and queries for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_topic ON public.sessions(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON public.sessions(created_at DESC);


-- ==============================================================================
-- 3. TABLE: answers
-- Records individual student question responses, correctness, and misconception diagnosis.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    grade INT NOT NULL CHECK (grade IN (5, 6)),
    tier TEXT NOT NULL,
    selected_option_id TEXT NOT NULL,
    correct_option_id TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points_earned INT NOT NULL DEFAULT 0,
    misconception_tag TEXT,
    explanation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Indexes on user_id and session for answers
CREATE INDEX IF NOT EXISTS idx_answers_user_id ON public.answers(user_id);
CREATE INDEX IF NOT EXISTS idx_answers_session_id ON public.answers(session_id);
CREATE INDEX IF NOT EXISTS idx_answers_user_topic ON public.answers(user_id, topic);


-- ==============================================================================
-- 4. TABLE: mastery
-- Tracks student mastery percentage (0-100) per curriculum domain topic.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    board TEXT NOT NULL DEFAULT 'georgia',
    topic TEXT NOT NULL,
    grade INT NOT NULL CHECK (grade IN (5, 6)),
    mastery_score NUMERIC(5, 2) NOT NULL DEFAULT 50.00 CHECK (mastery_score >= 0.0 AND mastery_score <= 100.0),
    total_attempted INT NOT NULL DEFAULT 0,
    total_correct INT NOT NULL DEFAULT 0,
    last_practiced_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_mastery_user_topic UNIQUE (user_id, board, topic, grade)
);

-- Indexes on user_id for mastery
CREATE INDEX IF NOT EXISTS idx_mastery_user_id ON public.mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_mastery_user_topic ON public.mastery(user_id, topic);


-- ==============================================================================
-- 5. TABLE: badges
-- Stores unlocked achievement badges per student user.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    badge_id TEXT NOT NULL,
    badge_name TEXT NOT NULL,
    badge_description TEXT,
    icon_emoji TEXT DEFAULT '🏆',
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT uq_badges_user_badge UNIQUE (user_id, badge_id)
);

-- Indexes on user_id for badges
CREATE INDEX IF NOT EXISTS idx_badges_user_id ON public.badges(user_id);
CREATE INDEX IF NOT EXISTS idx_badges_badge_id ON public.badges(badge_id);


-- ==============================================================================
-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- Enable RLS on all tables and restrict access so users can only manage their own data.
-- ==============================================================================

-- 6.1 profiles RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own profile"
    ON public.profiles FOR DELETE
    USING (auth.uid() = user_id);


-- 6.2 sessions RLS
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own sessions"
    ON public.sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions"
    ON public.sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions"
    ON public.sessions FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own sessions"
    ON public.sessions FOR DELETE
    USING (auth.uid() = user_id);


-- 6.3 answers RLS
ALTER TABLE public.answers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own answers"
    ON public.answers FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own answers"
    ON public.answers FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own answers"
    ON public.answers FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own answers"
    ON public.answers FOR DELETE
    USING (auth.uid() = user_id);


-- 6.4 mastery RLS
ALTER TABLE public.mastery ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own mastery"
    ON public.mastery FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own mastery"
    ON public.mastery FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own mastery"
    ON public.mastery FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own mastery"
    ON public.mastery FOR DELETE
    USING (auth.uid() = user_id);


-- 6.5 badges RLS
ALTER TABLE public.badges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own badges"
    ON public.badges FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own badges"
    ON public.badges FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own badges"
    ON public.badges FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own badges"
    ON public.badges FOR DELETE
    USING (auth.uid() = user_id);


-- ==============================================================================
-- 7. AUTOMATED TRIGGER: Create Profile On New Auth User
-- Automatically provisions a public.profiles record when a user registers.
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, user_id, email, display_name)
    VALUES (
        NEW.id,
        NEW.id,
        NEW.email,
        COALESCE(
            NEW.raw_user_meta_data->>'full_name',
            NEW.raw_user_meta_data->>'display_name',
            split_part(NEW.email, '@', 1),
            'Student'
        )
    )
    ON CONFLICT (id) DO UPDATE
    SET email = EXCLUDED.email,
        updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ==============================================================================
-- 8. HELPER TRIGGERS: Automated updated_at Timestamps
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tr_profiles_updated_at ON public.profiles;
CREATE TRIGGER tr_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS tr_sessions_updated_at ON public.sessions;
CREATE TRIGGER tr_sessions_updated_at
    BEFORE UPDATE ON public.sessions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS tr_mastery_updated_at ON public.mastery;
CREATE TRIGGER tr_mastery_updated_at
    BEFORE UPDATE ON public.mastery
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
