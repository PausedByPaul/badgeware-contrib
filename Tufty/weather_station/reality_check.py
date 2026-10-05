"""Outside-vs-here reality checks with lazy category banks."""

try:
    from . import weather_config as cfg
except ImportError:
    import weather_config as cfg


TEMP_DELTA_SIMILAR_C = 1.5
TEMP_DELTA_WARMER_C = 4.0
TEMP_DELTA_MUCH_WARMER_C = 7.0
HUMIDITY_DELTA_SIMILAR = 6
HUMIDITY_DELTA_MUCH = 16

PRESSURE_VERY_LOW_HPA = 980
PRESSURE_LOW_HPA = 1000
PRESSURE_HIGH_HPA = 1025
PRESSURE_VERY_HIGH_HPA = 1040

MOODS = (
    "devil",
    "laugh",
    "cool",
    "coffee",
    "rain",
    "sun",
    "fire",
    "snow",
    "tropical",
    "wind",
    "facepalm",
    "eyes",
    "thermal",
    "water",
    "skeptic",
)

REACTIONS = MOODS + (
    "plant",
    "ice",
    "side_eye",
    "droplet",
    "home",
    "umbrella",
    "cloud",
    "warning",
    "moon",
    "thermometer",
)


OPENERS = {
    "inside_much_warmer": (
        "It is much warmer here.",
        "Here is running several degrees hotter.",
        "The room has opened a heat account.",
        "Indoor temperature has ambitions.",
        "Indoors took heat personally.",
        "The thermal border is not subtle.",
        "Here appears to be hoarding warmth.",
        "The Tufty has found the warm side.",
        "Indoor climate is making bold choices.",
        "Temperature says the room is in charge.",
    ),
    "inside_warmer": (
        "It is warmer here.",
        "The room has a clear thermal lead.",
        "Inside is edging into cosy territory.",
        "Here wins the warmth contest.",
        "Outdoor air is being outvoted.",
        "The temperature gap is noticeable.",
        "Indoor warmth is doing actual work.",
        "The room has a thermal lead.",
        "Indoor warmth is showing off.",
        "Here has chosen cozy.",
    ),
    "inside_much_cooler": (
        "It is much cooler here.",
        "Inside has located the safe zone.",
        "The room is refusing outdoor heat.",
        "Here is running the cool build.",
        "Indoor air has excellent boundaries.",
        "The room found the cool lane.",
        "Cooling strategy appears successful.",
        "Outside heat stopped at the door.",
        "The room is winning by subtraction.",
        "Local air is doing calm work.",
    ),
    "inside_cooler": (
        "It is cooler here.",
        "Inside is slightly more sensible.",
        "The room is shaving off degrees.",
        "Here has a mild cooling advantage.",
        "Outdoor warmth is being moderated.",
        "The thermal gradient is useful.",
        "Inside feels better behaved.",
        "The local air is less dramatic.",
        "Here is keeping its head.",
        "Temperature discipline exists indoors.",
    ),
    "temperatures_similar": (
        "Inside and outside mostly agree.",
        "The temperature split is quiet.",
        "The climates called a truce.",
        "Reality briefly enabled sync.",
        "Temperature drama is unavailable.",
        "Thermal drama is absent.",
        "The climates have reached a truce.",
        "No major thermal scandal detected.",
        "Temperature contrast is behaving.",
        "Both sides seem civil.",
    ),
    "inside_very_humid": (
        "Humidity is getting bold here.",
        "Premium Damp is active.",
        "Local moisture has joined management.",
        "Indoor air is becoming clingy.",
        "Humidity has found a microphone.",
        "The room has a damp opinion.",
        "The room is one fern away.",
        "Local air is over-sharing.",
        "Moisture found management.",
        "Indoor humidity wants a promotion.",
    ),
    "inside_humid": (
        "It is a bit humid here.",
        "Local moisture is nudging upward.",
        "The room feels mildly steamed.",
        "Humidity is present and smug.",
        "Indoor air has texture.",
        "Comfort is meeting damp paperwork.",
        "Local humidity is not hiding.",
        "The room is slightly clingy.",
        "Moisture has entered the chat.",
        "Humidity deserves a side-eye.",
    ),
    "inside_dry": (
        "It is dry here.",
        "Indoor humidity is running lean.",
        "The room has chosen crisp mode.",
        "Moisture is keeping a low profile.",
        "Local air feels paperwork-dry.",
        "Humidity is underachieving indoors.",
        "The air has gone minimalist.",
        "Static electricity may feel invited.",
        "Indoor moisture is rationed.",
        "The room could use fewer desert vibes.",
    ),
    "inside_hot_and_humid": (
        "Warm and humid here.",
        "The room is both hot and clingy.",
        "Indoor air is trying to become soup.",
        "Heat and humidity are collaborating.",
        "The habitat has tropical ambitions.",
        "The room chose sauna logic.",
        "Warmth arrived with moisture backup.",
        "The room is doing damp heat.",
        "Tropical firmware is awake.",
        "Heat arrived with friends.",
    ),
    "inside_hot_and_dry": (
        "Warm and dry here.",
        "The room is doing desert cosplay.",
        "Indoor air feels toasted and tidy.",
        "Heat arrived without moisture.",
        "Local climate has biscuit energy.",
        "The habitat is warm but crisp.",
        "Dry heat is making a small speech.",
        "The room has kiln-adjacent vibes.",
        "Indoor warmth feels over-edited.",
        "The air is warm and withholding.",
    ),
    "inside_cold_and_humid": (
        "Cold and humid here.",
        "The room is offering cellar weather.",
        "Local air feels chilled and damp.",
        "Comfort has entered basement mode.",
        "Cold moisture is a bleak feature.",
        "Indoor climate needs a stern memo.",
        "The habitat is cool and clingy.",
        "Local humidity is not helping the chill.",
        "The room has discovered clammy.",
        "The room selected November.",
    ),
    "inside_cold_and_dry": (
        "Cold and dry here.",
        "The room is crisp, wrongly.",
        "Fridge paperwork is active.",
        "Comfort is wearing thin socks.",
        "Comfort brought thin socks.",
        "Warmth and damp opted out.",
        "The air feels underfunded.",
        "Local air feels underfunded.",
        "Austerity climate is live.",
        "The room needs tea.",
    ),
    "outside_rain_inside_comfortable": (
        "Rain outside, comfort here.",
        "Sky leak, room treaty.",
        "Rain stayed properly outside.",
        "Shelter is earning applause.",
        "Indoors chose standards.",
        "The room declined rain.",
        "Soggy plans remain external.",
        "The sofa beat the sky.",
        "Rain met a useful wall.",
        "Indoor civilization survives.",
    ),
    "outside_rain_inside_humid": (
        "Rain outside, humidity here.",
        "Both sides are discussing moisture.",
        "Moisture crossed borders.",
        "Rain found indoor sympathy.",
        "Water is the theme, unfortunately.",
        "Damp has diplomatic access.",
        "The room heard rain and joined in.",
        "The room joined the drizzle.",
        "Outside leaks; inside clings.",
        "The wet agenda is well represented.",
    ),
    "outside_rain_inside_hot": (
        "Rain outside, heat here.",
        "Outside is wet; the room is simmering.",
        "Rain outside, sauna inside.",
        "The room steamed the plot.",
        "Wet sky, warm room.",
        "Rain met indoor preheat.",
        "The climate split is wet versus warm.",
        "Indoor heat is ignoring the sky leak.",
        "Shelter works, ventilation may not.",
        "The air suggests laundry.",
    ),
    "outside_hot_inside_cool": (
        "Hot outside, cooler here.",
        "Outside is toast. Here isn't.",
        "The room rejected July.",
        "Solar nonsense stayed outside.",
        "Shade has won indoors.",
        "The Tufty found the safe thermal zone.",
        "Outside is spicy; here is managed.",
        "Cooling earns one nod.",
        "The door blocked toast.",
        "Heat stayed outside where it belongs.",
    ),
    "outside_hot_inside_hot": (
        "Hot outside and hot here.",
        "No safe thermal zone detected.",
        "The heat has breached containment.",
        "Heat breached containment.",
        "Both climates are running warm.",
        "Indoor comfort has joined outdoor panic.",
        "The door is not a heat firewall.",
        "Your habitat copied the weather homework.",
        "No cool refuge installed.",
        "Heat has achieved full coverage.",
    ),
    "outside_cold_inside_warm": (
        "Cold outside, warm here.",
        "Outside is fridge. Here isn't.",
        "The room defeated cold.",
        "Indoor warmth earned rent.",
        "Tea has jurisdiction here.",
        "The door did its job.",
        "Shelter has passed inspection.",
        "Cold stayed politely outside.",
        "Heating looks competent.",
        "The room kept civilization.",
    ),
    "outside_freezing_inside_comfortable": (
        "Ice stayed in its lane.",
        "The room refused cryo.",
        "Warmth made a decision.",
        "Cold storage remains outside.",
        "Frost can queue outside.",
        "Indoors chose survival.",
        "The wall beat winter.",
        "Here is legally cozy.",
        "Cold lost the argument.",
        "The room passed winter.",
    ),
    "outside_sunny_inside_dark": (
        "Sunny outside, dark here.",
        "Sun outside, cave indoors.",
        "The room left daylight unread.",
        "Curtains seized power.",
        "Photons were denied entry.",
        "The room has rejected daylight.",
        "Sunshine exists, apparently elsewhere.",
        "The sun got ghosted.",
        "Dust interrogation postponed.",
        "The room chose privacy.",
    ),
    "outside_dark_inside_bright": (
        "Dark outside, bright here.",
        "Night outside, audit lamp here.",
        "The room overruled darkness.",
        "Indoor photons are awake.",
        "Outside slept. Here didn't.",
        "Local lighting has ambition.",
        "The lamp has opinions.",
        "Night met local brightness.",
        "Photons have moved inside.",
        "Your room is ignoring night mode.",
    ),
    "outside_bad_inside_good": (
        "Outside is unpleasant; here is decent.",
        "The room wins today's climate debate.",
        "Outdoor conditions have been rejected.",
        "Inside is the sensible branch.",
        "The habitat is carrying the forecast.",
        "Outside can email its complaints.",
        "Local climate is doing damage control.",
        "Shelter remains undefeated.",
        "The room passes while outside sulks.",
        "Outside sulks. Here works.",
    ),
    "outside_good_inside_bad": (
        "Outside behaves. Here freelances.",
        "Nature passed. Interior climate did not.",
        "The room is the weather problem.",
        "The room needs supervision.",
        "The forecast is not the villain today.",
        "Indoor climate chose drama.",
        "Weather is not the problem.",
        "The room has lost to the sky.",
        "The habitat must explain.",
        "Outside brought balance.",
    ),
    "pressure_very_low": (
        "Pressure is very low.",
        "Pressure has slumped.",
        "Atmospheric pressure looks unsettled.",
        "The air column is slouching.",
        "Low pressure has entered with intent.",
        "The barometer looks theatrical.",
        "Barometric mood is gloomy.",
        "The atmosphere is not standing tall.",
        "The air column slouches.",
        "The weather stack looks unstable.",
    ),
    "pressure_low": (
        "Pressure is low.",
        "The barometer is pessimistic.",
        "Atmosphere looks a little moody.",
        "Pressure is below polite.",
        "The air column seems underfunded.",
        "The air column seems moody.",
        "Low pressure entered softly.",
        "Weather vibes lean unsettled.",
        "Barometric confidence is not high.",
        "The barometer raised an eyebrow.",
    ),
    "pressure_normal": (
        "Pressure looks normal.",
        "The barometer is behaving.",
        "Pressure passed inspection.",
        "The barometer behaves.",
        "The air column has decent posture.",
        "Barometric drama is unavailable.",
        "Pressure readings look civilized.",
        "Atmospheric admin is tidy.",
        "Nothing dramatic from the barometer.",
        "Pressure is steady enough for now.",
    ),
    "pressure_high": (
        "Pressure is high.",
        "The barometer looks confident.",
        "Atmosphere is standing tall.",
        "High pressure has entered politely.",
        "The air column brought credentials.",
        "Pressure is above the casual zone.",
        "Weather stability may be showing off.",
        "The barometer has become optimistic.",
        "Atmospheric confidence detected.",
        "Pressure is doing tidy numbers.",
    ),
    "pressure_very_high": (
        "Pressure is very high.",
        "The barometer is flexing.",
        "Atmosphere has tightened the bolts.",
        "High pressure is making a statement.",
        "The air column is overachieving.",
        "Pressure is standing on business.",
        "Pressure tightened the bolts.",
        "The atmosphere brought a clipboard.",
        "Pressure has gone full management.",
        "The numbers look aggressively stable.",
    ),
    "outdoor_only": (
        "Outside is all we have right now.",
        "Outside reports; here shrugs.",
        "The room declined telemetry.",
        "Local sensors are quiet.",
        "The sky gets the stage.",
        "Indoor data is off shift.",
        "The sensor stick is absent.",
        "No room weather today.",
        "Outside still has receipts.",
        "Here remains mysterious.",
    ),
    "local_only": (
        "Outside is offline.",
        "The room still testifies.",
        "Local sensors carry on.",
        "No internet, still air.",
        "Here has the receipts.",
        "Outdoor data can wait.",
        "The habitat remains measurable.",
        "Network drama stayed external.",
        "The room reports honestly.",
        "Offline mode still knows the room.",
    ),
    "both_unavailable": (
        "Reality is buffering.",
        "Both climates went quiet.",
        "Telemetry has gone for a walk.",
        "No readings, no panic, just silence.",
        "Telemetry left no note.",
        "Weather Station is awake; data is not.",
        "No readings, just manners.",
        "The climate desk stepped out.",
        "The atmosphere declined comment.",
        "Awaiting reality before checking it.",
    ),
}

TAILS = {
    "devil": (
        "Bold strategy.",
        "Questionable, but committed.",
        "This is how reputations happen.",
        "A choice was certainly made.",
        "The audit will be spicy.",
    ),
    "laugh": (
        "Comedy-grade climate control.",
        "Honestly, impressive nonsense.",
        "The numbers are doing material.",
        "A tiny farce with units.",
        "Absurd, yet measurable.",
    ),
    "cool": (
        "Civilisation survives.",
        "Rarely has staying put looked wiser.",
        "Competence, somehow.",
        "The safe zone is real.",
        "Sensible behaviour confirmed.",
    ),
    "coffee": (
        "Tea protocol recommended.",
        "A warm drink may be governance.",
        "Staying in was unusually competent.",
        "Comfort has a mug-shaped answer.",
        "Shelter and caffeine remain undefeated.",
    ),
    "rain": (
        "Moisture remains the main character.",
        "The damp agenda continues.",
        "Umbrella shareholders nod approvingly.",
        "Outdoor plans require waterproofing.",
        "Classic sky leak behaviour.",
    ),
    "sun": (
        "Photons are showing off.",
        "Solar theatre is open.",
        "Brightness budget approved.",
        "The yellow object seems operational.",
        "Daylight has entered production.",
    ),
    "fire": (
        "Cooling has a case.",
        "Hydration deserves priority.",
        "Thermal dignity is absent.",
        "Fans may testify.",
        "The air wants toast.",
    ),
    "snow": (
        "Warmth remains a core dependency.",
        "Frost has management ambitions.",
        "Gloves are infrastructure now.",
        "Winter is compiling locally.",
        "Cold storage is not a lifestyle.",
    ),
    "tropical": (
        "Rainforest paperwork is pending.",
        "A dehumidifier may feel seen.",
        "The air has jungle aspirations.",
        "Moisture is overachieving.",
        "Comfort is wearing a damp shirt.",
    ),
    "wind": (
        "Hair settings may not persist.",
        "Aerodynamics are now relevant.",
        "Loose objects should unionise.",
        "The air has opinions.",
        "Windchill is sharpening pencils.",
    ),
    "facepalm": (
        "Nature is judging quietly.",
        "The room needs a meeting.",
        "This was avoidable, probably.",
        "Choices were made.",
        "The dashboard is disappointed.",
    ),
    "eyes": (
        "Suspicious.",
        "Worth watching.",
        "The numbers are side-eyeing each other.",
        "No conclusions, only eyebrows.",
        "Something is up, scientifically.",
    ),
    "thermal": (
        "Thermal reality has spoken.",
        "Degrees are doing the storytelling.",
        "The heat map has opinions.",
        "Temperature is the loudest signal.",
        "The climate gradient has receipts.",
    ),
    "water": (
        "Humidity has receipts.",
        "Moisture is making policy.",
        "The damp metrics are not subtle.",
        "Water vapour is busy.",
        "The hygrometer looks vindicated.",
    ),
    "skeptic": (
        "Proceed with measured suspicion.",
        "The instruments are unconvinced.",
        "Acceptable, somehow.",
        "The data invites a raised eyebrow.",
        "Reality is doing edge cases.",
    ),
}

CATEGORY_MOODS = {
    "inside_much_warmer": "fire",
    "inside_warmer": "thermal",
    "inside_much_cooler": "cool",
    "inside_cooler": "cool",
    "temperatures_similar": "eyes",
    "inside_very_humid": "tropical",
    "inside_humid": "water",
    "inside_dry": "skeptic",
    "inside_hot_and_humid": "tropical",
    "inside_hot_and_dry": "fire",
    "inside_cold_and_humid": "facepalm",
    "inside_cold_and_dry": "coffee",
    "outside_rain_inside_comfortable": "coffee",
    "outside_rain_inside_humid": "rain",
    "outside_rain_inside_hot": "tropical",
    "outside_hot_inside_cool": "cool",
    "outside_hot_inside_hot": "fire",
    "outside_cold_inside_warm": "coffee",
    "outside_freezing_inside_comfortable": "coffee",
    "outside_sunny_inside_dark": "facepalm",
    "outside_dark_inside_bright": "eyes",
    "outside_bad_inside_good": "cool",
    "outside_good_inside_bad": "devil",
    "pressure_very_low": "skeptic",
    "pressure_low": "eyes",
    "pressure_normal": "cool",
    "pressure_high": "cool",
    "pressure_very_high": "skeptic",
    "outdoor_only": "eyes",
    "local_only": "eyes",
    "both_unavailable": "skeptic",
}

OPENERS.update(
    {
        "inside_much_warmer_and_humid": (
            "Here is much warmer and humid.",
            "The room is winning heat and moisture.",
            "Indoor air is doing tropical maths.",
            "Warmth and dampness have teamed up here.",
            "The local climate is overcommitted.",
            "Tropical firmware selected.",
            "The room is making summer indoors.",
            "The room built a biome.",
            "Heat and damp formed a pact.",
            "The habitat has left subtle behind.",
        ),
        "inside_much_warmer_and_dry": (
            "Here is much warmer and dry.",
            "The room is hot with very tidy moisture.",
            "Indoor air has chosen crisp heat.",
            "Warmth is high; humidity did not RSVP.",
            "The local climate is toasted but lean.",
            "Desert mode has admin rights.",
            "The room is warmer and slightly parched.",
            "Heat is present without the damp subplot.",
            "Here has a dry thermal advantage.",
            "The habitat is auditioning for kiln mode.",
        ),
        "inside_cooler_and_humid": (
            "Here is cooler but humid.",
            "Cool air kept the damp.",
            "The room found clammy.",
            "Chill arrived with moisture.",
            "Here is less warm but not less clingy.",
            "Humidity negotiated immunity.",
            "The cardigan has evidence.",
            "The room is calmer in degrees only.",
            "Here feels cooler with damp metadata.",
            "Cooler, yet damp.",
        ),
        "outside_cloud_inside_comfortable": (
            "Cloud outside, comfort here.",
            "The sky is grey; the room behaves.",
            "Grey sky, sane room.",
            "Cloud cover lost the indoor argument.",
            "Here is handling the grey day well.",
            "Clouds lost indoors.",
            "Outside is muted; here is measured.",
            "The room ignored the gloom.",
            "Indoor comfort beat grey.",
            "Weather is dull; indoors is useful.",
        ),
        "outside_wind_inside_warm": (
            "Wind outside, warmth here.",
            "Gusts outside, warmth here.",
            "The wind can stay on its side.",
            "The room declined gusts.",
            "Shelter did air diplomacy.",
            "Outside has motion; inside has heat.",
            "The room is declining the wind memo.",
            "Moving air lost indoors.",
            "The local air is refusing drama.",
            "Warmth ignored the wind memo.",
        ),
        "outside_wind_inside_cool": (
            "Wind outside, cool here.",
            "Outdoor air is moving and here stays calm.",
            "Gusts outside, cool indoors.",
            "Wind has not improved the indoor plot.",
            "Cool room, busy sky.",
            "The local air is measured and quiet.",
            "The room skipped the gusts.",
            "Busy sky, calm room.",
            "The wind is loud; local thermals are not.",
            "Wind stayed theatrical outside.",
        ),
        "outside_freezing_inside_cold": (
            "Freezing outside, cold here.",
            "Winter has partial access.",
            "Winter has partial access indoors.",
            "Cold is outside and negotiating entry.",
            "The room beat ice, barely.",
            "The habitat needs more warmth.",
            "Cold is negotiating indoors.",
            "Here avoided freezing only.",
            "Comfort needs reinforcements.",
            "Cold remains a local stakeholder.",
        ),
        "outside_cold_inside_cold": (
            "Cold outside and cold here.",
            "Cold copied indoors.",
            "No warm refuge detected.",
            "Cold got indoor access.",
            "The room echoed the forecast.",
            "Cold has representation here.",
            "Comfort missed both columns.",
            "The door owes paperwork.",
            "Local air needs a better plan.",
            "Local air needs a plan.",
        ),
        "outside_sunny_inside_comfortable": (
            "Sunny outside, comfortable here.",
            "Sun outside, sanity here.",
            "Outside has photons; here has balance.",
            "Photons and comfort coexist.",
            "This is the rare sensible split.",
            "The room handled daylight.",
            "Sun performed. Here behaved.",
            "Balance made a rare cameo.",
            "Daylight did not break indoors.",
            "Weather and room are both behaving.",
        ),
        "outside_fog_inside_bright": (
            "Fog outside, bright here.",
            "Fog outside, clarity here.",
            "The room out-resolved the sky.",
            "Fog has failed to enter the room.",
            "Visibility got local help.",
            "Fog failed at the wall.",
            "Indoor photons carried it.",
            "The room rejected ambiguity.",
            "Foggy outside, useful indoors.",
            "Outside blurred. Here didn't.",
        ),
        "pressure_low_and_raining": (
            "Low pressure and rain.",
            "The barometer and sky agree on drama.",
            "Pressure is down and water is up.",
            "Rain has pressure receipts.",
            "The barometer backed drizzle.",
            "Low pressure is not travelling alone.",
            "Rain has brought a pressure receipt.",
            "The atmosphere is leaning into it.",
            "Low pressure brought water.",
            "The barometer called this mood early.",
        ),
        "pressure_high_and_clear": (
            "High pressure and clear skies.",
            "Clear sky, smug barometer.",
            "Pressure brought evidence.",
            "Stability has filed a clean report.",
            "The atmosphere is unusually tidy.",
            "High pressure is doing useful work.",
            "The atmosphere looks tidy.",
            "The weather stack looks well behaved.",
            "Pressure and sky are sharing notes.",
            "The forecast desk may relax slightly.",
        ),
        "local_comfortable": (
            "Here looks comfortable.",
            "The room is behaving.",
            "The room is behaving like a room.",
            "Indoor climate passes the quick audit.",
            "No local climate scandal detected.",
            "The habitat is within ordinary limits.",
            "Here is boring in a useful way.",
            "Comfort metrics are holding steady.",
            "Local air is currently reasonable.",
            "Local air passed audit.",
        ),
    }
)

CATEGORY_MOODS.update(
    {
        "inside_much_warmer_and_humid": "tropical",
        "inside_much_warmer_and_dry": "fire",
        "inside_cooler_and_humid": "water",
        "outside_cloud_inside_comfortable": "cool",
        "outside_wind_inside_warm": "wind",
        "outside_wind_inside_cool": "wind",
        "outside_freezing_inside_cold": "snow",
        "outside_cold_inside_cold": "coffee",
        "outside_sunny_inside_comfortable": "sun",
        "outside_fog_inside_bright": "eyes",
        "pressure_low_and_raining": "rain",
        "pressure_high_and_clear": "cool",
        "local_comfortable": "cool",
    }
)

OPENERS.update(
    {
        "inside_much_warmer_and_drier": (
            "Free trial of desert mode.",
            "Here is much warmer, and the air is leaner.",
            "The room found heat and misplaced moisture.",
            "Indoor climate is hotter with a dry edge.",
            "Warmth is winning here while humidity retreats.",
            "Humidity left the meeting.",
            "Here is several degrees warmer and drier.",
            "The room is running warm with crisp air.",
            "Outside is cooler; here is warmer and drier.",
            "Indoor heat has arrived without damp backup.",
            "The room is hoarding warmth, not water.",
            "Toast climate, furnished.",
            "Dry heat got promoted.",
            "The thermostat has opinions.",
            "Here is warm enough to make dryness obvious.",
            "Cozy became a target.",
            "Static may start lobbying.",
            "Here beats outside on warmth and loses moisture.",
            "Two climates share one wall.",
            "Local warmth is doing the loud part today.",
        ),
        "inside_warmer_and_drier": (
            "Here is warmer and a bit drier.",
            "Warmth arrived, damp left.",
            "The room is crisp-cozy.",
            "Humidity quietly resigned.",
            "The local air is cosier and crisper.",
            "The thermostat seems smug.",
            "The room gained degrees and shed RH.",
            "Outside is cooler and a little wetter.",
            "Warm air brought paperwork.",
            "Dry comfort has entered.",
            "The room edited out damp.",
            "The room is quietly warmer and drier.",
            "Cozy came with static.",
            "The air is tidy-toast.",
            "Here has warmth and a dry margin.",
            "Moisture lost the vote.",
            "Warmth here comes with less cling.",
            "A small desert is forming.",
            "Warmth kept the keys.",
            "The room feels dry-proud.",
        ),
        "inside_much_warmer_and_more_humid": (
            "Here is much warmer and more humid.",
            "Tropical firmware upgraded.",
            "Indoor air is warmer with damp backup.",
            "Heat and damp formed government.",
            "The local climate is warm and clingy.",
            "The room grew weather.",
            "The room is doing heat with texture.",
            "Warmth rose locally and RH came along.",
            "Indoor climate has tropical paperwork.",
            "Warm humidity got ideas.",
            "Here beats outside on both warmth and damp.",
            "A biome is applying here.",
            "Steam-curious air is live.",
            "The thermostat met tropics.",
            "The indoor numbers are warm and damp.",
            "Moist heat took minutes.",
            "The air now has texture.",
            "Furniture entered greenhouse.",
            "Local comfort is negotiating with damp heat.",
            "The room feels fern-ready.",
        ),
        "inside_warmer_and_more_humid": (
            "Here is warmer and more humid.",
            "Warm damp has arrived.",
            "Indoor air has gained degrees and RH.",
            "The room chose tropical lite.",
            "Humidity brought a plus-one.",
            "Here has a warm, damp advantage.",
            "The air is getting chewy.",
            "Heat came with receipts.",
            "Damp warmth is campaigning.",
            "The room nudged both readings upward.",
            "A small biome is pending.",
            "The room found texture.",
            "Comfort now has clauses.",
            "Moisture joined the warmth.",
            "Here is warmer with a clingy subplot.",
            "The thermostat enabled cling.",
            "Warm air got damp ideas.",
            "The habitat is warmer and slightly damp.",
            "The habitat feels fern-curious.",
            "The room has a humid thermal lead.",
        ),
        "inside_cooler_and_drier": (
            "Here is cooler and drier.",
            "Cool, dry, competent.",
            "The room read the manual.",
            "Comfort seems accidental.",
            "No drama. Just air.",
            "Here is cooler without a damp penalty.",
            "The room understood the task.",
            "Sensible settings appeared.",
            "Dry coolness has manners.",
            "Cool minus damp wins.",
            "The air found professionalism.",
            "Climate control looks real.",
            "Someone configured comfort.",
            "The indoor column is cool and lean.",
            "Here is cooler and less clingy.",
            "The habitat found a crisp corner.",
            "Cooler air here is also drier air.",
            "The room has reduced the drama and RH.",
            "Local climate is quietly crisp.",
            "The habitat got sensible.",
        ),
        "inside_cooler_and_more_humid": (
            "Here is cooler but more humid.",
            "The room lost heat and kept moisture.",
            "Cool damp has arrived.",
            "Humidity won the appeal.",
            "Socks have been briefed.",
            "Here is cooler, but RH is higher.",
            "Temperature helped. Damp stayed.",
            "Cooling happened; dryness did not.",
            "The cave has electricity.",
            "Moisture kept its desk.",
            "Here is cooler with a damp footnote.",
            "Cooling got a wet footnote.",
            "The room is calm in degrees only.",
            "Local air is cooler and more adhesive.",
            "The habitat traded heat for humidity.",
            "Here is cooler, not exactly fresher.",
            "The cool side has a moisture clause.",
            "Indoor comfort is negotiating with RH.",
            "The room found shade and kept damp.",
            "Cooler air here still carries water.",
        ),
    }
)

CATEGORY_MOODS.update(
    {
        "inside_much_warmer_and_drier": "fire",
        "inside_warmer_and_drier": "thermal",
        "inside_much_warmer_and_more_humid": "tropical",
        "inside_warmer_and_more_humid": "water",
        "inside_cooler_and_drier": "cool",
        "inside_cooler_and_more_humid": "water",
    }
)

CATEGORY_REACTIONS = dict(CATEGORY_MOODS)
CATEGORY_REACTIONS.update(
    {
        "inside_much_warmer_and_humid": "plant",
        "inside_much_warmer_and_dry": "fire",
        "inside_much_warmer_and_drier": "fire",
        "inside_warmer_and_drier": "thermometer",
        "inside_much_warmer_and_more_humid": "plant",
        "inside_warmer_and_more_humid": "droplet",
        "inside_cooler_and_drier": "ice",
        "inside_cooler_and_more_humid": "droplet",
        "inside_hot_and_humid": "plant",
        "inside_hot_and_dry": "fire",
        "inside_cold_and_dry": "coffee",
        "outside_rain_inside_comfortable": "coffee",
        "outside_rain_inside_humid": "umbrella",
        "outside_hot_inside_cool": "ice",
        "outside_cold_inside_warm": "coffee",
        "outside_freezing_inside_comfortable": "coffee",
        "outside_sunny_inside_dark": "side_eye",
        "outside_dark_inside_bright": "moon",
        "pressure_low_and_raining": "umbrella",
        "pressure_high_and_clear": "sun",
        "local_comfortable": "home",
    }
)

_ANTI_TEMPLATE_TAILS = {
    "tail_inside_much_warmer": (
        "The thermostat looks smug.",
        "Indoor summer got ideas.",
        "Cozy is over budget.",
        "The sofa is preheating.",
        "Thermal ambition noted.",
    ),
    "tail_inside_warmer": (
        "The thermostat may boast.",
        "Cozy filed paperwork.",
        "Warmth won locally.",
        "The room seems pleased.",
        "Thermal admin agrees.",
    ),
    "tail_inside_much_cooler": (
        "The room kept its nerve.",
        "Shade appears competent.",
        "Toast was rejected.",
        "The wall did work.",
        "Cooling has receipts.",
    ),
    "tail_inside_cooler": (
        "Sensible preset found.",
        "The room chose peace.",
        "Comfort stopped shouting.",
        "The furniture can relax.",
        "Cooler heads prevailed.",
    ),
    "tail_temperatures_similar": (
        "Two climates, one opinion.",
        "Diplomacy has succeeded.",
        "The wall is off duty.",
        "Consensus feels suspicious.",
        "Drama has been cancelled.",
    ),
    "tail_inside_very_humid": (
        "Premium Damp continues.",
        "The fern lobby approves.",
        "Air texture is enabled.",
        "Moisture found a desk.",
        "Towels may gain power.",
    ),
    "tail_inside_humid": (
        "Damp is getting settled.",
        "The hygrometer raised a hand.",
        "Moisture brought minutes.",
        "Air texture increased.",
        "The room feels gently sticky.",
    ),
    "tail_inside_dry": (
        "Houseplants look legal.",
        "Static is networking.",
        "Hydration is external.",
        "Moisture left quietly.",
        "Crispness has authority.",
    ),
    "tail_inside_hot_and_humid": (
        "Soup-adjacent, regrettably.",
        "The fern lobby cheers.",
        "Air texture has mass.",
        "A small monsoon is pending.",
        "Tropical middleware runs.",
    ),
    "tail_inside_hot_and_dry": (
        "Kiln-lite is active.",
        "Humidity rage-quit.",
        "Roasting seems needless.",
        "The oven comparison hurts.",
        "Dry heat has admin.",
    ),
    "tail_inside_cold_and_humid": (
        "Socks matter now.",
        "November has credentials.",
        "Condensation is browsing.",
        "Cardigan logic applies.",
        "The cave has power.",
    ),
    "tail_inside_cold_and_dry": (
        "Sleeves are infrastructure.",
        "Warmth is optional.",
        "Furniture entered storage.",
        "February has installed.",
        "The thermostat is away.",
    ),
    "tail_outside_rain_inside_comfortable": (
        "Dry socks remain possible.",
        "Boundaries are working.",
        "The walls passed.",
        "Weather containment holds.",
        "Excellent shelter behaviour.",
    ),
    "tail_outside_rain_inside_humid": (
        "Damp got inside help.",
        "Moisture coordinated calendars.",
        "The wet theme persists.",
        "The room joined in.",
        "Humidity took notes.",
    ),
    "tail_outside_rain_inside_hot": (
        "Steam is on standby.",
        "The vents owe answers.",
        "Laundry logic applies.",
        "Warm rain got indoors.",
        "Atmosphere seems steamed.",
    ),
    "tail_outside_hot_inside_cool": (
        "Shade has a case.",
        "The wall blocked toast.",
        "Cooling earned a nod.",
        "July lost at the door.",
        "Civilisation gets one point.",
    ),
    "tail_outside_hot_inside_hot": (
        "Comfort left early.",
        "The door failed talks.",
        "Hydration looks relevant.",
        "Everything chose toast.",
        "Cooling opened a ticket.",
    ),
    "tail_outside_cold_inside_warm": (
        "Winter lost at the wall.",
        "Tea remains plausible.",
        "The room kept standards.",
        "Heating may keep its job.",
        "Civilisation has heating.",
    ),
    "tail_outside_freezing_inside_comfortable": (
        "Gloves stay optional.",
        "Winter lacks clearance.",
        "The room passed survival.",
        "Frost can queue outside.",
        "Warmth kept jurisdiction.",
    ),
    "tail_outside_sunny_inside_dark": (
        "Curtains declined access.",
        "Photons met a firewall.",
        "Privacy defeated daylight.",
        "The sun was ignored.",
        "Indoor HDR is cancelled.",
    ),
    "tail_outside_dark_inside_bright": (
        "The lamp is employed.",
        "Night lost indoors.",
        "Photons kept office hours.",
        "Visibility filed locally.",
        "Darkness lacks access.",
    ),
    "tail_outside_bad_inside_good": (
        "The sofa has evidence.",
        "Staying put wins narrowly.",
        "Shelter looks competent.",
        "The wall earns praise.",
        "Indoor standards hold.",
    ),
    "tail_outside_good_inside_bad": (
        "The thermostat looks implicated.",
        "Nature is winning.",
        "The room must explain.",
        "Indoor choices continue.",
        "The audit will be spicy.",
    ),
    "tail_pressure_very_low": (
        "Morale remains unmeasured.",
        "The barometer lowered expectations.",
        "Air-column budget cuts.",
        "Monday energy detected.",
        "Confidence is unavailable.",
    ),
    "tail_pressure_low": (
        "Morale remains unmeasured.",
        "The subplot is forming.",
        "The air column called tired.",
        "Expectations have lowered.",
        "The barometer is brooding.",
    ),
    "tail_pressure_normal": (
        "The dashboard seems disappointed.",
        "Drama has been postponed.",
        "Boring build selected.",
        "The barometer is reasonable.",
        "Even the air agrees.",
    ),
    "tail_pressure_high": (
        "The barometer looks smug.",
        "Paperwork is in order.",
        "The air column has a CV.",
        "Pressure owns the place.",
        "Admin is competent.",
    ),
    "tail_pressure_very_high": (
        "The atmosphere is standing tall.",
        "Management has arrived.",
        "Executive authority acquired.",
        "The air column is showing off.",
        "Confidence exceeds requirements.",
    ),
    "tail_outdoor_only": (
        "Indoors is off record.",
        "Only the sky filed.",
        "Local telemetry took leave.",
        "The room declined comment.",
        "No fiction will be added.",
    ),
    "tail_local_only": (
        "Outside is hearsay.",
        "Local sensors have the floor.",
        "The room kept receipts.",
        "Network drama can wait.",
        "Inside remains available.",
    ),
    "tail_both_unavailable": (
        "Reality lacks reality.",
        "Evidence is out for tea.",
        "The dashboard is improvising.",
        "Eyebrow retained.",
        "Witness protection suspected.",
    ),
    "tail_inside_much_warmer_and_humid": (
        "Tropical firmware insists.",
        "Heat and damp merged.",
        "The room grew weather.",
        "Air texture has mass.",
        "Greenhouse status pending.",
    ),
    "tail_inside_much_warmer_and_dry": (
        "Arizona installed locally.",
        "Dry heat has privileges.",
        "Static may organize.",
        "Humidity left the keys.",
        "Heat runs maintenance.",
    ),
    "tail_inside_cooler_and_humid": (
        "Moisture kept its desk.",
        "The cardigan has evidence.",
        "Damp negotiated immunity.",
        "Coolness has cave notes.",
        "Socks were briefed.",
    ),
    "tail_outside_cloud_inside_comfortable": (
        "The room ignored the gloom.",
        "Clouds lost the argument.",
        "Indoor balance held.",
        "The sofa remains useful.",
        "Grey stayed outside.",
    ),
    "tail_outside_wind_inside_warm": (
        "Gusts lack access.",
        "The wall has boundaries.",
        "Aerodynamics end here.",
        "Warmth ignored the memo.",
        "Loose objects stay bored.",
    ),
    "tail_outside_wind_inside_cool": (
        "Gusts lack access.",
        "The sky kept the drama.",
        "Aerodynamics stayed outside.",
        "Loose objects may relax.",
        "Cool air kept still.",
    ),
    "tail_outside_cold_inside_cold": (
        "Jumper difficulty enabled.",
        "Cold got guest access.",
        "Heating has questions.",
        "Sleeves are infrastructure.",
        "The forecast copied itself.",
    ),
    "tail_outside_sunny_inside_comfortable": (
        "Morale patch pending.",
        "The sky remembered brightness.",
        "Solar output passed.",
        "Comfort survived photons.",
        "The sun behaved itself.",
    ),
    "tail_outside_fog_inside_bright": (
        "Contrast wins locally.",
        "Fog lacks indoor rights.",
        "Visibility got help.",
        "The room stayed readable.",
        "Mist remained outside.",
    ),
    "tail_pressure_low_and_raining": (
        "Waterproof ink required.",
        "Wet bureaucracy continues.",
        "Rain brought evidence.",
        "The clouds coordinated.",
        "Damp package submitted.",
    ),
    "tail_pressure_high_and_clear": (
        "Supporting documentation arrived.",
        "The barometer is correct.",
        "Stability filed cleanly.",
        "The sky cooperated.",
        "Forecast admin can relax.",
    ),
    "tail_local_comfortable": (
        "Do not touch anything.",
        "Boring is excellent.",
        "The thermostat may stay.",
        "No intervention required.",
        "Unprecedented calm continues.",
    ),
    "tail_inside_warmer_and_drier": (
        "Humidity was not consulted.",
        "Static took minutes.",
        "The room chose crisp.",
        "Moisture resigned quietly.",
        "Tidy heat persists.",
    ),
    "tail_inside_warmer_and_more_humid": (
        "Humidity got promoted.",
        "Texture is enabled.",
        "The room feels adhesive.",
        "Tropical lite continues.",
        "The hygrometer is busy.",
    ),
    "tail_inside_cooler_and_drier": (
        "No notes from physics.",
        "Comfort read the manual.",
        "The room chose restraint.",
        "Professional air, somehow.",
        "Please change nothing.",
    ),
    "tail_inside_cooler_and_more_humid": (
        "Humidity won the appeal.",
        "Socks have been briefed.",
        "The cave has electricity.",
        "Condensation is thinking.",
        "Moisture kept minutes.",
    ),
    "tail_inside_much_warmer_and_drier": (
        "Desert mode got promoted.",
        "Static chairs the meeting.",
        "Humidity left the building.",
        "The toaster theory holds.",
        "Furniture entered dry heat.",
    ),
    "tail_inside_much_warmer_and_more_humid": (
        "Soup-adjacent territory.",
        "Humidity joined management.",
        "The room is fern-ready.",
        "Tropical firmware upgraded.",
        "Moist heat filed papers.",
    ),
}

MOODS = MOODS + tuple(_ANTI_TEMPLATE_TAILS)
TAILS.update(_ANTI_TEMPLATE_TAILS)

_ANTI_TEMPLATE_CATEGORY_MOODS = {
    "inside_much_warmer": "tail_inside_much_warmer",
    "inside_warmer": "tail_inside_warmer",
    "inside_much_cooler": "tail_inside_much_cooler",
    "inside_cooler": "tail_inside_cooler",
    "temperatures_similar": "tail_temperatures_similar",
    "inside_very_humid": "tail_inside_very_humid",
    "inside_humid": "tail_inside_humid",
    "inside_dry": "tail_inside_dry",
    "inside_hot_and_humid": "tail_inside_hot_and_humid",
    "inside_hot_and_dry": "tail_inside_hot_and_dry",
    "inside_cold_and_humid": "tail_inside_cold_and_humid",
    "inside_cold_and_dry": "tail_inside_cold_and_dry",
    "outside_rain_inside_comfortable": "tail_outside_rain_inside_comfortable",
    "outside_rain_inside_humid": "tail_outside_rain_inside_humid",
    "outside_rain_inside_hot": "tail_outside_rain_inside_hot",
    "outside_hot_inside_cool": "tail_outside_hot_inside_cool",
    "outside_hot_inside_hot": "tail_outside_hot_inside_hot",
    "outside_cold_inside_warm": "tail_outside_cold_inside_warm",
    "outside_freezing_inside_comfortable": "tail_outside_freezing_inside_comfortable",
    "outside_sunny_inside_dark": "tail_outside_sunny_inside_dark",
    "outside_dark_inside_bright": "tail_outside_dark_inside_bright",
    "outside_bad_inside_good": "tail_outside_bad_inside_good",
    "outside_good_inside_bad": "tail_outside_good_inside_bad",
    "pressure_very_low": "tail_pressure_very_low",
    "pressure_low": "tail_pressure_low",
    "pressure_normal": "tail_pressure_normal",
    "pressure_high": "tail_pressure_high",
    "pressure_very_high": "tail_pressure_very_high",
    "outdoor_only": "tail_outdoor_only",
    "local_only": "tail_local_only",
    "both_unavailable": "tail_both_unavailable",
    "inside_much_warmer_and_humid": "tail_inside_much_warmer_and_humid",
    "inside_much_warmer_and_dry": "tail_inside_much_warmer_and_dry",
    "inside_cooler_and_humid": "tail_inside_cooler_and_humid",
    "outside_cloud_inside_comfortable": "tail_outside_cloud_inside_comfortable",
    "outside_wind_inside_warm": "tail_outside_wind_inside_warm",
    "outside_wind_inside_cool": "tail_outside_wind_inside_cool",
    "outside_cold_inside_cold": "tail_outside_cold_inside_cold",
    "outside_sunny_inside_comfortable": "tail_outside_sunny_inside_comfortable",
    "outside_fog_inside_bright": "tail_outside_fog_inside_bright",
    "pressure_low_and_raining": "tail_pressure_low_and_raining",
    "pressure_high_and_clear": "tail_pressure_high_and_clear",
    "local_comfortable": "tail_local_comfortable",
    "inside_warmer_and_drier": "tail_inside_warmer_and_drier",
    "inside_warmer_and_more_humid": "tail_inside_warmer_and_more_humid",
    "inside_cooler_and_drier": "tail_inside_cooler_and_drier",
    "inside_cooler_and_more_humid": "tail_inside_cooler_and_more_humid",
    "inside_much_warmer_and_drier": "tail_inside_much_warmer_and_drier",
    "inside_much_warmer_and_more_humid": "tail_inside_much_warmer_and_more_humid",
}

_ANTI_TEMPLATE_REACTIONS = {
    category: CATEGORY_REACTIONS.get(category, CATEGORY_MOODS.get(category, "skeptic"))
    for category in _ANTI_TEMPLATE_CATEGORY_MOODS
}
CATEGORY_MOODS.update(_ANTI_TEMPLATE_CATEGORY_MOODS)
CATEGORY_REACTIONS.update(_ANTI_TEMPLATE_REACTIONS)

COMBINATION_FAMILIES = {
    "inside_hot_and_humid": "temperature_humidity",
    "inside_hot_and_dry": "temperature_humidity",
    "inside_cold_and_humid": "temperature_humidity",
    "inside_cold_and_dry": "temperature_humidity",
    "inside_much_warmer_and_humid": "temperature_humidity",
    "inside_much_warmer_and_dry": "temperature_humidity",
    "inside_much_warmer_and_drier": "temperature_humidity",
    "inside_warmer_and_drier": "temperature_humidity",
    "inside_much_warmer_and_more_humid": "temperature_humidity",
    "inside_warmer_and_more_humid": "temperature_humidity",
    "inside_cooler_and_humid": "temperature_humidity",
    "inside_cooler_and_drier": "temperature_humidity",
    "inside_cooler_and_more_humid": "temperature_humidity",
    "outside_rain_inside_comfortable": "weather_indoor_comfort",
    "outside_rain_inside_humid": "weather_indoor_humidity",
    "outside_rain_inside_hot": "weather_temperature",
    "outside_hot_inside_cool": "outside_inside_temperature",
    "outside_hot_inside_hot": "outside_inside_temperature",
    "outside_cold_inside_warm": "outside_inside_temperature",
    "outside_freezing_inside_comfortable": "outside_inside_temperature",
    "outside_freezing_inside_cold": "outside_inside_temperature",
    "outside_cold_inside_cold": "outside_inside_temperature",
    "outside_sunny_inside_dark": "weather_light",
    "outside_dark_inside_bright": "weather_light",
    "outside_bad_inside_good": "weather_indoor_comfort",
    "outside_good_inside_bad": "weather_indoor_comfort",
    "outside_cloud_inside_comfortable": "weather_indoor_comfort",
    "outside_wind_inside_warm": "weather_temperature",
    "outside_wind_inside_cool": "weather_temperature",
    "outside_sunny_inside_comfortable": "weather_indoor_comfort",
    "outside_fog_inside_bright": "weather_light",
    "pressure_low_and_raining": "pressure_weather",
    "pressure_high_and_clear": "pressure_weather",
}


def category_names():
    return tuple(sorted(OPENERS.keys()))


def category_count(category):
    if category not in OPENERS:
        return 0
    mood = CATEGORY_MOODS.get(category, "skeptic")
    return len(OPENERS[category]) * len(TAILS[mood])


def total_comment_count():
    return sum(category_count(category) for category in OPENERS)


def combined_comment_count():
    return sum(category_count(category) for category in COMBINATION_FAMILIES)


def single_factor_comment_count():
    return total_comment_count() - combined_comment_count()


def combination_family_counts():
    counts = {}
    for category, family in COMBINATION_FAMILIES.items():
        counts[family] = counts.get(family, 0) + category_count(category)
    return counts


def temp_humidity_combined_categories():
    return tuple(
        sorted(
            category
            for category, family in COMBINATION_FAMILIES.items()
            if family == "temperature_humidity"
        )
    )


def get_category_records(category):
    if category not in OPENERS:
        category = "temperatures_similar"
    mood = CATEGORY_MOODS.get(category, "skeptic")
    reaction = CATEGORY_REACTIONS.get(category, mood)
    records = []
    tails = TAILS[mood]
    for i, opener in enumerate(OPENERS[category]):
        for j, tail in enumerate(tails):
            phrase_id = "rc-{}-{:02d}{:02d}".format(category, i + 1, j + 1)
            records.append({"id": phrase_id, "text": opener + " " + tail, "mood": mood, "reaction": reaction})
    return records


def fallback_record(category):
    mood = CATEGORY_MOODS.get(category, "skeptic")
    reaction = CATEGORY_REACTIONS.get(category, mood)
    if "warmer" in category and "drier" in category:
        text = "Warmer and drier here. Bold climate strategy."
    elif "warmer" in category and ("humid" in category or "humidity" in category):
        text = "Warmer and more humid here. The room has plans."
    elif "cooler" in category and "drier" in category:
        text = "Cooler and drier here. Sensible air detected."
    elif "cooler" in category and ("humid" in category or "humidity" in category):
        text = "Cooler but more humid here. Mixed results."
    elif "rain" in category:
        text = "Rain outside. Shelter wins."
    elif "pressure" in category:
        text = "Pressure is worth watching."
    elif "sunny" in category or "clear" in category:
        text = "Sun outside. Reality is showing off."
    elif "cold" in category:
        text = "Cold is the main story. Warmth matters."
    elif "hot" in category:
        text = "Heat is the main story. Hydration matters."
    elif category == "outdoor_only":
        text = "Outside reports. Here is unavailable."
    elif category == "local_only":
        text = "Here reports. Outside is unavailable."
    elif category == "both_unavailable":
        text = "Awaiting reality before checking it."
    else:
        text = "Reality noted. Suspicious."
    return {"id": "rc-fallback-" + str(category), "text": text, "mood": mood, "reaction": reaction}


def normalize_pressure_hpa(value):
    if value is None:
        return None
    pressure = float(value)
    if pressure > 2000:
        pressure = pressure / 100.0
    return pressure


def pressure_category(value):
    pressure = normalize_pressure_hpa(value)
    if pressure is None:
        return None
    if pressure < PRESSURE_VERY_LOW_HPA:
        return "pressure_very_low"
    if pressure < PRESSURE_LOW_HPA:
        return "pressure_low"
    if pressure > PRESSURE_VERY_HIGH_HPA:
        return "pressure_very_high"
    if pressure > PRESSURE_HIGH_HPA:
        return "pressure_high"
    return "pressure_normal"


def temp_delta_category(delta):
    if delta is None:
        return None
    if delta >= TEMP_DELTA_MUCH_WARMER_C:
        return "inside_much_warmer"
    if delta >= TEMP_DELTA_WARMER_C:
        return "inside_warmer"
    if delta > TEMP_DELTA_SIMILAR_C:
        return "inside_warmer"
    if delta <= -TEMP_DELTA_MUCH_WARMER_C:
        return "inside_much_cooler"
    if delta <= -TEMP_DELTA_WARMER_C:
        return "inside_cooler"
    if delta < -TEMP_DELTA_SIMILAR_C:
        return "inside_cooler"
    return "temperatures_similar"


def humidity_delta_category(delta):
    if delta is None:
        return None
    if delta <= -HUMIDITY_DELTA_MUCH:
        return "inside_much_drier_than_outside"
    if delta < -HUMIDITY_DELTA_SIMILAR:
        return "inside_drier_than_outside"
    if delta >= HUMIDITY_DELTA_MUCH:
        return "inside_much_more_humid_than_outside"
    if delta > HUMIDITY_DELTA_SIMILAR:
        return "inside_more_humid_than_outside"
    return "humidity_similar"


def local_humidity_category(value):
    if value is None:
        return None
    if value < 30:
        return "inside_very_dry"
    if value < 38:
        return "inside_dry"
    if value > 72:
        return "inside_very_humid"
    if value > 62:
        return "inside_humid"
    return "inside_comfortable_humidity"


def local_temp_state(value):
    if value is None:
        return None
    if value >= 27:
        return "inside_hot"
    if value <= 17:
        return "inside_cold"
    if 19 <= value <= 24:
        return "inside_comfortable"
    return "inside_mild"


def outdoor_temp_state(value):
    if value is None:
        return None
    if value <= 0:
        return "outside_freezing"
    if value <= 7:
        return "outside_cold"
    if value >= 27:
        return "outside_hot"
    if 12 <= value <= 23:
        return "outside_comfortable"
    return "outside_mild"


def is_rainy(condition):
    name = str(condition or "").lower()
    return "rain" in name or "drizzle" in name or "shower" in name or "thunder" in name


def is_sunny(condition):
    name = str(condition or "").lower()
    return "sun" in name or "clear" in name


def is_dark_local(local):
    lux = None if not local else local.get("lux")
    return lux is not None and lux < 20


def derive_context(outdoor, local):
    outdoor = outdoor or {}
    local = local or {}
    out_t = outdoor.get("temperature_c")
    in_t = local.get("temperature_c")
    out_h = outdoor.get("humidity_percent")
    in_h = local.get("humidity_percent")
    out_p = normalize_pressure_hpa(outdoor.get("pressure_hpa"))
    in_p = normalize_pressure_hpa(local.get("pressure_hpa"))

    temp_delta = None if out_t is None or in_t is None else round(float(in_t) - float(out_t), 1)
    humidity_delta = None if out_h is None or in_h is None else int(round(float(in_h) - float(out_h)))
    pressure = in_p if in_p is not None else out_p

    return {
        "outdoor_available": bool(outdoor),
        "local_available": any(local.get(k) is not None for k in ("temperature_c", "humidity_percent", "pressure_hpa", "lux")),
        "outdoor_temp": out_t,
        "local_temp": in_t,
        "outdoor_humidity": out_h,
        "local_humidity": in_h,
        "outdoor_pressure_hpa": out_p,
        "local_pressure_hpa": in_p,
        "pressure_hpa": pressure,
        "temperature_delta_c": temp_delta,
        "humidity_delta_percent": humidity_delta,
        "temp_delta_category": temp_delta_category(temp_delta),
        "humidity_delta_category": humidity_delta_category(humidity_delta),
        "local_humidity_category": local_humidity_category(in_h),
        "local_temp_state": local_temp_state(in_t),
        "outdoor_temp_state": outdoor_temp_state(out_t),
        "pressure_category": pressure_category(pressure),
        "rainy": is_rainy(outdoor.get("condition")),
        "sunny": is_sunny(outdoor.get("condition")),
        "local_dark": is_dark_local(local),
        "outdoor_condition": outdoor.get("condition"),
        "precipitation_probability": outdoor.get("precipitation_probability"),
        "wind_speed": outdoor.get("wind_speed"),
        "is_day": outdoor.get("is_day"),
        "pressure_trend": local.get("pressure_trend") or outdoor.get("pressure_trend"),
    }


def rank_signals(context):
    signals = []
    if not context.get("outdoor_available") and not context.get("local_available"):
        return [(100, "both_unavailable")]
    if not context.get("outdoor_available"):
        signals.append((90, "local_only"))
    if not context.get("local_available"):
        signals.append((90, "outdoor_only"))

    temp_state = context.get("local_temp_state")
    hum_state = context.get("local_humidity_category")
    out_state = context.get("outdoor_temp_state")
    delta_category = context.get("temp_delta_category")
    humidity_delta = context.get("humidity_delta_category")
    pressure_kind = context.get("pressure_category")

    if delta_category in ("inside_much_warmer", "inside_warmer") and humidity_delta in (
        "inside_much_drier_than_outside",
        "inside_drier_than_outside",
    ):
        category = "inside_much_warmer_and_drier" if delta_category == "inside_much_warmer" else "inside_warmer_and_drier"
        score = 106 if delta_category == "inside_much_warmer" else 95
        signals.append((score, category))
    if delta_category in ("inside_much_warmer", "inside_warmer") and humidity_delta in (
        "inside_much_more_humid_than_outside",
        "inside_more_humid_than_outside",
    ):
        category = "inside_much_warmer_and_more_humid" if delta_category == "inside_much_warmer" else "inside_warmer_and_more_humid"
        score = 104 if delta_category == "inside_much_warmer" else 94
        signals.append((score, category))
    if delta_category in ("inside_much_cooler", "inside_cooler") and humidity_delta in (
        "inside_much_drier_than_outside",
        "inside_drier_than_outside",
    ):
        signals.append((94, "inside_cooler_and_drier"))
    if delta_category in ("inside_much_cooler", "inside_cooler") and humidity_delta in (
        "inside_much_more_humid_than_outside",
        "inside_more_humid_than_outside",
    ):
        signals.append((93, "inside_cooler_and_more_humid"))

    if temp_state == "inside_hot" and hum_state in ("inside_humid", "inside_very_humid"):
        signals.append((96, "inside_hot_and_humid"))
    if temp_state == "inside_hot" and hum_state in ("inside_dry", "inside_very_dry"):
        signals.append((92, "inside_hot_and_dry"))
    if temp_state == "inside_cold" and hum_state in ("inside_humid", "inside_very_humid"):
        signals.append((92, "inside_cold_and_humid"))
    if temp_state == "inside_cold" and hum_state in ("inside_dry", "inside_very_dry"):
        signals.append((90, "inside_cold_and_dry"))
    if context.get("rainy") and temp_state == "inside_comfortable":
        signals.append((98, "outside_rain_inside_comfortable"))
    if context.get("rainy") and hum_state in ("inside_humid", "inside_very_humid"):
        signals.append((94, "outside_rain_inside_humid"))
    if context.get("rainy") and temp_state == "inside_hot":
        signals.append((94, "outside_rain_inside_hot"))
    if out_state == "outside_hot" and context.get("temp_delta_category") in ("inside_much_cooler", "inside_cooler"):
        signals.append((99, "outside_hot_inside_cool"))
    if out_state == "outside_hot" and temp_state == "inside_hot":
        signals.append((97, "outside_hot_inside_hot"))
    if out_state == "outside_cold" and temp_state in ("inside_comfortable", "inside_hot"):
        signals.append((96, "outside_cold_inside_warm"))
    if out_state == "outside_freezing" and temp_state == "inside_comfortable":
        signals.append((99, "outside_freezing_inside_comfortable"))
    if context.get("sunny") and context.get("local_dark"):
        signals.append((99, "outside_sunny_inside_dark"))
    if context.get("rainy") and pressure_kind in ("pressure_low", "pressure_very_low"):
        signals.append((97, "pressure_low_and_raining"))
    if context.get("sunny") and pressure_kind in ("pressure_high", "pressure_very_high"):
        signals.append((83, "pressure_high_and_clear"))

    if delta_category:
        score = 86 if "much" in delta_category else 70
        signals.append((score, delta_category))
    if hum_state in ("inside_very_humid", "inside_humid", "inside_dry", "inside_very_dry"):
        category = "inside_very_humid" if hum_state == "inside_very_humid" else "inside_humid" if hum_state == "inside_humid" else "inside_dry"
        signals.append((72, category))
    if pressure_kind:
        score = 64 if pressure_kind in ("pressure_low", "pressure_high") else 74
        signals.append((score, pressure_kind))

    if not signals:
        signals.append((10, "local_comfortable"))
    return sorted(signals, reverse=True)


def select_category(outdoor, local):
    context = derive_context(outdoor, local)
    ranked = rank_signals(context)
    return ranked[0][1], context, ranked


def semantic_signature(context):
    return (
        context.get("temp_delta_category"),
        context.get("humidity_delta_category"),
        context.get("local_humidity_category"),
        context.get("local_temp_state"),
        context.get("outdoor_temp_state"),
        context.get("pressure_category"),
        bool(context.get("rainy")),
        bool(context.get("sunny")),
        bool(context.get("local_dark")),
        bool(context.get("outdoor_available")),
        bool(context.get("local_available")),
    )


def _trim(items, limit):
    if limit <= 0:
        return []
    return list(items or [])[-limit:]


def _presentation(record, fit_checker):
    if fit_checker is None:
        return dict(record)
    try:
        fitted = fit_checker(record)
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
        fitted = None
    if not fitted:
        return None
    selected = dict(record)
    selected.update(fitted)
    return selected


def _first_fitting(records, fit_checker, allowed):
    for record in records:
        if allowed(record):
            selected = _presentation(record, fit_checker)
            if selected is not None:
                return selected
    return None


def _fitting_fallback(category, fit_checker):
    fallback = fallback_record(category)
    selected = _presentation(fallback, fit_checker)
    if selected is not None:
        return selected
    compact = dict(fallback)
    compact["text"] = "Reality checked."
    return _presentation(compact, fit_checker) or compact


def select_record(category, global_recent=None, category_recent=None, fit_checker=None):
    global_recent = set(global_recent or [])
    category_recent = set(category_recent or [])
    records = get_category_records(category)
    if not records:
        return _fitting_fallback(category, fit_checker)

    selected = _first_fitting(records, fit_checker, lambda record: record["id"] not in global_recent and record["id"] not in category_recent)
    if selected is not None:
        return selected
    selected = _first_fitting(records, fit_checker, lambda record: record["id"] not in global_recent)
    if selected is not None:
        return selected
    selected = _first_fitting(records, fit_checker, lambda record: record["id"] not in category_recent)
    if selected is not None:
        return selected
    selected = _first_fitting(records, fit_checker, lambda _record: True)
    if selected is not None:
        return selected
    return _fitting_fallback(category, fit_checker)


class RealityCheckEngine:
    def __init__(self, history=None, refresh_ms=None):
        history = history or {}
        self.refresh_ms = cfg.COMMENTARY_REFRESH_MS if refresh_ms is None else int(refresh_ms)
        self.global_recent = _trim(history.get("global", []), cfg.GLOBAL_REALITY_HISTORY)
        self.category_recent = {}
        category_history = history.get("categories", {})
        if isinstance(category_history, dict):
            for category, ids in category_history.items():
                self.category_recent[category] = _trim(ids, cfg.PER_CATEGORY_REALITY_HISTORY)
        self.current = None
        self.current_category = None
        self.current_signature = None
        self.last_selected_ms = None

    def select(self, outdoor, local, now_ms=0, force=False, fit_checker=None):
        category, context, ranked = select_category(outdoor, local)
        signature = semantic_signature(context)
        expired = self.last_selected_ms is None or int(now_ms) - int(self.last_selected_ms) >= self.refresh_ms
        changed = signature != self.current_signature
        if not force and self.current is not None and not expired and not changed:
            return self.current, context, ranked, False

        record = select_record(category, self.global_recent, self.category_recent.get(category, []), fit_checker)
        self.global_recent = _trim(self.global_recent + [record["id"]], cfg.GLOBAL_REALITY_HISTORY)
        self.category_recent[category] = _trim(
            self.category_recent.get(category, []) + [record["id"]],
            cfg.PER_CATEGORY_REALITY_HISTORY,
        )
        self.current = record
        self.current_category = category
        self.current_signature = signature
        self.last_selected_ms = int(now_ms)
        return record, context, ranked, True

    def export_history(self):
        return {
            "global": list(self.global_recent),
            "categories": dict(self.category_recent),
        }
