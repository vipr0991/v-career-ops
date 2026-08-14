-- 0002_rls.sql — single-user RLS. Replace the literal below with the owner's
-- auth.users UUID after `supabase start` / cloud project creation.
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE unique_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY owner_all_evaluations ON evaluations
  FOR ALL TO authenticated
  USING (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid)
  WITH CHECK (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY owner_all_scan_history ON scan_history
  FOR ALL TO authenticated
  USING (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid)
  WITH CHECK (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY owner_all_unique_roles ON unique_roles
  FOR ALL TO authenticated
  USING (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid)
  WITH CHECK (auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid);
