// src/services/audioPlayer.ts

import { showNeuroCaption, hideNeuroCaption, startCaptionTimeout } from '../ui/neuroCaption';
import { singletonManager } from '../core/singletonManager';

interface AudioSegment {
    text: string;
    audio: HTMLAudioElement;
    duration: number; // <-- 新增：保存每个片段的时长
}

export class AudioPlayer {
    private audioQueue: AudioSegment[] = [];
    private isPlayingAudio: boolean = false;
    private currentPlayingAudio: HTMLAudioElement | null = null;
    private allSegmentsReceived: boolean = false;
    private errorSound: HTMLAudioElement; 
    private lastSegmentEnd: boolean = true;

    constructor() {
        this.errorSound = new Audio('/error.mp3'); 
        console.log("AudioPlayer initialized.");
    }

    public playErrorSound(): void {
        this.stopAllAudio(); 
        console.log("Playing dedicated error sound...");
        this.errorSound.play().catch(e => {
            console.error("Error playing dedicated error sound:", e);
        });
    }

    /**
     * 新增：添加音频片段时传入 duration
     */
    public addAudioSegment(text: string, audioBase64: string, duration: number): void { // <-- 增加 duration 参数
        // 新段落开始时，先隐藏字幕
        if (this.lastSegmentEnd) {
            hideNeuroCaption();
        }
        this.lastSegmentEnd = false;
        const audio = new Audio('data:audio/mp3;base64,' + audioBase64);
        
        // 检查静音状态
        try {
            const app = singletonManager.getAppInitializer();
            const muteButton = app.getMuteButton();
            audio.muted = muteButton.getIsMuted();
        } catch (e) {
            console.warn("Could not get mute state, defaulting to muted:", e);
            audio.muted = true;
        }
        
        this.audioQueue.push({ text, audio, duration }); // <-- 存储 duration
        console.log(`Audio segment added to queue. Queue size: ${this.audioQueue.length}`);
        if (!this.isPlayingAudio) {
            this.playNextAudioSegment();
        }
    }

    private playNextAudioSegment(): void {
        if (this.audioQueue.length > 0 && !this.isPlayingAudio) {
            this.isPlayingAudio = true;
            const currentSegment = this.audioQueue.shift()!;
            this.currentPlayingAudio = currentSegment.audio;
            
            // --- 核心修改：调用 showNeuroCaption 时传入时长 ---
            showNeuroCaption(currentSegment.text, currentSegment.duration);

            this.currentPlayingAudio.play().catch(e => {
                console.error("Error playing audio segment:", e);
                this.isPlayingAudio = false;
                this.currentPlayingAudio = null;
                this.playNextAudioSegment();
            });

            this.currentPlayingAudio.addEventListener('ended', () => {
                this.isPlayingAudio = false;
                this.currentPlayingAudio = null;
                this.playNextAudioSegment();
            }, { once: true });
        } else if (this.audioQueue.length === 0 && this.allSegmentsReceived) {
            console.log("Neuro's full audio response played. Starting caption timeout and resetting zoom.");
            startCaptionTimeout();
            try {
                singletonManager.getAppInitializer().getNeuroAvatar().resetZoom();
            } catch (e) {
                console.warn("Could not reset neuro avatar zoom at end of speech", e);
            }
        }
    }
    
    public setAllSegmentsReceived(): void {
        this.allSegmentsReceived = true;
        this.lastSegmentEnd = true;
    }

    public stopAllAudio(): void {
        if (this.currentPlayingAudio) {
            this.currentPlayingAudio.pause();
            this.currentPlayingAudio.currentTime = 0;
            this.currentPlayingAudio = null;
        }
        this.audioQueue.length = 0;
        this.isPlayingAudio = false;
        this.allSegmentsReceived = false;
        hideNeuroCaption(); // 强制隐藏字幕
        try {
            singletonManager.getAppInitializer().getNeuroAvatar().resetZoom();
        } catch (e) {
            console.warn("Could not reset neuro avatar zoom on stop", e);
        }
        console.log("Neuro audio playback stopped, queue cleared.");
    }
    
    public updateMuteState(): void {
        // 更新当前播放音频的静音状态
        if (this.currentPlayingAudio) {
            try {
                const app = singletonManager.getAppInitializer();
                const muteButton = app.getMuteButton();
                this.currentPlayingAudio.muted = muteButton.getIsMuted();
            } catch (e) {
                console.warn("Could not update current audio mute state:", e);
            }
        }
        
        // 更新队列中音频的静音状态
        for (const segment of this.audioQueue) {
            try {
                const app = singletonManager.getAppInitializer();
                const muteButton = app.getMuteButton();
                segment.audio.muted = muteButton.getIsMuted();
            } catch (e) {
                console.warn("Could not update queued audio mute state:", e);
            }
        }
    }
}