
-- Drop existing tables and policies if they exist

-- Drop policies
DROP POLICY IF EXISTS "Authenticated users can read their own profile data" ON auth.users;
DROP POLICY IF EXISTS "Authenticated users can update their own profile data" ON auth.users;
DROP POLICY IF EXISTS "Service role can update any user data" ON auth.users;

DROP POLICY IF EXISTS "Authenticated users can read their own organization data" ON public.organizations;
DROP POLICY IF EXISTS "Authenticated users can insert their own organization data" ON public.organizations;

DROP POLICY IF EXISTS "Authenticated users can read their own validated subscriptions" ON public.validated_subscriptions;
DROP POLICY IF EXISTS "Authenticated users can insert their own validated subscriptions" ON public.validated_subscriptions;
DROP POLICY IF EXISTS "Service role can update any validated subscriptions" ON public.validated_subscriptions;

DROP POLICY IF EXISTS "Authenticated users can read their own uploaded files" ON public.uploaded_files;
DROP POLICY IF EXISTS "Authenticated users can insert their own uploaded files" ON public.uploaded_files;

DROP POLICY IF EXISTS "Authenticated users can read their own enriched data" ON public.enriched_data;
DROP POLICY IF EXISTS "Authenticated users can insert their own enriched data" ON public.enriched_data;

DROP POLICY IF EXISTS "Service role can update any enriched data" ON public.enriched_data;

DROP POLICY IF EXISTS "Service role can insert logs" ON public.app_logs;
DROP POLICY IF EXISTS "Service role can read logs" ON public.app_logs;

-- Drop tables
DROP TABLE IF EXISTS public.profiles CASCADE;
DROP TABLE IF EXISTS public.organizations CASCADE;
DROP TABLE IF EXISTS public.validated_subscriptions CASCADE;
DROP TABLE IF EXISTS public.uploaded_files CASCADE;
DROP TABLE IF EXISTS public.enriched_data CASCADE;
DROP TABLE IF EXISTS public.app_logs CASCADE;

-- Create the tables

CREATE TABLE public.profiles (
  id uuid NOT NULL,
  updated_at timestamp with time zone NULL,
  username text NULL,
  full_name text NULL,
  avatar_url text NULL,
  website text NULL,
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_username_key UNIQUE (username),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE,
  CONSTRAINT username_length CHECK ((char_length(username) >= 3))
);

CREATE TABLE public.organizations (
  id serial NOT NULL,
  name text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  admin_user_id uuid NULL,
  CONSTRAINT organizations_pkey PRIMARY KEY (id),
  CONSTRAINT organizations_name_key UNIQUE (name),
  CONSTRAINT organizations_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.validated_subscriptions (
  id serial NOT NULL,
  user_id uuid NULL,
  merchant text NOT NULL,
  description text NULL,
  amount numeric NOT NULL,
  category text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT validated_subscriptions_pkey PRIMARY KEY (id),
  CONSTRAINT validated_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.uploaded_files (
  id serial NOT NULL,
  organization_id integer NULL,
  user_id uuid NULL,
  file_name text NOT NULL,
  data jsonb NOT NULL,
  uploaded_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT uploaded_files_pkey PRIMARY KEY (id),
  CONSTRAINT uploaded_files_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id),
  CONSTRAINT uploaded_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.enriched_data (
  id serial NOT NULL,
  user_id uuid NULL,
  file_name text NOT NULL,
  data jsonb NOT NULL,
  uploaded_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT enriched_data_pkey PRIMARY KEY (id),
  CONSTRAINT enriched_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.app_logs (
  id serial NOT NULL,
  action text NOT NULL,
  user_id uuid NULL,
  organization_id integer NULL,
  details jsonb NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT app_logs_pkey PRIMARY KEY (id),
  CONSTRAINT app_logs_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id),
  CONSTRAINT app_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_validated_subscriptions_user_id 
ON public.validated_subscriptions (user_id);

CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id 
ON public.uploaded_files (user_id);

CREATE INDEX IF NOT EXISTS idx_enriched_data_user_id 
ON public.enriched_data (user_id);

CREATE INDEX IF NOT EXISTS idx_organizations_admin_user_id 
ON public.organizations (admin_user_id);

-- Create the policies

-- Allow authenticated users to read their own profile data
CREATE POLICY "Authenticated users can read their own profile data" 
ON auth.users 
FOR SELECT 
USING (auth.uid() = id);

-- Allow authenticated users to update their own profile data
CREATE POLICY "Authenticated users can update their own profile data" 
ON auth.users 
FOR UPDATE 
USING (auth.uid() = id);

-- Allow service role to update any user data
CREATE POLICY "Service role can update any user data" 
ON auth.users 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own organization data
CREATE POLICY "Authenticated users can read their own organization data" 
ON public.organizations 
FOR SELECT 
USING (auth.uid() = admin_user_id);

-- Allow authenticated users to insert organization data
CREATE POLICY "Authenticated users can insert their own organization data" 
ON public.organizations 
FOR INSERT 
WITH CHECK (auth.uid() = admin_user_id);

-- Allow authenticated users to read their own validated subscriptions
CREATE POLICY "Authenticated users can read their own validated subscriptions" 
ON public.validated_subscriptions 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert validated subscriptions
CREATE POLICY "Authenticated users can insert their own validated subscriptions" 
ON public.validated_subscriptions 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any validated subscriptions
CREATE POLICY "Service role can update any validated subscriptions" 
ON public.validated_subscriptions 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own uploaded files
CREATE POLICY "Authenticated users can read their own uploaded files" 
ON public.uploaded_files 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert uploaded files
CREATE POLICY "Authenticated users can insert their own uploaded files" 
ON public.uploaded_files 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any uploaded files
CREATE POLICY "Service role can update any uploaded files" 
ON public.uploaded_files 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own enriched data
CREATE POLICY "Authenticated users can read their own enriched data" 
ON public.enriched_data 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert enriched data
CREATE POLICY "Authenticated users can insert their own enriched data" 
ON public.enriched_data 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any enriched data
CREATE POLICY "Service role can update any enriched data" 
ON public.enriched_data 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow service role to insert logs
CREATE POLICY "Service role can insert logs" 
ON public.app_logs 
FOR INSERT 
WITH CHECK (auth.role() = 'service_role');

-- Allow service role to read logs
CREATE POLICY "Service role can read logs" 
ON public.app_logs 
FOR SELECT 
USING (auth.role() = 'service_role');

-- Create the tables

CREATE TABLE public.profiles (
  id uuid NOT NULL,
  updated_at timestamp with time zone NULL,
  username text NULL,
  full_name text NULL,
  avatar_url text NULL,
  website text NULL,
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_username_key UNIQUE (username),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE,
  CONSTRAINT username_length CHECK ((char_length(username) >= 3))
);

CREATE TABLE public.organizations (
  id serial NOT NULL,
  name text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  admin_user_id uuid NULL,
  CONSTRAINT organizations_pkey PRIMARY KEY (id),
  CONSTRAINT organizations_name_key UNIQUE (name),
  CONSTRAINT organizations_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.validated_subscriptions (
  id serial NOT NULL,
  user_id uuid NULL,
  merchant text NOT NULL,
  description text NULL,
  amount numeric NOT NULL,
  category text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT validated_subscriptions_pkey PRIMARY KEY (id),
  CONSTRAINT validated_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.uploaded_files (
  id serial NOT NULL,
  organization_id integer NULL,
  user_id uuid NULL,
  file_name text NOT NULL,
  data jsonb NOT NULL,
  uploaded_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT uploaded_files_pkey PRIMARY KEY (id),
  CONSTRAINT uploaded_files_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id),
  CONSTRAINT uploaded_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.enriched_data (
  id serial NOT NULL,
  user_id uuid NULL,
  file_name text NOT NULL,
  data jsonb NOT NULL,
  uploaded_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT enriched_data_pkey PRIMARY KEY (id),
  CONSTRAINT enriched_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

CREATE TABLE public.app_logs (
  id serial NOT NULL,
  action text NOT NULL,
  user_id uuid NULL,
  organization_id integer NULL,
  details jsonb NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT app_logs_pkey PRIMARY KEY (id),
  CONSTRAINT app_logs_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id),
  CONSTRAINT app_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_validated_subscriptions_user_id 
ON public.validated_subscriptions (user_id);

CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id 
ON public.uploaded_files (user_id);

CREATE INDEX IF NOT EXISTS idx_enriched_data_user_id 
ON public.enriched_data (user_id);

CREATE INDEX IF NOT EXISTS idx_organizations_admin_user_id 
ON public.organizations (admin_user_id);

-- Create the policies

-- Allow authenticated users to read their own profile data
CREATE POLICY "Authenticated users can read their own profile data" 
ON auth.users 
FOR SELECT 
USING (auth.uid() = id);

-- Allow authenticated users to update their own profile data
CREATE POLICY "Authenticated users can update their own profile data" 
ON auth.users 
FOR UPDATE 
USING (auth.uid() = id);

-- Allow service role to update any user data
CREATE POLICY "Service role can update any user data" 
ON auth.users 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own organization data
CREATE POLICY "Authenticated users can read their own organization data" 
ON public.organizations 
FOR SELECT 
USING (auth.uid() = admin_user_id);

-- Allow authenticated users to insert organization data
CREATE POLICY "Authenticated users can insert their own organization data" 
ON public.organizations 
FOR INSERT 
WITH CHECK (auth.uid() = admin_user_id);

-- Allow authenticated users to read their own validated subscriptions
CREATE POLICY "Authenticated users can read their own validated subscriptions" 
ON public.validated_subscriptions 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert validated subscriptions
CREATE POLICY "Authenticated users can insert their own validated subscriptions" 
ON public.validated_subscriptions 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any validated subscriptions
CREATE POLICY "Service role can update any validated subscriptions" 
ON public.validated_subscriptions 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own uploaded files
CREATE POLICY "Authenticated users can read their own uploaded files" 
ON public.uploaded_files 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert uploaded files
CREATE POLICY "Authenticated users can insert their own uploaded files" 
ON public.uploaded_files 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any uploaded files
CREATE POLICY "Service role can update any uploaded files" 
ON public.uploaded_files 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow authenticated users to read their own enriched data
CREATE POLICY "Authenticated users can read their own enriched data" 
ON public.enriched_data 
FOR SELECT 
USING (auth.uid() = user_id);

-- Allow authenticated users to insert enriched data
CREATE POLICY "Authenticated users can insert their own enriched data" 
ON public.enriched_data 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Allow service role to update any enriched data
CREATE POLICY "Service role can update any enriched data" 
ON public.enriched_data 
FOR UPDATE 
USING (auth.role() = 'service_role');

-- Allow service role to insert logs
CREATE POLICY "Service role can insert logs" 
ON public.app_logs 
FOR INSERT 
WITH CHECK (auth.role() = 'service_role');

-- Allow service role to read logs
CREATE POLICY "Service role can read logs" 
ON public.app_logs 
FOR SELECT 
USING (auth.role() = 'service_role');

-- Drop existing policies on auth.users
drop policy if exists "Allow authenticated users to read their own data" on auth.users;
drop policy if exists "Allow authenticated users to update their own data" on auth.users;
drop policy if exists "Allow service role to update any user data" on auth.users;

-- Drop existing policies on public.organizations
drop policy if exists "Allow authenticated users to read their own organization data" on public.organizations;
drop policy if exists "Allow authenticated users to insert organization data" on public.organizations;
drop policy if exists "Allow service role to update any organization data" on public.organizations;

-- Drop existing policies on public.validated_subscriptions
drop policy if exists "Allow authenticated users to read their own validated subscriptions" on public.validated_subscriptions;
drop policy if exists "Allow authenticated users to insert validated subscriptions" on public.validated_subscriptions;
drop policy if exists "Allow service role to update any validated subscriptions" on public.validated_subscriptions;

-- Drop existing policies on public.uploaded_files
drop policy if exists "Allow authenticated users to read their own uploaded files" on public.uploaded_files;
drop policy if exists "Allow authenticated users to insert uploaded files" on public.uploaded_files;
drop policy if exists "Allow service role to update any uploaded files" on public.uploaded_files;

-- Drop existing policies on public.enriched_data
drop policy if exists "Allow authenticated users to read their own enriched data" on public.enriched_data;
drop policy if exists "Allow authenticated users to insert enriched data" on public.enriched_data;
drop policy if exists "Allow service role to update any enriched data" on public.enriched_data;

-- Drop existing policies on public.app_logs
drop policy if exists "Allow service role to insert logs" on public.app_logs;
drop policy if exists "Allow service role to read logs" on public.app_logs;

-- Recreate policies on auth.users
create policy "Allow authenticated users to read their own data"
on auth.users
for select
using (auth.uid() = id);

create policy "Allow authenticated users to update their own data"
on auth.users
for update
using (auth.uid() = id);

create policy "Allow service role to update any user data"
on auth.users
for update
using (auth.role() = 'service_role');

-- Recreate policies on public.organizations
create policy "Allow authenticated users to read their own organization data"
on public.organizations
for select
using (auth.uid() = admin_user_id);

create policy "Allow authenticated users to insert organization data"
on public.organizations
for insert
with check (auth.uid() = admin_user_id);

create policy "Allow service role to update any organization data"
on public.organizations
for update
using (auth.role() = 'service_role');

-- Recreate policies on public.validated_subscriptions
create policy "Allow authenticated users to read their own validated subscriptions"
on public.validated_subscriptions
for select
using (auth.uid() = user_id);

create policy "Allow authenticated users to insert validated subscriptions"
on public.validated_subscriptions
for insert
with check (auth.uid() = user_id);

create policy "Allow service role to update any validated subscriptions"
on public.validated_subscriptions
for update
using (auth.role() = 'service_role');

-- Recreate policies on public.uploaded_files
create policy "Allow authenticated users to read their own uploaded files"
on public.uploaded_files
for select
using (auth.uid() = user_id);

create policy "Allow authenticated users to insert uploaded files"
on public.uploaded_files
for insert
with check (auth.uid() = user_id);

create policy "Allow service role to update any uploaded files"
on public.uploaded_files
for update
using (auth.role() = 'service_role');

-- Recreate policies on public.enriched_data
create policy "Allow authenticated users to read their own enriched data"
on public.enriched_data
for select
using (auth.uid() = user_id);

create policy "Allow authenticated users to insert enriched data"
on public.enriched_data
for insert
with check (auth.uid() = user_id);

create policy "Allow service role to update any enriched data"
on public.enriched_data
for update
using (auth.role() = 'service_role');

-- Recreate policies on public.app_logs
create policy "Allow service role to insert logs"
on public.app_logs
for insert
with check (auth.role() = 'service_role');

create policy "Allow service role to read logs"
on public.app_logs
for select
using (auth.role() = 'service_role');

-- Allow authenticated users to read organizations
CREATE POLICY "Allow authenticated users to read organizations"
ON public.organizations
FOR SELECT
TO authenticated
USING (true);

-- Allow service role to perform any action
CREATE POLICY "Allow service role to perform any action"
ON public.organizations
FOR ALL
TO service_role
USING (true);

-- Allow anon users to read organizations (if needed)
CREATE POLICY "Allow anon users to read organizations"
ON public.organizations
FOR SELECT
TO anon
USING (true);