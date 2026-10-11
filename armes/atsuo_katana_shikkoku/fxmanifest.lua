fx_version 'cerulean'
game 'gta5'
lua54 'yes'

author 'Atsuo RP'
description 'Katana Shikkoku - arme de mêlée add-on (WEAPON_KATANA_SHIKKOKU)'
version '1.0.0'

files {
    'meta/weaponarchetypes.meta',
    'meta/weaponanimations.meta',
    'meta/pedpersonality.meta',
    'meta/weapons.meta',
}

data_file 'WEAPON_METADATA_FILE'  'meta/weaponarchetypes.meta'
data_file 'WEAPON_ANIMATIONS_FILE' 'meta/weaponanimations.meta'
data_file 'PED_PERSONALITY_FILE'  'meta/pedpersonality.meta'
data_file 'WEAPONINFO_FILE'       'meta/weapons.meta'

client_script 'client.lua'
