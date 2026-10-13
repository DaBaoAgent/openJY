"""就医引流 Seedance 提示词包 —— 西语版（es）10 条成品（Claude 手写）。

宝哥 2026-10-13 口径：项目转向**西语区**推广。
  · 口播台词全程**西班牙语**（重音字母 / ñ 齐全，语法地道；问句、感叹句按西语语法加 ¿ ¡）；
    面向西语区病患（西班牙 / 拉美）。
  · 语速**再快一档**（es 5.6–6.2 单位/秒；10s = 52–58 单位 ≈ 26–29 词）。
  · 人物/场景体现西语区背景（马德里街头、西语协调员、拉美/西班牙不同国籍与年龄段）。
  · 画面指令（person/scene/camera）仍用英文给 Seedance —— 台词（lines）是西语。

设计口径同英文批（见 catalog.py / promptpack.py）：10s 竖屏、单镜连续、直接口播对嘴型、
手持手机机位、人物边走边说话；每条 6 句台词，无阿拉伯数字，不碰疗效/绝对化/报价红线。
改内容只改这里；渲染/校验/落盘走 lib/jiuyi/promptpack.py 与 tools/jiuyi_prompts.py。
"""
from __future__ import annotations

from .promptpack import PromptPack

CATALOG_ES: list[PromptPack] = [
    PromptPack(
        id="jiuyi_es_m1_calle_01", angle="M1", title="Preguntan por qué China", language="es",
        person="a 33-year-old Spanish woman with wavy dark brown hair, mustard knit sweater",
        scene="a sunny street in Madrid, stone buildings and cafe terraces",
        camera=("handheld phone camera, slight natural shake; "
                "she walks along the Madrid street while talking to camera"),
        performance="warm, chatty delivery; she walks and speaks to camera",
        lines=["Preguntan por qué China", "Para mí fue muy claro",
               "Hospitales modernos, apoyo en español", "Reservar todo fue muy fácil",
               "Me sentí acompañada siempre", "Volvería aquí sin dudar"],
        voice=("her own natural voice, warm, clear Spanish with a Madrid accent, "
               "noticeably fast and fluid, continuous"),
        ambient="light European street ambience, distant Spanish chatter; no music",
    ),
    PromptPack(
        id="jiuyi_es_m2_habitacion_01", angle="M2", title="Vine por mi cirugía", language="es",
        person="a 47-year-old Mexican man with short black hair and a trimmed beard, light blue shirt",
        scene="a bright patient ward in a modern Chinese hospital, soft daylight",
        camera=("handheld phone camera, gentle shake; "
                "he walks slowly along the ward while talking to camera"),
        performance="calm, sincere delivery; he walks and speaks to camera",
        lines=["Vine a China por mi cirugía", "Hospitales modernos y coordinadores",
               "Visado y hotel, todo listo", "El presupuesto llegó primero",
               "Nunca me sentí perdido", "Todo me lo explicaron"],
        voice=("his own natural voice, clear Mexican Spanish, "
               "noticeably fast and continuous"),
        ambient="quiet ward room tone, faint distant footsteps; no music",
    ),
    PromptPack(
        id="jiuyi_es_m3_mito_01", angle="M3", title="Más fácil de lo que creí", language="es",
        person="a 39-year-old Colombian woman with long dark curly hair, white blouse",
        scene="a spacious modern hospital lobby with tall windows and green plants",
        camera=("handheld phone camera, slight natural shake; "
                "she walks across the lobby while talking to camera"),
        performance="honest, reflective delivery; she walks and speaks to camera",
        lines=["Pensé que sería difícil", "Esperas largas, sin español",
               "Pero todo estaba organizado", "Una coordinadora hablaba español",
               "Fue más fácil de lo que creí", "Mejor de lo esperado"],
        voice=("her own natural voice, clear Colombian Spanish, "
               "noticeably fast and fluid, continuous"),
        ambient="calm lobby ambience, soft distant voices; no music",
    ),
    PromptPack(
        id="jiuyi_es_m4_llegada_01", angle="M4", title="Un día completo", language="es",
        person="a 55-year-old Spanish man with grey hair, light jacket, small travel bag",
        scene="an airport arrival hall in China, glass doors and soft daylight",
        camera=("handheld phone camera, gentle shake; "
                "he walks through the arrival hall while talking to camera"),
        performance="calm, steady delivery; he walks and speaks to camera",
        lines=["Me esperaban en el aeropuerto", "Directo al hospital",
               "Análisis y luego el médico", "Todo en un mismo día",
               "Fue rápido de principio a fin", "Todo sin complicaciones"],
        voice=("his own natural voice, clear peninsular Spanish, "
               "noticeably fast and steady, continuous"),
        ambient="soft airport ambience, rolling suitcase wheels; no music",
    ),
    PromptPack(
        id="jiuyi_es_m5_costos_01", angle="M5", title="El presupuesto primero", language="es",
        person="a 61-year-old Spanish woman with silver hair and glasses, beige cardigan",
        scene="a quiet consultation room with a desk and a bright window",
        camera=("handheld phone camera, subtle shake; "
                "she walks into the consult room and settles while talking to camera"),
        performance="measured, sincere delivery; she walks in and speaks to camera",
        lines=["Temía mucho la factura", "Primero me dieron un presupuesto",
               "El hospital dio la cifra exacta", "Sin sorpresas al final",
               "Eso me dio tranquilidad", "Nada de costos ocultos"],
        voice=("her own natural voice, clear Spanish, "
               "noticeably fast and measured, continuous"),
        ambient="quiet consultation room tone, faint paper rustle; no music",
    ),
    PromptPack(
        id="jiuyi_es_m6_idioma_01", angle="M6", title="Sin barrera de idioma", language="es",
        person="a 35-year-old Argentine woman with straight dark hair, soft olive sweater",
        scene="a recovery ward beside a large window, plants on the sill",
        camera=("handheld phone camera, slight shake; "
                "she walks beside the ward window while talking to camera"),
        performance="warm, reassured delivery; she walks and speaks to camera",
        lines=["No hablo nada de chino", "Pero nunca estuve sola",
               "Mi coordinadora traducía todo", "Los médicos hablaban español",
               "Nunca hubo una barrera", "Me explicaron cada paso con calma"],
        voice=("her own natural voice, clear Argentine Spanish, "
               "noticeably fast and fluid, continuous"),
        ambient="quiet ward, faint birdsong outside; no music",
    ),
    PromptPack(
        id="jiuyi_es_m1_plaza_01", angle="M1", title="Por qué elegí China", language="es",
        person="a 41-year-old Peruvian man with dark hair and a short beard, denim jacket",
        scene="a riverside plaza at dusk, city lights reflecting on the water",
        camera=("handheld selfie phone camera, gentle shake; "
                "he walks along the riverside plaza while talking to camera"),
        performance="easy, upbeat delivery; he walks and speaks to camera",
        lines=["La gente pregunta por qué", "Para mí la respuesta es simple",
               "Hospitales modernos, atención en español", "Reservar me llevó una llamada",
               "Me trataron muy bien", "Volvería otra vez"],
        voice=("his own natural voice, clear Peruvian Spanish, "
               "noticeably fast and lively, continuous"),
        ambient="open riverside ambience, distant traffic and gentle wind; no music",
    ),
    PromptPack(
        id="jiuyi_es_m2_fisio_01", angle="M2", title="Vuelvo a caminar", language="es",
        person="a 63-year-old Chilean woman with short grey hair, soft blue cardigan",
        scene="a bright physiotherapy room with mats, rails and large windows",
        camera=("handheld phone camera, slight natural shake; "
                "she walks steadily across the physio room while talking to camera"),
        performance="grounded, grateful delivery; she walks and speaks to camera",
        lines=["Apenas podía caminar", "Hasta que encontré esta clínica",
               "La terapia aquí me ayudó", "Paso a paso, mucho mejor",
               "Mi terapeuta hablaba español", "Ahora camino sola cada día"],
        voice=("her own natural voice, warm Chilean Spanish, "
               "noticeably fast and steady, continuous"),
        ambient="quiet therapy room tone, faint soft footsteps; no music",
    ),
    PromptPack(
        id="jiuyi_es_m4_revision_01", angle="M4", title="La revisión fue fácil", language="es",
        person="a 49-year-old Spanish man with salt-and-pepper hair, navy shirt",
        scene="a quiet follow-up clinic room with a desk and a bright window",
        camera=("handheld phone camera, subtle shake; "
                "he walks into the follow-up room while talking to camera"),
        performance="steady, friendly delivery; he walks in and speaks to camera",
        lines=["Volví para mi revisión mensual", "La misma coordinadora y médico",
               "Recordaban todo mi caso", "Chequeo rápido y buenos consejos",
               "Sin repetir todo otra vez", "Me sentí muy tranquilo"],
        voice=("his own natural voice, clear peninsular Spanish, "
               "noticeably fast and steady, continuous"),
        ambient="quiet clinic room tone, faint clock tick; no music",
    ),
    PromptPack(
        id="jiuyi_es_m6_taxi_01", angle="M6", title="Del taxi a la planta", language="es",
        person="a 30-year-old Mexican woman with dark shoulder-length hair, beige trench coat",
        scene="a hospital drop-off area by the entrance, soft daylight",
        camera=("handheld phone camera, slight natural shake; "
                "she walks from the drop-off toward the entrance while talking to camera"),
        performance="warm, reassured delivery; she walks and speaks to camera",
        lines=["El taxi me dejó en la puerta", "Alguien ya me esperaba",
               "Me llevó hasta la planta", "Explicando cada paso en español",
               "Sin ninguna confusión", "Nunca me sentí perdida"],
        voice=("her own natural voice, clear Mexican Spanish, "
               "noticeably fast and fluid, continuous"),
        ambient="soft outdoor hospital ambience, distant traffic; no music",
    ),
]


def by_id(pack_id: str) -> PromptPack | None:
    for pack in CATALOG_ES:
        if pack.id == pack_id:
            return pack
    return None
