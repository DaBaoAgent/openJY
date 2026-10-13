"""就医引流 Seedance 提示词包 —— 两批成品（各 10 条，Claude 手写）。

设计口径（宝哥 2026-10-12）：
  · 10s 竖屏文生视频、单镜连续、**直接口播对嘴型**、**手持手机机位轻微晃动**、**人物边走边说话**；
  · **口播稍快、一条连贯、中途不停顿**（语速上限提到 5.0–5.6 单位/秒，见 promptpack.render 的 DELIVERY 段）；
  · 覆盖 M1-M6 六条叙事思路（lib/angles.py:70-76）、不同人物（外籍男女/不同年龄段）与场景
    （病房/走廊/问诊室/大厅/机场/街边/检查区）；
  · 每条 6 句英文台词，共 47-52 单位（= 24-26 个英文词）；台词全部去标点以外的口语短句，
    无阿拉伯数字，不碰疗效/绝对化/报价红线。

改内容只改这里；渲染/校验/落盘走 lib/jiuyi/promptpack.py 与 tools/jiuyi_prompts.py。
"""
from __future__ import annotations

from .promptpack import PromptPack

CATALOG: list[PromptPack] = [
    PromptPack(
        id="jiuyi_m2_ward_01", angle="M2", title="I came for surgery",
        person="a 45-year-old Western woman with short brown hair, casual grey blouse",
        scene="a bright patient ward, soft daylight through the blinds",
        camera=("handheld phone camera held at arm's length, slight natural shake; "
                "she walks slowly down the ward while talking to camera"),
        performance="relaxed, natural delivery; she walks and speaks at an easy, flowing pace",
        lines=["I came for surgery", "Modern hospitals, English coordinators",
               "Visa and hotel, all arranged", "The cost estimate came first",
               "I never felt lost", "Everything explained to me"],
        voice="her own natural voice, warm mid-range, clear English, slightly faster, fluid, continuous",
        ambient="quiet ward room tone, faint distant footsteps; no music",
    ),
    PromptPack(
        id="jiuyi_m4_arrival_01", angle="M4", title="Met at the airport",
        person="a 52-year-old Western man with greying hair, light jacket, small travel bag",
        scene="an airport arrival hall in China, glass doors and soft daylight",
        camera=("handheld phone camera, gentle natural shake; "
                "he walks through the arrival hall while talking to camera"),
        performance="calm, natural delivery; he walks and speaks at a steady pace",
        lines=["They met me at the airport", "Straight to the hospital",
               "Tests, then the doctor", "Everything in one day",
               "Smooth from start to end", "All went smoothly"],
        voice="his own natural voice, calm and steady, clear English, slightly faster, fluid, continuous",
        ambient="busy but soft arrival-hall ambience, rolling suitcase wheels; no music",
    ),
    PromptPack(
        id="jiuyi_m1_street_01", angle="M1", title="Why fly to China",
        person="a 29-year-old Western man in a hoodie, backpack over one shoulder",
        scene="a clean street just outside a large Chinese hospital, morning light",
        camera=("handheld selfie phone camera, slight shake; "
                "he walks along the street while talking to camera"),
        performance="easy, chatty delivery; he walks and speaks to camera",
        lines=["Why fly to China for care", "Public hospitals, modern tools",
               "English support throughout", "Costs explained up front",
               "That is why I came", "Simple from day one"],
        voice="his own natural voice, relaxed and youthful, clear English, slightly faster, fluid, continuous",
        ambient="light street ambience, distant traffic; no music",
    ),
    PromptPack(
        id="jiuyi_m3_myth_01", angle="M3", title="Easier than I feared",
        person="a 38-year-old Western woman with blonde hair tied back, denim jacket",
        scene="a spacious modern hospital lobby with tall windows",
        camera=("handheld phone camera, slight natural shake; "
                "she walks across the lobby while talking to camera"),
        performance="honest, reflective delivery; she walks and speaks to camera",
        lines=["I thought it would be hard", "Long waits, language gaps",
               "But everything was organized", "A coordinator spoke English",
               "Easier than I feared", "Better than I expected"],
        voice="her own natural voice, bright and clear, slightly faster, fluid, continuous",
        ambient="calm lobby ambience, soft distant chatter; no music",
    ),
    PromptPack(
        id="jiuyi_m5_cost_01", angle="M5", title="The estimate came first",
        person="a 60-year-old Western man with glasses and a navy polo shirt",
        scene="a quiet consultation room with a desk and a window",
        camera=("handheld phone camera, subtle shake; "
                "he walks into the consult room and settles while talking to camera"),
        performance="measured, sincere delivery; he walks in and speaks to camera",
        lines=["I feared the bill", "They gave an estimate first",
               "The hospital gave the quote", "No surprises at the end",
               "That gave me peace", "No hidden fees"],
        voice="his own natural voice, low and measured, clear English, slightly faster, fluid, continuous",
        ambient="quiet consultation room tone, faint paper rustle; no music",
    ),
    PromptPack(
        id="jiuyi_m6_language_01", angle="M6", title="No language barrier",
        person="a 30-year-old Western woman with dark curly hair, soft sweater",
        scene="a recovery ward beside a large window, plants on the sill",
        camera=("handheld phone camera, slight shake; "
                "she walks beside the ward window while talking to camera"),
        performance="warm, reassured delivery; she walks and speaks to camera",
        lines=["I speak no Chinese", "But I was never alone",
               "My coordinator translated everything", "Doctors explained in English",
               "Communication was never a problem", "Never a barrier here"],
        voice="her own natural voice, soft and clear, slightly faster, fluid, continuous",
        ambient="quiet ward, faint birdsong outside; no music",
    ),
    PromptPack(
        id="jiuyi_m2_corridor_02", angle="M2", title="Safe the whole way",
        person="a 58-year-old Western woman with silver hair, floral blouse",
        scene="a long clean hospital corridor with doors on both sides",
        camera=("handheld phone camera, slight natural shake; "
                "she walks slowly along the long corridor while talking to camera"),
        performance="gentle, steady delivery; she walks and speaks to camera",
        lines=["I traveled far for care", "The hospitals here are modern",
               "English coordinators guide you", "Every step was explained",
               "I felt safe throughout", "Care at every turn"],
        voice="her own natural voice, warm and gentle, clear English, slightly faster, fluid, continuous",
        ambient="quiet corridor tone, faint footsteps and a distant PA chime; no music",
    ),
    PromptPack(
        id="jiuyi_m4_checkup_01", angle="M4", title="One smooth process",
        person="a 44-year-old Western man with a trimmed beard, grey tee",
        scene="a modern diagnostic imaging area, soft ceiling light",
        camera=("handheld phone camera, slight shake; "
                "he walks through the imaging area while talking to camera"),
        performance="matter-of-fact delivery; he walks and speaks to camera",
        lines=["Checked in and scanned", "The whole process was quick",
               "Results explained to me clearly", "My coordinator stayed with me",
               "Then to the ward", "Smooth and fast"],
        voice="his own natural voice, friendly and clear, slightly faster, fluid, continuous",
        ambient="soft imaging-area hum, faint beep; no music",
    ),
    PromptPack(
        id="jiuyi_m1_street_02", angle="M1", title="People ask why China",
        person="a 29-year-old Western man with curly hair, denim shirt",
        scene="a street near the hospital at dusk, warm street light",
        camera=("handheld selfie phone camera, gentle shake; "
                "he walks down the street near the hospital while talking to camera"),
        performance="casual, upbeat delivery; he walks and speaks to camera",
        lines=["People ask why China", "The hospitals are modern",
               "The booking was simple", "An English team helped me",
               "I would come back again", "It was easier here"],
        voice="his own natural voice, easygoing, clear English, slightly faster, fluid, continuous",
        ambient="evening street ambience, distant cars, gentle wind; no music",
    ),
    PromptPack(
        id="jiuyi_m6_consult_02", angle="M6", title="Nothing lost in translation",
        person="a 50-year-old woman with straight dark hair, beige cardigan",
        scene="a consultation room with a coordinator's desk and a soft lamp",
        camera=("handheld phone camera, slight natural shake; "
                "she walks into the consult room while talking to camera"),
        performance="calm, grateful delivery; she walks in and speaks to camera",
        lines=["I needed an interpreter", "The clinic provided one",
               "She explained every step", "Forms, costs, all in English",
               "Nothing was lost in translation", "Clear from the start"],
        voice="her own natural voice, calm and clear, slightly faster, fluid, continuous",
        ambient="quiet consult room tone, faint clock tick; no music",
    ),

    # ── 第 2 批（2026-10-13，10 条全新：人物/场景/台词均与首批不重复）──────────────
    PromptPack(
        id="jiuyi_m1_hotel_01", angle="M1", title="Staying near the hospital",
        person="a 45-year-old Western man with short greying hair, olive field jacket",
        scene="a quiet hotel lobby near the hospital, warm wood and soft lamps",
        camera=("handheld phone camera held at arm's length, slight natural shake; "
                "he walks across the hotel lobby while talking to camera"),
        performance="easy, conversational delivery; he walks and speaks to camera",
        lines=["I booked the hotel first", "Short walk to hospital",
               "Morning walks were easy", "My coordinator chose it",
               "Everything was close by", "That made it simple"],
        voice="his own natural voice, calm and clear, slightly faster, fluid, continuous",
        ambient="soft hotel lobby ambience, faint luggage wheels and distant talk; no music",
    ),
    PromptPack(
        id="jiuyi_m1_plaza_01", angle="M1", title="Why I chose China",
        person="a 34-year-old Western woman with wavy auburn hair, light denim jacket",
        scene="a riverside plaza at dusk, city lights reflecting on the water",
        camera=("handheld selfie phone camera, gentle shake; "
                "she walks along the riverside plaza while talking to camera"),
        performance="warm, chatty delivery; she walks and speaks to camera",
        lines=["People ask why China", "For me it was simple",
               "Modern hospitals, English support", "Booking took one call",
               "I felt welcomed here", "I would come again"],
        voice="her own natural voice, bright and clear, slightly faster, fluid, continuous",
        ambient="open riverside ambience, distant traffic and gentle wind; no music",
    ),
    PromptPack(
        id="jiuyi_m2_physio_01", angle="M2", title="Back on my feet",
        person="a 62-year-old Western woman with short grey hair, soft blue cardigan",
        scene="a bright physiotherapy room with mats, rails and large windows",
        camera=("handheld phone camera, slight natural shake; "
                "she walks steadily across the physio room while talking to camera"),
        performance="grounded, grateful delivery; she walks and speaks to camera",
        lines=["I could barely walk", "Then I found this clinic",
               "Therapy here helped me", "Step by step, better",
               "My therapist spoke English", "Now I walk daily"],
        voice="her own natural voice, warm and steady, slightly faster, fluid, continuous",
        ambient="quiet therapy room tone, faint soft footsteps; no music",
    ),
    PromptPack(
        id="jiuyi_m2_hotel_02", angle="M2", title="My morning routine",
        person="a 41-year-old Western man with short dark hair, light stubble, white tee",
        scene="a sunlit hotel room in the morning, curtains half open",
        camera=("handheld phone camera, subtle shake; "
                "he walks across the hotel room while talking to camera"),
        performance="relaxed, matter-of-fact delivery; he walks and speaks to camera",
        lines=["Woke in my hotel", "Coffee, then a taxi",
               "At the clinic early", "Tests first, then doctor",
               "He explained the plan", "Back to rest by noon"],
        voice="his own natural voice, easy and clear, slightly faster, fluid, continuous",
        ambient="quiet hotel room tone, faint morning traffic outside; no music",
    ),
    PromptPack(
        id="jiuyi_m3_waiting_01", angle="M3", title="Not what I pictured",
        person="a 40-year-old Western man with a short beard, grey hooded top",
        scene="a calm hospital waiting area with soft seats and green plants",
        camera=("handheld phone camera, slight natural shake; "
                "he walks through the waiting area while talking to camera"),
        performance="honest, reflective delivery; he walks and speaks to camera",
        lines=["I pictured long queues", "Crowded halls, no English",
               "The waiting room was calm", "A coordinator came to me",
               "Not what I pictured", "Smoother than expected"],
        voice="his own natural voice, calm and clear, slightly faster, fluid, continuous",
        ambient="hushed waiting-area ambience, faint distant chatter; no music",
    ),
    PromptPack(
        id="jiuyi_m3_garden_01", angle="M3", title="Calm, not clinical",
        person="a 36-year-old Western woman with long straight hair, olive green sweater",
        scene="a hospital courtyard garden with trees, benches and soft afternoon light",
        camera=("handheld phone camera, gentle shake; "
                "she walks slowly through the courtyard garden while talking to camera"),
        performance="calm, thoughtful delivery; she walks and speaks to camera",
        lines=["I expected something cold", "Instead, a quiet garden",
               "Patients resting by trees", "It felt like a park",
               "Not clinical at all", "It felt human here"],
        voice="her own natural voice, soft and clear, slightly faster, fluid, continuous",
        ambient="open garden ambience, birdsong and rustling leaves; no music",
    ),
    PromptPack(
        id="jiuyi_m4_entrance_01", angle="M4", title="One day, start to finish",
        person="a 30-year-old Western woman with a dark ponytail, casual grey coat",
        scene="the main entrance of a large modern hospital, morning light",
        camera=("handheld phone camera, slight natural shake; "
                "she walks toward the hospital entrance while talking to camera"),
        performance="clear, upbeat delivery; she walks and speaks to camera",
        lines=["Met at the main gate", "Checked in, then tests",
               "A scan, then results", "The doctor saw me next",
               "All done in one day", "Simple and clear"],
        voice="her own natural voice, bright and clear, slightly faster, fluid, continuous",
        ambient="busy hospital entrance ambience, soft distant voices; no music",
    ),
    PromptPack(
        id="jiuyi_m4_followup_01", angle="M4", title="The follow-up was easy",
        person="a 48-year-old Western man with salt-and-pepper hair, navy shirt",
        scene="a quiet follow-up clinic room with a desk and a bright window",
        camera=("handheld phone camera, subtle shake; "
                "he walks into the follow-up room while talking to camera"),
        performance="steady, friendly delivery; he walks in and speaks to camera",
        lines=["Came back for my follow-up", "Same coordinator, same doctor",
               "They remembered my whole case", "A quick check, then advice",
               "No repeating everything", "That felt reassuring"],
        voice="his own natural voice, calm and clear, slightly faster, fluid, continuous",
        ambient="quiet clinic room tone, faint clock tick; no music",
    ),
    PromptPack(
        id="jiuyi_m5_billing_01", angle="M5", title="What it would cost",
        person="a 44-year-old Western man with glasses and a light blue shirt",
        scene="a reception and billing desk with soft lighting and a small plant",
        camera=("handheld phone camera, slight natural shake; "
                "he walks up to the billing desk and settles while talking to camera"),
        performance="measured, sincere delivery; he walks up and speaks to camera",
        lines=["Before I flew, I asked", "What would this cost",
               "They sent an estimate", "The hospital priced it clearly",
               "No surprises later", "So I booked the trip"],
        voice="his own natural voice, low and measured, slightly faster, fluid, continuous",
        ambient="quiet reception desk tone, faint keyboard taps; no music",
    ),
    PromptPack(
        id="jiuyi_m6_taxi_01", angle="M6", title="From the taxi to the ward",
        person="a 33-year-old Western woman with dark shoulder-length hair, beige trench coat",
        scene="a hospital drop-off area by the entrance, soft daylight",
        camera=("handheld phone camera, slight natural shake; "
                "she walks from the drop-off toward the entrance while talking to camera"),
        performance="warm, reassured delivery; she walks and speaks to camera",
        lines=["The taxi stopped outside", "Someone was waiting",
               "She walked me to the ward", "Every step explained in English",
               "No confusion at all", "I never felt alone"],
        voice="her own natural voice, soft and clear, slightly faster, fluid, continuous",
        ambient="soft outdoor hospital ambience, distant traffic; no music",
    ),
]


def by_id(pack_id: str) -> PromptPack | None:
    for pack in CATALOG:
        if pack.id == pack_id:
            return pack
    return None
