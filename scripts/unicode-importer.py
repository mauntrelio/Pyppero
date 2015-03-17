#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import pymongo
import urllib
import zipfile
import os

def import_unicode_db(db):

    # download last version of Unicode Database
    if not (os.path.isfile('ucd.all.flat.xml')):
     
        print "Downloading ucd.all.flat.zip"
        urllib.urlretrieve('http://www.unicode.org/Public/UCD/latest/ucdxml/ucd.all.flat.zip','ucd.all.flat.zip')

        zfile = zipfile.ZipFile("ucd.all.flat.zip")
        for name in zfile.namelist():
            (dirname, filename) = os.path.split(name)
            print "Decompressing %s" % filename
            zfile.extract(name, '.')

    else:
        filename = 'ucd.all.flat.xml'

    # inizializzazione
    decimal_codepoint = -1
    codepoint = ''
    name_aliases = [] 

    print "Comincio a leggere %s" % filename

    counter = 1

    with open(filename) as f:
        for line in f:

            line = line.strip()

            if counter % 1000 == 0:
                print "Inseriti %s codepoints" % counter
        
            if line == '</repertoire>':
                # ho raggiunto la fine del repertorio
                # inserisco l'ultimo codepoint
                if decimal_codepoint > -1:
                    db.unicode.update({'codepoint':codepoint},{'$set': update},True)
                #break
            
            if re.match(r'^<char',line):
                if decimal_codepoint > -1:
                    # inserisco il precedente codepoint nel db
                    db.unicode.update({'codepoint':codepoint},{'$set': update},True)
                    counter += 1

                # azzero i name_aliases e il codepoint
                name_aliases = [] 
                codepoint = ''
            
                # ricavo le proprietà del codepoint
                m = re.findall(r'([a-z_0-9]+)="([^"]*)"',line,re.IGNORECASE)

                # trasformo in lista di liste
                properties = list(list(p) for p in m)
                property_list = []

                # valuto codepoint esadecimale, decimale, carattere
                for p in properties:
                    if p[0] == 'cp':
                        codepoint = p[1]
                        property_list.append(['decimal_codepoint',int(codepoint,16)])
                        property_list.append(['char',unichr(decimal_codepoint).encode('utf-8')])
                    elif p[1] != 'N' and p[1] != '':   
                        # => codepoint stesso
                        p[1].replace('#',codepoint)
                        # sequenze di codepoint per decomposizione diventano liste
                        if re.match(r'/[0-9A-F]{4,5} ([0-9A-F]{4,5} ?)+/',p[1],re.IGNORECASE):
                            p[1] = p[1].split(' ')
                        # caratteristiche vere
                        elif p[1] == 'Y':
                            p[1] = 1
                        property_list.append(p)

                # trasformo in dictionary
                update = dict(p for p in property_list)

            # processazione dei name aliases
            if re.match(r'^<name-alias',line):
                na_properties = re.findall(r'([a-z_0-9]+)="([^"]*)"',line,re.IGNORECASE)
                na_properties = dict(na_p for na_p in na_properties)
                name_aliases.append(na_properties)

            if name_aliases:
                update['name_aliases'] = name_aliases

            ## TODO: processare i blocchi
            #if re.match(r'^<block ',line):
                #m = re.findall(r'([a-z_0-9]+)="([^"]*)"',line,re.IGNORECASE)
                #properties = list(list(p) for p in m)
                #properties = dict(p for p in properties)
                

## def import_unicode_names:
# download last version of Unicode names
#urllib.urlretrieve('http://www.unicode.org/Public/UCD/latest/ucd/NamesList.txt','NamesList.txt')
# Process names
#block = ''
#char = -1
#with open('NamesList.txt') as f:
#    for line in f:


## def import_unicode_confusables:
# confusables 
# http://www.unicode.org/Public/security/revision-03/confusablesSummary.txt

#idna, ust46 (da capire)
# http://www.unicode.org/Public/idna/6.3.0/IdnaMappingTable.txt

if __name__ == '__main__':

    # connect to db
    conn = pymongo.MongoClient()
    db = conn['mauio']

    import_unicode_db(db)
    #import_unicode_names(db)
    #import_unicode_confusables(db)
    