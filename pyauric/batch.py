from .bands import band_command

def assemble_batch_run(auric):
    """Yield the sequence of AURIC commands in a batch run.
    
    Parameters
    ----------
    am: AURICManager

    Yields
    ------
    cmd: Command in the batch run
    """
    sza = auric.params['SZA']
    daytime = (0<sza) and (sza<90)
    nighttime = (110<sza) and (sza<180)
    if not (daytime or nighttime):
        raise Exception("SZA is {}. AURIC needs 0<SZA<90 or 110<SZA<180.".format(sza))
    optically_thick = any(auric.radtrans_options.values())
    lyman_alpha = auric.exists('ly_alpha.opt')
    lyman_beta = auric.exists('ly_beta.opt')
    synthetic_spectra = auric.band_options
    use_eflux = auric.use_eflux
    yield from (auric.new_command(c) for c in airglow_sequence(daytime
                                                               , optically_thick
                                                               , lyman_alpha
                                                               , lyman_beta
                                                               , synthetic_spectra
                                                               , use_eflux))

def airglow_sequence(daytime
                     , optically_thick
                     , lyman_alpha
                     , lyman_beta
                     , synthetic_spectra
                     , use_eflux):
    yield 'atmos'
    yield 'ionos' # or getpim
    if daytime:
        yield from dayglow_sequence(use_eflux)
    else:
        yield from nightglow_sequence()
    yield 'losden'
    if optically_thick: yield "radtrans"
    yield "losint"
    if lyman_alpha: yield "ly_alpha"
    if lyman_beta: yield "ly_beta"
    yield "mergeint"
    for band, switch in synthetic_spectra.items(): # synthetic_spectra is a dict mapping commands to booleans
        if switch: yield band_command(band)
    if synthetic_spectra:
        yield "mergesyn"

def nightglow_sequence():
    """Yield the names of commands needed to model nightglow"""
    yield "niteglo"
    
def dayglow_sequence(use_eflux):#implement this fully later because nightglow is simpler.
    """Yield the names of commands needed to model dayglow."""
    yield from ['solar'
                , 'colden'
                , 'pesource'
                , 'eflux' if use_eflux else 'peflux'
                , 'e_impact'
                , 'daychem'
                , 'mergever'
    ]
