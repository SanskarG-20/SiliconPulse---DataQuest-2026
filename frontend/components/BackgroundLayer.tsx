import React from 'react';

export const BackgroundLayer: React.FC = () => {
    return (
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none bg-[#020617]">
            {/* Primary Radial Gradient for Depth */}
            <div
                className="absolute inset-0 opacity-40"
                style={{
                    background: 'radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%)'
                }}
            />

            {/* Grid Overlay */}
            <div
                className="absolute inset-0 opacity-[0.05]"
                style={{
                    backgroundImage: `linear-gradient(to right, #38bdf8 1px, transparent 1px), 
                            linear-gradient(to bottom, #38bdf8 1px, transparent 1px)`,
                    backgroundSize: '40px 40px'
                }}
            />

            {/* Cyan Glow Accents */}
            <div
                className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full opacity-15 blur-[120px]"
                style={{ background: '#0ea5e9' }}
            />
            <div
                className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full opacity-15 blur-[120px]"
                style={{ background: '#6366f1' }}
            />

            {/* Subtle Noise / Texture Overlay (Optional but adds 'cinematic' feel) */}
            <div
                className="absolute inset-0 opacity-[0.015] mix-blend-overlay"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3%3Ffilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
                }}
            />
        </div>
    );
};
