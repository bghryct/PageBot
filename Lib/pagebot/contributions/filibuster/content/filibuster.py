#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
"""
        history
        All the filibuster specific stuff, or things that are shared by all themes like copyright notices etc.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
3.0.0    - split all the content into babycontents
evb        - note: only one dictionary named 'content' allowed per module
        this limitation is to speed up loading

"""

__version__ = '4.0'


# ------------------------------------------------------
#    filibuster.org
#
content = {
        "filibuster_about":            [
'''These pages are generated by the <#filibuster_adj#> <#scriptname=filibuster_productname#><#scriptname#>.

'Filibuster.org, together with <#company#>, are proud to announce a new line of <#scriptname#>-based server applications, enabling midsize and large enterprises to establish a presence on internet and intranets, without having to deal with real-world content providers

<#scriptname#> is a Linux based client-server <#filibuster_productname#> application. Building on the succes of <#filibuster_adj#> technology.

<#scriptname#> is a <#filibuster_adj#> platform for <#filibuster_adj#> content generation and e-publishing.'''
],
        'filibuster_currentoffer':        ['Filibuster announces the acquisition of several strategically important companies.'],
        'filibuster_copyright':            [ '<#filibuster_about#> All content generated by <#scriptname#> is &copy; Filibuster.org, HTF & LTR Ventures, The Hague and New York.'
                                    ],

        'filibuster_adj':                ['component-based', 'open-source', 'Python-scripted', '<#figs_ord#> generation', 'synthetic', 'hermeneutic','algorithmic'],
        'filibuster_productname':        ['<#!bold, filibuster_productprefix#><#!bold, filibuster_productsuffix#>'],
        'filibuster_productprefix':        ['World', 'Page', 'Content', 'Material', 'Data', 'Spoof', 'Knowledge', 'AI-'],
        'filibuster_productsuffix':        ['Creator', 'Compiler', 'Builder', 'Assembler', 'Interpreter', 'Thinker'],
        
        #
        'filibuster_terms':        ["Don't you dare use any of the content, images, text, names or anything else - we'll send our lawyers <#broker#> after you!"],
        
        # note: the names of the following items have been standardised, don't change the name
        'filibuster_disclaimer'    :    ['Filibuster.org is randomly generated based on algorithms and word lists. Any similarity between Filibuster.org and any venture real or ficticious is completely coincidental, and moreover shows a real lack of imagination on your part. I mean, come on: "<#company#>." Please.'],
        'filibuster_privacy_statement':    ['''This privacy statement is applicable to filibuster.org, <#!bold, company#> and <#!bold, _company#>
                

                Considering you’re not really visiting a real website, we can’t make any genuine promises what we do with the data that we're not collecting.
                

                If you have any questions about the privacy policies of <#!bold, company#>, please contact <#!bold, name#>, our <#position#>.
<#eMail_biz_info#>
                
                '''],


    # ------------------------------------------------------
    #    mission statements and other non-consequential filler text
    #
    
    'filler_hotair':    ['<#creditcard_accepted#>',
            '<#company#>',
            'Have you checked in yet?',
            '<#company#> is Y2K compliant.',
            '<#company#> is <#p_acronym#> registered!',
            ],
    'filler_intro':    ['News provided by:', 
            'This news is brought to you by:',
            'Our <#j_thing#> partners:',
            '<#company#> is proud to be associated with:'
            ]
        }




