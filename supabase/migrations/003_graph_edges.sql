-- Create table for storing supply-chain graph edges
CREATE TABLE IF NOT EXISTS public.graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    relation TEXT NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(source, target, relation)
);

-- Index for fast lookup by source or target
CREATE INDEX IF NOT EXISTS idx_graph_edges_source ON public.graph_edges (source);
CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON public.graph_edges (target);

-- Enable RLS and allow broad access for the application
-- NOTE: CREATE POLICY has no IF NOT EXISTS, so drop first to keep this re-runnable
ALTER TABLE public.graph_edges ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow anonymous read graph_edges" ON public.graph_edges;
CREATE POLICY "Allow anonymous read graph_edges" ON public.graph_edges FOR SELECT USING (true);
DROP POLICY IF EXISTS "Allow all operations graph_edges" ON public.graph_edges;
CREATE POLICY "Allow all operations graph_edges" ON public.graph_edges FOR ALL USING (true) WITH CHECK (true);
