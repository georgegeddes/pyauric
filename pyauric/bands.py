_day_bands = ['n2_lbh'
          , 'n2_vk'
          , 'n2_1pg'
          , 'n2_2pg'
          , 'n2p_1ng'
          , 'n2p_mnl'
          , 'no_bands'
]

_night_bands = ['o2_nglow','o2_atm']

_bands = _day_bands + _night_bands

_band_cmd = {'n2_lbh':'syn_lbh'
             , 'n2_vk':'syn_vk'
             , 'n2_1pg':'syn_1pg'
             , 'n2_2pg':'syn_2pg'
             , 'n2p_1ng':'syn_1ng'
             , 'n2p_mnl':'syn_mnl'
             , 'no_bands':'syn_no'
             , 'o2_atm':'syn_atm'
             , 'o2_nglow':'syn_o2'
}

def band_command(band_name):
    return _band_cmd[band_name]
