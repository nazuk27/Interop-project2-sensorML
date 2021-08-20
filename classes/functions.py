import requests
from requests.structures import CaseInsensitiveDict
import xml.etree.ElementTree as ET
import xmltodict
import json
import os
import pandas as pd
class Call():
    def get_Capabilities(self, path=None):
        url = "https://sdf.ndbc.noaa.gov/sos/server.php"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/xml"
        headers["Accept"] = "application/xml"

        data = '''<?xml version="1.0" encoding="UTF-8"?>
                <GetCapabilities xmlns="http://www.opengis.net/ows/1.1" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 fragmentGetCapabilitiesRequest.xsd" service="SOS">
                  <AcceptVersions>
                    <Version>1.0.0</Version>
                  </AcceptVersions>
                  <Sections>
                    <Section>ServiceProvider</Section>
                    <Section>ServiceIdentification</Section>
                    <Section>Contents</Section>
                  </Sections>
                  <AcceptFormats>
                    <OutputFormat>text/xml</OutputFormat>
                  </AcceptFormats>
                </GetCapabilities>'''

        resp = requests.post(url, headers=headers, data=data)
        jsons = json.dumps(xmltodict.parse(resp.text))
        stations = json.loads(jsons)['sos:Capabilities']['sos:Contents']['sos:ObservationOfferingList']['sos:ObservationOffering']
        stations = list(filter(lambda x : x['gml:description'] != None, stations))[1:]
        station_data = []
        for station in stations:
            station_params = station['sos:observedProperty']
            station_obs = []
            for obs in station_params:
                try:
                    station_obs.append(obs['@xlink:href'].split('/')[-1])
                except Exception as e:
                    station_obs.append(None)
            station_data.append({
                'name': station['@gml:id'],
                'description': station['gml:description'],
                'cords': station['gml:boundedBy']['gml:Envelope']['gml:upperCorner'],
                'params': station_obs

            })
        server_details = json.loads(jsons)['sos:Capabilities']['ows:ServiceProvider']
        providerName = server_details['ows:ProviderName']
        providerSite = server_details['ows:ProviderSite']['@xlink:href']
        address = server_details['ows:ServiceContact']['ows:ContactInfo']['ows:Address']['ows:DeliveryPoint'] + ', ' + server_details['ows:ServiceContact']['ows:ContactInfo']['ows:Address']['ows:AdministrativeArea'] + ', ' + server_details['ows:ServiceContact']['ows:ContactInfo']['ows:Address']['ows:City'] + ', ' +  server_details['ows:ServiceContact']['ows:ContactInfo']['ows:Address']['ows:Country'] + ', ' + server_details['ows:ServiceContact']['ows:ContactInfo']['ows:Address']['ows:PostalCode']
        # df = pd.DataFrame.from_dict(station_data)
        # df.columns = ['cords', 'description', 'name', 'params']
        # if os.path.isfile(path + '\\classes' + '\\station_data.csv'):
        #     os.remove(path + '\\classes' + '\\station_data.csv')
        # df.to_csv(path + '\\classes' + '\\station_data.csv')
        return {'xml': resp.text,
                'providerName': providerName,
                'provideSite': providerSite,
                'address': address,
                'station': station_data}

    def descSensor(self, path):
        url = "https://sdf.ndbc.noaa.gov/sos/server.php"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/xml"
        headers["Accept"] = "application/xml"

        data = '''<?xml version="1.0" encoding="UTF-8"?>
                    <DescribeSensor xmlns="http://www.opengis.net/sos/1.0"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xmlns:sos="http://www.opengis.net/sos/1.0"
                    xsi:schemaLocation="http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
                    service="SOS" outputFormat="text/xml;subtype=&quot;sensorML/1.0.1&quot;" version="1.0.0">
                      <procedure>urn:ioos:sensor:wmo:42001::anemometer1</procedure>
                    </DescribeSensor>'''

        resp = requests.post(url, headers=headers, data=data)

        return resp.text

    def airTemp(self, path):
        filter_data = self.get_params_filter_station_data('air_temperature')
        return filter_data

    def wavesLevel(self, path):
        filter_data = self.get_params_filter_station_data('waves')
        return filter_data



    def returnData(self, resp):
        jsons = json.dumps(xmltodict.parse(resp.text))
        try:
            tree = json.loads(jsons)['om:ObservationCollection']['om:member']['om:Observation']
            gml_pos = \
            tree['om:featureOfInterest']['gml:FeatureCollection']['gml:location']['gml:MultiPoint']['gml:pointMembers'][
                'gml:Point']['gml:pos']
            station = 'Station ' + tree['om:featureOfInterest']['gml:FeatureCollection']['gml:location']['gml:MultiPoint'][
                'gml:pointMembers']['gml:Point']['gml:name'].split(':')[-1]
            values = tree['om:result']['swe2:DataStream']['swe2:values'].split('\n')
            data = []
            for val in values:
                split_val = val.split(',')
                data.append({'date': split_val[0], 'val': split_val[2]})
            return {'data': data, 'station': station, 'location': gml_pos, 'xml': resp.text}
        except Exception as e:
            text = json.loads(jsons)['ows:ExceptionReport']['ows:Exception']['ows:ExceptionText']
            return {'data': [], 'text': text}


    def get_params_filter_station_data(self, param):
        res = self.get_Capabilities()
        station_data = res['station']
        filtered_Data = []
        for station in station_data:
            if param in station['params']:
                filtered_Data.append(station)

        return filtered_Data


    def specific_sensor_data(self, sensorId, param, start_date, end_date):
        url = "https://sdf.ndbc.noaa.gov/sos/server.php"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/xml"
        headers["Accept"] = "application/xml"
        if param == 'waves':
            data = '''<?xml version="1.0" encoding="UTF-8"?>
                            <sos:GetObservation xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:om="http://www.opengis.net/om/1.0"
                            xsi:schemaLocation="http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
                            xmlns:sos="http://www.opengis.net/sos/1.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml/3.2"
                            service="SOS" version="1.0.0" srsName="EPSG:4326">
                             <sos:offering>urn:ioos:station:wmo:{0}</sos:offering>
                             <sos:eventTime>
                              <ogc:TM_During>
                               <ogc:PropertyName>om:samplingTime</ogc:PropertyName>
                               <gml:TimePeriod>
                                <gml:beginPosition>{1}</gml:beginPosition>
                                <gml:endPosition>{2}</gml:endPosition>
                               </gml:TimePeriod>
                              </ogc:TM_During>
                             </sos:eventTime>
                             <sos:observedProperty>waves</sos:observedProperty>
                             <sos:responseFormat>text/xml;subtype="om/1.0.0"</sos:responseFormat>
                             <sos:resultModel>om:Observation</sos:resultModel>
                             <sos:responseMode>inline</sos:responseMode>
                            </sos:GetObservation>'''.format(sensorId, start_date, end_date)
        else:
            data = '''<?xml version="1.0" encoding="UTF-8"?>
                    <sos:GetObservation xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:om="http://www.opengis.net/om/1.0"
                    xsi:schemaLocation="http://www.opengis.net/sos/1.0 http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
                    xmlns:sos="http://www.opengis.net/sos/1.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml/3.2"
                    service="SOS" version="1.0.0" srsName="EPSG:4326">
                      <sos:offering>urn:ioos:station:wmo:{0}</sos:offering>
                      <sos:eventTime>
                        <ogc:TM_During>
                          <ogc:PropertyName>om:samplingTime</ogc:PropertyName>
                          <gml:TimePeriod>
                            <gml:beginPosition>{1}</gml:beginPosition>
                            <gml:endPosition>{2}</gml:endPosition>
                          </gml:TimePeriod>
                        </ogc:TM_During>
                      </sos:eventTime>
                      <sos:observedProperty>air_temperature</sos:observedProperty>
                      <sos:responseFormat>text/xml;subtype="om/1.0.0"</sos:responseFormat>
                      <sos:resultModel>om:Observation</sos:resultModel>
                      <sos:responseMode>inline</sos:responseMode>
                    </sos:GetObservation>'''.format(sensorId, start_date, end_date)

        resp = requests.post(url, headers=headers, data=data)
        data = self.returnData(resp)
        return data


