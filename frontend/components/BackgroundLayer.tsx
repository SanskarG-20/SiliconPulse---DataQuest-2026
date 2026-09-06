import React from 'react';

export const BackgroundLayer: React.FC = () => {
    return (
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none bg-white dark:bg-[#050B1A]">
            {/* Theme-aware depth wash (light: paper glow / dark: void vignette) */}
            <div className="absolute inset-0 scene-vignette" />

            {/* Grid Overlay — uses --grid so it re-tints per theme */}
            <div
                className="absolute inset-0 opacity-[0.9] blueprint-grid dark:opacity-[0.9]"
                style={{ maskImage: 'radial-gradient(ellipse at center, black 60%, transparent 85%)' }}
            />
            <div className="absolute inset-0 opacity-[0.4] blueprint-grid-fine" />

            {/* Reticle corners - signature */}
            <div className="absolute top-6 left-6 w-12 h-12 border-l border-t scene-reticle opacity-60 hidden lg:block" />
            <div className="absolute top-6 right-6 w-12 h-12 border-r border-t scene-reticle opacity-60 hidden lg:block" />
            <div className="absolute bottom-6 left-6 w-12 h-12 border-l border-b scene-reticle opacity-60 hidden lg:block" />
            <div className="absolute bottom-6 right-6 w-12 h-12 border-r border-b scene-reticle opacity-60 hidden lg:block" />

            {/* Subtle wafer ring */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] rounded-full border scene-ring hidden xl:block" style={{ maskImage: 'radial-gradient(circle, black 55%, transparent 70%)' }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] h-[720px] rounded-full border border-dashed border-[#22D3EE]/10 hidden xl:block" />

            {/* Subtle Noise / Texture Overlay (Optional but adds 'cinematic' feel) */}
            <div
                className="absolute inset-0 opacity-[0.015] mix-blend-overlay dark:opacity-[0.015] dark:mix-blend-overlay"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
                }}
            />
        </div>
    );
};
