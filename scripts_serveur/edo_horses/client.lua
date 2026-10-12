-- EDO HORSES 1.0 : monture physique (inertie, allures, pentes, obstacles, chutes)
-- Le cheval monte est pilote de facon "cinematique" : le script calcule sa vitesse, sa rotation,
-- le suivi du sol et les collisions, puis cale les animations (pas / trot / petit galop / galop,
-- virages, montees, descentes) sur la vitesse reelle.

local horse, horseNet = nil, nil
local legDebug   -- defini plus bas (diagnostic)
local mounted, busy = false, false
local savedRagdoll = true

-- etat physique
local speed, yawRate, vz = 0.0, 0.0, 0.0
local gait, lastSpur = 0, 0           -- 0 arret, 1 pas, 2 trot, 3 petit galop, 4 galop
local hOff = 1.0                      -- hauteur du centre du cheval au-dessus du sol
local posZ = 0.0
local stamina, exhausted, lastDrain = Config.MaxStamina, false, 0
local curClip, curRider = nil, nil
local act = nil   -- animation en cours : monter / descendre / sauter
local slope = 0.0
local idleSince = 0
local grazing = false

local GAIT_LABEL = { [0] = 'ARRÊT', 'AU PAS', 'TROT', 'PETIT GALOP', 'GALOP' }

local seatOffset = Config.RiderOffset
local seatRot = Config.RiderRotation
do
    local kvp = GetResourceKvpString('edo_horses_seat3')
    if kvp then
        local x, y, z = kvp:match('([%-%d%.]+) ([%-%d%.]+) ([%-%d%.]+)')
        if x then seatOffset = vector3(tonumber(x), tonumber(y), tonumber(z)) end
    end
end

-- ------------------------------------------------------------
-- utilitaires
-- ------------------------------------------------------------
local function notify(msg)
    BeginTextCommandThefeedPost('STRING')
    AddTextComponentSubstringPlayerName(msg)
    EndTextCommandThefeedPostTicker(false, false)
end

local function help(msg)
    BeginTextCommandDisplayHelp('STRING')
    AddTextComponentSubstringPlayerName(msg)
    EndTextCommandDisplayHelp(0, false, false, -1)
end

local function loadDict(d)
    if HasAnimDictLoaded(d) then return true end
    RequestAnimDict(d)
    local t = GetGameTimer() + 5000
    while not HasAnimDictLoaded(d) and GetGameTimer() < t do Wait(0) end
    return HasAnimDictLoaded(d)
end

local function loadModel(m)
    if not IsModelInCdimage(m) then return false end
    RequestModel(m)
    local t = GetGameTimer() + 10000
    while not HasModelLoaded(m) and GetGameTimer() < t do Wait(0) end
    return HasModelLoaded(m)
end

local function approach(v, target, rate)
    if v < target then return math.min(target, v + rate) end
    return math.max(target, v - rate)
end

local function fwdVec(h)
    local r = math.rad(h)
    return -math.sin(r), math.cos(r)
end

-- sol sous (x, y) entre zTop et zBot (monde + objets), renvoie z ou nil
local function groundAt(x, y, zTop, zBot)
    local ray = StartExpensiveSynchronousShapeTestLosProbe(x, y, zTop, x, y, zBot, 17, horse or 0, 7)
    local _, hit, pos = GetShapeTestResult(ray)
    if hit == 1 then return pos.z end
    return nil
end

-- obstacle entre deux points (monde + vehicules + objets)
local function blocked(x1, y1, z1, x2, y2, z2)
    local ray = StartExpensiveSynchronousShapeTestLosProbe(x1, y1, z1, x2, y2, z2, 19, horse or 0, 7)
    local _, hit = GetShapeTestResult(ray)
    return hit == 1
end

local function isAlive(e) return e and DoesEntityExist(e) and not IsEntityDead(e) end

-- ------------------------------------------------------------
-- animations
-- ------------------------------------------------------------
local function bandOf(v)
    local a = math.abs(v)
    if a < 0.15 then return 0 end
    if a < (Config.Speed.walk + Config.Speed.trot) * 0.5 then return 1 end
    if a < (Config.Speed.trot + Config.Speed.canter) * 0.5 then return 2 end
    if a < (Config.Speed.canter + Config.Speed.gallop) * 0.5 then return 3 end
    return 4
end

local BAND_NAME = { [1] = 'walk', [2] = 'trot', [3] = 'canter', [4] = 'gallop' }

local function horseClip()
    local band = bandOf(speed)
    if band == 0 then
        if yawRate > 25.0 then return 'idle_turn_l', 1.0 end
        if yawRate < -25.0 then return 'idle_turn_r', 1.0 end
        return 'idle', 1.0
    end
    if speed < 0 then return 'walk', math.max(0.6, -speed / Config.AnimRefSpeed.walk) end
    local name = BAND_NAME[band]
    local clip = name
    if Config.TurnAnims and yawRate > Config.TurnAnimThreshold then clip = name .. '_turn_l'
    elseif Config.TurnAnims and yawRate < -Config.TurnAnimThreshold then clip = name .. '_turn_r'
    elseif Config.SlopeAnim and slope > Config.SlopeAnim then clip = name .. '_fwd_upp'
    elseif Config.SlopeAnim and slope < -Config.SlopeAnim then clip = name .. '_fwd_dwn' end
    local rate = math.abs(speed) / Config.AnimRefSpeed[name]
    return clip, math.max(0.65, math.min(1.45, rate))
end

-- recul : le cycle de marche est joue A L'ENVERS, image par image -> les pattes reculent une par une
local backPhase, walkDur = 0.0, nil
local curHorseClip = nil
local function updateHorseAnim(dt)
    local clip, rate = horseClip()
    curHorseClip = clip
    local reverse = speed < 0 and clip == 'walk'
    local key = reverse and 'walk_reverse' or clip
    if key ~= curClip or not IsEntityPlayingAnim(horse, Config.HorseDict, clip, 3) then
        TaskPlayAnim(horse, Config.HorseDict, clip, 4.0, -4.0, -1, 1, 0.0, false, false, false)
        if reverse and curClip ~= 'walk_reverse' then backPhase = 0.0 end
        curClip = key
    end
    if reverse then
        if not walkDur or walkDur <= 0 then walkDur = GetAnimDuration(Config.HorseDict, 'walk') end
        local dur = (walkDur and walkDur > 0) and walkDur or 1.1
        backPhase = (backPhase - dt * rate * Config.ReverseAnimRate / dur) % 1.0
        SetEntityAnimSpeed(horse, Config.HorseDict, clip, 0.0)
        SetEntityAnimCurrentTime(horse, Config.HorseDict, clip, backPhase)
    else
        SetEntityAnimSpeed(horse, Config.HorseDict, clip, rate)
    end
end

local armStyle = 1   -- une seule posture : renes
local handY, handZ = Config.ReinsIK and Config.ReinsIK.forward or 0.3, Config.ReinsIK and Config.ReinsIK.up or 0.2
do
    local kvp = GetResourceKvpString('edo_horses_hands4')
    if kvp then
        local a, b = kvp:match('([%-%d%.]+) ([%-%d%.]+)')
        if a then handY, handZ = tonumber(a), tonumber(b) end
    end
end
local legStyle = tonumber(GetResourceKvpString('edo_horses_legs4') or '') or Config.RiderLegs or 1
if not Config.LegStyles[legStyle] then legStyle = 1 end
local function legDict() return Config.LegStyles[legStyle].dict end
-- mouvements du corps : rebond synchronise sur les foulees, inclinaison dans les virages et a l'acceleration
local bodyRoll, bodyPitch, lastSpeed, lastAttach = 0.0, 0.0, 0.0, nil
local BOB = { [1] = { 0.010, 2 }, [2] = { 0.026, 2 }, [3] = { 0.038, 1 }, [4] = { 0.030, 1 } }
-- suivi du DOS du cheval : la selle monte/descend et bascule exactement comme les os de son dos
local backBones, backRest = nil, nil
local function boneLocal(name)
    local idx = GetEntityBoneIndexByName(horse, name)
    if not idx or idx == -1 then return nil end
    local w = GetWorldPositionOfEntityBone(horse, idx)
    return idx, GetOffsetFromEntityGivenWorldCoords(horse, w.x, w.y, w.z)
end
local tack = {}            -- harnachement (selle + bride) par cheval : [ped] = { saddle, bridle, ks, kb, ... }
local function seatShift()
    local sh = Config.DictSeatShift and Config.DictSeatShift[Config.HorseDict] or vector3(0.0, 0.0, 0.0)
    local t = horse and tack[horse]
    if t and t.saddle and Config.Tack and Config.Tack.enabled then
        sh = sh + vector3(0.0, 0.0, (Config.Tack.riderRaise or 0.03) * t.ks / 100.0)
    end
    return sh
end
local backCalibAt = nil   -- (obsolete, garde pour compatibilite)
-- REFERENCE DU DOS : positions des os du dos quand le cheval est DEBOUT AU REPOS (animations normales du jeu).
-- Prise automatiquement quand le cheval est immobile, sauvegardee, et jamais prise sur la pose brute.
local REF = nil
do
    local k = GetResourceKvpString('edo_horses_backref2')
    if k then
        local v = {}
        for n in k:gmatch('[-%d%.]+') do v[#v + 1] = tonumber(n) end
        if #v == 7 then REF = { mid = vector3(v[1], v[2], v[3]), front = vector3(0.0, v[4], v[5]), rear = vector3(0.0, v[6], v[7]) } end
    end
end
local function firstBone(h, list)
    for _, n in ipairs(list) do
        local i = GetEntityBoneIndexByName(h, n)
        if i and i ~= -1 then return { name = n, idx = i } end
    end
end
local function bonePos(h, b)
    local w = GetWorldPositionOfEntityBone(h, b.idx)
    return GetOffsetFromEntityGivenWorldCoords(h, w.x, w.y, w.z)
end
local function backBonesOf(h)
    local mid = firstBone(h, Config.HorseBackBones.mid)
    if not mid then return nil end
    return { mid = mid, front = firstBone(h, Config.HorseBackBones.front), rear = firstBone(h, Config.HorseBackBones.rear) }
end
local function captureRef(h)
    local bb = backBonesOf(h)
    if not bb or not bb.front or not bb.rear then return false end
    local m, f, r = bonePos(h, bb.mid), bonePos(h, bb.front), bonePos(h, bb.rear)
    REF = { mid = m, front = f, rear = r }
    SetResourceKvp('edo_horses_backref2', ('%.4f %.4f %.4f %.4f %.4f %.4f %.4f'):format(m.x, m.y, m.z, f.y, f.z, r.y, r.z))
    return true
end
-- mouvement du dos par rapport a la reference : hauteur, avancee, tangage
local function backDelta(h, bb)
    if not bb or not REF then return nil, 0.0, 0.0 end
    local m = bonePos(h, bb.mid)
    local pitch = 0.0
    if bb.front and bb.rear then
        local f, r = bonePos(h, bb.front), bonePos(h, bb.rear)
        local a = math.deg(math.atan(f.z - r.z, f.y - r.y)) - math.deg(math.atan(REF.front.z - REF.rear.z, REF.front.y - REF.rear.y))
        pitch = math.max(-15.0, math.min(15.0, a))
    end
    return m.z - REF.mid.z, pitch, m.y - REF.mid.y
end
local function findBack()
    backBones = horse and backBonesOf(horse) or nil
    backRest = REF
    if backBones then
        print(('[edo_horses] dos du cheval suivi : %s / %s / %s (reference %s)'):format(backBones.mid.name,
            backBones.front and backBones.front.name or '-', backBones.rear and backBones.rear.name or '-', REF and 'ok' or 'a prendre'))
    else
        print('[edo_horses] os du dos introuvables : rebond simule')
    end
end
local function backMotion()
    if not backBones or not REF then return nil, 0.0, 0.0 end
    return backDelta(horse, backBones)
end

-- enveloppe du dos : suit le HAUT des foulees (le corps ne descend jamais dans le cheval),
-- puis seule une partie des secousses est transmise au cavalier selon l'allure
local ENV = { z = nil, y = nil, p = nil }
local function envelope(key, v, dt)
    local e = ENV[key]
    if not e then ENV[key] = v return v end
    if key == 'z' and v > e then e = e + (v - e) * math.min(1.0, dt * 25.0)
    else e = e + (v - e) * math.min(1.0, dt / (Config.BackSmooth or 0.6)) end
    ENV[key] = e
    return e
end

-- PHYSIQUE DU CAVALIER : ressorts amortis (le corps suit le cheval avec un leger retard et un rebond naturel,
-- comme le "secondary motion" des jeux recents) au lieu d'etre colle de facon rigide
local SPR = { z = { x = 0.0, v = 0.0 }, p = { x = 0.0, v = 0.0 }, r = { x = 0.0, v = 0.0 } }
local function spring(s, target, k, c, dt)
    local steps = math.max(1, math.ceil(dt / 0.008))
    local h = dt / steps
    for _ = 1, steps do
        local acc = k * (target - s.x) - c * s.v
        s.v = s.v + acc * h
        s.x = s.x + s.v * h
    end
    return s.x
end
local function riderBody(ped, band, phase, dt)
    local tz, ty = 0.0, 0.0
    local backDz, backPitch, backDy = backMotion()
    if backDz then
        local f = (Config.BackFollow and Config.BackFollow[band]) or 1.0
        local ez = envelope('z', backDz, dt)
        tz = math.max(-0.25, math.min(0.25, ez + (backDz - ez) * f))
        ty = math.max(-0.4, math.min(0.4, envelope('y', backDy, dt)))
        local ep = envelope('p', backPitch, dt)
        backPitch = ep + (backPitch - ep) * f
    elseif band > 0 and BOB[band] and Config.RiderBob then
        local amp, fq = BOB[band][1], BOB[band][2]
        tz = amp * math.sin(2 * math.pi * fq * phase)
    end
    tz = tz + Config.SeatClearance + (Config.GaitClearance[band] or 0.0)
    local accel = dt > 0 and (speed - lastSpeed) / dt or 0.0
    lastSpeed = speed
    local tRoll = math.max(-Config.RiderLeanMax, math.min(Config.RiderLeanMax, -yawRate * 0.10 * math.min(1.0, math.abs(speed) / 3.0)))
    local tPitch = math.max(-6.0, math.min(6.0, accel * 1.2)) - (backPitch or 0.0)
    local P = Config.RiderPhysics
    local z = spring(SPR.z, tz, P.heightStiff, P.heightDamp, dt)
    local p = spring(SPR.p, tPitch, P.pitchStiff, P.pitchDamp, dt)
    local r = spring(SPR.r, tRoll, P.rollStiff, P.rollDamp, dt)
    -- le corps ne descend jamais sous la marge de securite (pas de traversee du dos)
    if z < tz - P.maxSink then z = tz - P.maxSink; SPR.z.x = z; SPR.z.v = math.max(0.0, SPR.z.v) end
    local sh = seatShift()
    AttachEntityToEntity(ped, horse, -1, seatOffset.x + sh.x, seatOffset.y + sh.y + ty, seatOffset.z + sh.z + z,
        seatRot.x + p, seatRot.y + r, seatRot.z, false, false, false, true, 2, true)
    return z
end

local function updateRiderAnim(ped, dt)
    dt = dt or 0.0
    local band = bandOf(speed)
    local ls = Config.LegStyles[legStyle]
    local dict = legDict()
    local clip, phase = nil, 0.0
    if ls.gaits then
        local g = band == 0 and 'idle' or BAND_NAME[band]
        if speed < 0 then g = 'walk' end
        clip = ls.prefix .. '_' .. g
    else
        local key = band == 0 and 'idle' or BAND_NAME[band]
        clip = Config.RiderAnim[key] or 'sit'
        if clip == 'sit' or ls.single then clip = ls.clip end
    end
    local changed = false
    if clip ~= curRider or not IsEntityPlayingAnim(ped, dict, clip, 3) then
        TaskPlayAnim(ped, dict, clip, 6.0, -6.0, -1, 1, 0.0, false, false, false)
        curRider = clip
        changed = true
    end
    -- le corps du cavalier suit EXACTEMENT les foulees du cheval (meme phase d'animation)
    if ls.gaits and band > 0 and horse and curHorseClip then
        phase = GetEntityAnimCurrentTime(horse, Config.HorseDict, curHorseClip) or 0.0
        SetEntityAnimSpeed(ped, dict, clip, 0.0)
        SetEntityAnimCurrentTime(ped, dict, clip, phase)
    elseif ls.gaits then
        SetEntityAnimSpeed(ped, dict, clip, 1.0)
    end
    local bob = 0.0
    if horse then bob = riderBody(ped, band, phase, dt) end
    -- haut du corps : calque optionnel (l'animation vivante contient deja bras et buste)
    local arms = Config.ArmStyles[armStyle]
    if arms and arms.dict and not ls.gaits and HasAnimDictLoaded(arms.dict) and (changed or not IsEntityPlayingAnim(ped, arms.dict, arms.clip, 3)) then
        TaskPlayAnim(ped, arms.dict, arms.clip, 4.0, -4.0, -1, 49, 0.0, false, false, false)
    end
    if arms and arms.dict and ls.gaits and IsEntityPlayingAnim(ped, arms.dict, arms.clip, 3) then
        StopAnimTask(ped, arms.dict, arms.clip, 2.0)
    end
    -- IK des bras : les mains tiennent les renes au-dessus des cuisses (suivent le rebond du corps)
    if arms and arms.ik and Config.ReinsIK and horse then
        for i, side in ipairs({ -1.0, 1.0 }) do
            local sh = seatShift()
            local p = GetOffsetFromEntityInWorldCoords(horse, seatOffset.x + sh.x + side * Config.ReinsIK.spread, seatOffset.y + sh.y + handY, seatOffset.z + sh.z + handZ + bob * 0.6)
            SetIkTarget(ped, i == 1 and 3 or 4, 0, 0, p.x, p.y, p.z, 0, 150, 150)
        end
    end
end

-- ------------------------------------------------------------
-- monter / descendre
-- ------------------------------------------------------------
local function attachRider(ped)
    local sh = seatShift()
    AttachEntityToEntity(ped, horse, -1, seatOffset.x + sh.x, seatOffset.y + sh.y, seatOffset.z + sh.z,
        seatRot.x, seatRot.y, seatRot.z, false, false, false, true, 2, true)
end

local function releaseHorse()
    grazing = false
    if not horse or not DoesEntityExist(horse) then return end
    FreezeEntityPosition(horse, false)
    ClearPedTasks(horse)
    curClip = nil
    idleSince = GetGameTimer()
end

-- ------------------------------------------------------------
-- MONTER / DESCENDRE ANIMES (stream/edo_monte2.ycd) : le corps suit une trajectoire fluide autour du cheval
-- cles : t, ecart sur le cote, avant/arriere, hauteur (0 = debout au sol, 1 = selle), +dz, orientation (deg)
-- ------------------------------------------------------------
local ACT_KEYS = {
    mount = {   -- facon RDR2 : marche a cote, agrippe, a plat ventre en travers de la selle, jambe par-dessus
        { 0.00, 0.75, 0.10, 0.0, 0.00, -20 }, { 0.12, 0.66, 0.08, 0.0, 0.02, -35 },
        { 0.24, 0.62, 0.06, 0.0, -0.08, -45 }, { 0.40, 0.30, 0.02, 1.0, 0.09, -70 },
        { 0.54, 0.26, 0.02, 1.0, 0.08, -70 }, { 0.70, 0.14, 0.00, 1.0, 0.13, -32 },
        { 0.85, 0.03, 0.00, 1.0, 0.04, -6 }, { 1.00, 0.00, 0.00, 1.0, 0.00, 0 } },
    dismount = {
        { 0.00, 0.00, 0.00, 1.0, 0.00, 0 }, { 0.16, 0.02, 0.00, 1.0, 0.06, -5 },
        { 0.38, 0.20, 0.00, 1.0, 0.20, -35 }, { 0.58, 0.55, 0.02, 0.45, 0.10, -80 },
        { 0.78, 0.74, 0.04, 0.0, -0.14, -45 }, { 1.00, 0.80, 0.05, 0.0, 0.00, -15 } },
    dismount_run = {
        { 0.00, 0.00, 0.00, 1.0, 0.00, 0 }, { 0.30, 0.25, 0.00, 1.0, 0.12, -25 },
        { 0.60, 0.75, 0.05, 0.4, 0.10, -15 }, { 0.80, 1.00, 0.10, 0.0, -0.15, -8 },
        { 1.00, 1.05, 0.12, 0.0, 0.00, -5 } },
}
local function hermite(ts, vs, t)
    local n = #ts
    if t <= ts[1] then return vs[1] end
    if t >= ts[n] then return vs[n] end
    local i = 1
    while ts[i + 1] < t do i = i + 1 end
    local function m(j)
        if j == 1 or j == n then return 0.0 end
        return (vs[j + 1] - vs[j - 1]) / (ts[j + 1] - ts[j - 1])
    end
    local h = ts[i + 1] - ts[i]
    local u = (t - ts[i]) / h
    local u2, u3 = u * u, u * u * u
    return vs[i] * (2 * u3 - 3 * u2 + 1) + m(i) * h * (u3 - 2 * u2 + u) + vs[i + 1] * (-2 * u3 + 3 * u2) + m(i + 1) * h * (u3 - u2)
end
local function wrap180(a) return (a + 180.0) % 360.0 - 180.0 end
local function sideFree(side)
    local p = GetEntityCoords(horse)
    local q = GetOffsetFromEntityInWorldCoords(horse, -side * 1.3, 0.0, 0.0)
    local h = StartExpensiveSynchronousShapeTestLosProbe(p.x, p.y, p.z, q.x, q.y, q.z, 1 + 16, horse, 7)
    local _, hit = GetShapeTestResult(h)
    return hit ~= 1
end
local function startAct(kind, side)
    local ped = PlayerPedId()
    local K = ACT_KEYS[kind]
    local sh = seatShift()
    local sx, sy, sz = seatOffset.x + sh.x, seatOffset.y + sh.y, seatOffset.z + sh.z
    local standZ = (Config.StandHeight or 1.0) - hOff
    local a = { kind = kind, side = side, t0 = GetGameTimer(), dur = Config.MountAnims[kind],
                clip = kind .. (side > 0 and '_l' or '_r'), ts = {}, xs = {}, ys = {}, zs = {}, yaws = {} }
    for i, k in ipairs(K) do
        a.ts[i] = k[1]
        a.xs[i] = sx - side * k[2]
        a.ys[i] = sy + k[3]
        a.zs[i] = standZ + (sz - standZ) * k[4] + k[5]
        a.yaws[i] = k[6] * side
    end
    if kind == 'mount' then   -- on part de la position reelle du joueur
        local pp = GetEntityCoords(ped)
        local o = GetOffsetFromEntityGivenWorldCoords(horse, pp.x, pp.y, pp.z)
        a.xs[1], a.ys[1], a.zs[1] = o.x, o.y, o.z
        a.yaws[1] = a.yaws[2] + wrap180(GetEntityHeading(ped) - GetEntityHeading(horse) - a.yaws[2])
    end
    act = a
    TaskPlayAnim(ped, Config.MountAnims.dict, a.clip, 6.0, -6.0, -1, 2, 0.0, false, false, false)
end

local dismount
local function stepAct()
    local ped = PlayerPedId()
    local a = act
    local t = (GetGameTimer() - a.t0) / (a.dur * 1000.0)
    if t >= 1.0 then
        act = nil
        if a.kind == 'mount' then
            curRider = nil
            for _, sp in pairs(SPR) do sp.x, sp.v = 0.0, 0.0 end
            updateRiderAnim(ped, 0.0)
        else
            local yaw = a.yaws[#a.yaws]
            dismount(false, { clip = a.clip, heading = GetEntityHeading(horse) + yaw, run = a.kind == 'dismount_run', speed = a.speed or 0.0, side = a.side })
        end
        return
    end
    if not IsEntityPlayingAnim(ped, Config.MountAnims.dict, a.clip, 3) then
        TaskPlayAnim(ped, Config.MountAnims.dict, a.clip, 8.0, -8.0, -1, 2, 0.0, false, false, false)
    end
    -- comme dans RDR2 : le cheval avance doucement pendant qu'on monte
    if a.kind == 'mount' and (Config.MountMoveSpeed or 0.0) > 0.0 then
        speed = Config.MountMoveSpeed * math.min(1.0, t / 0.25)
    end
    SetEntityAnimSpeed(ped, Config.MountAnims.dict, a.clip, 0.0)
    SetEntityAnimCurrentTime(ped, Config.MountAnims.dict, a.clip, math.min(0.999, t))
    AttachEntityToEntity(ped, horse, -1, hermite(a.ts, a.xs, t), hermite(a.ts, a.ys, t), hermite(a.ts, a.zs, t),
        0.0, 0.0, hermite(a.ts, a.yaws, t), false, false, false, true, 2, true)
    -- les mains s'appuient VRAIMENT sur le dos du cheval (la ou serait la selle), pas dans le vide
    local win = Config.MountHands and Config.MountHands.windows[a.kind]
    if win and t >= win[1] and t <= win[2] then
        local H = Config.MountHands
        local sh = seatShift()
        local near, far
        local tk = tack[horse]
        if tk and tk.saddlePos then
            -- selle presente : main du cote du joueur sur le POMMEAU, l'autre sur le TROUSSEQUIN
            local sc = 0.62 * tk.ks / 100.0
            local sp = tk.saddlePos
            near = { sp.x - a.side * 0.06, sp.y + 0.25 * sc, sp.z + 0.20 * sc + 0.02 }
            far  = { sp.x + a.side * 0.05, sp.y - 0.21 * sc, sp.z + 0.12 * sc + 0.02 }
        else
            local bz = 0.0
            if backBones and REF then
                local dz = backDelta(horse, backBones)
                bz = math.max(-0.15, math.min(0.15, dz or 0.0))
            end
            local baseZ = seatOffset.z + sh.z + H.up + bz
            near = { seatOffset.x + sh.x - a.side * H.spread, seatOffset.y + sh.y + H.forward, baseZ }
            far  = { seatOffset.x + sh.x + a.side * H.spread, seatOffset.y + sh.y + H.forward - 0.16, baseZ - 0.02 }
        end
        local nearPart = a.side > 0 and 3 or 4     -- 3 = main gauche, 4 = main droite
        local farPart  = a.side > 0 and 4 or 3
        for _, it in ipairs({ { nearPart, near }, { farPart, far } }) do
            local p = GetOffsetFromEntityInWorldCoords(horse, it[2][1], it[2][2], it[2][3])
            SetIkTarget(ped, it[1], 0, 0, p.x, p.y, p.z, 0, H.blendIn, H.blendOut)
        end
    end
end

function dismount(thrown, soft)
    if not mounted then return end
    local ped = PlayerPedId()
    mounted = false
    act = nil
    DetachEntity(ped, true, false)
    if soft then
        local p = GetEntityCoords(ped)
        local gz = groundAt(p.x, p.y, p.z + 1.5, p.z - 4.0) or (p.z - 1.0)
        SetEntityCoords(ped, p.x, p.y, gz, false, false, false, false)
        SetEntityHeading(ped, soft.heading)
        StopAnimTask(ped, Config.MountAnims.dict, soft.clip, 3.0)
        SetEntityCollision(ped, true, true)
        SetPedCanRagdoll(ped, savedRagdoll)
        SetPedLegIkMode(ped, 2)
        curRider = nil
        if soft.run then
            local fx, fy = fwdVec(GetEntityHeading(horse))
            local v = soft.speed * 0.8
            SetEntityVelocity(ped, fx * v - fy * soft.side * 0.8, fy * v + fx * soft.side * 0.8, 0.0)
            if soft.speed > (Config.RollDismountSpeed or 8.0) then
                SetPedCanRagdoll(ped, true)
                SetPedToRagdoll(ped, 900, 1500, 0, false, false, false)
            end
        end
        speed, yawRate, gait, vz = 0.0, 0.0, 0, 0.0
        releaseHorse()
        return
    end
    ClearPedTasksImmediately(ped)
    SetEntityCollision(ped, true, true)
    SetPedCanRagdoll(ped, savedRagdoll)
    SetPedLegIkMode(ped, 2)
    curRider = nil

    if horse and DoesEntityExist(horse) and not thrown then
        local p = GetOffsetFromEntityInWorldCoords(horse, -1.25, 0.0, 0.0)
        local gz = groundAt(p.x, p.y, p.z + 2.0, p.z - 5.0) or p.z
        SetEntityCoords(ped, p.x, p.y, gz, false, false, false, false)
        SetEntityHeading(ped, GetEntityHeading(horse))
    end
    speed, yawRate, gait, vz = 0.0, 0.0, 0, 0.0
    releaseHorse()
end

local function mount()
    if not isAlive(horse) then return end
    local ped = PlayerPedId()
    if IsEntityDead(ped) or IsPedInAnyVehicle(ped, false) then return end
    local arms = Config.ArmStyles[armStyle]
    if arms and arms.dict then loadDict(arms.dict) end
    if not loadDict(legDict()) or not loadDict(Config.HorseDict) or not loadDict(Config.MountAnims.dict) then
        return notify('~r~Animations indisponibles.')
    end
    -- cote : celui ou se trouve le joueur
    local pp = GetEntityCoords(ped)
    local po = GetOffsetFromEntityGivenWorldCoords(horse, pp.x, pp.y, pp.z)
    local side = po.x <= 0.0 and 1 or -1
    -- hauteur naturelle du cheval au-dessus du sol (mesuree debout, avant de le piloter)
    local hp = GetEntityCoords(horse)
    local gz = groundAt(hp.x, hp.y, hp.z + 1.0, hp.z - 4.0)
    if gz then hOff = math.max(0.3, math.min(2.2, hp.z - gz)) end
    posZ = hp.z

    if not REF and GetEntitySpeed(horse) < 0.3 then captureRef(horse) end
    ClearPedTasksImmediately(horse)
    FreezeEntityPosition(horse, true)       -- le script pilote le cheval : plus de poussee de l'IA
    grazing = false

    savedRagdoll = CanPedRagdoll(ped)
    ClearPedTasksImmediately(ped)
    SetPedCanRagdoll(ped, false)
    SetEntityCollision(ped, false, false)

    speed, yawRate, gait, vz = 0.0, 0.0, 0, 0.0
    curClip, curRider = nil, nil
    mounted = true
    findBack()
    ENV.z, ENV.y, ENV.p = nil, nil, nil
    for _, sp in pairs(SPR) do sp.x, sp.v = 0.0, 0.0 end
    SetPedLegIkMode(ped, 0)
    startAct('mount', side)
    stepAct()
end

local function throwRider(force)
    local ped = PlayerPedId()
    local fx, fy = fwdVec(GetEntityHeading(horse))
    dismount(true)
    SetPedCanRagdoll(ped, true)
    SetPedToRagdoll(ped, 3500, 4500, 0, false, false, false)
    SetEntityVelocity(ped, fx * force * 0.6, fy * force * 0.6, 2.5)
    ApplyDamageToPed(ped, Config.RiderCrashDamage, false)
    notify('~r~Tu as chute de cheval !')
end

-- ------------------------------------------------------------
-- apparition / sifflet
-- ------------------------------------------------------------
local horseGroup
local function setupHorsePed(h)
    -- textures d'origine : sans ca, GTA melange au hasard les variantes du modele (tete, corps, accessoires)
    SetPedDefaultComponentVariation(h)
    for comp = 0, 11 do
        if GetNumberOfPedDrawableVariations(h, comp) > 0 then
            SetPedComponentVariation(h, comp, 0, 0, 0)
        end
    end
    ClearAllPedProps(h)
    SetEntityAsMissionEntity(h, true, true)
    SetBlockingOfNonTemporaryEvents(h, true)
    SetPedFleeAttributes(h, 0, false)
    SetPedCanRagdoll(h, false)
    SetEntityMaxHealth(h, Config.HorseHealth)
    SetEntityHealth(h, Config.HorseHealth)
    if not horseGroup then
        local _, g = AddRelationshipGroup('EDO_HORSE')
        horseGroup = g
        SetRelationshipBetweenGroups(0, horseGroup, `PLAYER`)
        SetRelationshipBetweenGroups(0, `PLAYER`, horseGroup)
    end
    SetPedRelationshipGroupHash(h, horseGroup)
end

local function deleteHorse()
    if mounted then dismount(false) end
    if horse and DoesEntityExist(horse) then
        SetEntityAsMissionEntity(horse, true, true)
        DeleteEntity(horse)
    end
    horse, horseNet = nil, nil
    TriggerServerEvent('edo_horses:forget')
end

local function log(msg) print('[edo_horses] ' .. msg) end

local function spawnHorse(near)
    if GetResourceState('draft_horse') ~= 'started' then
        log('ERREUR : draft_horse n\'est pas demarre.')
        return notify('~r~La ressource draft_horse n\'est pas demarree.')
    end
    log('chargement du modele draft_horse...')
    if not IsModelInCdimage(Config.Model) then
        log('ERREUR : modele draft_horse introuvable (le stream du pack ne s\'est pas charge).')
        return notify('~r~Modele draft_horse introuvable (F8).')
    end
    if not loadModel(Config.Model) then
        log('ERREUR : le modele met trop de temps a charger (textures de 68 Mo).')
        return notify('~r~Le modele du cheval n\'a pas pu charger (F8).')
    end

    local ped = PlayerPedId()
    local dist = near and 5.0 or Config.SpawnBehind
    local p = GetOffsetFromEntityInWorldCoords(ped, 0.0, -dist, 0.0)
    local pos = p
    local gz = groundAt(p.x, p.y, p.z + 20.0, p.z - 20.0)
    if gz then pos = vector3(p.x, p.y, gz + 0.5) end
    local ok, safe = GetSafeCoordForPed(pos.x, pos.y, pos.z, false, 16)
    if ok and #(safe - pos) < 12.0 then pos = safe end

    horse = CreatePed(28, Config.Model, pos.x, pos.y, pos.z, GetEntityHeading(ped), true, true)
    SetModelAsNoLongerNeeded(Config.Model)
    if not horse or horse == 0 or not DoesEntityExist(horse) then
        horse = nil
        log('ERREUR : CreatePed a echoue.')
        return notify('~r~Echec de creation du cheval (F8).')
    end
    setupHorsePed(horse)
    if NetworkGetEntityIsNetworked(horse) then
        horseNet = NetworkGetNetworkIdFromEntity(horse)
        SetNetworkIdCanMigrate(horseNet, false)
        TriggerServerEvent('edo_horses:register', horseNet)
    end
    stamina, exhausted = Config.MaxStamina, false
    log(('cheval cree a %.1f m (%.1f %.1f %.1f)'):format(#(pos - GetEntityCoords(ped)), pos.x, pos.y, pos.z))
end

local function doWhistle()
    local ped = PlayerPedId()
    if not IsPedInAnyVehicle(ped, false) and loadDict('rcmnigel1c') then
        TaskPlayAnim(ped, 'rcmnigel1c', 'hailing_whistle_waive_a', 8.0, -8.0, 2200, 48, 0.0, false, false, false)
    end
    if not isAlive(horse) then
        if horse then deleteHorse() end
        spawnHorse(false)
    elseif #(GetEntityCoords(horse) - GetEntityCoords(ped)) > Config.TeleportDistance then
        deleteHorse()
        spawnHorse(false)
    end
    if isAlive(horse) then
        releaseHorse()
        local d = #(GetEntityCoords(horse) - GetEntityCoords(ped))
        TaskGoToEntity(horse, ped, -1, 2.2, d > 12.0 and 3.0 or 1.0, 1073741824, 0)
        notify('~y~Ton cheval arrive.')
    end
end

local function whistle()
    if busy then return end
    if mounted then return notify('Tu es deja a cheval.') end
    busy = true
    local ok, err = pcall(doWhistle)
    busy = false
    if not ok then
        log('ERREUR : ' .. tostring(err))
        notify('~r~Erreur cheval, regarde F8.')
    end
end

RegisterCommand(Config.Command, function() whistle() end, false)
RegisterCommand('+edo_siffler', function() whistle() end, false)
RegisterCommand('-edo_siffler', function() end, false)
RegisterKeyMapping('+edo_siffler', 'Siffler son cheval', 'keyboard', Config.WhistleKey)

RegisterCommand(Config.StoreCommand, function()
    if horse then deleteHorse() notify('~y~Cheval renvoye.') end
end, false)

-- allures du cheval : /chevalallures 1 (sur mesure) | 2 (cerf d'origine)
do
    local saved = tonumber(GetResourceKvpString('edo_horses_gaitdict') or '')
    if saved and Config.HorseDicts[saved] then Config.HorseDict = Config.HorseDicts[saved] end
end
RegisterCommand('chevalallures', function(_, a)
    local n = tonumber(a[1])
    if not n or not Config.HorseDicts[n] then
        return notify(('Allures : %s  (usage : /chevalallures 1 sur mesure | 2 cerf)'):format(Config.HorseDict))
    end
    if isAlive(horse) and IsEntityPlayingAnim(horse, Config.HorseDict, curHorseClip or 'idle', 3) then
        StopAnimTask(horse, Config.HorseDict, curHorseClip or 'idle', 2.0)
    end
    Config.HorseDict = Config.HorseDicts[n]
    loadDict(Config.HorseDict)
    walkDur, curClip = nil, nil
    SetResourceKvp('edo_horses_gaitdict', tostring(n))
    notify('~g~Allures : ' .. Config.HorseDict)
end, false)

-- test d'une animation du cheval (a pied, a cote de lui) : /chevalanim walk_turn_l
RegisterCommand('chevalanim', function(_, a)
    if not isAlive(horse) or mounted or not a[1] then return notify('Usage : /chevalanim nom (descendu du cheval)') end
    loadDict(Config.HorseDict)
    TaskPlayAnim(horse, Config.HorseDict, a[1], 4.0, -4.0, 4000, 1, 0.0, false, false, false)
end, false)

-- position des mains (renes) : /chevalmains avant hauteur   ex : /chevalmains 0.30 0.20
RegisterCommand('chevalmains', function(_, a)
    local y, z = tonumber(a[1]), tonumber(a[2])
    if not z then return notify(('Mains : %.2f %.2f  (usage : /chevalmains avant hauteur)'):format(handY, handZ)) end
    handY, handZ = y, z
    SetResourceKvp('edo_horses_hands4', ('%.3f %.3f'):format(y, z))
    print(('[edo_horses] Config.ReinsIK forward = %.3f, up = %.3f'):format(y, z))
    notify('~g~Mains reglees et sauvegardees.')
end, false)

-- diagnostic : position reelle des os des jambes (F8 + console serveur)
legDebug = function()
    local ped = PlayerPedId()
    local bones = { {'LT',58271},{'LC',63931},{'LF',14201},{'LO',2108},{'RT',51826},{'RC',36864},{'RF',52301},{'RO',20781},{'PV',11816} }
    local out = {}
    for _, b in ipairs(bones) do
        local idx = GetPedBoneIndex(ped, b[2])
        local w = GetWorldPositionOfEntityBone(ped, idx)
        local o = GetOffsetFromEntityGivenWorldCoords(ped, w.x, w.y, w.z)
        out[#out + 1] = ('%s=%.3f,%.3f,%.3f'):format(b[1], o.x, o.y, o.z)
    end
    local line = 'EDODBG ' .. legStyle .. ' ' .. table.concat(out, ' ')
    print(line)
    TriggerServerEvent('edo_horses:debug', line)
end
RegisterCommand('chevaldebug', function() legDebug() notify('~g~Diagnostic envoye.') end, false)

-- posture des jambes : /chevaljambes 1 | 2 | 3
RegisterCommand('chevaljambes', function(_, a)
    local n = tonumber(a[1])
    if not n or not Config.LegStyles[n] then
        local t = {}
        for i, st in ipairs(Config.LegStyles) do t[#t + 1] = i .. ' ' .. st.name end
        return notify('Usage : /chevaljambes ' .. table.concat(t, ' | '))
    end
    if not loadDict(Config.LegStyles[n].dict) then return notify('~r~Animation indisponible.') end
    local ped = PlayerPedId()
    StopAnimTask(ped, legDict(), curRider or 'sit', 2.0)
    legStyle = n
    SetResourceKvp('edo_horses_legs4', tostring(n))
    curRider = nil
    print(('[edo_horses] Config.RiderLegs = %d (%s)'):format(n, Config.LegStyles[n].name))
    notify('~g~Jambes : ' .. Config.LegStyles[n].name)
end, false)


-- reglage de la selle en jeu : /chevalselle x y z  (sans argument : affiche la valeur)
RegisterCommand('chevalselle', function(_, a)
    local x, y, z = tonumber(a[1]), tonumber(a[2]), tonumber(a[3])
    if not z then
        return notify(('Selle : %.2f %.2f %.2f  (usage : /chevalselle x y z)'):format(seatOffset.x, seatOffset.y, seatOffset.z))
    end
    seatOffset = vector3(x, y, z)
    SetResourceKvp('edo_horses_seat3', ('%.3f %.3f %.3f'):format(x, y, z))
    if mounted then attachRider(PlayerPedId()) end
    print(('[edo_horses] Config.RiderOffset = vector3(%.3f, %.3f, %.3f)'):format(x, y, z))
    notify('~g~Selle reglee et sauvegardee.')
end, false)

-- ------------------------------------------------------------
-- boucle de pilotage
-- ------------------------------------------------------------
local DISABLED = { 21, 22, 23, 24, 25, 32, 33, 34, 35, 36, 37, 44, 45, 47, 58, 69, 70, 92, 114, 140, 141, 142, 143, 257, 263, 264 }

local function readInput(now)
    for i = 1, #DISABLED do DisableControlAction(0, DISABLED[i], true) end
    DisableControlAction(0, 30, true); DisableControlAction(0, 31, true)
    DisablePlayerFiring(PlayerId(), true)
    if IsPauseMenuActive() or IsNuiFocused() or act then return false, false, 0.0, false, false, false end

    local ud = GetDisabledControlNormal(0, 31)
    local fwd = IsDisabledControlPressed(0, 32) or ud < -0.3
    local back = IsDisabledControlPressed(0, 33) or ud > 0.3
    local steer = GetDisabledControlNormal(0, 30)
    if IsDisabledControlPressed(0, 34) then steer = -1.0 elseif IsDisabledControlPressed(0, 35) then steer = 1.0 end
    return fwd, back, steer, IsDisabledControlJustPressed(0, 21), IsDisabledControlPressed(0, 21), IsDisabledControlPressed(0, 36)
end

local function ride(now, dt)
    local ped = PlayerPedId()
    local fwd, back, steer, spurTap, spurHeld, walkHeld = readInput(now)
    local pos = GetEntityCoords(horse)
    local heading = GetEntityHeading(horse)
    local gz0 = posZ - hOff

    -- eau
    local inWater, waterZ = GetWaterHeight(pos.x, pos.y, pos.z + 2.0)
    local depth = inWater and (waterZ - gz0) or 0.0

    -- allure demandee
    local maxGait = exhausted and 2 or 4
    if depth > 0.5 then maxGait = math.min(maxGait, Config.WaterMaxGait) end
    if Config.ControlStyle == 'tsushima' then
        if not fwd then gait = 0
        elseif walkHeld then gait = 1
        elseif spurHeld then gait = 4
        else gait = 2 end
    else
        if not fwd then gait = 0
        else
            if gait == 0 then gait = 1 end
            if spurTap then gait = gait + 1; lastSpur = now end
            if gait == 4 and now - lastSpur > Config.GallopKeepMs then gait = 3 end
        end
    end
    gait = math.min(gait, maxGait)

    -- vitesse cible (+ effet de pente et de virage)
    local target = ({ [0] = 0.0, Config.Speed.walk, Config.Speed.trot, Config.Speed.canter, Config.Speed.gallop })[gait]
    if target > 0 then
        target = target * (1.0 - math.max(-0.25, math.min(0.5, slope * Config.SlopeSpeedLoss * 2.0)))
        if math.abs(steer) > 0.5 and gait >= 3 then target = target * Config.TurnSlowdown end
    end
    if back then
        if speed > 0.3 then speed = approach(speed, 0.0, Config.Brake * dt)
        else speed = approach(speed, -Config.Speed.reverse, Config.Accel * dt) end
    else
        local rate = (target > speed) and Config.Accel or Config.Decel
        if gait >= 3 and target > speed then rate = rate * 1.25 end
        speed = approach(speed, target, rate * dt)
    end

    -- rotation avec inertie
    local band = bandOf(speed)
    local tr = band == 0 and Config.TurnRate.idle or Config.TurnRate[BAND_NAME[band]]
    yawRate = approach(yawRate, -steer * tr, Config.TurnAccel * dt)
    heading = (heading + yawRate * dt) % 360.0
    local fx, fy = fwdVec(heading)

    -- obstacles devant / derriere
    if math.abs(speed) > 0.05 then
        local dir = speed > 0 and 1.0 or -1.0
        local reach = Config.HorseLength + math.abs(speed) * dt + 0.35
        local sx, sy = pos.x + fx * dir * 0.3, pos.y + fy * dir * 0.3
        local ex, ey = pos.x + fx * dir * reach, pos.y + fy * dir * reach
        local px, py = -fy * 0.35, fx * 0.35
        local hit = false
        for _, h in ipairs({ 0.75, 1.45 }) do
            local z = gz0 + h
            if blocked(sx, sy, z, ex, ey, z) or blocked(sx + px, sy + py, z, ex + px, ey + py, z)
                or blocked(sx - px, sy - py, z, ex - px, ey - py, z) then hit = true break end
        end
        -- pente trop raide devant
        if not hit then
            local ax, ay = pos.x + fx * dir * (Config.HorseLength + 0.4), pos.y + fy * dir * (Config.HorseLength + 0.4)
            local gzA = groundAt(ax, ay, gz0 + 2.5, gz0 - 3.0)
            if gzA and (gzA - gz0) / (Config.HorseLength + 0.4) > Config.MaxSlope then hit = true end
            if depth > Config.MaxWaterDepth and dir > 0 then hit = true end
        end
        if hit then
            if speed > Config.CrashSpeed then
                local f = speed
                speed = 0.0
                SetEntityHealth(horse, math.max(1, GetEntityHealth(horse) - 40))
                throwRider(f)
                return
            end
            speed = 0.0
        end
    end

    -- PNJ percutes
    if speed > Config.PedKnockSpeed then
        local hx, hy = pos.x + fx * Config.HorseLength, pos.y + fy * Config.HorseLength
        for _, p in ipairs(GetGamePool('CPed')) do
            if p ~= ped and p ~= horse and not IsPedAPlayer(p) and not IsPedInAnyVehicle(p, false) then
                local pp = GetEntityCoords(p)
                if (pp.x - hx) ^ 2 + (pp.y - hy) ^ 2 < 1.0 and math.abs(pp.z - pos.z) < 2.0 then
                    SetPedToRagdoll(p, 2500, 3500, 0, false, false, false)
                    ApplyForceToEntity(p, 1, fx * speed * 0.8, fy * speed * 0.8, 2.0, 0.0, 0.0, 0.0, 0, false, true, true, false, true)
                    speed = speed * 0.8
                end
            end
        end
    end

    -- deplacement + suivi du sol
    local nx, ny = pos.x + fx * speed * dt, pos.y + fy * speed * dt
    local gz = groundAt(nx, ny, gz0 + 1.6, gz0 - 8.0)
    local stepD = math.abs(speed * dt)
    local targetZ = gz and (gz + hOff) or nil
    if targetZ and posZ - targetZ < 0.45 then
        if vz < -Config.FallThrowSpeed then
            vz = 0.0
            posZ = targetZ
            SetEntityHealth(horse, math.max(1, GetEntityHealth(horse) - 60))
            throwRider(6.0)
            return
        end
        vz = 0.0
        posZ = posZ + (targetZ - posZ) * math.min(1.0, dt * 14.0)
        if stepD > 0.001 then
            local s = (gz - gz0) / stepD
            slope = slope + (math.max(-1.0, math.min(1.0, s)) * (speed >= 0 and 1 or -1) - slope) * math.min(1.0, dt * 4.0)
        else
            slope = slope * (1.0 - math.min(1.0, dt * 4.0))
        end
    else
        -- chute libre (rebord, falaise)
        vz = vz - 9.81 * dt
        posZ = posZ + vz * dt
        if targetZ and posZ < targetZ then posZ = targetZ end
    end

    SetEntityCoordsNoOffset(horse, nx, ny, posZ, false, false, false)
    SetEntityHeading(horse, heading)

    -- endurance
    local b = bandOf(speed)
    if b == 4 then
        stamina = math.max(0.0, stamina - Config.StaminaDrain.gallop * dt); lastDrain = now
    elseif b == 3 then
        stamina = math.max(0.0, stamina - Config.StaminaDrain.canter * dt); lastDrain = now
    end
    if stamina <= 0.0 and not exhausted then
        exhausted = true
        notify('~o~Ton cheval est epuise.')
    end

    updateHorseAnim(dt)
    if act then stepAct() else updateRiderAnim(ped, dt) end

    if Config.Debug then
        SetTextFont(4); SetTextScale(0.34, 0.34); SetTextColour(255, 255, 255, 230); SetTextOutline()
        BeginTextCommandDisplayText('STRING')
        AddTextComponentSubstringPlayerName(('%s | %.1f m/s | pente %.2f | endurance %d%% | %s')
            :format(GAIT_LABEL[gait], speed, slope, math.floor(stamina), curClip or '-'))
        EndTextCommandDisplayText(0.015, 0.80)
    end

    if not act and (IsDisabledControlJustPressed(0, 51) or IsControlJustPressed(0, 51)) then
        local side = sideFree(1) and 1 or (sideFree(-1) and -1 or 1)
        local kind = math.abs(speed) < (Config.RunDismountSpeed or 2.0) and 'dismount' or 'dismount_run'
        startAct(kind, side)
        act.speed = math.abs(speed)
    end
end

CreateThread(function()
    local last = GetGameTimer()
    while true do
        local now = GetGameTimer()
        local dt = math.min(0.1, (now - last) / 1000.0)
        last = now

        if mounted then
            Wait(0)
            local ped = PlayerPedId()
            if not isAlive(horse) or IsEntityDead(ped) or not IsEntityAttachedToEntity(ped, horse) then
                dismount(not isAlive(horse))
            else
                ride(now, dt)
            end
        elseif isAlive(horse) then
            local ped = PlayerPedId()
            local d = #(GetEntityCoords(ped) - GetEntityCoords(horse))
            if d < Config.MountDistance and not IsPedInAnyVehicle(ped, false) and not IsEntityDead(ped) then
                Wait(0)
                help('~INPUT_CONTEXT~ Monter a cheval')
                if IsControlJustPressed(0, 51) then mount() end
            else
                Wait(200)
                -- seul et immobile depuis un moment : il broute
                if not grazing and now - idleSince > Config.GrazeAfterMs and GetEntitySpeed(horse) < 0.2 then
                    if loadDict('creatures@deer@amb@world_deer_grazing@base') then
                        TaskPlayAnim(horse, 'creatures@deer@amb@world_deer_grazing@base', 'base', 2.0, -2.0, -1, 1, 0.0, false, false, false)
                        grazing = true
                    end
                end
            end
        else
            Wait(500)
        end
    end
end)

-- recuperation d'endurance + pont HUD
local hudWarned = false
CreateThread(function()
    local prev = GetGameTimer()
    while true do
        Wait(200)
        local now = GetGameTimer()
        local dt = (now - prev) / 1000.0
        prev = now
        if horse and now - lastDrain > Config.StaminaRegenDelayMs then
            stamina = math.min(Config.MaxStamina, stamina + Config.StaminaRegen * dt)
            if exhausted and stamina >= Config.ExhaustedRecovery then
                exhausted = false
                if mounted then notify('~g~Ton cheval a repris son souffle.') end
            end
        end
        if GetResourceState(Config.HudResource) == 'started' then
            local alive = isAlive(horse)
            local health = alive and math.floor(math.max(0, (GetEntityHealth(horse) - 100) / math.max(1, GetEntityMaxHealth(horse) - 100) * 100)) or 0
            local ok = pcall(function()
                exports[Config.HudResource]:SetHorse({ active = mounted, health = health,
                    stamina = stamina / Config.MaxStamina * 100, gait = GAIT_LABEL[mounted and bandOf(speed) or 0] })
            end)
            if not ok and not hudWarned then print('[edo_horses] HUD : export SetHorse indisponible.') hudWarned = true end
        end
    end
end)

-- ------------------------------------------------------------
-- HARNACHEMENT : selle + bride (stream/edo_selle_k*.ydr, edo_bride_k*.ydr, edo_sellerie.ytd/.ytyp)
-- Pose sur TOUS les chevaux du modele (chaque joueur les voit), taille choisie en mesurant le squelette.
-- La selle suit le dos (os du dos), la bride suit la tete (os de la tete et de la bouche).
-- ------------------------------------------------------------
local DEER_BODY, DEER_HEAD = 0.938, 0.2546   -- distances de reference du squelette (encolure-bassin, nuque-bouche)
local tackForce = tonumber(GetResourceKvpString('edo_horses_tacksize') or '')
local tackOff = nil
do
    local k = GetResourceKvpString('edo_horses_tackoff')
    if k then
        local v = {}
        for n in k:gmatch('[-%d%.]+') do v[#v + 1] = tonumber(n) end
        if #v == 3 then tackOff = vector3(v[1], v[2], v[3]) end
    end
end
local tackOn = GetResourceKvpString('edo_horses_tackon') ~= '0'
local function nearestSize(k)
    if tackForce then return tackForce end
    local best, bd = Config.Tack.sizes[1], 1e9
    for _, sz in ipairs(Config.Tack.sizes) do
        if math.abs(sz - k) < bd then best, bd = sz, math.abs(sz - k) end
    end
    return best
end
local function spawnProp(name, h)
    local m = GetHashKey(name)
    if not IsModelInCdimage(m) then return nil end
    RequestModel(m)
    local t = GetGameTimer() + 3000
    while not HasModelLoaded(m) and GetGameTimer() < t do Wait(0) end
    if not HasModelLoaded(m) then return nil end
    local p = GetEntityCoords(h)
    local o = CreateObject(m, p.x, p.y, p.z + 1.0, false, false, false)
    SetModelAsNoLongerNeeded(m)
    SetEntityCollision(o, false, false)
    SetEntityCanBeDamaged(o, false)
    SetEntityInvincible(o, true)
    return o
end
local function removeTack(h)
    local t = tack[h]
    if not t then return end
    for _, o in ipairs({ t.saddle, t.bridle }) do
        if o and DoesEntityExist(o) then DeleteEntity(o) end
    end
    tack[h] = nil
end
local function addTack(h)
    local t = { ks = 140, kb = 140 }
    t.bb = backBonesOf(h)
    t.head = firstBone(h, { 'SKEL_Head' })
    t.mouthL = firstBone(h, { 'FB_L_Lip_Corner_000', 'FB_UpperLip_000', 'FB_Jaw_000' })
    t.mouthR = firstBone(h, { 'FB_R_Lip_Corner_000', 'FB_UpperLip_000', 'FB_Jaw_000' })
    -- taille : mesuree sur le squelette du cheval
    if t.bb and t.bb.front and t.bb.rear and t.bb.front.name == 'SKEL_Neck_1' and t.bb.rear.name == 'SKEL_Pelvis' then
        local f, r = bonePos(h, t.bb.front), bonePos(h, t.bb.rear)
        t.ks = nearestSize(#(f - r) / DEER_BODY * 100.0)
    end
    if t.head and t.mouthL and t.mouthR then
        local hd = bonePos(h, t.head)
        local mo = (bonePos(h, t.mouthL) + bonePos(h, t.mouthR)) * 0.5
        t.kb = nearestSize(#(mo - hd) / DEER_HEAD * 100.0)
    else
        t.kb = t.ks
    end
    tack[h] = t
    t.saddle = spawnProp(Config.Tack.saddle .. t.ks, h)
    if t.head and t.mouthL then t.bridle = spawnProp(Config.Tack.bridle .. t.kb, h) end
    if h == horse then
        print(('[edo_horses] harnachement : selle %s%d, bride %s%d'):format(Config.Tack.saddle, t.ks, Config.Tack.bridle, t.kb))
        if not t.saddle then print('[edo_horses] ATTENTION : modele de selle introuvable (stream / ytyp ?)') end
    end
end
local function updateTack(h, t)
    -- SELLE : meme reference que le cavalier, suit le dos
    if t.saddle and DoesEntityExist(t.saddle) then
        local base = (h == horse) and seatOffset or Config.RiderOffset
        local off = tackOff or Config.Tack.saddleOffset
        local dz, pitch, dy = backDelta(h, t.bb)
        dz, dy = dz or 0.0, dy or 0.0
        local p = vector3(base.x + off.x, base.y + off.y + dy, base.z + off.z + dz)
        t.saddlePos, t.saddlePitch = p, pitch
        AttachEntityToEntity(t.saddle, h, -1, p.x, p.y, p.z, pitch, 0.0, 0.0, false, false, false, false, 2, true)
    end
    -- BRIDE : orientee comme la tete (de la nuque vers la bouche)
    if t.bridle and DoesEntityExist(t.bridle) then
        local hd = bonePos(h, t.head)
        local mo = (bonePos(h, t.mouthL) + bonePos(h, t.mouthR)) * 0.5
        local u = mo - hd
        local len = #u
        if len > 0.01 then
            u = u / len
            local pitch = math.deg(math.asin(math.max(-1.0, math.min(1.0, u.z))))
            local yaw = math.deg(math.atan(-u.x, u.y))
            local B = Config.Tack.bridleOffset
            local p = hd + u * B.y + vector3(0.0, 0.0, B.z)
            AttachEntityToEntity(t.bridle, h, -1, p.x, p.y, p.z, pitch, 0.0, yaw, false, false, false, false, 2, true)
        end
    end
end
-- gestion : cherche les chevaux autour (toutes les secondes), met a jour chaque image
local stillSince, lastRef = nil, nil
CreateThread(function()
    local lastScan = 0
    while true do
        local now = GetGameTimer()
        if not (Config.Tack and Config.Tack.enabled and tackOn) then
            for h in pairs(tack) do removeTack(h) end
            Wait(1000)
        else
            if now - lastScan > 1000 then
                lastScan = now
                local me = GetEntityCoords(PlayerPedId())
                local seen = {}
                for _, p in ipairs(GetGamePool('CPed')) do
                    if GetEntityModel(p) == Config.Model and not IsEntityDead(p) and #(GetEntityCoords(p) - me) < Config.Tack.range then
                        seen[p] = true
                        if not tack[p] then addTack(p) end
                    end
                end
                for h in pairs(tack) do
                    if not seen[h] or not DoesEntityExist(h) then removeTack(h) end
                end
                -- reference du dos : cheval immobile, debout, non monte, ne broute pas
                if isAlive(horse) and not mounted and not grazing and not act and GetEntitySpeed(horse) < 0.05 then
                    stillSince = stillSince or now
                    if now - stillSince > 2500 and (not REF or now - (lastRef or 0) > 15000) then
                        if captureRef(horse) then lastRef = now end
                    end
                else
                    stillSince = nil
                end
            end
            local any = false
            for h, t in pairs(tack) do
                if DoesEntityExist(h) then updateTack(h, t) any = true end
            end
            Wait(any and 0 or 250)
        end
    end
end)

-- /chevalharnais            : afficher / masquer selle et bride
-- /chevalharnais taille 140 : forcer la taille (100 120 140 160 180) | /chevalharnais taille auto
-- /chevalharnais selle x y z : decaler la selle (sauvegarde)
RegisterCommand('chevalharnais', function(_, a)
    if a[1] == 'taille' then
        tackForce = tonumber(a[2])
        SetResourceKvp('edo_horses_tacksize', tackForce and tostring(tackForce) or '')
        for h in pairs(tack) do removeTack(h) end
        return notify('~g~Taille du harnachement : ' .. (tackForce and tostring(tackForce) or 'auto'))
    elseif a[1] == 'selle' then
        local x, y, z = tonumber(a[2]), tonumber(a[3]), tonumber(a[4])
        if not z then
            local o = tackOff or Config.Tack.saddleOffset
            return notify(('Selle : %.2f %.2f %.2f  (usage : /chevalharnais selle x y z)'):format(o.x, o.y, o.z))
        end
        tackOff = vector3(x, y, z)
        SetResourceKvp('edo_horses_tackoff', ('%.3f %.3f %.3f'):format(x, y, z))
        print(('[edo_horses] Config.Tack.saddleOffset = vector3(%.3f, %.3f, %.3f)'):format(x, y, z))
        return notify('~g~Selle deplacee.')
    end
    tackOn = not tackOn
    SetResourceKvp('edo_horses_tackon', tackOn and '1' or '0')
    notify(tackOn and '~g~Selle et bride : affichees' or '~y~Selle et bride : masquees')
end, false)

exports('GetHorseStamina', function() return stamina end)
exports('GetHorseGait', function() return GAIT_LABEL[bandOf(speed)] end)
exports('IsMountedOnHorse', function() return mounted end)
exports('GetHorseEntity', function() return horse end)

AddEventHandler('onResourceStop', function(res)
    if res == GetCurrentResourceName() then
        deleteHorse()
        for h in pairs(tack) do removeTack(h) end
    end
end)

CreateThread(function() Wait(2000) log('EDO HORSES 1.8.1 charge. /cheval ou H pour siffler.') end)
