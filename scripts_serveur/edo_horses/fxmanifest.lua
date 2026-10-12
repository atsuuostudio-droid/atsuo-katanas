fx_version 'cerulean'
game 'gta5'

author 'ATSUO'
description 'EDO Horses 1.0 - monture physique facon Red Dead / Ghost of Tsushima'
version '1.8.1'

lua54 'yes'

shared_script 'config.lua'
client_script 'client.lua'
server_script 'server.lua'

dependency 'draft_horse'

-- selle + bride (modeles 3D)
files { 'stream/edo_sellerie2.ytyp' }
data_file 'DLC_ITYP_REQUEST' 'stream/edo_sellerie2.ytyp'
