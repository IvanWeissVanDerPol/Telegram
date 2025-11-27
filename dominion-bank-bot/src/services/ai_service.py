"""
AI Service using Groq API for generating creative content.
"""
import os
import logging
import random
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)

# System prompts for different content types
SYSTEM_PROMPTS = {
    "task": """Eres un generador de tareas para un juego de rol BDSM.
Genera tareas creativas, seguras y consensuadas para sumis@s.
Las tareas deben ser divertidas y apropiadas para un chat de Telegram.
Responde SOLO con la tarea, sin explicaciones adicionales.
Usa emojis para hacerlo visualmente atractivo.
Mantén las tareas en 2-3 oraciones máximo.""",

    "challenge": """Eres un generador de retos para un juego de rol BDSM.
Genera retos creativos y divertidos entre usuarios.
Los retos deben ser apropiados para un chat grupal.
Responde SOLO con el reto, sin explicaciones.
Usa emojis y hazlo dramático pero divertido.
Máximo 2-3 oraciones.""",

    "punishment": """Eres un narrador dramático de castigos en un juego de rol BDSM.
Describe castigos creativos de forma teatral y entretenida.
Todo es ficticio y parte del juego. Hazlo dramático pero divertido.
Responde SOLO con la descripción del castigo.
Usa emojis y lenguaje evocador.
Máximo 3-4 oraciones.""",

    "reward": """Eres un generador de recompensas para un juego de rol BDSM.
Genera recompensas creativas y gratificantes para sumis@s obedientes.
Las recompensas pueden ser privilegios, alabanzas especiales, o beneficios en el juego.
Responde SOLO con la recompensa descrita.
Usa emojis positivos.
Máximo 2-3 oraciones.""",

    "scene": """Eres un narrador de escenas de roleplay BDSM.
Crea descripciones atmosféricas y evocadoras para ambientar escenas.
Las descripciones deben establecer el ambiente sin ser explícitas.
Usa lenguaje sensorial: sonidos, olores, texturas, iluminación.
Responde SOLO con la descripción de la escena.
Máximo 4-5 oraciones.""",

    "ritual": """Eres un narrador de rituales y ceremonias BDSM.
Describe rituales solemnes y significativos entre Dom y sub.
El tono debe ser ceremonioso y respetuoso.
Incluye elementos simbólicos y gestos significativos.
Responde SOLO con la descripción del ritual.
Máximo 4-5 oraciones.""",

    "protocol": """Eres un generador de protocolos BDSM.
Crea reglas y protocolos que un@ sumis@ debe seguir.
Los protocolos deben ser claros, realizables y respetuosos.
Genera 3-5 reglas numeradas.
Responde SOLO con las reglas, sin explicaciones.""",

    "fantasy": """Eres un generador de escenarios de fantasía para roleplay BDSM.
Crea premisas interesantes para juegos de rol entre usuarios.
Los escenarios deben ser creativos e inspiradores.
Sugiere roles, ambientación y objetivo del juego.
Responde SOLO con el escenario descrito.
Máximo 4-5 oraciones.""",

    "truth": """Eres un generador de preguntas para Verdad o Reto versión BDSM.
Genera preguntas reveladoras pero apropiadas sobre preferencias, experiencias o deseos.
Las preguntas deben ser intrigantes pero respetuosas.
Responde SOLO con la pregunta.
Una sola pregunta por respuesta.""",

    "dare": """Eres un generador de retos para Verdad o Reto versión BDSM.
Genera retos creativos y divertidos apropiados para un chat de Telegram.
Los retos pueden ser performativos, creativos o sociales.
Responde SOLO con el reto.
Máximo 2 oraciones.""",

    "prediction": """Eres un oráculo místico que hace predicciones dramáticas y divertidas.
Genera predicciones sobre el "destino" del usuario en el juego.
Usa lenguaje místico y dramático pero con humor.
Las predicciones pueden ser sobre suerte, relaciones, o aventuras en el juego.
Responde SOLO con la predicción.
Máximo 3-4 oraciones.""",

    "title": """Eres un generador de títulos nobiliarios y honoríficos BDSM.
Crea títulos creativos y únicos basados en el rol del usuario.
Para Dominantes: títulos de poder, nobleza, autoridad.
Para Sumis@s: títulos de servicio, devoción, gracia.
Para Switches: títulos duales o versátiles.
Responde SOLO con el título (sin explicación).
Formato: [Emoji] Título Completo""",

    "bio": """Eres un escritor de biografías para perfiles BDSM.
Crea descripciones de perfil interesantes y atractivas.
El tono debe coincidir con el rol del usuario.
Incluye elementos misteriosos o intrigantes.
Responde SOLO con la biografía.
Máximo 3-4 oraciones evocadoras.""",

    "compatibility": """Eres un analista de compatibilidad para parejas BDSM.
Analiza la compatibilidad entre dos perfiles basándote en sus roles y características.
Sé positivo pero honesto, señalando fortalezas y áreas de crecimiento.
Usa un tono místico/astrológico divertido.
Incluye un porcentaje de compatibilidad creativo.
Responde con el análisis completo.
Máximo 5-6 oraciones.""",

    "flavor_whip": """Eres un narrador dramático de azotes en un juego BDSM.
Describe el momento del azote de forma teatral y evocadora.
Incluye el sonido, la reacción, el ambiente.
Hazlo dramático pero elegante.
Máximo 2-3 oraciones. Usa emojis.""",

    "flavor_dungeon": """Eres un narrador de calabozos en un juego BDSM.
Describe el momento de encierro de forma atmosférica.
Incluye detalles del calabozo: oscuridad, frío, silencio.
Hazlo inmersivo pero no excesivo.
Máximo 2-3 oraciones. Usa emojis.""",

    "flavor_collar": """Eres un narrador de ceremonias de collar en BDSM.
Describe el momento del collaring de forma solemne y significativa.
Es un momento importante de compromiso.
Hazlo ceremonioso y emotivo.
Máximo 3-4 oraciones. Usa emojis.""",

    "dice_interpret": """Eres un intérprete de dados perversos en un juego BDSM.
Te darán el resultado de un dado y debes interpretarlo creativamente.
El resultado determina una acción, intensidad, o consecuencia.
Hazlo divertido y sorprendente.
Máximo 2-3 oraciones. Usa emojis.""",
}


class AIService:
    """Service for AI-generated content using Groq."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI service."""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        self.model = "llama-3.1-8b-instant"  # Fast and efficient
        self._enabled = False

        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self._enabled = True
                logger.info("AI Service initialized with Groq")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("No GROQ_API_KEY found, AI features disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if AI service is available."""
        return self._enabled and self.client is not None

    async def generate(
        self,
        prompt_type: str,
        context: str = "",
        max_tokens: int = 200,
        temperature: float = 0.8
    ) -> Optional[str]:
        """Generate content using AI.

        Args:
            prompt_type: Type of content to generate (task, punishment, etc.)
            context: Additional context for the generation
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-1.0)

        Returns:
            Generated text or None if failed
        """
        if not self.is_enabled:
            return self._get_fallback(prompt_type, context)

        system_prompt = SYSTEM_PROMPTS.get(prompt_type)
        if not system_prompt:
            logger.error(f"Unknown prompt type: {prompt_type}")
            return None

        try:
            user_message = context if context else "Genera contenido creativo."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            result = response.choices[0].message.content.strip()
            logger.debug(f"AI generated [{prompt_type}]: {result[:50]}...")
            return result

        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self._get_fallback(prompt_type, context)

    def _get_fallback(self, prompt_type: str, context: str = "") -> str:
        """Get fallback content when AI is unavailable."""
        fallbacks = {
            "task": [
                "📝 Escribe 3 razones por las que mereces servir.",
                "🧎 Practica tu postura de sumisión por 5 minutos.",
                "✍️ Escribe un poema de devoción para tu Dom.",
                "🎭 Cuenta una fantasía que nunca hayas compartido.",
                "📸 Describe tu lugar favorito para servir.",
            ],
            "challenge": [
                "⚔️ Mantén silencio por los próximos 10 mensajes.",
                "🎯 Haz 3 cumplidos sinceros a otros miembros.",
                "🔥 Confiesa algo que nunca hayas dicho en el grupo.",
                "💪 Demuestra tu obediencia siguiendo la próxima orden sin preguntar.",
            ],
            "punishment": [
                "⚡ El látigo deja su marca... una lección que no olvidarás.",
                "🔥 Las consecuencias de la desobediencia son claras.",
                "⛓️ El castigo ha sido aplicado. Que sirva de recordatorio.",
            ],
            "reward": [
                "🌟 Has demostrado ser digno/a de reconocimiento especial.",
                "👑 Tu servicio ha sido ejemplar. Mereces alabanza.",
                "💎 Una recompensa por tu devoción inquebrantable.",
            ],
            "scene": [
                "🕯️ Las velas parpadean, proyectando sombras danzantes...",
                "🏰 El silencio del calabozo es roto solo por respiraciones...",
                "⛓️ El sonido metálico de las cadenas resuena en la oscuridad...",
            ],
            "prediction": [
                "🔮 Las estrellas auguran... cambios interesantes en tu destino.",
                "✨ El oráculo ve sumisión en tu futuro... o dominación.",
                "🌙 La luna revela que una conexión intensa te aguarda.",
            ],
            "title": [
                "👑 Señor/a de las Sombras Eternas",
                "⛓️ Guardián/a del Calabozo Carmesí",
                "🔥 Domador/a de Voluntades",
                "💎 Joya Devota del Reino",
                "🌙 Servidor/a de la Luna Oscura",
            ],
            "truth": [
                "¿Cuál es tu fantasía más secreta que nunca has confesado?",
                "¿Qué límite te gustaría explorar pero te da miedo?",
                "¿Cuál fue tu experiencia más intensa en el mundo BDSM?",
            ],
            "dare": [
                "Envía un mensaje de sumisión/dominación al último usuario que habló.",
                "Describe tu escena ideal en 3 emojis.",
                "Haz una reverencia virtual al Dom más cercano.",
            ],
        }

        options = fallbacks.get(prompt_type, ["🎲 El destino ha hablado..."])
        return random.choice(options)

    # Convenience methods for specific content types

    async def generate_task(self, sub_name: str, dom_name: str = None) -> str:
        """Generate a task for a submissive."""
        context = f"Genera una tarea para {sub_name}"
        if dom_name:
            context += f" ordenada por {dom_name}"
        return await self.generate("task", context)

    async def generate_challenge(self, challenger: str, target: str) -> str:
        """Generate a challenge between users."""
        context = f"{challenger} reta a {target}. Genera un reto apropiado."
        return await self.generate("challenge", context)

    async def generate_punishment(self, dom: str, sub: str, reason: str = None) -> str:
        """Generate a creative punishment description."""
        context = f"{dom} castiga a {sub}"
        if reason:
            context += f" por: {reason}"
        return await self.generate("punishment", context)

    async def generate_reward(self, dom: str, sub: str) -> str:
        """Generate a reward for good behavior."""
        context = f"{dom} recompensa a {sub} por su buen comportamiento."
        return await self.generate("reward", context)

    async def generate_scene(self, theme: str = None) -> str:
        """Generate a scene description."""
        context = f"Describe una escena de: {theme}" if theme else "Describe una escena atmosférica de mazmorra."
        return await self.generate("scene", context)

    async def generate_ritual(self, dom: str, sub: str, ritual_type: str = "sumisión") -> str:
        """Generate a ritual description."""
        context = f"Describe un ritual de {ritual_type} entre {dom} (Dom) y {sub} (sub)."
        return await self.generate("ritual", context)

    async def generate_protocol(self, sub_name: str) -> str:
        """Generate protocol rules for a sub."""
        context = f"Genera un protocolo de comportamiento para {sub_name}."
        return await self.generate("protocol", context)

    async def generate_fantasy(self) -> str:
        """Generate a fantasy scenario."""
        context = "Genera un escenario de fantasía BDSM para roleplay."
        return await self.generate("fantasy", context)

    async def generate_truth(self) -> str:
        """Generate a truth question."""
        return await self.generate("truth", "Genera una pregunta de verdad.")

    async def generate_dare(self) -> str:
        """Generate a dare."""
        return await self.generate("dare", "Genera un reto atrevido pero apropiado.")

    async def generate_prediction(self, user_name: str) -> str:
        """Generate a fortune prediction."""
        context = f"Predice el destino de {user_name} en el mundo BDSM."
        return await self.generate("prediction", context)

    async def generate_title(self, user_name: str, role: str) -> str:
        """Generate a noble/BDSM title."""
        context = f"Genera un título para {user_name} que es {role}."
        return await self.generate("title", context)

    async def generate_bio(self, user_name: str, role: str) -> str:
        """Generate a profile bio."""
        context = f"Escribe una biografía para {user_name}, un/a {role}."
        return await self.generate("bio", context)

    async def analyze_compatibility(self, user1: str, role1: str, user2: str, role2: str) -> str:
        """Analyze compatibility between two users."""
        context = f"Analiza la compatibilidad entre {user1} ({role1}) y {user2} ({role2})."
        return await self.generate("compatibility", context, max_tokens=300)

    async def flavor_whip(self, dom: str, sub: str, reason: str = None) -> str:
        """Generate flavor text for whipping."""
        context = f"{dom} azota a {sub}"
        if reason:
            context += f". Razón: {reason}"
        return await self.generate("flavor_whip", context)

    async def flavor_dungeon(self, jailer: str, prisoner: str, hours: int) -> str:
        """Generate flavor text for dungeon."""
        context = f"{jailer} encierra a {prisoner} en el calabozo por {hours} horas."
        return await self.generate("flavor_dungeon", context)

    async def flavor_collar(self, dom: str, sub: str) -> str:
        """Generate flavor text for collaring."""
        context = f"{dom} coloca un collar a {sub}."
        return await self.generate("flavor_collar", context)

    async def interpret_dice(self, dice_result: int, dice_type: str) -> str:
        """Interpret a dice roll result."""
        context = f"El dado de {dice_type} cayó en {dice_result}. Interpreta este resultado."
        return await self.generate("dice_interpret", context)


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create the AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
