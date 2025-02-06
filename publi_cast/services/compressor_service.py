import numpy as np
from scipy import signal
import soundfile as sf

class Compressor:
    def __init__(self, 
                 compress_ratio=0.5,
                 hardness=0.5, 
                 floor=-32,
                 noise_factor=0,
                 scale_max=0.99,
                 left_exponent=2,
                 right_exponent=4):
        
        self.compress_ratio = compress_ratio
        self.hardness = (1.1 - hardness) * 3
        self.left_width_s = (self.hardness ** 2) * 510 / 1000  # Convert to seconds
        self.right_width_s = (self.hardness ** 2) * 340 / 1000
        self.floor = floor
        self.noise_factor = noise_factor
        self.scale_max = scale_max
        self.left_exponent = left_exponent
        self.right_exponent = right_exponent
        self.window_size = 1500
        
    def linear_to_db(self, x):
        return 20 * np.log10(np.maximum(np.abs(x), 1e-10))
    
    def db_to_linear(self, x):
        return 10 ** (x / 20)
    
    def make_curve(self, max_val, power, coeff):
        x = 0
        curve = []
        while True:
            y = (x / coeff) ** power
            if y > max_val:
                break
            curve.append(y)
            x += 1
        return curve, len(curve)
    
    def init_para(self):
        left_curve, left_len = self.make_curve(10000, self.left_exponent, self.left_width)
        right_curve, right_len = self.make_curve(10000, self.right_exponent, self.right_width)
        
        self.para = np.zeros(left_len + right_len - 1)
        self.para_mid = left_len
        
        # Fill left side
        self.para[:left_len] = left_curve
        
        # Fill right side
        self.para[left_len:] = right_curve[::-1]
        
    def process_buffer(self, buffer):
        # Convert to dB
        db_buffer = self.linear_to_db(buffer)
        
        # Apply compression envelope
        envelope = self.compute_envelope(db_buffer)
        
        # Apply compression ratio
        compressed = envelope * self.compress_ratio
        
        # Convert back to linear and apply gain
        gain = self.db_to_linear(-compressed) * self.scale_max
        
        return buffer * gain
    
    def compute_envelope(self, db_buffer):
        envelope = np.zeros_like(db_buffer)
        
        # Implement envelope following using parabolic interpolation
        i = 0
        while i < len(db_buffer):
            # Find next peak
            j = i + 1
            while j < len(db_buffer) and db_buffer[j] > db_buffer[i]:
                j += 1
                
            # Apply envelope
            envelope[i:j] = np.maximum(
                db_buffer[i:j],
                np.minimum(self.floor,
                          db_buffer[i] + (db_buffer[j-1] - db_buffer[i]) * 
                          np.linspace(0, 1, j-i))
            )
            
            i = j
            
        return envelope

    def process(self, audio_data, sample_rate):
        """Main processing function"""
        self.left_width = int(self.left_width_s * sample_rate)
        self.right_width = int(self.right_width_s * sample_rate)
        
        self.init_para()
        
        # Handle mono/stereo
        if len(audio_data.shape) == 1:
            return self.process_buffer(audio_data)
        else:
            processed = np.zeros_like(audio_data)
            for channel in range(audio_data.shape[1]):
                processed[:, channel] = self.process_buffer(audio_data[:, channel])
            return processed

    def process_direct(self, audio_data):
    # Handle mono/stereo
        if len(audio_data.shape) == 1:
            return self.process_buffer(audio_data)
        else:
            processed = np.zeros_like(audio_data)
            for channel in range(audio_data.shape[1]):
                processed[:, channel] = self.process_buffer(audio_data[:, channel])
            return processed


def compress_audio(input_file, output_file, **kwargs):
    """Utility function to compress audio files"""
    audio_data, sample_rate = sf.read(input_file)
    
    compressor = Compressor(**kwargs)
    processed_audio = compressor.process(audio_data, sample_rate)
    
    sf.write(output_file, processed_audio, sample_rate)
