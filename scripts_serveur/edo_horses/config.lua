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
-- Allures du cheval : animations sur mesure (stream/edo_cheval3.ycd) : pas 4 temps, trot diagonal,
-- petit galop 3 temps, galop 4 temps, sabots poses au sol, encolure / dos / queue qui bougent.
-- Changeable en jeu : /chevalallures 1 (edo_cheval) | 2 (anciennes animations du cerf)  (sauvegarde par joueur)
Config.HorseDicts = { 'edo_cheval3', 'creatures@deer@move' }
Config.HorseDict = Config.HorseDicts[1]
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
-- Jambes : VRAIE posture de cavalier (animation sur mesure stream/edo_cavalier.ycd) :
-- jambes qui descendent le long du ventre, genoux en avant, pieds dans les etriers.
-- Changeable en jeu : /chevaljambes 1 | 2 | 3 | 4 (sauvegarde par joueur)
Config.RiderLegs = 1
Config.LegStyles = {
    -- corps VIVANT : une animation par allure (respiration, roulis au pas, rebond au trot, balancier au galop),
    -- calee image par image sur les foulees du cheval
    { name = 'cavalier',        dict = 'edo_cavalier3', prefix = 'ride_b', gaits = true },
    { name = 'cavalier serre',  dict = 'edo_cavalier3', prefix = 'ride_a', gaits = true },
    { name = 'cavalier ecarte', dict = 'edo_cavalier3', prefix = 'ride_c', gaits = true },
    -- postures fixes (anciennes)
    { name = 'fixe',            dict = 'edo_cavalier',  clip = 'ride_b', single = true },
}
Config.RiderBob = true        -- rebond simule (seulement si les os du dos du cheval sont introuvables)
-- La selle suit les os du DOS du cheval (pas de traversee quand le dos monte au galop)
Config.HorseBackBones = {
    mid   = { 'SKEL_Spine2', 'SKEL_Spine3', 'SKEL_Spine1', 'SKEL_Spine_Root', 'SKEL_Spine0' },
    front = { 'SKEL_Neck_1', 'SKEL_Spine3', 'SKEL_Neck0' },
    rear  = { 'SKEL_Pelvis', 'SKEL_Spine0', 'SKEL_Spine_Root' },
}
Config.SeatClearance = 0.03   -- marge au-dessus du dos (m) : plus = moins de contact avec le cheval
Config.GaitClearance = { [0] = 0.0, 0.0, 0.0, 0.0, 0.01 }   -- marge en plus selon l'allure (arret, pas, trot, petit galop, galop) : le corps reste assis
-- part des secousses du dos transmise au corps (0 = immobile, 1 = suit tout) : leger au pas, fort au galop
Config.BackFollow = { [0] = 0.3, 0.3, 0.6, 0.9, 1.0 }
Config.BackSmooth = 0.6   -- (s) lissage de la hauteur moyenne du dos
-- Physique du corps (ressorts amortis) : raideur = vitesse de reaction, amortissement = absence de rebond
Config.RiderPhysics = {
    heightStiff = 260.0, heightDamp = 30.0,   -- haut / bas : le corps pese dans la selle (pas de rebond qui le fait decoller)
    pitchStiff  = 90.0,  pitchDamp  = 13.0,   -- avant / arriere : le buste "suit" l'acceleration avec un temps de retard
    rollStiff   = 70.0,  rollDamp   = 12.0,   -- cotes : le corps se penche dans les virages en douceur
    maxSink     = 0.015,                     -- le corps ne s'enfonce jamais de plus de 1,5 cm sous la selle
}
Config.RiderLeanMax = 9.0     -- inclinaison max dans les virages (degres)

-- Haut du corps : posture "renes" (mains serrees devant), jouee PAR-DESSUS la posture des jambes.
Config.RiderArms = 1
Config.ArmStyles = {
    { name = 'renes', dict = 'anim@move_m@prisoner_cuffed', clip = 'idle', ik = true },
}
-- Point vise par les mains (par rapport a la selle) : avant / hauteur / ecart entre les mains.
-- Reglable en jeu : /chevalmains 0.40 0.04 (sauvegarde auto). Mettre Config.ReinsIK = false pour couper.
Config.ReinsIK = { forward = 0.40, up = 0.04, spread = 0.07 }


-- Position du cavalier sur le dos du cheval (reglable en jeu : /chevalselle x y z, sauvegarde auto)
Config.RiderOffset   = vector3(0.0, -0.08, 0.32)
-- decalage de la selle selon le jeu d'animations du cheval (s'ajoute a /chevalselle) : x, y (- = vers l'arriere), z
Config.DictSeatShift = {}   -- (plus besoin : la selle et le cavalier suivent les os du dos)
Config.RiderRotation = vector3(0.0, 0.0, 0.0)

-- ============================================================
--  SIFFLET / APPARITION
-- ============================================================
Config.SpawnBehind     = 12.0   -- le cheval apparait derriere toi et te rejoint
Config.TeleportDistance = 220.0 -- trop loin : il reapparait pres de toi
Config.MountDistance   = 2.6
-- HARNACHEMENT (selle + bride japonaises) pose sur tous les chevaux du modele
Config.Tack = {
    enabled = true,
    range = 90.0,                               -- distance d'affichage (m)
    sizes = { 100, 120, 140, 160, 180 },        -- tailles disponibles (choisie automatiquement)
    saddle = 'edo_selle_k', bridle = 'edo_bride_k',
    saddleOffset = vector3(0.0, 0.0, -0.12),    -- position de la selle par rapport au cavalier (z - = plus bas)
    riderRaise = 0.03,                          -- le cavalier s'assoit SUR la selle (epaisseur du siege)
    bridleOffset = vector3(0.0, 0.0, 0.0),      -- y = le long de la tete (vers la bouche), z = hauteur
}
-- monter / descendre animes (stream/edo_monte.ycd) : durees en secondes
Config.MountAnims = { dict = 'edo_monte2', mount = 1.90, dismount = 1.45, dismount_run = 0.85 }
Config.MountMoveSpeed = 1.3     -- le cheval avance pendant qu'on monte (0 = il reste immobile)
-- mains posees sur le dos pendant qu'on monte / descend (relatif a la selle) :
-- forward = vers l'avant (pommeau), up = hauteur (negatif = plus bas, contre le dos), spread = ecart gauche/droite
-- windows = moment de l'animation (0 a 1) ou les mains sont posees
Config.MountHands = { forward = 0.20, up = -0.14, spread = 0.10, blendIn = 180, blendOut = 220,
                      windows = { mount = { 0.08, 0.72 }, dismount = { 0.10, 0.66 }, dismount_run = { 0.02, 0.32 } } }
Config.StandHeight = 1.0        -- hauteur du centre du joueur debout au-dessus du sol
Config.RunDismountSpeed = 2.0   -- au-dela : on saute du cheval en marche
Config.RollDismountSpeed = 8.0  -- au-dela (galop) : on roule au sol a la reception
Config.GrazeAfterMs    = 20000  -- seul et immobile : il broute

Config.Debug = false            -- affiche allure / vitesse / endurance a l'ecran
