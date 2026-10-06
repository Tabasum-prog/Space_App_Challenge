'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Play, Pause, Maximize } from 'lucide-react';

interface InteractiveCanvasProps {
    fieldId: string;
    mode: 'blink' | 'swipe' | 'difference';
}

export default function InteractiveCanvas({ fieldId, mode }: InteractiveCanvasProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [zoom, setZoom] = useState(1);
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    
    // Swipe state
    const [swipeRatio, setSwipeRatio] = useState(0.5);
    
    // Blink state
    const [blinkOn, setBlinkOn] = useState(true);
    const [isPlaying, setIsPlaying] = useState(false);
    const [blinkSpeed, setBlinkSpeed] = useState(500); // ms
    
    // Images
    const [imgA, setImgA] = useState<HTMLImageElement | null>(null);
    const [imgB, setImgB] = useState<HTMLImageElement | null>(null);
    const [imgDiff, setImgDiff] = useState<HTMLImageElement | null>(null);
    
    useEffect(() => {
        const loadImg = (src: string) => {
            const img = new Image();
            img.src = src;
            return img;
        };
        
        // Load mock PNGs generated for viewing
        setImgA(loadImg(`/data/${fieldId}/pass1.png`));
        setImgB(loadImg(`/data/${fieldId}/pass2.png`));
        setImgDiff(loadImg(`/data/${fieldId}/diff.png`));
    }, [fieldId]);
    
    useEffect(() => {
        if (!isPlaying) return;
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        if (mediaQuery.matches) {
            setIsPlaying(false);
            return;
        }
        
        const interval = setInterval(() => {
            setBlinkOn(prev => !prev);
        }, blinkSpeed);
        return () => clearInterval(interval);
    }, [isPlaying, blinkSpeed]);

    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.save();
        ctx.translate(offset.x, offset.y);
        ctx.scale(zoom, zoom);
        
        const renderImg = (img: HTMLImageElement | null, clipWidth?: number) => {
            if (!img || !img.complete) return;
            if (clipWidth !== undefined) {
                ctx.save();
                ctx.beginPath();
                ctx.rect(0, 0, clipWidth, img.height);
                ctx.clip();
                ctx.drawImage(img, 0, 0);
                ctx.restore();
            } else {
                ctx.drawImage(img, 0, 0);
            }
        };
        
        if (mode === 'blink') {
            renderImg(blinkOn ? imgA : imgB);
        } else if (mode === 'swipe') {
            renderImg(imgB);
            if (imgA && imgA.complete) {
                renderImg(imgA, imgA.width * swipeRatio);
                ctx.fillStyle = '#ff0000';
                ctx.fillRect(imgA.width * swipeRatio - 2 / zoom, 0, 4 / zoom, imgA.height);
            }
        } else if (mode === 'difference') {
            renderImg(imgDiff);
        }
        
        ctx.restore();
    };

    useEffect(() => {
        let req: number;
        const loop = () => {
            draw();
            req = requestAnimationFrame(loop);
        };
        loop();
        return () => cancelAnimationFrame(req);
    });

    const handleWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.1 : 0.9;
        
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const newZoom = Math.min(Math.max(0.1, zoom * factor), 10);
        
        setOffset({
            x: mouseX - (mouseX - offset.x) * (newZoom / zoom),
            y: mouseY - (mouseY - offset.y) * (newZoom / zoom)
        });
        setZoom(newZoom);
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (isDragging) {
            setOffset({
                x: e.clientX - dragStart.x,
                y: e.clientY - dragStart.y
            });
        }
    };

    const handleMouseUp = () => setIsDragging(false);

    return (
        <div className="relative w-full h-[600px] bg-black rounded-lg overflow-hidden border border-gray-700 select-none">
            <canvas 
                ref={canvasRef} 
                width={800} 
                height={600} 
                className="w-full h-full cursor-grab active:cursor-grabbing touch-none"
                onWheel={handleWheel}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
            />
            
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-gray-900/80 backdrop-blur-md p-3 rounded-xl border border-gray-700 flex gap-4 items-center">
                <button onClick={() => { setZoom(1); setOffset({x:0, y:0}); }} className="p-2 bg-gray-800 rounded hover:bg-gray-700 text-gray-200">
                    <Maximize size={20} />
                </button>
                
                {mode === 'blink' && (
                    <>
                        <button onClick={() => setIsPlaying(!isPlaying)} className="p-2 bg-blue-600 rounded hover:bg-blue-500 text-white">
                            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                        </button>
                        <input type="range" min="100" max="1000" value={1100 - blinkSpeed} onChange={(e) => setBlinkSpeed(1100 - parseInt(e.target.value))} className="w-24 accent-blue-500" />
                    </>
                )}
                
                {mode === 'swipe' && (
                    <input type="range" min="0" max="100" value={swipeRatio * 100} onChange={(e) => setSwipeRatio(parseInt(e.target.value) / 100)} className="w-32 accent-blue-500" />
                )}
            </div>
        </div>
    );
}
