Config = {}

-- ============================================================
--  GENERAL
-- ============================================================
Config.Model        = `draft_horse`      -- nom du ped (peds.meta)
Config.Command      = 'cheval'           -- /cheval : siffler (fait venir / apparaitre le cheval)
Config.StoreCommand = 'rangercheval'     -- /rangercheval : renvoyer le cheval
Config.WhistleKey   = 'H'                -- touche du sifflet (modifiable par chaque joueur : Parametres > Raccourcis > FiveM)
Config.HudResource  = 'edo_hud'          -- HUD qui recoit exports:SetHorse (optionnel)
Config.HorseHealth  = 600                -- points de vie du cheval

-- Style de controle :
--  'rdr2'     : Z = au pas, chaque appui sur SHIFT monte d'une allure (trot > petit galop > galop).
--               Le galop se maintient en tapotant SHIFT (comme Red Dead).
--  'tsushima' : Z = trot, SHIFT maintenu = galop, CTRL maintenu = au pas (comme Ghost of Tsushima).
Config.ControlStyle = 'rdr2'
Config.GallopKeepMs = 1600               -- (rdr2) sans nouvel appui SHIFT, le galop retombe au petit galop

-- ============================================================
--  PHYSIQUE (m/s, m/s², degres/s)
-- ============================================================
Config.Speed = { walk = 1.9, trot = 4.2, canter = 7.2, gallop = 11.5, reverse = 0.9 }
Config.ReverseAnimRate = 1.0   -- vitesse des pas en reculant (pattes trop rapides : baisse ; trop lentes : monte)
Config.Accel      = 2.6     -- prise de vitesse (inertie)
Config.Decel      = 3.2     -- ralentissement quand on relache Z
Config.Brake      = 8.5     -- freinage avec S
Config.TurnRate   = { idle = 80.0, walk = 95.0, trot = 78.0, canter = 62.0, gallop = 50.0 }
Config.TurnAccel  = 320.0   -- a quelle vitesse le cheval "engage" un virage (plus bas = plus lourd)
Config.TurnSlowdown = 0.88  -- au galop, tourner fort fait perdre un peu de vitesse

Config.MaxSlope      = 0.95 -- pente max montable (0.95 ~ 44 degres)
Config.SlopeSpeedLoss = 0.35 -- en montee la vitesse baisse, en descente elle monte un peu
Config.MaxWaterDepth = 1.4  -- au-dela, le cheval refuse d'avancer
Config.WaterMaxGait  = 2    -- dans l'eau : trot maximum
Config.HorseLength   = 1.15 -- distance centre -> poitrail (detection des obstacles)
Config.CrashSpeed    = 8.0  -- percuter un mur au-dessus de cette vitesse = chute du cavalier
Config.FallThrowSpeed = 9.0 -- chute verticale au-dela = cavalier projete
Config.RiderCrashDamage = 25
Config.PedKnockSpeed = 4.5  -- au-dela, les PNJ percutes tombent

-- ============================================================
--  ENDURANCE
-- ============================================================
Config.MaxStamina = 100.0
Config.StaminaDrain = { canter = 1.5, gallop = 8.0 }   -- par seconde
Config.StaminaRegen = 6.0
Config.StaminaRegenDelayMs = 1500
Config.ExhaustedRecovery = 25.0   -- epuise : trot max jusqu'a ce seuil

-- ============================================================
--  ANIMATIONS
-- ============================================================
Config.HorseDict = 'creatures@deer@move'
-- vitesse "naturelle" de chaque animation : sert a caler les pattes sur la vitesse reelle
-- (si les sabots glissent : monte la valeur ; s'ils pedalent trop vite : baisse-la)
Config.AnimRefSpeed = { walk = 1.9, trot = 4.2, canter = 7.2, gallop = 11.5 }
Config.SlopeAnim = false          -- animations montee/descente du modele : desactivees (elles font basculer le cheval)
Config.TurnAnims = true          -- animations de virage (mettre false si le cheval se deforme en tournant)
Config.TurnAnimThreshold = 40.0   -- vitesse de rotation (deg/s) a partir de laquelle on joue l'animation de virage

-- Cavalier : posture de pilote (jambes ecartees, buste en avant au galop)
Config.RiderAnim = { idle = 'sit', walk = 'sit', trot = 'sit', canter = 'sit_fast', gallop = 'sit_fast',
                     leanL = 'lean_l_slow', leanR = 'lean_r_slow' }
Config.RiderLean = true
-- Jambes : posture assise (changeable en jeu : /chevaljambes 1 a 9, sauvegarde par joueur)
Config.RiderLegs = 1
Config.LegStyles = {
    { name = 'quad (jambes ecartees)', dict = 'veh@bike@quad@front@base',    clip = 'sit' },
    { name = 'chopper (pieds devant)', dict = 'veh@bike@chopper@front@base', clip = 'sit' },
    { name = 'moto cross',             dict = 'veh@bike@dirt@front@base',    clip = 'sit' },
    { name = 'moto cross haute',       dict = 'veh@bike@dirt@front@base',    clip = 'sit_high' },
    { name = 'sportive',               dict = 'veh@bike@sport@front@base',   clip = 'sit' },
    { name = 'jet-ski (tres ecartees)', dict = 'veh@boat@jetski@front@base', clip = 'sit_idle' },
    { name = 'jet-ski passager',        dict = 'veh@boat@jetski@rear@base',  clip = 'sit_idle' },
    { name = 'quad haute',              dict = 'veh@bike@quad@front@base',   clip = 'sit_high' },
    { name = 'quad passager',           dict = 'anim@veh@bike@quad@verus@rear@base', clip = 'sit' },
}

-- Haut du corps : posture "renes" (mains serrees devant), jouee PAR-DESSUS la posture des jambes.
Config.RiderArms = 1
Config.ArmStyles = {
    { name = 'renes', dict = 'anim@move_m@prisoner_cuffed', clip = 'idle', ik = true },
}
-- Point vise par les mains (par rapport a la selle) : avant / hauteur / ecart entre les mains.
-- Reglable en jeu : /chevalmains 0.40 0.04 (sauvegarde auto). Mettre Config.ReinsIK = false pour couper.
Config.ReinsIK = { forward = 0.40, up = 0.04, spread = 0.07 }


-- Position du cavalier sur le dos du cheval (reglable en jeu : /chevalselle x y z, sauvegarde auto)
Config.RiderOffset   = vector3(0.0, -0.05, 0.28)
Config.RiderRotation = vector3(0.0, 0.0, 0.0)

-- ============================================================
--  SIFFLET / APPARITION
-- ============================================================
Config.SpawnBehind     = 12.0   -- le cheval apparait derriere toi et te rejoint
Config.TeleportDistance = 220.0 -- trop loin : il reapparait pres de toi
Config.MountDistance   = 2.6
Config.GrazeAfterMs    = 20000  -- seul et immobile : il broute

Config.Debug = false            -- affiche allure / vitesse / endurance a l'ecran
