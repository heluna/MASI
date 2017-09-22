# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 08:54:42 2017

@author: user
"""

from pygeometa.core import render_template
import os

def yamlToXml(yaml, schemapath, output):
    xml_string = render_template(yaml, schema_local=schemapath)
    with open(output, 'xb') as ff:
        ff.write(xml_string.encode('utf-8'))

if __name__ == "__main__":
    
    yaml_dir = r'C:\Users\user\Desktop\pygeometa\YAML'  
    schemapath = r'C:\Users\user\Desktop\pygeometa\J2templates'  
    out_dir =  r'Z:\mtb\georef'
    
    for path, subdir, files in os.walk(yaml_dir):
            for file in files:
                if file.endswith(".yml"): 
                    yaml = os.path.basename(file)
                    filename = os.path.splitext(yaml)[0]
                    yamlfile = os.path.join(yaml_dir, yaml )
                    out = os.path.join(out_dir, (filename+".xml"))
                    try:
                        yamlToXml(yamlfile, schemapath, out)
                    except Exception as e:
                        print(e)    
