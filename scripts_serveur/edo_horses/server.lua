-- EDO HORSES : suivi des chevaux pour les supprimer quand leur proprietaire se deconnecte
local horses = {}

RegisterNetEvent('edo_horses:register', function(netId)
    local src = source
    if type(netId) ~= 'number' then return end
    local old = horses[src]
    if old and old ~= netId then
        local e = NetworkGetEntityFromNetworkId(old)
        if e ~= 0 and DoesEntityExist(e) then DeleteEntity(e) end
    end
    horses[src] = netId
    print(('[EDO HORSES] %s (%d) a siffle son cheval.'):format(GetPlayerName(src) or '?', src))
end)

RegisterNetEvent('edo_horses:forget', function()
    horses[source] = nil
end)

AddEventHandler('playerDropped', function()
    local src = source
    local netId = horses[src]
    if netId then
        local e = NetworkGetEntityFromNetworkId(netId)
        if e ~= 0 and DoesEntityExist(e) then DeleteEntity(e) end
        horses[src] = nil
    end
end)
