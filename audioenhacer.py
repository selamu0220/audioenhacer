import streamlit as st
import soundfile as sf
import numpy as np
from scipy import signal as nr
import os
import tempfile
from io import BytesIO

class AudioEnhancerPro:
    def __init__(self):
        self.audio_path = None
        self.final_audio = None
        self.sr = None
        
        # Parámetros de procesamiento predeterminados
        self.processing_params = {
            'gain': 1.0,
            'bass_boost': 2.0,
            'treble_boost': 1.5,
            'compression': 0.7,
            'presence': 1.3
        }
        
    def apply_professional_enhancement(self, audio_data):
        # Aplicar ganancia
        audio_data = audio_data * self.processing_params['gain']

        # Refuerzo de graves (filtro paso bajo)
        b, a = nr.butter(4, 150 / (self.sr / 2), btype='lowpass')
        bass = nr.lfilter(b, a, audio_data)
        audio_data = audio_data + (bass * (self.processing_params['bass_boost'] - 1))

        # Refuerzo de agudos (filtro paso alto)
        b, a = nr.butter(4, 4000 / (self.sr / 2), btype='highpass')
        treble = nr.lfilter(b, a, audio_data)
        audio_data = audio_data + (treble * (self.processing_params['treble_boost'] - 1))

        # Compresión
        audio_data = self.apply_compression(audio_data)

        # Mejora de presencia
        audio_data = self.enhance_presence(audio_data)

        return np.clip(audio_data, -1, 1)

    def apply_compression(self, audio_data):
        threshold = 0.3
        ratio = 4 + (self.processing_params['compression'] * 6)

        # Compresión básica
        magnitude = np.abs(audio_data)
        compressed = np.copy(audio_data)
        mask = magnitude > threshold
        compressed[mask] = (
                                   threshold +
                                   (magnitude[mask] - threshold) / ratio
                           ) * np.sign(audio_data[mask])

        return compressed

    def enhance_presence(self, audio_data):
        # Filtro de presencia (2-4 kHz)
        b, a = nr.butter(2, [2000 / (self.sr / 2), 4000 / (self.sr / 2)], btype='bandpass')
        presence = nr.lfilter(b, a, audio_data)

        # Ajustar la cantidad de presencia
        enhanced = audio_data + (presence * (self.processing_params['presence'] - 1))

        return enhanced

    def process_audio(self, audio_file):
        try:
            # Guardar archivo cargado temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_file.getvalue())
                temp_path = tmp_file.name
            
            # Cargar archivo
            audio_data, self.sr = sf.read(temp_path)
            
            # Eliminar archivo temporal
            os.unlink(temp_path)
            
            # Convertir a mono si es estéreo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Aplicar efectos
            self.final_audio = self.apply_professional_enhancement(audio_data)
            
            return True
        except Exception as e:
            st.error(f"Error durante el procesamiento: {str(e)}")
            return False

def main():
    st.set_page_config(
        page_title="🎙️ Audio Enhancer Pro Studio",
        layout="wide"
    )
    
    st.title("🎙️ Audio Enhancer Pro Studio")
    st.write("Mejora la calidad de tus grabaciones de audio con esta herramienta profesional")
    
    # Inicializar el procesador de audio
    if 'enhancer' not in st.session_state:
        st.session_state.enhancer = AudioEnhancerPro()
    
    enhancer = st.session_state.enhancer
    
    # Sidebar con controles
    st.sidebar.title("Controles de Procesamiento")
    
    # Controles deslizantes en la barra lateral
    enhancer.processing_params['gain'] = st.sidebar.slider(
        "Ganancia", 0.0, 2.0, enhancer.processing_params['gain'], 0.1)
    
    enhancer.processing_params['bass_boost'] = st.sidebar.slider(
        "Refuerzo de Graves", 0.0, 4.0, enhancer.processing_params['bass_boost'], 0.1)
    
    enhancer.processing_params['treble_boost'] = st.sidebar.slider(
        "Refuerzo de Agudos", 0.0, 3.0, enhancer.processing_params['treble_boost'], 0.1)
    
    enhancer.processing_params['compression'] = st.sidebar.slider(
        "Compresión", 0.0, 1.0, enhancer.processing_params['compression'], 0.05)
    
    enhancer.processing_params['presence'] = st.sidebar.slider(
        "Presencia", 0.0, 2.0, enhancer.processing_params['presence'], 0.1)
    
    # Subida de archivo
    uploaded_file = st.file_uploader(
        "Selecciona un archivo de audio", 
        type=["wav", "mp3", "flac", "ogg"],
        help="Formatos soportados: WAV, MP3, FLAC, OGG"
    )
    
    col1, col2 = st.columns(2)
    
    process_button = col1.button("Procesar Audio", use_container_width=True)
    
    if uploaded_file is not None:
        if process_button:
            with st.spinner("Procesando audio..."):
                success = enhancer.process_audio(uploaded_file)
                
                if success:
                    st.success("¡Procesamiento completado!")
                    
                    # Mostrar audio original
                    st.subheader("Audio Original")
                    st.audio(uploaded_file)
                    
                    # Mostrar audio procesado
                    if enhancer.final_audio is not None:
                        st.subheader("Audio Procesado")
                        
                        # Convertir audio procesado a wav para reproducción
                        buffer = BytesIO()
                        sf.write(buffer, enhancer.final_audio, enhancer.sr, format='WAV')
                        buffer.seek(0)
                        
                        st.audio(buffer)
                        
                        # Botón de descarga
                        wav_bytes = buffer.getvalue()
                        st.download_button(
                            label="Descargar Audio Procesado",
                            data=wav_bytes,
                            file_name="audio_procesado.wav",
                            mime="audio/wav"
                        )
    else:
        st.info("Por favor, sube un archivo de audio para comenzar.")
    
    # Información adicional
    with st.expander("Acerca de Audio Enhancer Pro"):
        st.write("""
        **Audio Enhancer Pro Studio** es una herramienta diseñada para mejorar la calidad de tus grabaciones de audio.
        
        Características principales:
        - Ajuste de ganancia
        - Refuerzo de graves y agudos
        - Compresión dinámica
        - Mejora de presencia
        
        Esta aplicación está construida con Streamlit y procesa audio en tiempo real.
        """)

if __name__ == "__main__":
    main()
