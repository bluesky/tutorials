

### Setup persistent metadata for each scan
RE.md['group'] = 'PI_for_group'
RE.md['instrument'] = 'virtual'
RE.md['sample'] = 'bytes'














def md_info(default_md = RE.md):
    '''Formatted print of RunEngine metadata.'''

    print('Current peristent metadata for each scan are:')
    for info in default_md:
        val = default_md[info]
        print(f'    {info:_<30} : {val}')
    print('\n\n Use \'md_info()\' or \'RE.md\' to inspect again.')
    
#md_info()
