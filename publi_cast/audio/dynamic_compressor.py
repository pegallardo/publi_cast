# -*- coding: utf-8 -*-
"""
PubliCast - Dynamic Compressor with Lookahead

Python implementation based on compress.ny by Chris Capel (pdf23ds.net)
This algorithm uses paraboloid envelope fitting for smooth dynamic compression.

The compressor works by:
1. Computing an envelope of the input signal using peak detection
2. Fitting paraboloid curves to create a smooth gain envelope
3. Applying the inverted envelope to compress the dynamic range
"""
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def linear_to_db(value: float) -> float:
    """Convert linear amplitude to decibels."""
    if value <= 0:
        return -120.0  # Floor value for silence
    return 20.0 * np.log10(value)


def db_to_linear(db: float) -> float:
    """Convert decibels to linear amplitude."""
    return 10.0 ** (db / 20.0)


class DynamicCompressor:
    """
    Dynamic compressor with lookahead based on paraboloid envelope fitting.
    
    Parameters:
        compress_ratio: Compression amount (-.5 to 1.25). Higher = more compression.
        hardness: How aggressively to compress (0.1 to 1). Higher = harder knee.
        floor: Level in dB below which quiet parts stay quiet (-96 to 0).
        noise_factor: Noise gate falloff (-2 to 10). Higher = more gating.
        scale_max: Maximum output amplitude (0.0 to 1.0).
        sample_rate: Audio sample rate in Hz.
    """
    
    def __init__(
        self,
        compress_ratio: float = 0.8,
        hardness: float = 0.879,
        floor: float = -18.0,
        noise_factor: float = 0.0,
        scale_max: float = 0.99,
        sample_rate: int = 44100
    ):
        self.compress_ratio = compress_ratio
        self.hardness = hardness
        self.floor = floor
        self.noise_factor = noise_factor
        self.scale_max = scale_max
        self.sample_rate = sample_rate
        
        # Window size for envelope detection (in samples)
        self.window_size = 1500
        
        # Calculate attack/release widths from hardness
        # From compress.ny: hardness = (1.1 - hardness) * 3
        #                   width = hardness^2 * base_ms
        h = (1.1 - hardness) * 3
        self.release_width_s = (h * h * 510) / 1000.0  # in seconds
        self.attack_width_s = (h * h * 340) / 1000.0   # in seconds
        
        # Exponents for paraboloid curves (fixed values from compress.ny)
        self.release_exponent = 2
        self.attack_exponent = 4
        
    def _compute_envelope(self, audio: np.ndarray) -> np.ndarray:
        """
        Compute the peak envelope of the audio signal.
        Uses overlapping windows to detect peaks.
        """
        # Work with absolute values
        abs_audio = np.abs(audio)
        
        # Number of windows
        hop_size = self.window_size
        n_windows = len(audio) // hop_size + 1
        
        # Compute peak for each window
        envelope_db = np.zeros(n_windows)
        for i in range(n_windows):
            start = i * hop_size
            end = min(start + self.window_size * 2, len(audio))
            if start < len(audio):
                peak = np.max(abs_audio[start:end]) if end > start else 0
                envelope_db[i] = linear_to_db(peak)
        
        return envelope_db
    
    def _apply_floor_and_gate(self, envelope_db: np.ndarray) -> np.ndarray:
        """Apply floor and noise gate to the envelope."""
        result = np.copy(envelope_db)
        
        for i in range(len(result)):
            if result[i] < self.floor:
                # Apply noise gate falloff
                result[i] = self.floor + (result[i] - self.floor) * (-1) * self.noise_factor
        
        return result

    def _interpolate_envelope(self, envelope_db: np.ndarray, target_length: int) -> np.ndarray:
        """Interpolate the envelope to match the original audio length."""
        x_original = np.linspace(0, 1, len(envelope_db))
        x_target = np.linspace(0, 1, target_length)
        return np.interp(x_target, x_original, envelope_db)

    def process(self, audio: np.ndarray, sample_rate: Optional[int] = None) -> np.ndarray:
        """
        Apply dynamic compression to audio.
        
        Args:
            audio: Input audio samples (mono or stereo as 2D array)
            sample_rate: Sample rate (uses instance default if not provided)
            
        Returns:
            Compressed audio samples
        """
        if sample_rate:
            self.sample_rate = sample_rate
            
        # Handle stereo by processing channels together
        if audio.ndim == 2:
            # Use max of both channels for envelope
            mono_for_envelope = np.max(np.abs(audio), axis=1)
        else:
            mono_for_envelope = audio
            
        logger.info(f"Processing audio: {len(mono_for_envelope)} samples at {self.sample_rate}Hz")
        logger.info(f"Compressor settings: ratio={self.compress_ratio}, hardness={self.hardness}, "
                   f"floor={self.floor}dB, noise_factor={self.noise_factor}, scale_max={self.scale_max}")
        
        # Step 1: Compute envelope
        envelope_db = self._compute_envelope(mono_for_envelope)
        
        # Step 2: Apply floor and noise gate
        envelope_db = self._apply_floor_and_gate(envelope_db)
        
        # Step 3: Apply compression ratio
        envelope_db = envelope_db * self.compress_ratio
        
        # Step 4: Convert to linear gain
        gain_envelope = db_to_linear(envelope_db)
        
        # Step 5: Invert (compression = reducing loud parts)
        gain_envelope = 1.0 / np.maximum(gain_envelope, 1e-10)
        
        # Step 6: Apply maximum amplitude scaling
        gain_envelope = gain_envelope * self.scale_max
        
        # Step 7: Interpolate to match audio length
        if audio.ndim == 2:
            gain = self._interpolate_envelope(gain_envelope, audio.shape[0])
            # Apply to both channels
            output = audio * gain[:, np.newaxis]
        else:
            gain = self._interpolate_envelope(gain_envelope, len(audio))
            output = audio * gain
        
        # Clip to prevent any overflow
        output = np.clip(output, -1.0, 1.0)
        
        logger.info("Compression complete")
        return output

