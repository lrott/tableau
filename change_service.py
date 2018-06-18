# Change Oracle service or other item as specified in the XML path
# 1. Load tdsx file
# 2. Extract the tds file and edit the service name
# 3. Delete the original tds from the tdsx and replace it with the edited file
import os
import shutil
import tempfile
import xml.etree.ElementTree
import zipfile

# function to unzip and delete the old datasource file
def remove_from_zip(tdsx_name, tds_name):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with zipfile.ZipFile(tdsx_name, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename != tds_name:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, tdsx_name)
    finally:
        shutil.rmtree(tempdir)

if __name__ == '__main__':

    # inputs
    datasource = 'oracle_test'          # name of your file
    service_update = 'ORACLE_PROD'      # new service name
    file_location = 'server/folder'     # location of file to change
    tdsx_path = file_location + datasource + '.tdsx'
    xml_path = './connection/named-connections/named-connection/connection' # xml path for field to edit
    
    tmpdir = tempfile.mkdtemp()

    # extract the tds file from the tdsx
    with zipfile.ZipFile(tdsx_path, 'r') as zip_ref:
        tds_file = [zip_ref.extract(tds, tmpdir) for tds in zip_ref.namelist() if tds.endswith('.tds')][0]
    tds_string = os.path.basename(tds_file)

    # edit XML to change the service name
    et = xml.etree.ElementTree.parse(tds_file)
    root = et.getroot()
    filter = root.findall(xml_path)
    for item in filter:
        item.attrib['service'] = service_update   
    et.write(tds_file)

    # delete old tds from tdsx and replace it with the new one
    remove_from_zip(tdsx_path, tds_string)
    with zipfile.ZipFile(tdsx_path, 'a') as z:
        z.write(tds_file, arcname=tds_string)
        print('Successfully changed Oracle service to {service}'.format(service=service_update))
    
    # remove temp file
    shutil.rmtree(tmpdir)